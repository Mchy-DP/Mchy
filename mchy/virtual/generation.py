
from typing import List, Sequence
from mchy.common.config import Config
from mchy.stmnt.helpers import runtime_error_tellraw_formatter
from mchy.stmnt.struct.cmds import SmtRawCmd
from mchy.stmnt.struct.cmds.assign import SmtAssignCmd
from mchy.stmnt.struct.linker import SmtLinker, SmtVarFlavour
from mchy.stmnt.struct import SmtModule, SmtMchyFunc, SmtCmd, SmtCommentCmd, CommentImportance
from mchy.common.com_cmd import ComCmd
from mchy.stmnt.tag_cleanup import get_cleanup_stmnts
from mchy.virtual.vir_dirs import VirFolder, VirMCHYFile
from mchy.virtual.vir_dp import VirDP


def convert(smt_module: SmtModule, config: Config = Config()) -> VirDP:
    vir_dp = VirDP(config)

    # ===== Linker Building =====
    # Build function linking
    config.logger.very_verbose(f"VIR: Building function loc linking table")
    vir_dp.linker.add_func(smt_module.import_ns_function, vir_dp.import_param_default_file.get_namespace_loc())
    for smt_func in smt_module.get_smt_mchy_funcs():
        for rix in range(0, config.recursion_limit + 1):  # Plus 1 as the recursion error technically happens 1 stack frame deeper
            vir_dp.linker.add_func(
                smt_func,
                f"{vir_dp.mchy_func_fld.get_namespace_loc()}/{smt_func.get_unique_ident()}/s{rix}/",
                rix
            )
    vir_dp.linker.add_frag_path_override(smt_module.import_ns_function, vir_dp.extra_frags_import_ns.get_namespace_loc())
    vir_dp.linker.add_frag_path_override(smt_module.setup_function, vir_dp.extra_frags_setup.get_namespace_loc())
    vir_dp.linker.add_frag_path_override(smt_module.initial_function, vir_dp.extra_frags_init.get_namespace_loc())
    vir_dp.linker.add_frag_path_override(smt_module.ticking_function, vir_dp.extra_frags_tick.get_namespace_loc())

    # Build scoreboard & storage linking
    config.logger.very_verbose(f"VIR: Building Scoreboard & storage loc linking table")
    for var in smt_module.initial_function.get_all_vars():
        vir_dp.linker.add_bland_var(var, ["mchy_glob"], stackless=True)
    for var in smt_module.setup_function.get_all_vars():
        vir_dp.linker.add_bland_var(var, ["mchy_extra", "setup"], stackless=True)
    for var in smt_module.ticking_function.get_all_vars():
        vir_dp.linker.add_bland_var(var, ["mchy_extra", "ticking"], stackless=True)
    for var in smt_module.import_ns_function.get_all_vars():
        vir_dp.linker.add_bland_var(var, ["mchy_extra", "import"], stackless=True)
    for smt_func in smt_module.get_smt_mchy_funcs():
        for var in smt_func.get_all_vars():
            if var == smt_func.executor_var:
                vir_dp.linker.add_bland_var(var, ["mchy_func", smt_func.get_unique_ident()], stackless=False, var_type=SmtVarFlavour.VAR, this_override=True)
            else:
                vir_dp.linker.add_mchy_var(var, smt_func)

    # ===== Command generation =====
    load_master_tag_cleanup: List[ComCmd] = []

    # build core files:
    # setup error state compiler util
    _extra_error_state_begin = VirMCHYFile("error_state_begin.mcfunction", vir_dp.compiler_util_fld)
    _extra_error_state_core = VirMCHYFile("error_state_core.mcfunction", vir_dp.compiler_util_fld)
    _extra_error_state_begin.extend(convert_smtcmds([SmtAssignCmd(smt_module.error_state_variable, smt_module.get_const_with_val(1))], vir_dp.linker, 0, config))
    _extra_error_state_begin.append(ComCmd(f"function {_extra_error_state_core.get_namespace_loc()}"))
    _extra_error_state_core.append(ComCmd(f"function {_extra_error_state_core.get_namespace_loc()}"))

    # Add required scoreboard objectives
    config.logger.very_verbose(f"VIR: Adding scoreboard objective creation commands to load_master file")
    vir_dp.load_master_file.extend(SmtCommentCmd("Build Scoreboard", generator="MCHY", importance=CommentImportance.TITLE).virtualize(vir_dp.linker, 0))
    for obj in vir_dp.linker.get_all_sb_objs():
        vir_dp.load_master_file.append(ComCmd(f"scoreboard objectives add {obj} dummy"))

    # Add constants
    config.logger.very_verbose(f"VIR: Adding scoreboard const creation commands to load_master file")
    vir_dp.load_master_file.extend(SmtCommentCmd("Build Scoreboard Constants", generator="MCHY", importance=CommentImportance.TITLE).virtualize(vir_dp.linker, 0))
    vir_dp.load_master_file.append(ComCmd(f"scoreboard objectives add {vir_dp.linker.get_const_obj()} dummy"))
    for const_val in smt_module.get_all_int_consts():
        vir_dp.load_master_file.append(ComCmd(f"scoreboard players set c{const_val.value} {vir_dp.linker.get_const_obj()} {const_val.value}"))

    # Add import_ns work and setup to the load master file
    config.logger.very_verbose(f"VIR: Adding Initial setup to the load_master file")
    vir_dp.load_master_file.extend(SmtCommentCmd("Setup", generator="MCHY", importance=CommentImportance.TITLE).virtualize(vir_dp.linker, 0))
    vir_dp.load_master_file.extend(convert_smtcmds(smt_module.setup_function.func_frag.body, vir_dp.linker, 0, config=config))
    load_master_tag_cleanup.extend(convert_smtcmds(get_cleanup_stmnts(smt_module.setup_function, vir_dp.linker, 0), vir_dp.linker, 0, config))

    # Add top-level scope to load master file
    config.logger.very_verbose(f"VIR: Building top-level scope into load_master file")
    vir_dp.load_master_file.extend(SmtCommentCmd("Top-Level Scope", generator="MCHY", importance=CommentImportance.TITLE).virtualize(vir_dp.linker, 0))
    top_level_commands: List[ComCmd] = convert_smtcmds(smt_module.initial_function.func_frag.body, vir_dp.linker, 0, config=config)
    if config.testing_comments:
        vir_dp.load_master_file.append(ComCmd("# TESTING: top-level-start"))
    vir_dp.load_master_file.extend(top_level_commands)
    if config.testing_comments:
        vir_dp.load_master_file.append(ComCmd("# TESTING: top-level-end"))
    load_master_tag_cleanup.extend(convert_smtcmds(get_cleanup_stmnts(smt_module.initial_function, vir_dp.linker, 0), vir_dp.linker, 0, config))
    if len(load_master_tag_cleanup) >= 1:
        vir_dp.load_master_file.extend(SmtCommentCmd("Global Scope Tag Cleanup", generator="MCHY", importance=CommentImportance.TITLE).virtualize(vir_dp.linker, 0))
        vir_dp.load_master_file.extend(load_master_tag_cleanup)

    # Add ticking commands to tick master file
    config.logger.very_verbose(f"VIR: Building master tick in tick_master file")
    vir_dp.tick_master_file.extend(SmtCommentCmd("Calling Ticking Functions", generator="MCHY", importance=CommentImportance.TITLE).virtualize(vir_dp.linker, 0))
    tick_commands: List[ComCmd] = convert_smtcmds(smt_module.ticking_function.func_frag.body, vir_dp.linker, 0, config=config)
    if config.testing_comments:
        vir_dp.tick_master_file.append(ComCmd("# TESTING: tick-call-start"))
    vir_dp.tick_master_file.extend(tick_commands)
    if config.testing_comments:
        vir_dp.tick_master_file.append(ComCmd("# TESTING: tick-call-end"))

    # Rendering special-case fragments
    config.logger.very_verbose(f"VIR: Building special fragments")
    for frag in smt_module.import_ns_function.fragments:
        frag_file = VirMCHYFile(frag.get_frag_name()+".mcfunction", vir_dp.extra_frags_import_ns)
        frag_file.extend(convert_smtcmds(frag.body, vir_dp.linker, 0, config=config))
    for frag in smt_module.setup_function.fragments:
        frag_file = VirMCHYFile(frag.get_frag_name()+".mcfunction", vir_dp.extra_frags_setup)
        frag_file.extend(convert_smtcmds(frag.body, vir_dp.linker, 0, config=config))
    for frag in smt_module.initial_function.fragments:
        frag_file = VirMCHYFile(frag.get_frag_name()+".mcfunction", vir_dp.extra_frags_init)
        frag_file.extend(convert_smtcmds(frag.body, vir_dp.linker, 0, config=config))

    # handle functions
    for smt_func in smt_module.get_smt_mchy_funcs():
        vir_dp.mchy_func_fld.add_child(convert_mchy_func(smt_func, vir_dp, config, _extra_error_state_begin))

    return vir_dp


