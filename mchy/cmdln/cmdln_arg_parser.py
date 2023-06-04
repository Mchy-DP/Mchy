import argparse
import json
import sys
from typing import Any, Dict, List, Optional, Tuple
from mchy.common.config import Config
from mchy.common.com_logger import ComLogger
from os import path as os_path
from pathlib import Path as PathlibPath


def parse_args(args: Optional[List[str]] = None) -> Tuple[str, Config]:
    """Parse a set of arguments into a tuple containing the filename to compile and a config object"""
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "file",
        help="The '.mchy' file to compile into a datapack."
    )
    parser.add_argument(
        "-o", "--output",
        help="Output folder location, usually the datapacks folder of a minecraft world save.  Defaults to the current directory."
    )
    group_debug = parser.add_mutually_exclusive_group()
    group_debug.add_argument(
        "-d", "--debug", action="store_true",
        help="Include structures in the output datapack to aid debugging at the expense of significantly reducing datapack performance"
    )
    group_debug.add_argument(
        "--no-debug", action="store_true",
        help="Suppress debug structures.  Only required to counteract debug flag set by json config."
    )
    group_verbosity = parser.add_mutually_exclusive_group()
    group_verbosity.add_argument(
        "-v", "--verbose", action="count",
        help="Compile with extra info on the complication progress"
    )
    group_verbosity.add_argument(
        "-q", "--quiet", action="store_true",
        help="Silence all non-error output"
    )
    group_optimise = parser.add_mutually_exclusive_group()
    group_optimise.add_argument("-o1", action="store_true", help="Perform only minor optimizations with no major structural changes.")
    group_optimise.add_argument("-o2", action="store_true", help="Perform more moderate optimizations however debug should be preserved.")
    group_optimise.add_argument("-o3", action="store_true", help="Perform major optimizations maximizing the speed of the output datapack.")
    group_optimise.add_argument("-o0", action="store_true", help="Suppress optimization.  Only require to counteract optimization set by json config")
    parser.add_argument(
        "-j", "--json-config", default="./mchy_config.json",
        help=(
            "Specify the location of a json configuration file.  The file can contain values for any of the flags mentioned here but " +
            "can be overridden by also providing that option at command line.  Defaults to mchy_config.json in the current directory."
        )
    )
    parser.add_argument(
        "--log-file", help="Specify the location of the log file."
    )
    group_log_keeping = parser.add_mutually_exclusive_group()
    group_log_keeping.add_argument(
        "--overwrite-log", action="store_true", help="Overwrite the log file every time unless '--keep-log' is set."
    )
    group_log_keeping.add_argument(
        "--no-overwrite-log", action="store_true", dest="keep_log", help=(
            "Prevent the log file being overwritten. Only required to counteract --overwrite-log flag set by json config."
        )
    )
    group_backup = parser.add_mutually_exclusive_group()
    group_backup.add_argument(
        "--no-backup", action="store_true",
        help="Suppress backup creation. Improves '(5/6) Writing to disk' compiler step duration."
    )
    group_backup.add_argument(
        "--force-backup", action="store_true",
        help="Force backup creation. Only required to counteract --no-backup flag set by json config."
    )
    parser.add_argument(
        '--recursion-limit', type=int, default=None,
        help='The maximum level of recursion. Default is 32. Large values may cause slow compilations.'
    )

    pargs: argparse.Namespace = parser.parse_args(args)

    # create queue to store log messages created before the logger is initialized
    early_messages: List[Tuple[ComLogger.Level, str]] = []

    # Early print of read args
    _early_args_msg = "Read arguments: " + repr(dict(sorted(pargs.__dict__.items(), key=lambda x: x[0].lower())))
    early_messages.append((ComLogger.Level.Verbose, _early_args_msg))
    if pargs.verbose is not None and pargs.verbose >= 2:
        print(_early_args_msg)  # Very early errors may mean that logging cannot being thus print is performed immediacy if in very verbose mode

    # ==================================== Begin args parsing ==================================== #
    # === Check and load json config
    json_dict: Dict[str, Any] = {}
    if os_path.exists(pargs.json_config):
        with open(pargs.json_config) as json_file:
            json_dict = json.load(json_file)
        json_dict = {key.lstrip("-"): value for key, value in json_dict.items()}
        early_messages.append((ComLogger.Level.VeryVerbose, "json file loaded successfully"))

    # === Get Verbosity
    verbosity: int = 0
    if pargs.quiet:
        verbosity = -1
    elif pargs.verbose is not None:
        verbosity = pargs.verbose
    else:
        if "quiet" in json_dict:
            verbosity = -1
        elif "q" in json_dict:
            verbosity = -1
        elif "verbose" in json_dict:
            verbosity = json_dict["verbose"]
        elif "v" in json_dict:
            verbosity = json_dict["v"]
        # Other options provided even though not technically valid as it is clear what was intended
        elif "verbosity" in json_dict:
            verbosity = json_dict["verbosity"]
        elif "vv" in json_dict:
            verbosity = 2
    early_messages.append((ComLogger.Level.VeryVerbose, f"Verbosity is {verbosity}"))

    # === Get log file
    _log_file: Optional[str] = None
    if pargs.log_file is not None:
        _log_file = pargs.log_file
    else:
        if "log_file" in json_dict.keys():
            _log_file = json_dict["log_file"]
        elif "log-file" in json_dict.keys():
            _log_file = json_dict["log-file"]
        elif "log" in json_dict.keys():
            _log_file = json_dict["log"]
        # TODO: possibly default to log file in install location?

    log_path: Optional[str]
    if _log_file is not None:
        log_path = os_path.abspath(_log_file)
    else:
        log_path = None
    early_messages.append((ComLogger.Level.Verbose, f"Logfile '{_log_file}' read, yielding logging path '{log_path}'"))

    # === Check if overwrite log is set
    log_overwritten: bool
    if pargs.keep_log:
        log_overwritten = False
    elif pargs.overwrite_log:
        log_overwritten = True
    else:
        if "keep_log" in json_dict.keys() or "keep-log" in json_dict.keys():
            log_overwritten = False
        elif "overwrite_log" in json_dict.keys() or "overwrite-log" in json_dict.keys():
            log_overwritten = True
        else:
            log_overwritten = False  # By default do not overwrite the log

    # === Build logger
    _logger_level: ComLogger.Level
    verbosity_level: Config.Verbosity
    if verbosity == -1:
        _logger_level = ComLogger.Level.Error
        verbosity_level = Config.Verbosity.QUIET
    elif verbosity == 0:
        _logger_level = ComLogger.Level.Info
        verbosity_level = Config.Verbosity.NORMAL
    elif verbosity == 1:
        _logger_level = ComLogger.Level.Verbose
        verbosity_level = Config.Verbosity.VERBOSE
    elif verbosity == 2:
        _logger_level = ComLogger.Level.VeryVerbose
        verbosity_level = Config.Verbosity.VV
    else:
        early_messages.append((ComLogger.Level.Warn, f"Failed during startup: Invalid logging level {verbosity}, Defaulting to logging all."))
        _logger_level = ComLogger.Level.VeryVerbose
        verbosity_level = Config.Verbosity.VV

    logger = ComLogger(_logger_level, "MAIN", logging_file_path=log_path, overwrite_logfile=log_overwritten)
    logger.info("======= Logging beginning =======")

    # === Empty early logs queue:
    for level, msg in early_messages:
        logger.log(level, "Early: "+msg)
    logger.very_verbose("Early Logs complete")

    # === Get output file location
    _output_file: str
    if pargs.output is None:
        if "output" in json_dict.keys():
            _output_file = json_dict["output"]
        elif "o" in json_dict.keys():
            _output_file = json_dict["o"]
        else:
            _output_file = "./"
    else:
        _output_file = pargs.output

    output_path: str = os_path.abspath(_output_file)
    logger.very_verbose(f"Output file '{_output_file}' requested, absolute path is '{output_path}'")

    # === Get debug structures requested
    mchy_debug: bool
    if pargs.no_debug:
        mchy_debug = False
    elif pargs.debug:
        mchy_debug = True
    else:
        if "no_debug" in json_dict.keys() or "no-debug" in json_dict.keys():
            mchy_debug = False
        elif "debug" in json_dict.keys():
            mchy_debug = True
        else:
            mchy_debug = Config.DEFAULT_DEBUG_MODE

    # === Get Optimization Level
    optimization: Config.Optimize
    if pargs.o0:
        optimization = Config.Optimize.NOTHING
    elif pargs.o3:
        optimization = Config.Optimize.O3
    elif pargs.o2:
        optimization = Config.Optimize.O2
    elif pargs.o1:
        optimization = Config.Optimize.O1
    else:
        if "o0" in json_dict.keys() or "O0" in json_dict.keys():
            optimization = Config.Optimize.NOTHING
        elif "o3" in json_dict.keys() or "O3" in json_dict.keys():
            optimization = Config.Optimize.O3
        elif "o2" in json_dict.keys() or "O2" in json_dict.keys():
            optimization = Config.Optimize.O2
        elif "o1" in json_dict.keys() or "O1" in json_dict.keys():
            optimization = Config.Optimize.O1
        else:
            optimization = Config.Optimize.NOTHING

    # === Get backup needed
    do_backup: bool
    if pargs.force_backup:
        do_backup = True
    elif pargs.no_backup:
        do_backup = False
    else:
        if "backup" in json_dict.keys() or "force_backup" in json_dict.keys() or "force-backup" in json_dict.keys():
            do_backup = True
        elif "no_backup" in json_dict.keys() or "no-backup" in json_dict.keys():
            do_backup = False
        else:
            do_backup = Config.DEFAULT_DO_BACKUP

    # === Get recursion limit
    recursion_limit: int
    if pargs.recursion_limit is not None:
        recursion_limit = pargs.recursion_limit
    else:
        if "recursion_limit" in json_dict.keys():
            recursion_limit = json_dict["recursion_limit"]
        elif "recursion-limit" in json_dict.keys():
            recursion_limit = json_dict["recursion-limit"]
        else:
            recursion_limit = Config.DEFAULT_RECURSION_LIMIT

    # === Get mchy file
    _mchy_file = pargs.file
    mchy_file_path = os_path.abspath(_mchy_file)
    if os_path.exists(mchy_file_path):
        logger.very_verbose(f"Input file '{_mchy_file}' requested, Found at '{mchy_file_path}'")
    else:
        logger.error(f"File-Not-Found: Input file '{_mchy_file}' could not be found at '{mchy_file_path}'")
        sys.exit(1)
    if os_path.splitext(mchy_file_path)[1] != ".mchy":
        logger.warn(f"Input file '{_mchy_file}' has extension '{os_path.splitext(mchy_file_path)[1]}', '.mchy' expected - double check file is correct?")

    # === Get project name/namespace
    project_namespace = (PathlibPath(mchy_file_path).stem).lower().replace(" ", "_")
    project_name = project_namespace.replace("_", " ").title()

    return (mchy_file_path, Config(
        project_name=project_name,
        project_namespace=project_namespace,
        recursion_limit=recursion_limit,
        logger=logger,
        output_path=output_path,
        debug_mode=mchy_debug,
        verbosity=verbosity_level,
        optimisation=optimization,
        do_backup=do_backup
    ))
