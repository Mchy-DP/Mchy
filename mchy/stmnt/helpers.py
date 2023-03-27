
from mchy.common.com_types import ExecType
from mchy.errors import VirtualRepError
from mchy.stmnt.struct.atoms import SmtAtom, SmtVar
from mchy.stmnt.struct.linker import SmtExecVarLinkage, SmtLinker


def smt_get_exec_vdat(executor: SmtAtom, linker: SmtLinker) -> SmtExecVarLinkage:
    exec_type = executor.get_type()
    if not isinstance(exec_type, ExecType):
        raise VirtualRepError(f"Executor unexpectedly of type {exec_type}, ExecType required")
    if not isinstance(executor, SmtVar):
        raise VirtualRepError(f"Executor is of type {type(executor).__name__} SmtVar required")
    exec_vdat = linker.lookup_var(executor)
    if not isinstance(exec_vdat, SmtExecVarLinkage):
        raise VirtualRepError(f"Executor's variable data for `{repr(executor)}` does not include tag despite being of executable type?")
    return exec_vdat


def runtime_error_tellraw_formatter(message: str) -> str:
    return (
        r'''tellraw @p ["",'''
        + r'''{"text":"DEBUG: ","italic":true,"color":"red","hoverEvent":'''
          + r'''{"action":"show_text","contents":[{"text":"This message was emitted because the datapack was ran in debug mode","color":"red"}]}'''
        + r'''},{"text":"Runtime Error: ","bold":true,"color":"red","hoverEvent":'''
          + r'''{"action":"show_text","contents":[{"text":"Debug mode detected a problem that the compiler missed","color":"red"}]}'''
        + r'''},{"text":"'''+message.replace('"', '\\"')+r'''","color":"dark_red"}''' +
        r''']'''
    )
