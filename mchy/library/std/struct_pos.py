from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, Union

from mchy.cmd_modules.chains import IChain, IChainLink
from mchy.cmd_modules.docs_data import DocsData
from mchy.cmd_modules.function import IParam
from mchy.cmd_modules.name_spaces import Namespace
from mchy.cmd_modules.struct import IField, IStruct
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import ComType, ExecCoreTypes, ExecType, InertCoreTypes, InertType
from mchy.contextual.struct.expr import CtxChainLink, CtxExprNode, CtxExprPyStruct
from mchy.contextual.struct.expr.literals import CtxExprLitFloat, CtxExprLitInt, CtxExprLitNull
from mchy.contextual.struct.expr.structs import CtxPyStruct
from mchy.contextual.struct.expr.var import CtxExprVar
from mchy.errors import ContextualisationError, ConversionError, VirtualRepError
from mchy.library.std.ns import STD_NAMESPACE
from mchy.stmnt.struct.atoms import SmtAtom
from mchy.stmnt.struct.struct import SmtPyStructInstance


class StructPos(IStruct):

    def get_docs(self) -> DocsData:
        return DocsData(
            short_summary="Stores a position in the world for later reference"
        )

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_name(self) -> str:
        return "Pos"

    def get_fields(self) -> Sequence[IField]:
        return [
            IField("x", float),
            IField("y", float),
            IField("z", float),
            IField("dx", float),
            IField("dy", float),
            IField("dz", float),
            IField("rx", float),
            IField("ry", float),
            IField("rz", float),
            IField("origin", ExecType(ExecCoreTypes.ENTITY, True)),
        ]

    @staticmethod
    def _cast_int_if_close(x: float) -> Union[float, int]:
        if abs(round(x) - x) < 0.000001:
            return round(x)
        return x

    @staticmethod
    def build_position_string(instance: SmtPyStructInstance, *, suppress_y_coord: bool = False, cast_to_int: bool = False) -> Tuple[str, Optional[SmtAtom]]:
        # Get fields
        f_x = instance.get_asserting_type_or_NIL("x", float)
        f_y = instance.get_asserting_type_or_NIL("y", float)
        f_z = instance.get_asserting_type_or_NIL("z", float)
        f_dx = instance.get_asserting_type_or_NIL("dx", float)
        f_dy = instance.get_asserting_type_or_NIL("dy", float)
        f_dz = instance.get_asserting_type_or_NIL("dz", float)
        f_rx = instance.get_asserting_type_or_NIL("rx", float)
        f_ry = instance.get_asserting_type_or_NIL("ry", float)
        f_rz = instance.get_asserting_type_or_NIL("rz", float)
        f_origin = instance.get_asserting_type_or_NIL("origin", SmtAtom)  # type: ignore  # mypy false positive
        # Sanitize data
        if any([f_rx != instance.NIL, f_ry != instance.NIL, f_rz != instance.NIL]):
            # Rotational/directed coords are used
            if not all([f_rx != instance.NIL, f_ry != instance.NIL, f_rz != instance.NIL]):
                raise VirtualRepError("If any rotational values are defined then all of them must be")
            if (f_x != instance.NIL or f_dx != instance.NIL or f_y != instance.NIL or f_dy != instance.NIL or f_z != instance.NIL or f_dz != instance.NIL):
                VirtualRepError(f"Rotational coordinates are defined, cannot override with relative or absolute alternatives (pos={instance.render()})")
        else:
            # constant/reletive coords only
            if f_x == instance.NIL and f_dx == instance.NIL:
                raise VirtualRepError(f"No value for x? (pos={instance.render()})")
            if f_y == instance.NIL and f_dy == instance.NIL:
                raise VirtualRepError(f"No value for y? (pos={instance.render()})")
            if f_z == instance.NIL and f_dz == instance.NIL:
                raise VirtualRepError(f"No value for z? (pos={instance.render()})")
            if f_x != instance.NIL and f_dx != instance.NIL:
                raise VirtualRepError(f"Multiple values for x? (pos={instance.render()})")
            if f_y != instance.NIL and f_dy != instance.NIL:
                raise VirtualRepError(f"Multiple values for y? (pos={instance.render()})")
            if f_z != instance.NIL and f_dz != instance.NIL:
                raise VirtualRepError(f"Multiple values for z? (pos={instance.render()})")
        if (f_origin == instance.NIL) and any(
                    [f_dx != instance.NIL, f_dy != instance.NIL, f_dz != instance.NIL, f_rx != instance.NIL, f_ry != instance.NIL, f_rz != instance.NIL]
                ):
            raise VirtualRepError(f"Relative coord without origin? (pos={instance.render()})")
        # cast floats near ints to ints
        if f_x != instance.NIL:
            f_x = StructPos._cast_int_if_close(f_x)
        if f_y != instance.NIL:
            f_y = StructPos._cast_int_if_close(f_y)
        if f_z != instance.NIL:
            f_z = StructPos._cast_int_if_close(f_z)
        if f_dx != instance.NIL:
            f_dx = StructPos._cast_int_if_close(f_dx)
        if f_dy != instance.NIL:
            f_dy = StructPos._cast_int_if_close(f_dy)
        if f_dz != instance.NIL:
            f_dz = StructPos._cast_int_if_close(f_dz)
        if f_rx != instance.NIL:
            f_rx = StructPos._cast_int_if_close(f_rx)
        if f_ry != instance.NIL:
            f_ry = StructPos._cast_int_if_close(f_ry)
        if f_rz != instance.NIL:
            f_rz = StructPos._cast_int_if_close(f_rz)
        # force cast to int if needed
        if cast_to_int:
            if f_x != instance.NIL:
                f_x = round(f_x)
            if f_y != instance.NIL:
                f_y = round(f_y)
            if f_z != instance.NIL:
                f_z = round(f_z)
        # build coord_string
        coord_string: str = (
            (
                (str(f_x) if f_x != instance.NIL else "") +
                (f"~{f_dx}" if f_dx != instance.NIL else "") +
                (f"^{f_rx}" if f_rx != instance.NIL else "") + " "
            ) + (
                (
                    (str(f_y) if f_y != instance.NIL else "") +
                    (f"~{f_dy}" if f_dy != instance.NIL else "") +
                    (f"^{f_ry}" if f_ry != instance.NIL else "") + " "
                ) if not suppress_y_coord else ""
            ) + (
                (str(f_z) if f_z != instance.NIL else "") +
                (f"~{f_dz}" if f_dz != instance.NIL else "") +
                (f"^{f_rz}" if f_rz != instance.NIL else "")
            )
        )
        if f_origin == instance.NIL:
            return coord_string, None
        else:
            return coord_string, f_origin


