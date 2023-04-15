

from abc import ABC, abstractmethod, abstractproperty
from itertools import zip_longest
from typing import Any, List, Optional, TypeVar, Union

from mchy.common.com_loc import ComLoc

_GenNode = TypeVar('_GenNode', bound='Node')
_LitNode = TypeVar('_LitNode', bound='ExprLitGen')


class Node(ABC):

    def __init__(self, *initial_children: 'Node', _loc: ComLoc = ComLoc(), **kwargs):
        super().__init__(**kwargs)
        self.children: List[Node] = list(initial_children)
        self.loc: ComLoc = _loc

    def with_loc(self: _GenNode, loc: ComLoc) -> _GenNode:
        self.loc = loc
        return self

    def clone(self: _GenNode) -> _GenNode:
        """Create a deep copy of this node"""
        children: List[Node] = []
        for child in self.children:
            children.append(child.clone())
        return type(self)(*children)

    def replace_child(self, child_index: int, new_tree: 'Node'):
        """Replace this node's child at `child_index` with `new_tree`

        Args:
            child_index: The index to replace at
            new_tree: The new node to insert

        Raises:
            ValueError: Raised if there is no node at `child_index`
        """
        if child_index >= len(self.children):
            raise ValueError(f"Replacement impossible, no child of `{str(self)}` at index `{child_index}`")
        self.children = self.children[:child_index] + [new_tree] + self.children[child_index+1:]

    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join([type(child).__name__ for child in self.children])})"

    def deep_repr(self) -> str:
        return f"{type(self).__name__}({', '.join([child.deep_repr() for child in self.children])})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Node):
            return type(self) == type(other) and all(
                [s_child == o_child for s_child, o_child in zip_longest(self.children, other.children, fillvalue=None)]
            )
        return False


class Root(Node):
    pass


class Scope(Node):

    def __init__(self, *stmnts: 'Union[Stmnt, FunctionDecl]', **kwargs):
        super().__init__(*stmnts, **kwargs)
        self.stmnts: List[Union[Stmnt, FunctionDecl]] = list(stmnts)


class FunctionDecl(Node):

    def __init__(
                self,
                func_name: str,
                exec_type: 'TypeNode',
                return_type: 'TypeNode',
                body: 'Node',
                decorators: List['Decorator'],
                def_loc: ComLoc,
                *params: 'ParamDecl',
                **kwargs
            ):
        super().__init__(exec_type, return_type, body, *decorators, *params, **kwargs)
        self.func_name: str = func_name
        self.exec_type: TypeNode = exec_type
        self.return_type: TypeNode = return_type
        self.body: Node = body
        self.decorators: List[Decorator] = decorators
        self.params: List[ParamDecl] = list(params)
        self.def_loc: ComLoc = def_loc  # The loc associated with the def token -- used in downstream errors

    def clone(self: 'FunctionDecl') -> 'FunctionDecl':
        return type(self)(
            self.func_name,
            self.exec_type.clone(),
            self.return_type.clone(),
            self.body.clone(),
            [d.clone() for d in self.decorators],
            self.def_loc,
            *[param.clone() for param in self.params]
        )

    def __eq__(self, other: object) -> bool:
        return (super().__eq__(other) and isinstance(other, FunctionDecl) and (self.func_name == other.func_name))

    def deep_repr(self) -> str:
        return (
            super().deep_repr().split("(")[0] +
            f"(decorators=[{', '.join(repr(d) for d in self.decorators)}], " +
            f"func_name={self.func_name}, exec_type={repr(self.exec_type)}, return_type={repr(self.return_type)}" +
            f"params=["+', '.join(f"{param.param_name}: {repr(param.param_type)}"+("" if param.default_value is None else " = ...") for param in self.params)+"]" +
            f"body={type(self.body).__name__}(...)"
        )


class ParamDecl(Node):

    def __init__(self, param_name: 'ExprLitIdent', param_type: 'TypeNode', default_value: Optional['ExprGen'] = None, **kwargs):
        initial_children = [param_name, param_type]
        if default_value is not None:
            initial_children.append(default_value)
        super().__init__(*initial_children, **kwargs)
        self.param_name: ExprLitIdent = param_name
        self.param_type: TypeNode = param_type
        self.default_value: Optional[ExprGen] = default_value


