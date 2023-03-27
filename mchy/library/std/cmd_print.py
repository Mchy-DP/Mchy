from abc import ABC, abstractmethod
from dataclasses import dataclass, replace as dataclass_clone
import json
from typing import Collection, Dict, List, Optional, Sequence, Tuple, Union

from mchy.cmd_modules.function import IFunc, IParam
from mchy.cmd_modules.helper import NULL_CTX_TYPE
from mchy.cmd_modules.name_spaces import Namespace
from mchy.cmd_modules.smt_cmds.simple_const_str_tellraw import SmtSimpleStrConstTellrawCmd
from mchy.common.com_cmd import ComCmd
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType, TypeUnion, matches_type
from mchy.common.config import Config
from mchy.library.std.struct_color import StructColor
from mchy.stmnt.struct.linker import SmtExecVarLinkage, SmtLinker, SmtObjVarLinkage, SmtVarLinkage
from mchy.library.std.ns import STD_NAMESPACE
from mchy.stmnt.struct import SmtAtom, SmtCmd, SmtFunc, SmtModule
from mchy.stmnt.struct.atoms import SmtConstFloat, SmtConstInt, SmtConstNull, SmtConstStr, SmtStruct, SmtVar, SmtWorld
from mchy.errors import StatementRepError, UnreachableError, VirtualRepError


@dataclass(frozen=True)
class _TellrawFormatting:
    color: str = "white"
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    obfuscated: bool = False

    def add_formatting(self, component: dict) -> None:
        component["bold"] = self.bold
        component["italic"] = self.italic
        component["underlined"] = self.underline
        component["strikethrough"] = self.strikethrough
        component["obfuscated"] = self.obfuscated
        component["color"] = self.color


@dataclass
class _TellrawHover:
    hover_text: Tuple['_TellrawCompText', ...] = ()

    def add_hover(self, component: dict) -> None:
        component["hoverEvent"] = {"action": "show_text", "contents": [x.get_component_dict() for x in self.hover_text]}


class _TellrawComponent(ABC):

    @abstractmethod
    def get_component_dict(self) -> dict:
        ...

    def get_component(self) -> str:
        return json.dumps(self.get_component_dict())


@dataclass
class _TellrawCompText(_TellrawComponent):
    text: str
    formatting: _TellrawFormatting
    hovering: Optional[_TellrawHover] = None

    def get_component_dict(self) -> dict:
        component_dict: dict = {}
        component_dict["text"] = self.text
        self.formatting.add_formatting(component_dict)
        if self.hovering is not None:
            self.hovering.add_hover(component_dict)
        return component_dict


@dataclass
class _TellrawCompSelector(_TellrawComponent):
    selector: str
    formatting: _TellrawFormatting
    hovering: Optional[_TellrawHover] = None

    def get_component_dict(self) -> dict:
        component_dict: dict = {}
        component_dict["selector"] = self.selector
        self.formatting.add_formatting(component_dict)
        if self.hovering is not None:
            self.hovering.add_hover(component_dict)
        return component_dict


@dataclass
class _TellrawCompObjective(_TellrawComponent):
    player: str
    objective: str
    formatting: _TellrawFormatting
    hovering: Optional[_TellrawHover] = None

    def get_component_dict(self) -> dict:
        component_dict: dict = {}
        component_dict["score"] = {"name": self.player, "objective": self.objective}
        self.formatting.add_formatting(component_dict)
        if self.hovering is not None:
            self.hovering.add_hover(component_dict)
        return component_dict


@dataclass
class _TellrawCompNBT(_TellrawComponent):
    namespace: str
    path: str
    formatting: _TellrawFormatting
    hovering: Optional[_TellrawHover] = None

    def get_component_dict(self) -> dict:
        component_dict: dict = {}
        component_dict["storage"] = self.namespace
        component_dict["nbt"] = self.path
        self.formatting.add_formatting(component_dict)
        if self.hovering is not None:
            self.hovering.add_hover(component_dict)
        return component_dict