class ChainLinkPos(IChainLink):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_name(self) -> str:
        return "pos"

    def get_params(self) -> Optional[Sequence[IParam]]:
        return None


class ChainPosConstant(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkPos

    def get_name(self) -> str:
        return "constant"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("x", InertType(InertCoreTypes.FLOAT, const=True)),
            IParam("y", InertType(InertCoreTypes.FLOAT, const=True)),
            IParam("z", InertType(InertCoreTypes.FLOAT, const=True)),
        ]

    def get_chain_type(self) -> ComType:
        return StructPos.get_type()

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: CtxPyStruct) -> 'CtxExprPyStruct':
        this_link = chain_links[-1]
        return CtxExprPyStruct(struct, {
            "x": this_link.get_arg_for_param_described("x", CtxExprLitFloat).value,
            "y": this_link.get_arg_for_param_described("y", CtxExprLitFloat).value,
            "z": this_link.get_arg_for_param_described("z", CtxExprLitFloat).value
        })


class ChainPosGet(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkPos

    def get_name(self) -> str:
        return "get"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.ENTITY, True)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("dx", InertType(InertCoreTypes.FLOAT, const=True), CtxExprLitInt(0, src_loc=ComLoc())),
            IParam("dy", InertType(InertCoreTypes.FLOAT, const=True), CtxExprLitInt(0, src_loc=ComLoc())),
            IParam("dz", InertType(InertCoreTypes.FLOAT, const=True), CtxExprLitInt(0, src_loc=ComLoc())),
        ]

    def get_chain_type(self) -> ComType:
        return StructPos.get_type()

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: CtxPyStruct) -> 'CtxExprPyStruct':
        exec_type = executor.get_type()
        if not isinstance(exec_type, ExecType):
            raise ContextualisationError(f"Executor not of executable type?")
        if exec_type.target == ExecCoreTypes.WORLD:
            raise ConversionError(f"executor.pos.get() cannot be called on executor's of type world")
        this_link = chain_links[-1]
        return CtxExprPyStruct(struct, {
            "dx": this_link.get_arg_for_param_described("dx", CtxExprLitFloat).value,
            "dy": this_link.get_arg_for_param_described("dy", CtxExprLitFloat).value,
            "dz": this_link.get_arg_for_param_described("dz", CtxExprLitFloat).value,
            "origin": executor
        })


