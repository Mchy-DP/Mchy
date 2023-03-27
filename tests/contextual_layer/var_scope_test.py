
from mchy.contextual.struct import VarScope, InertType, MarkerDeclVar, CtxVar
from mchy.errors import ConversionError
import pytest


def test_scope_basic_functions_work():
    var_scope = VarScope()
    assert var_scope.var_defined("var1") is False
    assert var_scope.get_var("var1") is None
    marker = MarkerDeclVar().with_enclosing_function(None)
    var_scope.register_new_var("var1",  InertType("int"), False, marker)
    assert var_scope.var_defined("var1") is True
    assert var_scope.get_var("var1") == CtxVar("var1", InertType("int"), False, marker)


def test_double_definition_fails():
    var_scope = VarScope()
    marker = MarkerDeclVar().with_enclosing_function(None)
    var_scope.register_new_var("var1",  InertType("int"), False, marker)
    with pytest.raises(ConversionError):
        var_scope.register_new_var("var1",  InertType("int"), False, marker)


def test_re_definition_fails():
    var_scope = VarScope()
    var_scope.register_new_var("var1",  InertType("int"), False, MarkerDeclVar().with_enclosing_function(None))
    with pytest.raises(ConversionError):
        var_scope.register_new_var("var1",  InertType("str", const=True), True, MarkerDeclVar().with_enclosing_function(None))