class Decorator(Node):

    def __init__(self, decorator_name: 'ExprLitIdent', **kwargs):
        super().__init__(decorator_name, **kwargs)
        self.decorator_name_ident: ExprLitIdent = decorator_name

    @property
    def dec_name(self) -> str:
        return self.decorator_name_ident.value


class Stmnt(Node):
    pass


class WhileLoop(Stmnt):

    def __init__(self, cond: 'ExprGen', body: 'CodeBlock', **kwargs):
        super().__init__(cond, body, **kwargs)
        self.cond: ExprGen = cond
        self.body: CodeBlock = body


class ForLoop(Stmnt):

    def __init__(self, index_var_ident: 'ExprLitIdent', lower_bound: 'ExprGen', upper_bound: 'ExprGen', body: 'CodeBlock', **kwargs):
        super().__init__(index_var_ident, lower_bound, upper_bound, body, **kwargs)
        self.index_var_ident: ExprLitIdent = index_var_ident
        self.lower_bound: ExprGen = lower_bound
        self.upper_bound: ExprGen = upper_bound
        self.body: CodeBlock = body

    def clone(self: 'ForLoop') -> 'ForLoop':
        return type(self)(self.index_var_ident, self.lower_bound, self.upper_bound, self.body)


class IfStruct(Stmnt):

    def __init__(self, cond: 'ExprGen', body: 'CodeBlock', elif_struct: Optional['ElifStruct'] = None, else_struct: Optional['ElseStruct'] = None, **kwargs):
        initial_children: List[Node] = [cond, body]
        if elif_struct is not None:
            initial_children.append(elif_struct)
        if else_struct is not None:
            initial_children.append(else_struct)
        super().__init__(*initial_children, **kwargs)
        self.cond: ExprGen = cond
        self.body: CodeBlock = body
        self.elif_struct: Optional['ElifStruct'] = elif_struct
        self.else_struct: Optional['ElseStruct'] = else_struct


class ElifStruct(Stmnt):

    def __init__(self, cond: 'ExprGen', body: 'Node', elif_struct: Optional['ElifStruct'] = None, **kwargs):
        initial_children = [cond, body]
        if elif_struct is not None:
            initial_children.append(elif_struct)
        super().__init__(*initial_children, **kwargs)
        self.cond: ExprGen = cond
        self.body: Node = body
        self.elif_cont: Optional['ElifStruct'] = elif_struct


class ElseStruct(Stmnt):

    def __init__(self, body: 'Node', **kwargs):
        super().__init__(body, **kwargs)
        self.body: Node = body


class CodeBlock(Stmnt):
    pass


class VariableDecl(Stmnt):

    def __init__(self, read_only_type: bool, var_type: 'TypeNode', var_ident: 'ExprLitIdent', assignment_target: Optional['ExprGen'] = None, **kwargs):
        initial_children: List[Node] = [var_type]
        if assignment_target is not None:
            initial_children.append(assignment_target)
        super().__init__(*initial_children, **kwargs)
        self.read_only_type: bool = read_only_type
        self.var_type: TypeNode = var_type
        self.var_ident: ExprLitIdent = var_ident
        self.rhs: Optional['ExprGen'] = assignment_target

    @property
    def var_name(self) -> str:
        return self.var_ident.value

    def clone(self: 'VariableDecl') -> 'VariableDecl':
        return type(self)(self.read_only_type, self.var_type.clone(), self.var_ident, self.rhs.clone() if self.rhs is not None else None)

    def __eq__(self, other: object) -> bool:
        return (
            super().__eq__(other) and isinstance(other, VariableDecl) and
            (self.read_only_type == other.read_only_type) and
            (self.var_name == other.var_name)
        )

    def __repr__(self) -> str:
        return super().__repr__()[:-1] + f", name='{self.var_name}', read_only={self.read_only_type})"

    def deep_repr(self) -> str:
        left, right = super().deep_repr().split("(", 1)
        return left + f"(name='{self.var_name}', read_only={self.read_only_type}, " + right