class ChainPosSetCoord(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkPos

    def get_name(self) -> str:
        return "set_coord"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.WORLD, False)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("old_pos", StructPos.get_type()),
            IParam("force_x", InertType(InertCoreTypes.FLOAT, const=True, nullable=True), CtxExprLitNull(src_loc=ComLoc())),
            IParam("force_y", InertType(InertCoreTypes.FLOAT, const=True, nullable=True), CtxExprLitNull(src_loc=ComLoc())),
            IParam("force_z", InertType(InertCoreTypes.FLOAT, const=True, nullable=True), CtxExprLitNull(src_loc=ComLoc())),
        ]

    def get_chain_type(self) -> ComType:
        return StructPos.get_type()

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: CtxPyStruct) -> 'CtxExprPyStruct':
        binding: Dict[str, Any] = {}
        this_link = chain_links[-1]
        old_pos = this_link.get_arg_for_param_of_name("old_pos")
        if not isinstance(old_pos, CtxExprPyStruct):
            raise ContextualisationError(f"Struct param not a literal struct, found: `{repr(old_pos)}`")
        # check old_pos not directed (uses ^ style coords rather than ~ or constants)
        _defined_f_labels = {field.label for field in old_pos.struct_instance.get_set_fields()}
        if any((f_label in _defined_f_labels) for f_label in {"rx", "ry", "rz"}):
            raise ConversionError(f"Cannot call set_coord on directed positions, coordinate would be inconsistent")
        # build bindings
        for param_name, struct_name, preserve_name in (("force_x", "x", "dx"), ("force_y", "y", "dy"), ("force_z", "z", "dz")):
            arg_value = this_link.get_arg_for_param_of_name(param_name)
            if isinstance(arg_value, CtxExprLitNull):
                if preserve_name in old_pos.get_set_field_names():
                    binding[preserve_name] = old_pos.get_py_field_data(preserve_name, float)
                elif struct_name in old_pos.get_set_field_names():
                    binding[struct_name] = old_pos.get_py_field_data(struct_name, float)
                else:
                    raise ContextualisationError(f"Supplied position in invalid state: neither `{preserve_name}` nor `{struct_name}` provided")
            elif isinstance(arg_value, CtxExprLitFloat):
                binding[struct_name] = arg_value.value
            elif isinstance(arg_value, CtxExprLitInt):
                binding[struct_name] = float(arg_value.value)
            else:
                raise ContextualisationError(f"argument of param `{param_name}` is neither a int or null, found {repr(arg_value)}")
        # add origin to bindings
        binding["origin"] = old_pos.get_mchy_field_data("origin", ExecType(ExecCoreTypes.ENTITY, group=True))

        # return the new pos
        return CtxExprPyStruct(struct, binding)


class ChainPosGetDirected(IChain):

    def get_namespace(self) -> 'Namespace':
        return STD_NAMESPACE

    def get_predecessor_type(self) -> Union[Type['IChainLink'], ExecType]:
        return ChainLinkPos

    def get_name(self) -> str:
        return "get_directed"

    def get_refined_executor(self) -> ExecType:
        return ExecType(ExecCoreTypes.ENTITY, True)

    def get_params(self) -> Optional[Sequence[IParam]]:
        return [
            IParam("rx", InertType(InertCoreTypes.FLOAT, const=True), CtxExprLitInt(0, src_loc=ComLoc())),
            IParam("ry", InertType(InertCoreTypes.FLOAT, const=True), CtxExprLitInt(0, src_loc=ComLoc())),
            IParam("rz", InertType(InertCoreTypes.FLOAT, const=True), CtxExprLitInt(0, src_loc=ComLoc())),
        ]

    def get_chain_type(self) -> ComType:
        return StructPos.get_type()

    def yield_struct_instance(self, executor: 'CtxExprNode', chain_links: List['CtxChainLink'], struct: CtxPyStruct) -> 'CtxExprPyStruct':
        exec_type = executor.get_type()
        if not isinstance(exec_type, ExecType):
            raise ContextualisationError(f"Executor not of executable type?")
        if exec_type.target == ExecCoreTypes.WORLD:
            raise ConversionError(f"executor.pos.get_directed() cannot be called on executor's of type world")
        this_link = chain_links[-1]
        return CtxExprPyStruct(struct, {
            "rx": this_link.get_arg_for_param_described("rx", CtxExprLitFloat).value,
            "ry": this_link.get_arg_for_param_described("ry", CtxExprLitFloat).value,
            "rz": this_link.get_arg_for_param_described("rz", CtxExprLitFloat).value,
            "origin": executor
        })
