
from mchy.cmd_modules.name_spaces import Namespace


class _TestNamespace(Namespace):

    def __init__(self, name: str) -> None:
        # The root testing namespace is it's own parent on construction but thus is undone immediately so that no loops exist by the time it's visible
        super().__init__(name, self)
        self.parent_ns = None
        self.children = set()


ROOT_TESTING_NAMESPACE = _TestNamespace("__meta_testing__")