class Assignment(Stmnt):

    def __init__(self, lhs: 'ExprGen', rhs: 'ExprGen', **kwargs):
        super().__init__(lhs, rhs, **kwargs)
        self.lhs: ExprGen = lhs
        self.rhs: ExprGen = rhs


class UserComment(Stmnt):

    def __init__(self, comment_text: str, **kwargs):
        super().__init__(**kwargs)
        self.comment_text = comment_text

    def clone(self: 'UserComment') -> 'UserComment':
        return type(self)(self.comment_text)

    def __eq__(self, other: object) -> bool:
        return (
            super().__eq__(other) and isinstance(other, UserComment) and
            (self.comment_text == other.comment_text)
        )

    def __repr__(self) -> str:
        return super().__repr__()[:-1] + f"comment_text='{self.comment_text}')"

    def deep_repr(self) -> str:
        return repr(self)


class ReturnLn(Stmnt):

    def __init__(self, target: 'ExprGen', **kwargs):
        super().__init__(target, **kwargs)
        self.target: ExprGen = target


class TypeNode(Node):

    def __init__(self, core_type: str, *, group: bool = False, compile_const: bool = False, nullable: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.core_type: str = core_type
        self.group: bool = group
        self.compile_const: bool = compile_const
        self.nullable: bool = nullable

    def clone(self: 'TypeNode') -> 'TypeNode':
        return type(self)(self.core_type, group=self.group, compile_const=self.compile_const, nullable=self.nullable)

    def __eq__(self, other: object) -> bool:
        return (
            super().__eq__(other) and isinstance(other, TypeNode) and
            (self.core_type == other.core_type) and
            (self.group == other.group) and
            (self.compile_const == other.compile_const) and
            (self.nullable == other.nullable)
        )

    def get_typestr(self) -> str:
        type_str: str = self.core_type
        if self.compile_const:
            type_str += "!"
        if self.nullable:
            type_str += "?"
        if self.group:
            type_str = f"Group[{type_str}]"
        return type_str

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.get_typestr()})"

    def deep_repr(self) -> str:
        return repr(self)


class ExprGen(Stmnt):
    """common parent of expression classes"""

    @abstractmethod
    def get_src(self) -> str:
        ...


class ExprFuncCall(ExprGen):

    def __init__(self, executor: ExprGen, func_name: 'ExprLitIdent', *params: 'ExprFragParam', **kwargs):
        super().__init__(executor, func_name, *params, **kwargs)
        self.executor: ExprGen = executor
        self.func_name_ident: ExprLitIdent = func_name
        self.params: List[ExprFragParam] = list(params)

    @property
    def func_name(self) -> str:
        return self.func_name_ident.value

    def get_src(self) -> str:
        return self.executor.get_src() + "." + self.func_name_ident.value + "("+", ".join(param.get_src() for param in self.params)+")"


class ExprFragParam(ExprGen):
    """Represents Call-site `parameter=expr` in a function call"""

    def __init__(self, *, value: ExprGen, label: Optional['ExprLitIdent'] = None, **kwargs):
        initial_children: List[Node] = []
        if label is not None:
            initial_children.append(label)
        initial_children.append(value)
        super().__init__(*initial_children, **kwargs)
        self.value: ExprGen = value
        self.label_ident: Optional[ExprLitIdent] = label

    @property
    def label(self) -> Optional[str]:
        return self.label_ident.value if self.label_ident is not None else None

    def get_src(self) -> str:
        return (f"{self.label} = " if self.label is None else "") + self.value.get_src()


class ExprPropertyAccess(ExprGen):

    def __init__(self, source: ExprGen, property_name: 'ExprLitIdent', **kwargs):
        super().__init__(source, property_name, **kwargs)
        self.source: ExprGen = source
        self.property_name_ident: ExprLitIdent = property_name

    @property
    def property_name(self) -> str:
        return self.property_name_ident.value

    def get_src(self) -> str:
        return self.source.get_src() + "." + self.property_name


class ExprExponent(ExprGen):

    def __init__(self, base: ExprGen, exponent: ExprGen, **kwargs):
        super().__init__(base, exponent, **kwargs)
        self.base: ExprGen = base
        self.exponent: ExprGen = exponent

    def get_src(self) -> str:
        return self.base.get_src() + "**" + self.exponent.get_src()


