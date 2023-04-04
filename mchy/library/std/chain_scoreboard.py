from typing import Collection, Dict, List, Optional, Sequence, Tuple, Type, Union

from mchy.cmd_modules.chains import IChain, IChainLink
from mchy.cmd_modules.function import IParam
from mchy.cmd_modules.helper import NULL_CTX_TYPE, get_exec_vdat, get_key_with_type, get_link_of_type
from mchy.cmd_modules.name_spaces import Namespace
from mchy.common.com_cmd import ComCmd
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType, TypeUnion, matches_type
from mchy.common.config import Config
from mchy.contextual.struct.expr import CtxExprLitStr, CtxExprLits, CtxExprNode, CtxChainLink
from mchy.contextual.struct.expr.literals import CtxExprLitNull
from mchy.errors import ConversionError, StatementRepError, VirtualRepError
from mchy.library.std.ns import STD_NAMESPACE
from mchy.library.std.struct_color import StructColor
from mchy.stmnt.struct import SmtAtom, SmtCmd, SmtFunc, SmtModule
from mchy.stmnt.struct.atoms import SmtConstInt, SmtConstStr, SmtStruct, SmtVar
from mchy.stmnt.struct.linker import SmtLinker, SmtObjVarLinkage


# Statements
class SmtSbAddObjCmd(SmtCmd):

    def __init__(self, obj_name: str, obj_type: str) -> None:
        self.obj_name: str = obj_name
        self.obj_type: str = obj_type

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.obj_name}, obj_type={self.obj_type})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        return [ComCmd(f"scoreboard objectives add {self.obj_name} {self.obj_type}")]


class SmtSbRemoveObjCmd(SmtCmd):

    def __init__(self, obj_name: str) -> None:
        self.obj_name: str = obj_name

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.obj_name})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        return [ComCmd(f"scoreboard objectives remove {self.obj_name}")]


class SmtSbSetDisplayObjCmd(SmtCmd):

    def __init__(self, obj_name: str, display_loc: str) -> None:
        self.obj_name: str = obj_name
        self.display_loc: str = display_loc

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.obj_name}, display_loc={self.display_loc})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        return [ComCmd(f"scoreboard objectives setdisplay {self.display_loc} {self.obj_name}")]


class SmtSbJsonNameObjCmd(SmtCmd):

    def __init__(self, obj_name: str, json_name: str) -> None:
        self.obj_name: str = obj_name
        self.json_name: str = json_name

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.obj_name}, json={self.json_name})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        return [ComCmd(f"scoreboard objectives modify {self.obj_name} displayname {self.json_name}")]


class SmtSbHeartObjCmd(SmtCmd):

    def __init__(self, obj_name: str, render_hearts: bool) -> None:
        self.obj_name: str = obj_name
        self.render_hearts: bool = render_hearts

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.obj_name})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        return [ComCmd(f"scoreboard objectives modify {self.obj_name} rendertype {'hearts' if self.render_hearts else 'integer'}")]


class SmtSbObjGetExecCmd(SmtCmd):

    def __init__(self, executor: SmtAtom, obj_name: str, variable: SmtVar) -> None:
        self.executor: SmtAtom = executor
        self.obj_name: str = obj_name
        self.variable: SmtVar = variable

    def __repr__(self) -> str:
        return f"{type(self).__name__}(executor={repr(self.executor)}, obj={self.obj_name}, var={self.variable})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        exec_vdat = get_exec_vdat(self.executor, linker)
        out_vdat = linker.lookup_var(self.variable)
        if not isinstance(out_vdat, SmtObjVarLinkage):
            raise VirtualRepError(f"Output register for `{repr(self.variable)}` does not have attached scoreboard?")
        return [ComCmd(
            f"execute store result score {out_vdat.var_name} {out_vdat.get_objective(stack_level)} run " +
            f"scoreboard players get {exec_vdat.get_selector(stack_level)} {self.obj_name}"
        )]


