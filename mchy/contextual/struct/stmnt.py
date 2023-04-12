

import enum
from typing import TYPE_CHECKING, List, Literal, Optional, Union
from mchy.common.com_loc import ComLoc
from mchy.common.com_types import matches_type

from mchy.contextual.struct.expr import CtxExprNode
from mchy.contextual.struct.var_scope import CtxVar, VarScope
from mchy.contextual.struct.misc import SpecialTok
from mchy.errors import ConversionError
from mchy.mchy_ast.nodes import ExprGen

if TYPE_CHECKING:
    from mchy.contextual.struct.ctx_func import CtxMchyFunc


class CtxStmnt:
    pass


class CtxForLoop(CtxStmnt):

    def __init__(self, index_var: CtxVar, index_var_loc: ComLoc, lower_bound: CtxExprNode, upper_bound: CtxExprNode, exec_body: List[CtxStmnt]) -> None:
        self.index_var: CtxVar = index_var
        self.index_var_loc: ComLoc = index_var_loc
        self.lower_bound: CtxExprNode = lower_bound
        self.upper_bound: CtxExprNode = upper_bound
        self.exec_body: List[CtxStmnt] = exec_body

    def __repr__(self) -> str:
        body_str: str = ""
        if len(self.exec_body) == 1:
            body_str = f", body=[{repr(self.exec_body)}]"
        elif len(self.exec_body) >= 2:
            body_str = f", body=[{repr(self.exec_body)}, ...]"
        return type(self).__name__ + f"(var={repr(self.index_var.name)}, range=({repr(self.lower_bound)})..({repr(self.upper_bound)}){body_str})"


class CtxWhileLoop(CtxStmnt):

    def __init__(self, cond: CtxExprNode, exec_body: List[CtxStmnt]) -> None:
        self.cond: CtxExprNode = cond
        self.exec_body: List[CtxStmnt] = exec_body

    def __repr__(self) -> str:
        body_str: str = ""
        if len(self.exec_body) == 1:
            body_str = f", body=[{repr(self.exec_body)}]"
        elif len(self.exec_body) >= 2:
            body_str = f", body=[{repr(self.exec_body)}, ...]"
        return type(self).__name__ + f"(cond={repr(self.cond)}{body_str})"


class CtxBranch:  # If statement branch

    def __init__(self, cond: CtxExprNode, exec_body: List[CtxStmnt]) -> None:
        self.cond: CtxExprNode = cond
        self.exec_body: List[CtxStmnt] = exec_body


class CtxIfStmnt(CtxStmnt):

    def __init__(self, if_branch: CtxBranch, elif_branches: List[CtxBranch], else_branch: Optional[CtxBranch]) -> None:
        self.if_branch: CtxBranch = if_branch
        self.elif_branches: List[CtxBranch] = elif_branches
        self.else_branch: Optional[CtxBranch] = else_branch

    @property
    def branches(self) -> List[CtxBranch]:
        return [self.if_branch] + self.elif_branches + ([self.else_branch] if self.else_branch is not None else [])

    def __repr__(self) -> str:
        return (  # if (<FULL TEXT>) {<... if not empty>} elif (...) {<... if not empty>} else {<... if not empty>} -- only 1 component after if will ever be rendered
            type(self).__name__ + "(if (" + repr(self.if_branch.cond) + ") {" +
            ("..." if len(self.if_branch.exec_body) >= 1 else "") + "}" +
            ((" elif (...) {" + ("..." if len(self.elif_branches[0].exec_body) >= 1 else "") + "} ...") if len(self.elif_branches) > 1 else
                ((" else {" + ("..." if len(self.else_branch.exec_body) >= 1 else "") + "}") if self.else_branch is not None else "")) + ")"
        )


class Markers(CtxStmnt):
    pass


class MarkerDeclVar(Markers):

    def __init__(self) -> None:
        self._enclosing_function: Union[Literal[SpecialTok.UNASSIGNED], Optional['CtxMchyFunc']] = SpecialTok.UNASSIGNED
        self._default_assignment: Union[Literal[SpecialTok.UNASSIGNED], Optional['CtxAssignment']] = SpecialTok.UNASSIGNED

    def with_default_assignment(self, default_val: Optional['CtxAssignment']) -> 'MarkerDeclVar':
        self._default_assignment = default_val
        return self

    def with_enclosing_function(self, function: Optional['CtxMchyFunc']) -> 'MarkerDeclVar':
        self._enclosing_function = function
        return self

    @property
    def default_assignment(self) -> Optional['CtxAssignment']:
        if self._default_assignment == SpecialTok.UNASSIGNED:
            raise TypeError(f"Partially initialized variable marker declaration: no default assignment")
        return self._default_assignment

    @property
    def enclosing_function(self) -> Optional['CtxMchyFunc']:
        if self._enclosing_function == SpecialTok.UNASSIGNED:
            raise TypeError(f"Partially initialized variable marker declaration: no enclosing function")
        return self._enclosing_function

    def __repr__(self) -> str:
        return type(self).__name__ + f"({repr(self.default_assignment)})"


class MarkerParamDefault(Markers):

    def __init__(self, param: str, param_default: Optional[CtxExprNode]) -> None:
        self.param_name: str = param
        self.param_default: Optional[CtxExprNode] = param_default


class MarkerDeclFunc(Markers):

    def __init__(self, param_markers: List[MarkerParamDefault]) -> None:
        self._func: Optional['CtxMchyFunc'] = None
        self.param_markers: List[MarkerParamDefault] = param_markers

    def with_func(self, func: 'CtxMchyFunc') -> None:
        if self._func is not None:
            raise ValueError("Cannot double link function")
        self._func = func

    @property
    def func(self) -> 'CtxMchyFunc':
        if self._func is None:
            raise ValueError("No function linked")
        return self._func

    def __repr__(self) -> str:
        return type(self).__name__ + "(" + self.func.render() + ")"


class CtxExprHolder(CtxStmnt):

    def __init__(self, expr: CtxExprNode) -> None:
        self.expr: CtxExprNode = expr

    def __repr__(self) -> str:
        return type(self).__name__ + f"({repr(self.expr)})"


class CtxAssignment(CtxStmnt):

    def __init__(self, var: CtxVar, rhs: CtxExprNode) -> None:
        self.var: CtxVar = var
        self.rhs: CtxExprNode = rhs
        if not matches_type(self.var.var_type, self.rhs.get_type()):
            # TODO: add human readable rhs to error message
            raise ConversionError(
                f"Cannot assign expression of type `{self.rhs.get_type().render()}` to variable of type " +
                f"`{self.var.var_type.render()}`. ({self.var.render()} = ...)"
            ).with_loc(rhs.loc)

    def __repr__(self) -> str:
        return type(self).__name__ + f"({self.var.render()} = {repr(self.rhs)})"


class CtxReturn(CtxStmnt):

    def __init__(self, target: CtxExprNode) -> None:
        self.target: CtxExprNode = target

    def __repr__(self) -> str:
        return type(self).__name__ + f"({repr(self.target)})"


class CtxScopedCodeBlock(CtxStmnt):

    def __init__(self) -> None:
        self.stmnts: List[CtxStmnt] = []
        self.var_scope: VarScope = VarScope()