class ExprMult(ExprGen):

    def __init__(self, left: ExprGen, right: ExprGen, **kwargs):
        super().__init__(left, right, **kwargs)
        self.left: ExprGen = left
        self.right: ExprGen = right

    def get_src(self) -> str:
        return self.left.get_src() + " * " + self.right.get_src()


class ExprDiv(ExprGen):

    def __init__(self, left: ExprGen, right: ExprGen, **kwargs):
        super().__init__(left, right, **kwargs)
        self.left: ExprGen = left
        self.right: ExprGen = right

    def get_src(self) -> str:
        return self.left.get_src() + " / " + self.right.get_src()


class ExprMod(ExprGen):

    def __init__(self, left: ExprGen, right: ExprGen, **kwargs):
        super().__init__(left, right, **kwargs)
        self.left: ExprGen = left
        self.right: ExprGen = right

    def get_src(self) -> str:
        return self.left.get_src() + " % " + self.right.get_src()


class ExprPlus(ExprGen):

    def __init__(self, left: ExprGen, right: ExprGen, **kwargs):
        super().__init__(left, right, **kwargs)
        self.left: ExprGen = left
        self.right: ExprGen = right

    def get_src(self) -> str:
        return self.left.get_src() + " + " + self.right.get_src()


class ExprMinus(ExprGen):

    def __init__(self, left: ExprGen, right: ExprGen, **kwargs):
        super().__init__(left, right, **kwargs)
        self.left: ExprGen = left
        self.right: ExprGen = right

    def get_src(self) -> str:
        return self.left.get_src() + " - " + self.right.get_src()


class ExprEquality(ExprGen):

    def __init__(self, left: ExprGen, right: ExprGen, **kwargs):
        super().__init__(left, right, **kwargs)
        self.left: ExprGen = left
        self.right: ExprGen = right

    def get_src(self) -> str:
        return self.left.get_src() + " == " + self.right.get_src()


class ExprInequality(ExprGen):

    def __init__(self, left: ExprGen, right: ExprGen, **kwargs):
        super().__init__(left, right, **kwargs)
        self.left: ExprGen = left
        self.right: ExprGen = right

    def get_src(self) -> str:
        return self.left.get_src() + " != " + self.right.get_src()


class ExprCompGTE(ExprGen):

    def __init__(self, left: ExprGen, right: ExprGen, **kwargs):
        super().__init__(left, right, **kwargs)
        self.left: ExprGen = left
        self.right: ExprGen = right

    def get_src(self) -> str:
        return self.left.get_src() + " >= " + self.right.get_src()


class ExprCompGT(ExprGen):

    def __init__(self, left: ExprGen, right: ExprGen, **kwargs):
        super().__init__(left, right, **kwargs)
        self.left: ExprGen = left
        self.right: ExprGen = right

    def get_src(self) -> str:
        return self.left.get_src() + " > " + self.right.get_src()


class ExprCompLTE(ExprGen):

    def __init__(self, left: ExprGen, right: ExprGen, **kwargs):
        super().__init__(left, right, **kwargs)
        self.left: ExprGen = left
        self.right: ExprGen = right

    def get_src(self) -> str:
        return self.left.get_src() + " <= " + self.right.get_src()


class ExprCompLT(ExprGen):

    def __init__(self, left: ExprGen, right: ExprGen, **kwargs):
        super().__init__(left, right, **kwargs)
        self.left: ExprGen = left
        self.right: ExprGen = right

    def get_src(self) -> str:
        return self.left.get_src() + " < " + self.right.get_src()


class ExprNot(ExprGen):

    def __init__(self, target: ExprGen, **kwargs):
        super().__init__(target, **kwargs)
        self.target: ExprGen = target

    def get_src(self) -> str:
        return "not " + self.target.get_src()


class ExprAnd(ExprGen):

    def __init__(self, left: ExprGen, right: ExprGen, **kwargs):
        super().__init__(left, right, **kwargs)
        self.left: ExprGen = left
        self.right: ExprGen = right

    def get_src(self) -> str:
        return self.left.get_src() + " and " + self.right.get_src()