class SmtSbObjSetExecCmd(SmtCmd):

    def __init__(self, executor: SmtAtom, obj_name: str, value: SmtAtom) -> None:
        self.executor: SmtAtom = executor
        self.obj_name: str = obj_name
        self.value: SmtAtom = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}(executor={repr(self.executor)}, obj={self.obj_name}, value={self.value})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        exec_vdat = get_exec_vdat(self.executor, linker)

        if isinstance(self.value, SmtVar):
            value_vdat = linker.lookup_var(self.value)
            if not isinstance(value_vdat, SmtObjVarLinkage):
                raise VirtualRepError(f"Output register for `{repr(self.value)}` does not have attached scoreboard?")
            return [ComCmd(
                f"scoreboard players operation {exec_vdat.get_selector(stack_level)} {self.obj_name} = {value_vdat.var_name} {value_vdat.get_objective(stack_level)}"
            )]
        elif isinstance(self.value, SmtConstInt):
            return [ComCmd(
                f"scoreboard players set {exec_vdat.get_selector(stack_level)} {self.obj_name} {self.value.value}"
            )]
        else:
            raise VirtualRepError(f"Unknown atom type `{type(self.value).__name__}` found in `{type(self).__name__}`")


class SmtSbObjAddExecCmd(SmtCmd):

    def __init__(self, executor: SmtAtom, obj_name: str, value: SmtAtom) -> None:
        self.executor: SmtAtom = executor
        self.obj_name: str = obj_name
        self.value: SmtAtom = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}(executor={repr(self.executor)}, obj={self.obj_name}, value={self.value})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        exec_vdat = get_exec_vdat(self.executor, linker)

        if isinstance(self.value, SmtVar):
            value_vdat = linker.lookup_var(self.value)
            if not isinstance(value_vdat, SmtObjVarLinkage):
                raise VirtualRepError(f"Output register for `{repr(self.value)}` does not have attached scoreboard?")
            return [ComCmd(
                f"scoreboard players operation {exec_vdat.get_selector(stack_level)} {self.obj_name} += {value_vdat.var_name} {value_vdat.get_objective(stack_level)}"
            )]
        elif isinstance(self.value, SmtConstInt):
            return [ComCmd(
                f"scoreboard players add {exec_vdat.get_selector(stack_level)} {self.obj_name} {self.value.value}"
            )]
        else:
            raise VirtualRepError(f"Unknown atom type `{type(self.value).__name__}` found in `{type(self).__name__}`")


class SmtSbObjSubtractExecCmd(SmtCmd):

    def __init__(self, executor: SmtAtom, obj_name: str, value: SmtAtom) -> None:
        self.executor: SmtAtom = executor
        self.obj_name: str = obj_name
        self.value: SmtAtom = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}(executor={repr(self.executor)}, obj={self.obj_name}, value={self.value})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        exec_vdat = get_exec_vdat(self.executor, linker)

        if isinstance(self.value, SmtVar):
            value_vdat = linker.lookup_var(self.value)
            if not isinstance(value_vdat, SmtObjVarLinkage):
                raise VirtualRepError(f"Output register for `{repr(self.value)}` does not have attached scoreboard?")
            return [ComCmd(
                f"scoreboard players operation {exec_vdat.get_selector(stack_level)} {self.obj_name} -= {value_vdat.var_name} {value_vdat.get_objective(stack_level)}"
            )]
        elif isinstance(self.value, SmtConstInt):
            return [ComCmd(
                f"scoreboard players remove {exec_vdat.get_selector(stack_level)} {self.obj_name} {self.value.value}"
            )]
        else:
            raise VirtualRepError(f"Unknown atom type `{type(self.value).__name__}` found in `{type(self).__name__}`")


class SmtSbObjResetExecCmd(SmtCmd):

    def __init__(self, executor: SmtAtom, obj_name: str) -> None:
        self.executor: SmtAtom = executor
        self.obj_name: str = obj_name

    def __repr__(self) -> str:
        return f"{type(self).__name__}(executor={repr(self.executor)}, obj={self.obj_name})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        exec_vdat = get_exec_vdat(self.executor, linker)
        return [ComCmd(
            f"scoreboard players reset {exec_vdat.get_selector(stack_level)} {self.obj_name}"
        )]


class SmtSbObjFullResetExecCmd(SmtCmd):

    def __init__(self, executor: SmtAtom) -> None:
        self.executor: SmtAtom = executor

    def __repr__(self) -> str:
        return f"{type(self).__name__}(executor={repr(self.executor)})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        exec_vdat = get_exec_vdat(self.executor, linker)
        return [ComCmd(
            f"scoreboard players reset {exec_vdat.get_selector(stack_level)}"
        )]


class SmtSbObjEnableExecCmd(SmtCmd):

    def __init__(self, executor: SmtAtom, obj_name: str) -> None:
        self.executor: SmtAtom = executor
        self.obj_name: str = obj_name

    def __repr__(self) -> str:
        return f"{type(self).__name__}(executor={repr(self.executor)}, obj={self.obj_name})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        exec_vdat = get_exec_vdat(self.executor, linker)
        return [ComCmd(
            f"scoreboard players enable {exec_vdat.get_selector(stack_level)} {self.obj_name}"
        )]