class SmtComplexPrintingTellrawCmd(SmtCmd):

    def __init__(self, *msg: SmtAtom) -> None:
        self.msgs: Tuple[SmtAtom, ...] = tuple(msg)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.msgs})"

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        cmds: List[ComCmd] = []
        formatting = _TellrawFormatting()
        comps: List[_TellrawComponent] = []
        for atom in self.msgs:
            if isinstance(atom, SmtConstInt):
                comps.append(_TellrawCompText(str(atom.value), formatting))
            elif isinstance(atom, SmtConstStr):
                comps.append(_TellrawCompText(str(atom.value), formatting))
            elif isinstance(atom, SmtConstFloat):
                comps.append(_TellrawCompText(str(atom.value), formatting))
            elif isinstance(atom, SmtConstNull):
                comps.append(_TellrawCompText(str("<null>"), formatting))
            elif isinstance(atom, SmtWorld):
                comps.append(_TellrawCompText(str("<world>"), formatting))
            elif isinstance(atom, SmtVar):
                var_type = atom.get_type()
                variable_data: SmtVarLinkage = linker.lookup_var(atom)
                if isinstance(var_type, InertType):
                    if isinstance(variable_data, SmtObjVarLinkage):
                        comps.append(_TellrawCompObjective(variable_data.var_name, variable_data.get_objective(stack_level), formatting))
                    else:
                        if var_type.target == InertCoreTypes.NULL:
                            comps.append(_TellrawCompText("<null>", formatting))
                        else:
                            if var_type.nullable:
                                # ensure that if this might be null then it's value is <null>
                                pathing_var = "1b"
                                for path_elem in reversed(variable_data.get_store_path().split(".")):
                                    pathing_var = "{"+path_elem+":"+pathing_var+"}"
                                cmds.append(ComCmd(
                                    f"execute if data storage {variable_data.ns} {pathing_var} run data " +
                                    f"modify storage {variable_data.ns} {variable_data.get_store_path(stack_level)}.{variable_data.var_name}.value set value \"<null>\""
                                ))
                            comps.append(_TellrawCompNBT(variable_data.ns, f"{variable_data.get_store_path(stack_level)}.{variable_data.var_name}.value", formatting))
                elif isinstance(var_type, ExecType):
                    if var_type.target == ExecCoreTypes.WORLD:
                        comps.append(_TellrawCompText(str("<world>"), formatting))
                    elif var_type.target in (ExecCoreTypes.PLAYER, ExecCoreTypes.ENTITY):
                        if isinstance(variable_data, SmtExecVarLinkage):
                            comps.append(_TellrawCompSelector(variable_data.get_selector(stack_level), formatting))
                        else:
                            raise VirtualRepError(f"Executable type variable `{repr(atom)}` has no tag attached to var-data?")
                    else:
                        raise VirtualRepError(f"Exec type `{var_type.render()}` is missing print support?")
                else:
                    raise VirtualRepError(f"var type of {type(var_type)} is missing from print")
            elif isinstance(atom, SmtStruct):
                if atom.get_type() == StructColor.get_type():
                    formatting = dataclass_clone(formatting, color=atom.struct_instance.get_asserting_type("color_code", str))
                else:
                    raise VirtualRepError(f"Unknown struct type in print `{atom.get_type()}`?")
            else:
                raise VirtualRepError(f"{type(atom)} - missing from print")
        cmds.append(ComCmd(f'tellraw @a ["", '+', '.join(comp.get_component() for comp in comps)+']'))
        return cmds


class CmdPrint(IFunc):

    def get_namespace(self) -> Namespace:
        return STD_NAMESPACE

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "print"

    def get_params(self) -> Sequence[IParam]:
        return []

    def get_extra_param_type(self) -> Optional[Union[ComType, TypeUnion]]:
        return TypeUnion(
            InertType(InertCoreTypes.STR, const=True, nullable=True),
            InertType(InertCoreTypes.FLOAT, const=True, nullable=True),
            InertType(InertCoreTypes.INT, nullable=True),
            InertType(InertCoreTypes.BOOL, nullable=True),
            InertType(InertCoreTypes.NULL),
            ExecType(ExecCoreTypes.WORLD, group=False),
            StructColor.get_type()
            # TODO: Expand valid types: executable types
        )

    def get_return_type(self) -> ComType:
        return NULL_CTX_TYPE

    def stmnt_conv(
                self, executor: SmtAtom, param_binding: Dict[str, SmtAtom], extra_binding: List['SmtAtom'], module: SmtModule, function: SmtFunc, config: Config
            ) -> Tuple[List[SmtCmd], 'SmtAtom']:
        return [SmtComplexPrintingTellrawCmd(*extra_binding)], module.get_null_const()