def convert_mchy_func(smt_func: SmtMchyFunc, vir_dp: VirDP, config: Config, error_endpoint: VirMCHYFile) -> VirFolder:
    func_fld = VirFolder(smt_func.get_unique_ident())
    for rix in range(0, config.recursion_limit + 1):
        sn_fld = VirFolder(f"s{rix}", func_fld)
        fragments = VirFolder("fragments", sn_fld)
        run_file = VirMCHYFile("run.mcfunction", sn_fld)
        if rix < config.recursion_limit:
            run_file.extend(convert_smtcmds(smt_func.func_frag.body, vir_dp.linker, rix, config))
            for frag in smt_func.fragments:
                frag_file = VirMCHYFile(frag.get_frag_name()+".mcfunction", fragments)
                frag_file.extend(convert_smtcmds(frag.body, vir_dp.linker, rix, config))
            run_file.extend(convert_smtcmds(get_cleanup_stmnts(smt_func, vir_dp.linker, rix), vir_dp.linker, rix, config))
        else:
            # Recursion limit runtime error:
            run_file.extend(convert_smtcmds([
                SmtRawCmd(runtime_error_tellraw_formatter(f"recursion limit ({config.recursion_limit}) reached in function `{smt_func.get_func_name()}`", debug=False)),
                ], vir_dp.linker, rix, config
            ))
            run_file.append(ComCmd(f"function {error_endpoint.get_namespace_loc()}"))
    return func_fld


def convert_smtcmds(smt_cmds: Sequence[SmtCmd], linker: SmtLinker, stack_level: int, config: Config) -> List[ComCmd]:
    vir_cmds: List[ComCmd] = []
    for smt_cmd in smt_cmds:
        if stack_level == 0:
            config.logger.very_verbose(f"VIR: generating commands for {repr(smt_cmd)})")
        else:
            config.logger.trace(f"VIR: generating commands for {repr(smt_cmd)})")
        vir_cmds.extend(smt_cmd.virtualize(linker, stack_level))
    return vir_cmds