class SmtSbObjPlayGetCmd(SmtCmd):

    def __init__(self, obj_name: str, player_name: str, variable: SmtVar) -> None:
        self.obj_name: str = obj_name
        self.player_name: str = player_name
        self.variable: SmtVar = variable

    def __repr__(self) -> str:
        return f"{type(self).__name__}(obj={self.obj_name}, player={self.player_name}, var={self.variable})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        out_vdat = linker.lookup_var(self.variable)
        if not isinstance(out_vdat, SmtObjVarLinkage):
            raise VirtualRepError(f"Output register for `{repr(self.variable)}` does not have attached scoreboard?")
        return [ComCmd(
            f"execute store result score {out_vdat.var_name} {out_vdat.get_objective(stack_level)} run " +
            f"scoreboard players get {self.player_name} {self.obj_name}"
        )]


class SmtSbObjPlaySetCmd(SmtCmd):

    def __init__(self, obj_name: str, player_name: str, value: SmtAtom) -> None:
        self.obj_name: str = obj_name
        self.player_name: str = player_name
        self.value: SmtAtom = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}(obj={self.obj_name}, player={self.player_name}, value={self.value})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        if isinstance(self.value, SmtVar):
            value_vdat = linker.lookup_var(self.value)
            if not isinstance(value_vdat, SmtObjVarLinkage):
                raise VirtualRepError(f"Output register for `{repr(self.value)}` does not have attached scoreboard?")
            return [ComCmd(
                f"scoreboard players operation {self.player_name} {self.obj_name} = {value_vdat.var_name} {value_vdat.get_objective(stack_level)}"
            )]
        elif isinstance(self.value, SmtConstInt):
            return [ComCmd(
                f"scoreboard players set {self.player_name} {self.obj_name} {self.value.value}"
            )]
        else:
            raise VirtualRepError(f"Unknown atom type `{type(self.value).__name__}` found in `{type(self).__name__}`")


class SmtSbObjPlayAddCmd(SmtCmd):

    def __init__(self, obj_name: str, player_name: str, value: SmtAtom) -> None:
        self.obj_name: str = obj_name
        self.player_name: str = player_name
        self.value: SmtAtom = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}(obj={self.obj_name}, player={self.player_name}, value={self.value})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        if isinstance(self.value, SmtVar):
            value_vdat = linker.lookup_var(self.value)
            if not isinstance(value_vdat, SmtObjVarLinkage):
                raise VirtualRepError(f"Output register for `{repr(self.value)}` does not have attached scoreboard?")
            return [ComCmd(
                f"scoreboard players operation {self.player_name} {self.obj_name} += {value_vdat.var_name} {value_vdat.get_objective(stack_level)}"
            )]
        elif isinstance(self.value, SmtConstInt):
            return [ComCmd(
                f"scoreboard players add {self.player_name} {self.obj_name} {self.value.value}"
            )]
        else:
            raise VirtualRepError(f"Unknown atom type `{type(self.value).__name__}` found in `{type(self).__name__}`")


class SmtSbObjPlaySubtractCmd(SmtCmd):

    def __init__(self, obj_name: str, player_name: str, value: SmtAtom) -> None:
        self.obj_name: str = obj_name
        self.player_name: str = player_name
        self.value: SmtAtom = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}(obj={self.obj_name}, player={self.player_name}, value={self.value})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        if isinstance(self.value, SmtVar):
            value_vdat = linker.lookup_var(self.value)
            if not isinstance(value_vdat, SmtObjVarLinkage):
                raise VirtualRepError(f"Output register for `{repr(self.value)}` does not have attached scoreboard?")
            return [ComCmd(
                f"scoreboard players operation {self.player_name} {self.obj_name} -= {value_vdat.var_name} {value_vdat.get_objective(stack_level)}"
            )]
        elif isinstance(self.value, SmtConstInt):
            return [ComCmd(
                f"scoreboard players remove {self.player_name} {self.obj_name} {self.value.value}"
            )]
        else:
            raise VirtualRepError(f"Unknown atom type `{type(self.value).__name__}` found in `{type(self).__name__}`")


class SmtSbObjPlayResetCmd(SmtCmd):

    def __init__(self, obj_name: str, player_name: str) -> None:
        self.obj_name: str = obj_name
        self.player_name: str = player_name

    def __repr__(self) -> str:
        return f"{type(self).__name__}(obj={self.obj_name}, player={self.player_name})"

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        return [ComCmd(
            f"scoreboard players reset {self.player_name} {self.obj_name}"
        )]


