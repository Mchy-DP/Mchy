import datetime
from typing import Collection, Dict, List, Optional, Sequence, Tuple, Type, Union

from mchy.cmd_modules.chains import IChain, IChainLink
from mchy.cmd_modules.function import IFunc, IParam
from mchy.cmd_modules.helper import NULL_CTX_TYPE, get_exec_vdat, get_key_with_type, get_struct_instance
from mchy.cmd_modules.name_spaces import Namespace
from mchy.common.com_cmd import ComCmd
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType
from mchy.common.config import Config
from mchy.contextual.struct.expr import CtxChainLink, CtxExprLits, CtxExprLitStr, CtxExprNode
from mchy.errors import ConversionError, StatementRepError, VirtualRepError
from mchy.library.std.cmd_kill import SmtKillCmd
from mchy.library.std.cmd_summon import SmtSummonCmd
from mchy.library.std.ns import STD_NAMESPACE
from mchy.library.std.struct_pos import StructPos
from mchy.stmnt.struct import SmtAtom, SmtCmd, SmtFunc, SmtModule
from mchy.stmnt.struct.atoms import SmtConstFloat, SmtConstStr, SmtVar
from mchy.stmnt.struct.linker import SmtExecVarLinkage, SmtLinker


class SmtRotationSetCmd(SmtCmd):

    def __init__(self, executor: SmtAtom, hrz: float, vrt: float) -> None:
        self.executor: SmtAtom = executor
        exec_type = self.executor.get_type()
        if not isinstance(exec_type, ExecType):
            raise StatementRepError(f"Attempted to create {type(self).__name__} with executor of type {exec_type}, ExecType required")
        self.hrz: float = hrz
        self.vrt: float = vrt

    def __repr__(self) -> str:
        return f"{type(self).__name__}(exec={self.executor}, hrz={self.hrz}, vrt={self.vrt})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        exec_vdat = get_exec_vdat(self.executor, linker)
        return [ComCmd(f"execute as {exec_vdat.get_selector(stack_level)} at @s run tp @s ~ ~ ~ {self.hrz} {self.vrt}")]


class SmtRotationMatchCmd(SmtCmd):

    def __init__(self, executor: SmtAtom, match_entity: SmtAtom) -> None:
        self.executor: SmtAtom = executor
        exec_type = self.executor.get_type()
        if not isinstance(exec_type, ExecType):
            raise StatementRepError(f"Attempted to create {type(self).__name__} with executor of type {exec_type}, ExecType required")
        self.match_entity: SmtAtom = match_entity
        match_entity_type = self.match_entity.get_type()
        if not isinstance(match_entity_type, ExecType):
            raise StatementRepError(f"Attempted to create {type(self).__name__} with match_entity of type {match_entity_type}, ExecType required")

    def __repr__(self) -> str:
        return f"{type(self).__name__}(exec={self.executor}, match_entity={self.match_entity})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        exec_vdat = get_exec_vdat(self.executor, linker)
        match_vdat = get_exec_vdat(self.match_entity, linker)
        return [ComCmd(f"execute as {exec_vdat.get_selector(stack_level)} at @s rotated as {match_vdat.get_selector(stack_level)} run tp ^ ^ ^")]


class SmtRotationFaceEntityCmd(SmtCmd):

    def __init__(self, executor: SmtAtom, target_entity: SmtAtom) -> None:
        self.executor: SmtAtom = executor
        exec_type = self.executor.get_type()
        if not isinstance(exec_type, ExecType):
            raise StatementRepError(f"Attempted to create {type(self).__name__} with executor of type {exec_type}, ExecType required")
        self.target_entity: SmtAtom = target_entity
        exec_type = self.target_entity.get_type()
        if not isinstance(exec_type, ExecType):
            raise StatementRepError(f"Attempted to create {type(self).__name__} with target_entity of type {exec_type}, ExecType required")

    def __repr__(self) -> str:
        return f"{type(self).__name__}(exec={self.executor}, target_entity={self.target_entity})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        exec_vdat = get_exec_vdat(self.executor, linker)
        target_vdat = get_exec_vdat(self.target_entity, linker)
        return [ComCmd(f"execute as {exec_vdat.get_selector(stack_level)} at @s run tp @s ~ ~ ~ facing entity {target_vdat.get_selector(stack_level)}")]


