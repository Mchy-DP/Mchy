from typing import Tuple
from mchy.contextual.struct.module import CtxModule
from mchy.mchy_ast.convert_parse import mchy_parse
from mchy.mchy_ast.nodes import Root as ASTRoot
from mchy.contextual.generation import convert as conv_ast_cst
from mchy.stmnt.generation import convert as conv_cst_smt
from mchy.virtual.generation import convert as conv_smt_vir
from mchy.common.config import Config

from mchy.stmnt.struct.module import SmtModule
from mchy.virtual.vir_dp import VirDP
from typing import List
from mchy.virtual.vir_dirs import VirFolder, VirMCHYFile
import re


def conversion_helper(code: str) -> Tuple[ASTRoot, CtxModule, SmtModule, VirDP]:
    config: Config = Config()
    # TEXT -> AST
    ast_root_node: ASTRoot = mchy_parse(code, config)

    # AST -> CST
    ctx_module: CtxModule = conv_ast_cst(ast_root_node, config=config)

    # CST -> SmtRep
    smt_module: SmtModule = conv_cst_smt(ctx_module, config=config)

    # SmtRep -> VirtualDP
    vir_dp: VirDP = conv_smt_vir(smt_module, config=config)

    return (ast_root_node, ctx_module, smt_module, vir_dp)


def get_lines_matching(file: VirMCHYFile, regex_pattern: str) -> List[str]:
    output: List[str] = []
    compiled_regex = re.compile(regex_pattern)
    for line in file.lines:
        if compiled_regex.match(line.cmd):
            output.append(line.cmd)
    return output


def any_line_matches(file: VirMCHYFile, regex_pattern: str) -> bool:
    return len(get_lines_matching(file, regex_pattern)) >= 1


def get_file_matching_name(folder: VirFolder, regex_pattern: str) -> VirMCHYFile:
    output: List[VirMCHYFile] = []
    compiled_regex = re.compile(regex_pattern)
    for file in folder.children:
        if isinstance(file, VirMCHYFile) and compiled_regex.match(file.fs_name):
            output.append(file)

    if len(output) == 0:
        raise ValueError(f"No file matching r\"/{regex_pattern}/\" in directory {folder.fs_name}.  Files scanned: {', '.join(child.fs_name for child in folder.children)}")
    if len(output) >= 2:
        raise ValueError(f"Multiple files match r\"/{regex_pattern}/\" in directory {folder.fs_name}.  Files found: {', '.join(child.fs_name for child in output)}")
    return output[0]


def get_folder_matching_name(parent_folder: VirFolder, regex_pattern: str) -> VirFolder:
    output: List[VirFolder] = []
    compiled_regex = re.compile(regex_pattern)
    for folder in parent_folder.children:
        if isinstance(folder, VirFolder) and compiled_regex.match(folder.fs_name):
            output.append(folder)

    if len(output) == 0:
        raise ValueError(
            f"No child folder matching r\"/{regex_pattern}/\" in directory {parent_folder.fs_name}.  " +
            f"Scanned: {', '.join(child.fs_name for child in parent_folder.children)}"
        )
    if len(output) >= 2:
        raise ValueError(f"Multiple files match r\"/{regex_pattern}/\" in directory {parent_folder.fs_name}.  Found: {', '.join(child.fs_name for child in output)}")
    return output[0]