# Chainlink's
class ChainLinkScoreboard(IChainLink):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "scoreboard"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None


class ChainLinkScoreboardAdd(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboard

    def get_name(self) -> str:
        return "add_obj"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("name", InertType(InertCoreTypes.STR, True)),
            IParam("obj_type", InertType(InertCoreTypes.STR, True), CtxExprLitStr("dummy", src_loc=ComLoc())),
        ]

    def get_chain_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        _, add_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardAdd)
        name: str = get_key_with_type(add_binding, "name", SmtConstStr).value
        obj_type: str = get_key_with_type(add_binding, "obj_type", SmtConstStr).value
        return [SmtSbAddObjCmd(name, obj_type)], module.get_null_const()


class ChainLinkScoreboardRemove(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboard

    def get_name(self) -> str:
        return "remove_obj"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("name", InertType(InertCoreTypes.STR, True))
        ]

    def get_chain_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        _, add_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardRemove)
        name: str = get_key_with_type(add_binding, "name", SmtConstStr).value
        return [SmtSbRemoveObjCmd(name)], module.get_null_const()


class ChainLinkScoreboardConf(IChainLink):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboard

    def get_name(self) -> str:
        return "conf"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None


class ChainLinkScoreboardConfDisplay(IChainLink):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboardConf

    def get_name(self) -> str:
        return "display"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None


class ChainLinkScoreboardConfDisplayBelowName(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboardConfDisplay

    def get_name(self) -> str:
        return "below_name"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("name", InertType(InertCoreTypes.STR, True, True))
        ]

    def get_chain_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        _, add_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardConfDisplayBelowName)
        name: str = add_binding["name"].value if isinstance(add_binding["name"], SmtConstStr) else ''
        return [SmtSbSetDisplayObjCmd(name, "belowName")], module.get_null_const()


class ChainLinkScoreboardConfDisplayList(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboardConfDisplay

    def get_name(self) -> str:
        return "list"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("name", InertType(InertCoreTypes.STR, True, True))
        ]

    def get_chain_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        _, add_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardConfDisplayList)
        name: str = add_binding["name"].value if isinstance(add_binding["name"], SmtConstStr) else ''
        return [SmtSbSetDisplayObjCmd(name, "list")], module.get_null_const()


class ChainLinkScoreboardConfDisplaySidebar(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboardConfDisplay

    def get_name(self) -> str:
        return "sidebar"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("name", InertType(InertCoreTypes.STR, True, True)),
            IParam("team_color", InertType(InertCoreTypes.STR, True, True), CtxExprLitNull(src_loc=ComLoc()))
        ]

    def get_chain_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        _, add_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardConfDisplaySidebar)
        name: str = add_binding["name"].value if isinstance(add_binding["name"], SmtConstStr) else ''
        sidebar: str = "sidebar" + ((".team." + add_binding["team_color"].value) if isinstance(add_binding["team_color"], CtxExprLitStr) else '')
        return [SmtSbSetDisplayObjCmd(name, sidebar)], module.get_null_const()


class ChainLinkScoreboardConfJsonName(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboardConf

    def get_name(self) -> str:
        return "json_name"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("obj_name", InertType(InertCoreTypes.STR, True))
        ]

    def get_extra_param_type(self) -> Optional[Union[ComType, TypeUnion]]:
        return TypeUnion(
            InertType(InertCoreTypes.STR, True),
            StructColor.get_type()
        )

    def get_chain_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        _, add_binding, extra_args = get_link_of_type(clink_param_binding, ChainLinkScoreboardConfJsonName)
        obj_name: str = get_key_with_type(add_binding, "obj_name", SmtConstStr).value
        json_comps: List[str] = []
        json_comp: List[Tuple[str, str]] = []

        def flatten_current_comps_if_needed():
            nonlocal json_comp, json_comps
            if len(json_comp) >= 1:
                json_comps.append("{" + ", ".join(f'"{comp_id}":"{comp_value}"' for comp_id, comp_value in json_comp) + "}")
                json_comp = []

        for e_arg in extra_args:
            if isinstance(e_arg, SmtConstStr):
                json_comp.append(("text", e_arg.value))
            elif isinstance(e_arg, SmtStruct):
                flatten_current_comps_if_needed()
                if e_arg.get_type() == StructColor.get_type():
                    json_comp.append(("color", e_arg.struct_instance.get_asserting_type("color_code", str)))
                else:
                    raise StatementRepError(f"Unknown struct type in conj.json_name `{e_arg.get_type()}`?")
            else:
                raise StatementRepError(f"Unknown atom type: `{type(e_arg).__name__}`")
        flatten_current_comps_if_needed()
        json_name: str = "[" + ", ".join(json_comps) + "]"
        return [SmtSbJsonNameObjCmd(obj_name, json_name)], module.get_null_const()


