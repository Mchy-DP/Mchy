
import traceback
from mchy.contextual.struct.module import CtxModule
from mchy.errors import ConversionError
from mchy.mchy_ast.convert_parse import mchy_parse
from mchy.mchy_ast.nodes import Root as ASTRoot
from mchy.contextual.generation import convert as conv_ast_cst
from mchy.stmnt.generation import convert as conv_cst_smt
from mchy.virtual.generation import convert as conv_smt_vir
from mchy.cmdln.cmdln_arg_parser import parse_args
from mchy.common.config import Config
from os import path as os_path

from mchy.stmnt.struct.module import SmtModule
from mchy.virtual.vir_dp import VirDP


def main_by_cmdln():
    """The main entry point for the program when ran via the command line"""
    filename, config = parse_args()
    file_path = os_path.abspath(filename)
    if not os_path.exists(file_path):
        print(f"File '{filename}' could not be found.  Looking at location: '{file_path}'")
    with open(file_path) as file:
        file_text = file.read()

    return main_by_arg(file_text, config)


def main_by_arg(file_text: str, config: Config):
    """The main entry point for the program when called directly from code"""
    config.logger.verbose_print(f"Compiling Project '{config.project_name}'" + (" with debug enabled" if config.debug_mode else ""))
    config.logger.very_verbose(f"src code: {repr(file_text)}")
    try:
        config.logger.verbose_print("(1/6) Beginning Compilation")
        # TEXT -> AST
        ast_root_node: ASTRoot = mchy_parse(file_text, config)

        config.logger.verbose_print("(2/6) Resolving Contextual Information")
        # AST -> CST
        ctx_module: CtxModule = conv_ast_cst(ast_root_node, config=config)

        config.logger.verbose_print("(3/6) Statement Linking")
        # CST -> SmtRep
        smt_module: SmtModule = conv_cst_smt(ctx_module, config=config)

        config.logger.verbose_print("(4/6) Generating Virtual Commands")
        # SmtRep -> VirtualDP
        vir_dp: VirDP = conv_smt_vir(smt_module, config=config)

        config.logger.verbose_print("(5/6) Writing to disk")
        # write DP to disk
        vir_dp.write_to_disk()

        if config.verbosity.value >= config.Verbosity.VERBOSE.value:
            config.logger.verbose_print("")  # Print an empty line to aid readability in verbose mode
        config.logger.print("Compilation Successful!")
    except ConversionError as err:
        config.logger.very_verbose("Conversion Error: "+repr(err))
        config.logger.error(err.msg())
    except Exception as err:
        config.logger.very_verbose("Compiler Error: "+traceback.format_exc())
        config.logger.very_verbose("Compiler Error: "+repr(err))
        config.logger.error("Compiler Error: "+str(err))
