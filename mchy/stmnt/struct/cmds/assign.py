
from typing import List
from mchy.common.com_cmd import ComCmd
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertType, StructType
from mchy.errors import UnreachableError, VirtualRepError
from mchy.stmnt.struct.linker import SmtLinker, SmtVarLinkage, SmtObjVarLinkage, SmtExecVarLinkage
from mchy.stmnt.struct.abs_cmd import SmtCmd
from mchy.stmnt.struct.atoms import SmtAtom, SmtConstFloat, SmtConstInt, SmtConstNull, SmtConstStr, SmtStruct, SmtVar, SmtWorld


class SmtAssignCmd(SmtCmd):

    def __init__(self, target_var: SmtVar, value: SmtAtom) -> None:
        self.target_var: SmtVar = target_var
        self.value: SmtAtom = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.target_var.typed_repr()} = {self.value})"

    def _target_stack_level(self, stack_level: int) -> int:
        """Overwritten by children facilitating stack frame creation/destruction"""
        return stack_level

    def _source_stack_level(self, stack_level: int) -> int:
        """Overwritten by children facilitating stack frame creation/destruction"""
        return stack_level

    def _vir_obj_target(self, target_vdat: SmtObjVarLinkage, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        if isinstance(self.value, SmtVar):
            source_vdat: SmtVarLinkage = linker.lookup_var(self.value)
            if isinstance(source_vdat, SmtObjVarLinkage):
                return [ComCmd(
                    f"scoreboard players operation {target_vdat.var_name} {target_vdat.get_objective(self._target_stack_level(stack_level))} = " +
                    f"{source_vdat.var_name} {source_vdat.get_objective(self._source_stack_level(stack_level))}"
                )]
            return [ComCmd(
                f"execute store result score {target_vdat.var_name} {target_vdat.get_objective(self._target_stack_level(stack_level))} " +
                f"run data get storage {source_vdat.ns} {source_vdat.get_store_path(self._source_stack_level(stack_level))}.{source_vdat.var_name}.value"
            )]
        elif isinstance(self.value, SmtConstInt):
            return [ComCmd(f"scoreboard players set {target_vdat.var_name} {target_vdat.get_objective(self._target_stack_level(stack_level))} {self.value.value}")]
        else:
            raise VirtualRepError(
                f"Variable `{target_vdat.var_name}` from objective `{target_vdat.get_objective(self._target_stack_level(stack_level))}` attempted to assign " +
                f"to unknown atom of type `{type(self.value).__name__}`"
            )

    def _vir_exec_target_var_source(self, target_vdat: SmtVarLinkage, target_type: ExecType, source_var: SmtVar, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        if target_type.target == ExecCoreTypes.WORLD:
            return []  # No operation required to assign to world
        elif target_type.target in (ExecCoreTypes.PLAYER, ExecCoreTypes.ENTITY):
            if not isinstance(target_vdat, SmtExecVarLinkage):
                raise VirtualRepError(
                    f"Attempted to assign to the executable variable `{target_vdat.var_name}` however it has no tag attached"
                )
            source_vdat = linker.lookup_var(source_var)
            if not isinstance(source_vdat, SmtExecVarLinkage):
                raise VirtualRepError(
                    f"Attempted to assign to the executable variable `{target_vdat.var_name}` however " +
                    f"the source variable `{source_vdat.var_name}` has no tag attached"
                )
            source_type = source_var.get_type()
            if not isinstance(source_type, ExecType):
                raise VirtualRepError(f"Cannot assign Executable type ({target_type}) to an Inert type ({source_type}) in assignment ({repr(self)})")
            if source_type.target == ExecCoreTypes.WORLD:
                raise VirtualRepError(
                    f"Cannot assign variable `{target_vdat.var_name}` of type `{target_type.render()}` to variable " +
                    f"`{source_vdat.var_name}` of type `{source_type}` - `{source_type}` is not a valid `{target_type.render()}`"
                )
            return [
                ComCmd(f"tag {target_vdat.get_selector(self._target_stack_level(stack_level))} remove {target_vdat.get_full_tag(self._target_stack_level(stack_level))}"),
                ComCmd(f"tag {source_vdat.get_selector(self._source_stack_level(stack_level))} add {target_vdat.get_full_tag(self._target_stack_level(stack_level))}")
            ]
        else:
            raise UnreachableError(f"Unhandled var exec target `{repr(target_type)}`")

    def _vir_inert_target_var_source(self, target_vdat: SmtVarLinkage, source_var: SmtVar, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        source_vdat: SmtVarLinkage = linker.lookup_var(source_var)
        if isinstance(source_vdat, SmtObjVarLinkage):
            return [
                ComCmd(
                    f"execute store result storage {target_vdat.ns} {target_vdat.get_store_path(self._target_stack_level(stack_level))}.{target_vdat.var_name}.value " +
                    f"int 1 run scoreboard players get {source_vdat.var_name} {source_vdat.get_objective(self._source_stack_level(stack_level))}"
                ), ComCmd(
                    f"data modify storage {target_vdat.ns} {target_vdat.get_store_path(self._target_stack_level(stack_level))}.{target_vdat.var_name}.is_null " +
                    f"set value 0b"
                )
            ]
        else:
            return [
                ComCmd(
                    f"data modify storage {target_vdat.ns} {target_vdat.get_store_path(self._target_stack_level(stack_level))}.{target_vdat.var_name}.value set " +
                    f"from storage {source_vdat.ns} {source_vdat.get_store_path(self._source_stack_level(stack_level))}.{source_vdat.var_name}.value"
                ),
                ComCmd(
                    f"data modify storage {target_vdat.ns} {target_vdat.get_store_path(self._target_stack_level(stack_level))}.{target_vdat.var_name}.is_null set " +
                    f"from storage {source_vdat.ns} {source_vdat.get_store_path(self._source_stack_level(stack_level))}.{source_vdat.var_name}.is_null"
                ),
            ]

    def _vir_inert_target_const_source(self, target_vdat: SmtVarLinkage, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        cmds: List[ComCmd] = []
        if isinstance(self.value, SmtConstInt):
            cmds.append(ComCmd(
                f"data modify storage {target_vdat.ns} {target_vdat.get_store_path(self._target_stack_level(stack_level))}.{target_vdat.var_name}.value " +
                f"set value {self.value.value}"
            ))
        elif isinstance(self.value, SmtConstStr):
            cmds.append(ComCmd(
                f'data modify storage {target_vdat.ns} {target_vdat.get_store_path(self._target_stack_level(stack_level))}.{target_vdat.var_name}.value set value "' +
                self.value.value.replace('"', '\\"') + '"'
            ))
        elif isinstance(self.value, SmtConstFloat):
            cmds.append(ComCmd(
                f"data modify storage {target_vdat.ns} {target_vdat.get_store_path(self._target_stack_level(stack_level))}.{target_vdat.var_name}.value " +
                f"set value {round(self.value.value, 18)}d"
            ))
        elif isinstance(self.value, SmtConstNull):
            return [ComCmd(
                f"data modify storage {target_vdat.ns} {target_vdat.get_store_path(self._target_stack_level(stack_level))}.{target_vdat.var_name}.is_null " +
                f"set value 1b"
            )]
        else:
            raise VirtualRepError(
                f"Variable `{target_vdat.var_name}` from objective `{target_vdat.get_store_path(self._target_stack_level(stack_level))}` attempted to assign " +
                f"to unknown atom of type `{type(self.value).__name__}`"
            )

        if isinstance(self.value, (SmtConstInt, SmtConstStr, SmtConstFloat)):
            # If assigning to an atom that cannot be null
            target_type = self.target_var.get_type()
            if not isinstance(target_type, InertType):
                raise VirtualRepError(f"Non-Inert type `{self.target_var.get_type()}` assigning to integer `{self.value.value}`")
            if target_type.nullable:
                # Only bother to use a command removing is_null for variables that might currently be null
                cmds.append(ComCmd(
                    f"data modify storage {target_vdat.ns} {target_vdat.get_store_path(self._target_stack_level(stack_level))}.{target_vdat.var_name}.is_null set value 0b"
                ))
        return cmds

    def virtualize(self, linker: 'SmtLinker', stack_level: int) -> List[ComCmd]:
        target_type: ComType = self.target_var.get_type()
        target_vdat: SmtVarLinkage = linker.lookup_var(self.target_var)
        if isinstance(target_vdat, SmtObjVarLinkage):  # Peal off int operations
            return self._vir_obj_target(target_vdat, linker, stack_level)
        elif isinstance(target_type, ExecType):
            if isinstance(self.value, SmtVar):
                return self._vir_exec_target_var_source(target_vdat, target_type, self.value, linker, stack_level)
            elif isinstance(self.value, SmtWorld):
                return []  # No operation required to assign to world
            else:
                raise VirtualRepError(f"Assigning to exec-typed variable `{repr(self.target_var)}` however source is neither a SmtVar or world, found: {repr(self.value)}")
        elif isinstance(target_type, InertType):
            if isinstance(self.value, SmtVar):
                return self._vir_inert_target_var_source(target_vdat, self.value, linker, stack_level)
            else:
                return self._vir_inert_target_const_source(target_vdat, linker, stack_level)
        elif isinstance(target_type, StructType):
            raise VirtualRepError(f"Assigning to variable `{repr(self.target_var)}` which is of type 'StructType' during VirtualRep layer?")
        else:
            raise VirtualRepError(f"Unhandled assignment case: `{repr(self)}`.  (target_type={target_type}, target_vdat_type={type(target_vdat)})")


class SmtSpecialStackIncTargetAssignCmd(SmtAssignCmd):
    # Used when setting up next stack frame from this one

    def _target_stack_level(self, stack_level: int) -> int:
        return stack_level + 1


class SmtSpecialStackIncSourceAssignCmd(SmtAssignCmd):
    # Used when setting up next stack frame from this one

    def _source_stack_level(self, stack_level: int) -> int:
        return stack_level + 1