class ChainLinkScoreboardConfHearts(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboardConf

    def get_name(self) -> str:
        return "hearts"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("obj_name", InertType(InertCoreTypes.STR, True)),
            IParam("list_as_hearts", InertType(InertCoreTypes.BOOL, True))
        ]

    def get_chain_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        _, add_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardConfJsonName)
        obj_name: str = get_key_with_type(add_binding, "obj_name", SmtConstStr).value
        hearts: bool = (get_key_with_type(add_binding, "list_as_hearts", SmtConstInt).value >= 1)
        return [SmtSbHeartObjCmd(obj_name, hearts)], module.get_null_const()


class ChainLinkScoreboardObj(IChainLink):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboard

    def get_name(self) -> str:
        return "obj"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("obj_name", InertType(InertCoreTypes.STR, True)),
        ]


class ChainLinkScoreboardObjGet(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboardObj

    def get_name(self) -> str:
        return "get"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.ENTITY, False)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return []

    def get_chain_type(self) -> ComType:
        return InertType(InertCoreTypes.INT)

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        if not matches_type(ExecType(ExecCoreTypes.ENTITY, False), executor.get_type()):
            raise ConversionError(f"Player-Scoreboard get can only operate on single entities not groups (or world)")
        _, add_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObj)
        obj_name: str = get_key_with_type(add_binding, "obj_name", SmtConstStr).value
        output_register = function.new_pseudo_var(InertType(InertCoreTypes.INT))
        return [SmtSbObjGetExecCmd(executor, obj_name, output_register)], output_register


class ChainLinkScoreboardObjSet(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboardObj

    def get_name(self) -> str:
        return "set"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.ENTITY, True)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("value", InertType(InertCoreTypes.INT))
        ]

    def get_chain_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        if not matches_type(ExecType(ExecCoreTypes.ENTITY, True), executor.get_type()):
            raise ConversionError(f"Player-Scoreboard set can only operate on entities not world")
        _, name_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObj)
        obj_name: str = get_key_with_type(name_binding, "obj_name", SmtConstStr).value
        _, set_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObjSet)
        value: SmtAtom = set_binding["value"]
        return [SmtSbObjSetExecCmd(executor, obj_name, value)], module.get_null_const()


class ChainLinkScoreboardObjAdd(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboardObj

    def get_name(self) -> str:
        return "add"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.ENTITY, True)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("value", InertType(InertCoreTypes.INT))
        ]

    def get_chain_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        if not matches_type(ExecType(ExecCoreTypes.ENTITY, True), executor.get_type()):
            raise ConversionError(f"Player-Scoreboard set can only operate on entities not world")
        _, name_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObj)
        obj_name: str = get_key_with_type(name_binding, "obj_name", SmtConstStr).value
        _, set_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObjAdd)
        value: SmtAtom = set_binding["value"]
        return [SmtSbObjAddExecCmd(executor, obj_name, value)], module.get_null_const()


class ChainLinkScoreboardObjSub(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboardObj

    def get_name(self) -> str:
        return "sub"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.ENTITY, True)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("value", InertType(InertCoreTypes.INT))
        ]

    def get_chain_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        if not matches_type(ExecType(ExecCoreTypes.ENTITY, True), executor.get_type()):
            raise ConversionError(f"Player-Scoreboard set can only operate on entities not world")
        _, name_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObj)
        obj_name: str = get_key_with_type(name_binding, "obj_name", SmtConstStr).value
        _, set_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObjSub)
        value: SmtAtom = set_binding["value"]
        return [SmtSbObjSubtractExecCmd(executor, obj_name, value)], module.get_null_const()


class ChainLinkScoreboardObjEnable(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboardObj

    def get_name(self) -> str:
        return "enable"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.ENTITY, True)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return []

    def get_chain_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        if not matches_type(ExecType(ExecCoreTypes.ENTITY, True), executor.get_type()):
            raise ConversionError(f"Player-Scoreboard set can only operate on entities not world")
        _, name_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObj)
        obj_name: str = get_key_with_type(name_binding, "obj_name", SmtConstStr).value
        return [SmtSbObjEnableExecCmd(executor, obj_name)], module.get_null_const()