class ExprOr(ExprGen):

    def __init__(self, left: ExprGen, right: ExprGen, **kwargs):
        super().__init__(left, right, **kwargs)
        self.left: ExprGen = left
        self.right: ExprGen = right

    def get_src(self) -> str:
        return self.left.get_src() + " or " + self.right.get_src()


class ExprNullCoal(ExprGen):

    def __init__(self, optional_expr: ExprGen, default_expr: ExprGen, **kwargs):
        super().__init__(optional_expr, default_expr, **kwargs)
        self.optional_expr: ExprGen = optional_expr
        self.default_expr: ExprGen = default_expr

    def get_src(self) -> str:
        return self.optional_expr.get_src() + " ?? " + self.default_expr.get_src()


class ExprLitGen(ExprGen):
    """common parent of literal classes"""

    def __init__(self, literal_value, **kwargs):
        super().__init__(**kwargs)
        self._validate_value(literal_value)
        self._value = literal_value

    @property
    @abstractmethod
    def value(self) -> Any:
        """The literal's value"""
        ...

    @abstractmethod
    def _validate_value(self, value) -> None:
        """Raises errors if `value` is invalid for this literal"""
        ...

    def clone(self: _LitNode) -> _LitNode:
        return type(self)(self._value)

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other) and isinstance(other, ExprLitGen) and self._value_matches(other._value)

    def _value_matches(self, other_value):
        return self._value == other_value

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._value})"

    def deep_repr(self) -> str:
        return repr(self)


class ExprLitIdent(ExprLitGen):

    @property
    def value(self) -> str:
        return self._value

    def _validate_value(self, value) -> None:
        if not isinstance(value, str):
            raise TypeError(f"value for `{type(self).__name__}` must be an `str` not `{type(value).__name__}`")

    def get_src(self) -> str:
        return str(self.value)


class ExprLitStr(ExprLitGen):

    @property
    def value(self) -> str:
        return self._value

    def _validate_value(self, value) -> None:
        if not isinstance(value, str):
            raise TypeError(f"value for `{type(self).__name__}` must be an `str` not `{type(value).__name__}`")

    def get_src(self) -> str:
        return '"' + self.value.replace('"', '\\"') + '"'


class ExprLitFloat(ExprLitGen):

    @property
    def value(self) -> float:
        return self._value

    def _validate_value(self, value) -> None:
        if not isinstance(value, float):
            raise TypeError(f"value for `{type(self).__name__}` must be an `float` not `{type(value).__name__}`")

    def get_src(self) -> str:
        return str(self.value)


class ExprLitInt(ExprLitGen):

    @property
    def value(self) -> int:
        return self._value

    def _validate_value(self, value) -> None:
        if not isinstance(value, int):
            raise TypeError(f"value for `{type(self).__name__}` must be an `int` not `{type(value).__name__}`")

    def get_src(self) -> str:
        return str(self.value)


class ExprLitNull(ExprLitGen):

    @property
    def value(self) -> None:
        return self._value

    def _validate_value(self, value) -> None:
        if value is not None:
            raise TypeError(f"value for `{type(self).__name__}` must be `None` not of type `{type(value).__name__}`")

    def get_src(self) -> str:
        return "null"


class ExprLitWorld(ExprLitGen):

    @property
    def value(self) -> None:
        return self._value

    def _validate_value(self, value) -> None:
        if value is not None:
            raise TypeError(f"value for `{type(self).__name__}` must be `None` not of type `{type(value).__name__}`")

    def get_src(self) -> str:
        return "world"


class ExprLitThis(ExprLitGen):

    @property
    def value(self) -> None:
        return self._value

    def _validate_value(self, value) -> None:
        if value is not None:
            raise TypeError(f"value for `{type(self).__name__}` must be `None` not of type `{type(value).__name__}`")

    def get_src(self) -> str:
        return "this"


class ExprLitBool(ExprLitGen):

    @property
    def value(self) -> bool:
        return self._value

    def _validate_value(self, value) -> None:
        if not isinstance(value, bool):
            raise TypeError(f"value for `{type(self).__name__}` must be an `bool` not `{type(value).__name__}`")

    def get_src(self) -> str:
        return "true" if self.value else "false"
