

from mchy.virtual.vir_dirs import VirFolder, VirRawFile


def test_add_child():
    foo = VirFolder("foo", None)
    foo.add_child(VirRawFile("bar.raw"))
    assert len(foo.children) == 1
    assert foo.children[0]._parent == foo


def test_implicit_add_child():
    foo = VirFolder("foo", None)
    VirRawFile("bar.raw", foo)
    assert len(foo.children) == 1
    assert foo.children[0]._parent == foo


def test_delete():
    foo = VirFolder("foo", None)
    bar = VirRawFile("bar.raw", foo)
    assert len(foo.children) == 1
    assert bar._parent == foo
    bar.delete()
    assert len(foo.children) == 0
    assert bar._parent is None


def test_delete_child():
    foo = VirFolder("foo", None)
    bar = VirRawFile("bar.raw", foo)
    assert len(foo.children) == 1
    assert bar._parent == foo
    foo.delete_child(bar)
    assert len(foo.children) == 0
    assert bar._parent is None


def test_delete_multiple_child():
    foo = VirFolder("foo", None)
    bar1 = VirRawFile("bar1.raw", foo)
    bar2 = VirRawFile("bar2.raw", foo)
    bar3 = VirRawFile("bar3.raw", foo)
    bar4 = VirRawFile("bar4.raw", foo)
    assert len(foo.children) == 4
    assert bar1._parent == foo
    assert bar2._parent == foo
    assert bar3._parent == foo
    assert bar4._parent == foo
    foo.delete_child(bar1)
    foo.delete_child(bar3)
    assert len(foo.children) == 2
    assert bar1._parent is None
    assert bar2._parent == foo
    assert bar3._parent is None
    assert bar4._parent == foo


def test_delete_nested_children():
    foo = VirFolder("foo", None)
    a = VirFolder("a", foo)
    b = VirFolder("b", a)
    c = VirFolder("c", b)
    bar = VirRawFile("bar.raw", c)
    assert len(foo.children) == 1
    assert len(a.children) == 1
    assert len(b.children) == 1
    assert len(c.children) == 1
    assert a._parent == foo
    assert b._parent == a
    assert c._parent == b
    assert bar._parent == c
    a.delete_child(b)
    assert len(foo.children) == 1
    assert len(a.children) == 0
    assert len(b.children) == 0
    assert len(c.children) == 0
    assert a._parent == foo
    assert b._parent is None
    assert c._parent is None
    assert bar._parent is None
