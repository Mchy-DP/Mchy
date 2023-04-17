
from mchy.cmd_modules.name_spaces import Namespace
from mchy.cmdln.late_err_intercepts import perform_intercepts
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ExecCoreTypes, ExecType
from mchy.contextual.struct.module import CtxModule
from mchy.errors import ConversionError
from mchy.common.config import Config


def test_perform_intercepts_partial_chain():
    # Build module
    ctx_module = CtxModule(Config())
    ctx_module.import_ns(Namespace.get_namespace("std"))

    # get `get_players` chainlink
    _get_players_ctx_clink = ctx_module.get_chain_link(ExecType(ExecCoreTypes.WORLD, False), "get_players", ComLoc())
    get_players_iclink = _get_players_ctx_clink.ichainlink

    # Build error
    err = ConversionError("Test error")
    err.with_intercept(ConversionError.InterceptFlags.PARTIAL_CHAIN_OPTIONS, get_players_iclink)

    # Attempt intercept
    perform_intercepts(err, None, ctx_module, None, None)

    # Test intercept succeeded
    assert ".find()" in err.msg
