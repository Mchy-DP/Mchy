
import enum
import logging
import sys
import inspect
from typing import Optional, Set, Tuple
import os
from os import path as os_path


class _StringRef():

    def __init__(self) -> None:
        self._value: Optional[str] = None

    def set_value(self, value: str):
        self._value = value

    @property
    def value(self) -> str:
        if self._value is not None:
            return self._value
        raise ValueError("Value requested before assignment")


class ComLogger:

    _INITIALIZED_LOGGERS: Set[str] = set()

    class Level(enum.Enum):
        VeryVerbose = 5  # Detailed updates on compiling progress
        Verbose = 9      # Broad updates on compiling progress
        Info = 20        # Default StdOut visible
        Warn = 30
        Error = 40       # Quiet will only let Error through

    def __init__(self, std_out_level: Level, unique_name: str, logging_file_path: Optional[str] = None, overwrite_logfile: bool = False) -> None:
        self._level: ComLogger.Level = std_out_level
        self._logging_file: Optional[str] = logging_file_path
        self._overwrite_logfile: bool = overwrite_logfile
        self._logging_fname: _StringRef = _StringRef()
        self._logging_fline: _StringRef = _StringRef()
        if unique_name in ComLogger._INITIALIZED_LOGGERS:
            raise ValueError(f"Logging wrapper with unique name `{unique_name}` double initialized")
        self._logger = logging.getLogger(f"MCHY-{unique_name}")
        self._logger.setLevel(ComLogger.Level.VeryVerbose.value if logging_file_path is not None else std_out_level.value)
        logging.addLevelName(9, 'VERBOSE')
        logging.addLevelName(5, 'VV')

        _current_logging_file_name = self._logging_fname
        _current_logging_file_line = self._logging_fline

        class RecordDataFilter(logging.Filter):
            def filter(self, record):
                record.calling_name = _current_logging_file_name.value
                record.calling_line = _current_logging_file_line.value
                return True

        # Add stdout logger in VeryVerbose mode
        if std_out_level.value <= ComLogger.Level.VeryVerbose.value:
            stdout_handle = logging.StreamHandler(sys.stdout)
            stdout_handle.setLevel(std_out_level.value)
            stdout_handle.setFormatter(logging.Formatter('%(levelname)8s@%(calling_name)24s::%(calling_line)-4s: %(message)s'))
            stdout_handle.addFilter(lambda record: record.levelno <= ComLogger.Level.Info.value)
            stdout_handle.addFilter(RecordDataFilter())  # type: ignore  # false positive
            self._logger.addHandler(stdout_handle)

        # Add stderr logger
        stderr_handle = logging.StreamHandler(sys.stderr)
        stderr_handle.setLevel(max(ComLogger.Level.Warn.value, std_out_level.value))
        stderr_handle.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        stderr_handle.addFilter(RecordDataFilter())  # type: ignore  # false positive
        self._logger.addHandler(stderr_handle)

        # Add file logger if defined
        if logging_file_path is not None:
            if self._overwrite_logfile and os_path.exists(logging_file_path):
                os.remove(logging_file_path)
            log_file_handle = logging.FileHandler(logging_file_path)
            log_file_handle.setLevel(ComLogger.Level.VeryVerbose.value)
            log_file_handle.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)8s@%(calling_name)24s::%(calling_line)-4s: %(message)s'))
            log_file_handle.addFilter(RecordDataFilter())  # type: ignore  # false positive
            self._logger.addHandler(log_file_handle)

    def _update_context(self) -> None:
        try:
            # Type may result in AttributeError's which are caught hence type checker warnings are disabled
            func_path = __file__
            frame = inspect.currentframe()
            while func_path == __file__:
                frame = frame.f_back  # type: ignore
                func_path: str = frame.f_code.co_filename  # type: ignore
            func_line: str = str(frame.f_lineno)  # type: ignore
        except AttributeError:
            self._logging_fname.set_value("unknown?")
            self._logging_fline.set_value("###")
        else:
            # Try to limit the path to only mchy files
            try:
                relative_path = func_path.split("mchy", 1)[1]
            except IndexError:
                relative_path = func_path
            func_path_comps: list[str] = relative_path.split(os_path.sep)
            func_path_comps_r = list(reversed(func_path_comps))  # reversed so that pop removes the start of the path
            while len(func_path_comps_r) >= 2 and len(os_path.sep.join(func_path_comps_r)) > 21:  # 21 = (calling_name format string max len) - 3
                func_path_comps_r.pop()

            # extract sections from remaining path
            file_name = func_path_comps_r[0]
            extra_rel_info = "("+"/".join(reversed(func_path_comps_r[1:]))+") " if len(func_path_comps_r) > 1 else ""

            # update referenced values
            self._logging_fname.set_value(extra_rel_info + file_name)
            self._logging_fline.set_value(func_line)

    def trace(self, msg: str) -> None:
        pass  # Currently unused - May in the future be added for prints which would make the log-file difficult to read if included normally

    def very_verbose(self, msg: str) -> None:
        self._update_context()
        self._logger.log(ComLogger.Level.VeryVerbose.value, msg)

    def verbose(self, msg: str) -> None:
        self._update_context()
        self._logger.log(ComLogger.Level.Verbose.value, msg)

    def verbose_print(self, msg: str) -> None:
        self._update_context()
        if self._level.value <= ComLogger.Level.Verbose.value:
            self._logger.log(ComLogger.Level.Verbose.value, "VPrinting: "+repr(msg)[1:-1])
            print(msg)
        else:
            self._logger.log(ComLogger.Level.Verbose.value, "Suppressed VPrinting: "+repr(msg)[1:-1])

    def info(self, msg: str) -> None:
        self._update_context()
        self._logger.log(ComLogger.Level.Info.value, msg)

    def print(self, msg: str) -> None:
        self._update_context()
        if self._level.value <= ComLogger.Level.Info.value:
            self._logger.log(ComLogger.Level.Info.value, "IPrinting: "+repr(msg)[1:-1])
            print(msg)
        else:
            self._logger.log(ComLogger.Level.Info.value, "Suppressed IPrinting: "+repr(msg)[1:-1])

    def warn(self, msg: str) -> None:
        self._update_context()
        self._logger.log(ComLogger.Level.Warn.value, msg)

    def error(self, msg: str) -> None:
        self._update_context()
        self._logger.log(ComLogger.Level.Error.value, msg)

    def log(self, level: Level, msg: str) -> None:
        if level == ComLogger.Level.VeryVerbose:
            self.very_verbose(msg)
        elif level == ComLogger.Level.Verbose:
            self.verbose(msg)
        elif level == ComLogger.Level.Info:
            self.info(msg)
        elif level == ComLogger.Level.Warn:
            self.warn(msg)
        elif level == ComLogger.Level.Error:
            self.error(msg)
        else:
            self.error(f"Unknown msg level `{level}` found while trying to log `{msg}`")