class ChainLinkScoreboardObjReset(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboardObj

    def get_name(self) -> str:
        return "reset"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.ENTITY, True)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return []

    def get_chain_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        if not matches_type(ExecType(ExecCoreTypes.ENTITY, True), executor.get_type()):
            raise ConversionError(f"Player-Scoreboard set can only operate on entities not world")
        _, name_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObj)
        obj_name: str = get_key_with_type(name_binding, "obj_name", SmtConstStr).value
        return [SmtSbObjResetExecCmd(executor, obj_name)], module.get_null_const()


class ChainLinkScoreboardReset(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboard

    def get_name(self) -> str:
        return "reset"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.ENTITY, True)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return []

    def get_chain_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        if not matches_type(ExecType(ExecCoreTypes.ENTITY, True), executor.get_type()):
            raise ConversionError(f"Player-Scoreboard set can only operate on entities not world")
        return [SmtSbObjFullResetExecCmd(executor)], module.get_null_const()


class ChainLinkScoreboardObjPlayer(IChainLink):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboardObj

    def get_name(self) -> str:
        return "player"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("fake_player", InertType(InertCoreTypes.STR, True)),
        ]


class ChainLinkScoreboardObjPlayerGet(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboardObjPlayer

    def get_name(self) -> str:
        return "get"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return []

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_chain_type(self) -> ComType:
        return InertType(InertCoreTypes.INT)

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        _, obj_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObj)
        obj_name: str = get_key_with_type(obj_binding, "obj_name", SmtConstStr).value
        _, play_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObjPlayer)
        player_name: str = get_key_with_type(play_binding, "fake_player", SmtConstStr).value
        output_register = function.new_pseudo_var(InertType(InertCoreTypes.INT))
        return [SmtSbObjPlayGetCmd(obj_name, player_name, output_register)], output_register


class ChainLinkScoreboardObjPlayerSet(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboardObjPlayer

    def get_name(self) -> str:
        return "set"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("value", InertType(InertCoreTypes.INT))
        ]

    def get_chain_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        _, obj_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObj)
        obj_name: str = get_key_with_type(obj_binding, "obj_name", SmtConstStr).value
        _, play_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObjPlayer)
        player_name: str = get_key_with_type(play_binding, "fake_player", SmtConstStr).value
        _, set_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObjPlayerSet)
        value: SmtAtom = set_binding["value"]
        return [SmtSbObjPlaySetCmd(obj_name, player_name, value)], module.get_null_const()


class ChainLinkScoreboardObjPlayerAdd(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboardObjPlayer

    def get_name(self) -> str:
        return "add"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("value", InertType(InertCoreTypes.INT))
        ]

    def get_chain_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        _, obj_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObj)
        obj_name: str = get_key_with_type(obj_binding, "obj_name", SmtConstStr).value
        _, play_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObjPlayer)
        player_name: str = get_key_with_type(play_binding, "fake_player", SmtConstStr).value
        _, set_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObjPlayerAdd)
        value: SmtAtom = set_binding["value"]
        return [SmtSbObjPlayAddCmd(obj_name, player_name, value)], module.get_null_const()


class ChainLinkScoreboardObjPlayerSub(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboardObjPlayer

    def get_name(self) -> str:
        return "sub"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("value", InertType(InertCoreTypes.INT))
        ]

    def get_chain_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        _, obj_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObj)
        obj_name: str = get_key_with_type(obj_binding, "obj_name", SmtConstStr).value
        _, play_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObjPlayer)
        player_name: str = get_key_with_type(play_binding, "fake_player", SmtConstStr).value
        _, set_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObjPlayerSub)
        value: SmtAtom = set_binding["value"]
        return [SmtSbObjPlaySubtractCmd(obj_name, player_name, value)], module.get_null_const()


class ChainLinkScoreboardObjPlayerReset(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkScoreboardObjPlayer

    def get_name(self) -> str:
        return "reset"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return []

    def get_chain_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        _, obj_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObj)
        obj_name: str = get_key_with_type(obj_binding, "obj_name", SmtConstStr).value
        _, play_binding, _ = get_link_of_type(clink_param_binding, ChainLinkScoreboardObjPlayer)
        player_name: str = get_key_with_type(play_binding, "fake_player", SmtConstStr).value
        return [SmtSbObjPlayResetCmd(obj_name, player_name)], module.get_null_const()