class ChainLinkRotate(IChainLink):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ExecType(ExecCoreTypes.ENTITY, True)

    def get_name(self) -> str:
        return "rotate"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None


class ChainRotateSet(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkRotate

    def get_name(self) -> str:
        return "set"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.ENTITY, True)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("horizontal", InertType(InertCoreTypes.FLOAT, const=True)),
            IParam("vertical", InertType(InertCoreTypes.FLOAT, const=True)),
        ]

    def get_chain_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        # get data
        rotate_set_binding: Optional[Dict[str, 'SmtAtom']] = None
        for link, param_binding, _ in clink_param_binding:
            if isinstance(link, ChainRotateSet):
                rotate_set_binding = param_binding
            elif isinstance(link, ChainLinkRotate):
                continue
            else:
                raise StatementRepError(f"Unknown chainlink {repr(link)}")
        # confirm expected links found
        if rotate_set_binding is None:
            config.logger.very_verbose(f"Observed binding lacks expected element: {repr(clink_param_binding)}")
            raise StatementRepError("Rotational chainlink missing from own generator?")
        # generate command
        horizontal = get_key_with_type(rotate_set_binding, "horizontal", SmtConstFloat).value
        vertical = get_key_with_type(rotate_set_binding, "vertical", SmtConstFloat).value
        return [SmtRotationSetCmd(executor, horizontal, vertical)], module.get_null_const()


class ChainRotateMatch(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkRotate

    def get_name(self) -> str:
        return "match"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.ENTITY, True)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("target_entity", ExecType(ExecCoreTypes.ENTITY, False))
        ]

    def get_chain_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        # get data
        rotate_matching_binding: Optional[Dict[str, 'SmtAtom']] = None
        for link, param_binding, _ in clink_param_binding:
            if isinstance(link, ChainRotateMatch):
                rotate_matching_binding = param_binding
            elif isinstance(link, ChainLinkRotate):
                continue
            else:
                raise StatementRepError(f"Unknown chainlink {repr(link)}")
        # confirm expected links found
        if rotate_matching_binding is None:
            config.logger.very_verbose(f"Observed binding lacks expected element: {repr(clink_param_binding)}")
            raise StatementRepError("Rotational chainlink missing from own generator?")
        # generate command
        target_entity = rotate_matching_binding["target_entity"]
        return [SmtRotationMatchCmd(executor, target_entity)], module.get_null_const()


class ChainRotateFace(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkRotate

    def get_name(self) -> str:
        return "face"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.ENTITY, True)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("target_location", StructPos.get_type())
        ]

    def get_chain_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: 'SmtAtom', clink_param_binding: List[Tuple[IChainLink, Dict[str, 'SmtAtom'], List['SmtAtom']]],
                module: 'SmtModule', function: 'SmtFunc', config: Config
            ) -> Tuple[List['SmtCmd'], 'SmtAtom']:
        # get data
        rotate_facing_binding: Optional[Dict[str, 'SmtAtom']] = None
        for link, param_binding, _ in clink_param_binding:
            if isinstance(link, ChainRotateFace):
                rotate_facing_binding = param_binding
            elif isinstance(link, ChainLinkRotate):
                continue
            else:
                raise StatementRepError(f"Unknown chainlink {repr(link)}")
        # confirm expected links found
        if rotate_facing_binding is None:
            config.logger.very_verbose(f"Observed binding lacks expected element: {repr(clink_param_binding)}")
            raise StatementRepError("Rotational chainlink missing from own generator?")
        # generate command
        target_location = rotate_facing_binding["target_location"]
        facing_marker_register = function.new_pseudo_var(ExecType(ExecCoreTypes.ENTITY, False))
        return [
            SmtSummonCmd(facing_marker_register, target_location, "minecraft:marker", None),  # make a marker at target location
            SmtRotationFaceEntityCmd(executor, facing_marker_register),  # face it
            SmtKillCmd(facing_marker_register)  # kill the marker
        ], module.get_null_const()
