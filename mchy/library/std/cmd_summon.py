from typing import Collection, Dict, List, Optional, Sequence, Tuple

from mchy.cmd_modules.function import IFunc, IParam
from mchy.cmd_modules.helper import NULL_CTX_TYPE, get_exec_vdat, get_key_with_type, get_struct_instance
from mchy.cmd_modules.name_spaces import Namespace
from mchy.common.com_cmd import ComCmd
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType, matches_type
from mchy.common.config import Config
from mchy.contextual.struct.expr.literals import CtxExprLitNull, CtxExprLitStr
from mchy.errors import ConversionError, LibConversionError, StatementRepError, VirtualRepError
from mchy.library.std.ns import STD_NAMESPACE
from mchy.library.std.struct_pos import StructPos
from mchy.stmnt.struct import SmtAtom, SmtCmd, SmtFunc, SmtModule
from mchy.stmnt.struct.atoms import SmtConstInt, SmtConstNull, SmtConstStr, SmtVar
from mchy.stmnt.struct.linker import SmtExecVarLinkage, SmtLinker


class SmtSummonCmd(SmtCmd):

    def __init__(self, output_register: SmtVar, location: SmtAtom, entity_type: str, nbt_data: Optional[str]) -> None:
        self.output_register: SmtVar = output_register
        self.location: SmtAtom = location
        loc_type = self.location.get_type()
        if loc_type != StructPos.get_type():
            raise StatementRepError(f"Attempted to create {type(self).__name__} with location of type {loc_type.render()}, {StructPos.get_type().render()} required")
        self.entity_type: str = entity_type
        self.nbt_data: Optional[str] = nbt_data
        if self.nbt_data is not None:
            if self.nbt_data[0] == "{" and self.nbt_data[-1] == "}":
                self.nbt_data = self.nbt_data[1:-1]
            else:
                raise StatementRepError("Summon nbt_data must start with `{` and end with `}`")

    def __repr__(self) -> str:
        return f"{type(self).__name__}(out_var={repr(self.output_register)}, location={self.location}, entity_type={self.entity_type}, nbt_data={self.nbt_data})"

    @staticmethod
    def _err_build(cix: int, nbt_data: str) -> str:
        return f"at index {cix} near `... {nbt_data[max(cix-12,0):cix+12]} ...`"

    @staticmethod
    def parse_nbt_data(nbt_data: str, tag_insert: str) -> str:
        if "\"" in tag_insert:
            raise VirtualRepError("Tag to insert cannot contain \" - this is an invalid char for minecraft tags")
        # force single trailing comma
        nbt_data = nbt_data.rstrip(",") + ","
        summon_data: str = "{"  # The final output
        # shortcircuit operation if the text "Tags" doesn't appear in nbt (no point doing full on parsing if it's not there)
        if "Tags" not in nbt_data:
            summon_data += nbt_data.lstrip(",")
            nbt_data = ""
        # ===== FULL ON SHODDY NBT PARSING =====  - Replace with proper nbt parser once written
        key_stage = True  # If this is the key building phase or the value building phase
        not_outer_comma_buffer: str = ""  # The buffer to build outermost keys/values into
        braces: List[str] = []  # The scoping stack for braces
        string: Optional[str] = None  # str if in string None otherwise,  str value will be the string start char
        str_escaping = False  # Set to true when `\` encountered so that the next char will not terminate the str
        in_tags_key: bool = False  # If currently parsing the value of the `Tags:` key
        found_tags_key: bool = False  # "If we ever found the `Tags:` key during parsing"
        for cix, char in enumerate(nbt_data):  # Ensures trailing comma to trigger buffer clear
            # DEBUG PRINT - Leave commented when not debugging to aid future devs debugging this code
            # print(f"Processing char {cix:3}: `{char}` --- kv={int(key_stage)} string={repr(string):4} {'ESC' if str_escaping else ''} {braces=} buffer={not_outer_comma_buffer}")
            if string is None:
                # Start string
                if char == "'":
                    string = char
                elif char == "\"":
                    string = char
                # Open brace
                elif char == "(":
                    braces.append("(")
                elif char == "[":
                    braces.append("[")
                elif char == "{":
                    braces.append("{")
                # close brace
                elif char == ")":
                    if not (len(braces) >= 1 and braces[-1] == "("):
                        raise LibConversionError(f"Summon nbt invalid: Unbalanced brackets, unexpected ')', parsing failed {SmtSummonCmd._err_build(cix, nbt_data)}")
                    braces.pop()
                elif char == "]":
                    if not (len(braces) >= 1 and braces[-1] == "["):
                        raise LibConversionError(f"Summon nbt invalid: Unbalanced brackets, unexpected ']', parsing failed {SmtSummonCmd._err_build(cix, nbt_data)}")
                    braces.pop()
                elif char == "}":
                    if not (len(braces) >= 1 and braces[-1] == "{"):
                        raise LibConversionError("Summon nbt invalid: Unbalanced brackets, unexpected '}', parsing failed "+SmtSummonCmd._err_build(cix, nbt_data))
                    braces.pop()
            else:
                # Should string stop?
                if str_escaping:
                    str_escaping = False
                else:  # Only stop the string if not escaping
                    if char == string:
                        string = None
                    elif char == "\\":
                        str_escaping = True

            if len(braces) == 0 and (string is None):
                # In outermost scope
                if char == ":" and key_stage:
                    # Reached the end of a key
                    if len(not_outer_comma_buffer) == 0:
                        raise LibConversionError(f"Summon nbt invalid: buffer empty {SmtSummonCmd._err_build(cix, nbt_data)} - possibly double comma?")
                    if not_outer_comma_buffer.strip(" ") == "Tags":
                        in_tags_key = True
                    summon_data += not_outer_comma_buffer + ":"
                    not_outer_comma_buffer = ""
                    key_stage = False
                    continue
                if char == "," and (not key_stage):
                    # reached the end of a value
                    if len(not_outer_comma_buffer) == 0:
                        raise LibConversionError(f"Summon nbt invalid: Completely empty kv-value found {SmtSummonCmd._err_build(cix, nbt_data)}")
                    if in_tags_key:  # If the key this value is associated with is 'Tags'
                        if not_outer_comma_buffer[0] != "[":
                            LibConversionError(f"Summon nbt invalid: Tags does not start with `[` {SmtSummonCmd._err_build(cix, nbt_data)}")
                        elif not_outer_comma_buffer[-1] != "]":
                            LibConversionError(f"Summon nbt invalid: Tags does not start with `]` {SmtSummonCmd._err_build(cix, nbt_data)}")
                        _tags = not_outer_comma_buffer[1:-1].split(",")
                        _tags = [_tg for _tg in _tags if _tg.strip() != ""]
                        _tags.append("\""+tag_insert+"\"")
                        not_outer_comma_buffer = "[" + ",".join(_tags) + "]"
                        in_tags_key = False
                        found_tags_key = True
                    summon_data += not_outer_comma_buffer + ","
                    not_outer_comma_buffer = ""
                    key_stage = True
                    continue
            not_outer_comma_buffer += char
        if not key_stage:
            raise LibConversionError(f"Summon nbt invalid: Ended without closing value {SmtSummonCmd._err_build(cix, nbt_data)}")
        if not_outer_comma_buffer != "" and not_outer_comma_buffer != ",":  # Unparsed trailing comma's are fine -> we added them anyway
            raise VirtualRepError(f"Hanging chars in buffer: `{not_outer_comma_buffer}` not processed")
        if not found_tags_key:
            summon_data += f'Tags:["{tag_insert}"],'
        summon_data = summon_data.rstrip(",")  # Remove the trailing comma parsing usually produces
        summon_data += "}"
        return summon_data

    def virtualize(self, linker: SmtLinker, stack_level: int) -> List[ComCmd]:
        # Get output register tag
        out_vdat = linker.lookup_var(self.output_register)
        if not isinstance(out_vdat, SmtExecVarLinkage):
            raise VirtualRepError(f"Executor's variable data for `{repr(self.output_register)}` does not include tag despite being of executable type?")
        out_reg_tag = out_vdat.get_full_tag(stack_level)
        # Build summon data
        summon_data: str
        if self.nbt_data is None:
            summon_data = '{Tags:["'+out_reg_tag+'"]}'
        else:
            summon_data = SmtSummonCmd.parse_nbt_data(self.nbt_data, out_reg_tag)
        # get pos data
        pos_str, executor = StructPos.build_position_string(get_struct_instance(self.location))
        cmd = f"summon {self.entity_type} {pos_str} {summon_data}"
        # Build commands
        empty_tag_command = ComCmd(f"tag {out_vdat.get_selector(stack_level)} remove {out_vdat.get_full_tag(stack_level)}")
        if executor is None:
            return [empty_tag_command, ComCmd(cmd)]
        else:
            exec_vdat = get_exec_vdat(executor, linker)
            return [empty_tag_command, ComCmd(f"execute at {exec_vdat.get_selector(stack_level)} run {cmd}")]


