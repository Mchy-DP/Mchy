
from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Sequence, Tuple, Union
from os import path as os_path

from mchy.errors import VirtualRepError
from mchy.common.com_cmd import ComCmd


class VirFSNode(ABC):
    """
    Virtual filesystem node - common parent of folders and files
    """

    def __init__(self, name: str, parent: Optional['VirFolder'] = None) -> None:
        self._parent: Optional['VirFolder'] = None  # Only set by contining folder
        self._name: str = name
        if parent is not None:
            self.link_parent(parent)

    def link_parent(self, parent: 'VirFolder') -> None:
        """Add link `parent` to this node and add this node as a child of parent if it is not already

        Args:
            parent: The folder to set as the parent

        Raises:
            VirtualRepError: If parent is already added
        """
        if self._parent is not None:
            raise VirtualRepError(f"Attempted to double link parent on `{self._name}`. (`{self._parent.path}` -> `{parent.path}`)")
        if self not in parent.children:
            parent.add_child(self)  # This will re-call this function once self is registered as a child
        else:
            self._parent = parent

    def get_namespace_loc(self) -> str:
        """Get the minecraft namespace-rooted path to this (e.g. ns:generated/extra/example)"""
        if self._parent is None:
            raise VirtualRepError(f"Attempted to resolve root folders namespace location -> No namespace authority in virtual filesystem.  Error path: {self.fs_name}")
        try:
            return self._parent.get_namespace_loc() + "/" + os_path.splitext(self.fs_name)[0]
        except VirtualRepError as e:
            raise VirtualRepError(str(e)+f"/{self.fs_name}").with_traceback(e.__traceback__) from None

    def delete(self) -> None:
        if self._parent is not None:
            if self in self._parent.children:
                self._parent.delete_child(self)  # This will re-call this function once self is unregistered as a child
            else:
                self._parent = None

    @property
    def fs_name(self) -> str:
        return self._name

    @property
    def path(self) -> str:
        if self._parent is None:
            return self.fs_name
        return os_path.join(self._parent.path, self.fs_name)


class VirFolder(VirFSNode):

    def __init__(self, name: str, parent: Optional['VirFolder'] = None, initial_children: Sequence[VirFSNode] = ()) -> None:
        super().__init__(name, parent)
        self._children: List[VirFSNode] = []
        for child in initial_children:
            self.add_child(child)

    def add_child(self, child: VirFSNode):
        self._children.append(child)
        child.link_parent(self)

    def delete_child(self, child: VirFSNode):
        self._children.remove(child)
        child.delete()

    def delete(self) -> None:
        for child in self.children:
            self.delete_child(child)
        super().delete()

    @property
    def children(self) -> Tuple[VirFSNode, ...]:
        return tuple(self._children)

    def get_child_with_name(self, name: str) -> Optional[VirFSNode]:
        for child in self._children:
            if child.fs_name == name:
                return child
        return None


class VirNSFolder(VirFolder):

    def __init__(self, ns_loc: str, name: str, parent: Optional['VirFolder'] = None, initial_children: Sequence[VirFSNode] = ()) -> None:
        super().__init__(name, parent, initial_children)
        self._ns_loc: str = ns_loc

    def get_namespace_loc(self) -> str:
        return self._ns_loc


class VirRawFile(VirFSNode):

    def __init__(self, name: str, parent: Optional['VirFolder'] = None, initial_contents: str = "") -> None:
        super().__init__(name, parent)
        self._content: str = initial_contents

    @property
    def content(self) -> str:
        return self._content


class VirBaseMCHYFile(VirFSNode):
    """Base class for MCHY files"""

    @property
    @abstractmethod
    def lines(self) -> Tuple[ComCmd, ...]:
        ...

    @abstractmethod
    def append(self, line: ComCmd) -> None:
        ...

    def get_file_data(self) -> str:
        return "\n".join(line.cmd for line in self.lines)

    def extend(self, lines: Sequence[ComCmd]) -> None:
        for line in lines:
            self.append(line)


class VirMCHYFile(VirBaseMCHYFile):

    def __init__(self, name: str, parent: Optional['VirFolder'] = None, initial_contents: Sequence[ComCmd] = ()) -> None:
        super().__init__(name, parent)
        self._lines: List[ComCmd] = list(initial_contents)

    @property
    def lines(self) -> Tuple[ComCmd, ...]:
        return tuple(self._lines)

    def append(self, line: ComCmd) -> None:
        if not isinstance(line, ComCmd):
            raise VirtualRepError("Attempted to append non-command")
        self._lines.append(line)


class VirDynamicMCHYFile(VirBaseMCHYFile):

    class _Section:

        def __init__(self, initial_contents: Sequence[ComCmd] = ()) -> None:
            self._lines: List[ComCmd] = list(initial_contents)

        def append(self, line: ComCmd):
            self._lines.append(line)

        def extend(self, lines: Sequence[ComCmd]) -> None:
            self._lines.extend(lines)

        @property
        def lines(self) -> Tuple[ComCmd, ...]:
            return tuple(self._lines)

    class InsertionCursor:

        def __init__(self, section: 'VirDynamicMCHYFile._Section'):
            self._section: 'VirDynamicMCHYFile._Section' = section

        def append(self, line: ComCmd):
            self._section.append(line)

        def extend(self, lines: Sequence[ComCmd]) -> None:
            self._section.extend(lines)

    def __init__(self, name: str, parent: Optional['VirFolder'] = None, initial_contents: Sequence[ComCmd] = ()) -> None:
        super().__init__(name, parent)
        self._file_sections: List[VirDynamicMCHYFile._Section] = []
        self._active_section = self._new_section(initial_contents)

    def _new_section(self, initial_contents: Sequence[ComCmd] = ()) -> _Section:
        new_section = VirDynamicMCHYFile._Section(initial_contents)
        self._file_sections.append(new_section)
        return new_section

    @property
    def lines(self) -> Tuple[ComCmd, ...]:
        return tuple(line for section in self._file_sections for line in section.lines)

    def append(self, line: ComCmd) -> None:
        if not isinstance(line, ComCmd):
            raise VirtualRepError("Attempted to append non-command")
        self._active_section.append(line)

    def reserve_spot(self) -> InsertionCursor:
        cursor = VirDynamicMCHYFile.InsertionCursor(self._new_section())
        self._active_section = self._new_section()
        return cursor