class CmdSummon(IFunc):

    def get_namespace(self) -> Namespace:
        return STD_NAMESPACE

    def get_executor_type(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "summon"

    def get_params(self) -> Sequence[IParam]:
        return [
            IParam("location", StructPos.get_type()),
            IParam("entity_type", InertType(InertCoreTypes.STR, const=True)),
            IParam("nbt_data", InertType(InertCoreTypes.STR, const=True, nullable=True), CtxExprLitNull(src_loc=ComLoc()))
        ]

    def get_return_type(self) -> ComType:
        return ExecType(ExecCoreTypes.ENTITY, group=False)

    def stmnt_conv(
                self, executor: SmtAtom, param_binding: Dict[str, SmtAtom], extra_binding: List['SmtAtom'], module: SmtModule, function: SmtFunc, config: Config
            ) -> Tuple[List[SmtCmd], 'SmtAtom']:
        location = param_binding["location"]
        entity_type: str = get_key_with_type(param_binding, "entity_type", SmtConstStr).value
        nbt_data_param = param_binding["nbt_data"]
        nbt_data: Optional[str]
        if isinstance(nbt_data_param, SmtConstNull):
            nbt_data = None
        elif isinstance(nbt_data_param, SmtConstStr):
            nbt_data = nbt_data_param.value
        else:
            raise StatementRepError(f"Unknown param atom `{type(nbt_data_param).__name__}` expected, str/null atom")
        output_register = function.new_pseudo_var(ExecType(ExecCoreTypes.ENTITY, False))
        return [SmtSummonCmd(output_register, location, entity_type, nbt_data)], output_register
