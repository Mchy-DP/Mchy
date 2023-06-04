

from abc import ABC, abstractmethod
import re
from typing import Dict, FrozenSet, List, MutableSet, Optional, Tuple, Type, Union
from mchy.common.config import Config
from mchy.errors import ConversionError, VirtualRepError
from mchy.virtual.vir_dirs import VirFSNode, VirFolder, VirMCHYFile, VirNSFolder
from mchy.virtual.vir_dp import VirDP


# ===== Core Structures =====


class VirOptimisation(ABC):

    __optimizations: List['VirOptimisation'] = []
    __singleton_access: Dict[Type['VirOptimisation'], 'VirOptimisation'] = {}

    @staticmethod
    def optimizations() -> Tuple['VirOptimisation', ...]:
        return tuple(VirOptimisation.__optimizations)

    @classmethod
    def get(cls) -> 'VirOptimisation':
        return VirOptimisation.__singleton_access[cls]

    def __init_subclass__(cls) -> None:
        VirOptimisation.__singleton_access[cls] = cls()
        VirOptimisation.__optimizations.append(cls.get())
        return super().__init_subclass__()

    @abstractmethod
    def cost(self) -> int:
        """The cost of this optimization, more expensive optimizations are tried later

        0 - basically free
        1 - cheap
        2 - normal
        3 - expensive (major file changes e.g. functions)
        4 - very expensive (many file changes)
        5 - regeneration (optimizations equivalent to regenerating the original VirDP)
        """
        ...

    @abstractmethod
    def level(self) -> Config.Optimize:
        ...

    @abstractmethod
    def optimize(self, vir_dp: VirDP) -> Optional[VirDP]:
        ...


def optimize(vir_dp: VirDP) -> VirDP:
    """Optimizations may change the passed in VirDP and will return the VirDP to treat as optimal"""
    optimisations: List[VirOptimisation] = []
    for opt in VirOptimisation.optimizations():
        if opt.level().value <= vir_dp._config.optimisation.value:
            optimisations.append(opt)
    optimisations.sort(key=lambda opt: opt.cost())

    for _ in range(10000):  # Prevents inf loops
        for opt in optimisations:
            res = opt.optimize(vir_dp)
            if res is not None:
                vir_dp = res
                break
        else:
            break  # If we couldn't apply any optimizations: Stop
    else:
        vir_dp._config.logger.warn("Over 10000 optimisation applied, infinite loop probable, Ending")

    return vir_dp


# ===== Optimisations =====

class CallableFilesOnly(VirOptimisation):

    def cost(self) -> int:
        return 5  # This is VERY expensive

    def level(self) -> Config.Optimize:
        return Config.Optimize.O2

    _REGEX_FUNC_LINE = re.compile(r"^(execute.*run )?function (.*:[^/]*(/.*)*)$")

    def _parse_link(self, vir_dp: VirDP, function_line: str) -> Optional[VirMCHYFile]:
        """Get the VirDP file linked to via the function_line or None if it is an external resource"""
        ns, path = function_line.split(":")
        if ns != vir_dp._config.project_namespace:
            return None  # Call doesn't link to this datapack
        path_elems = path.split("/")
        if path_elems[0] != "generated":
            return None  # This call references functions we didn't generate
        cur_path = ns+":"+path_elems[0]
        cur_loc: VirFSNode = vir_dp.generated_root
        for path_elem in path_elems[1:]:
            if not isinstance(cur_loc, VirFolder):
                raise ConversionError(f"Encountered path that performs a directory lookup on a file: {cur_path}")
            cur_path += "/" + path_elem
            for child in cur_loc.children:
                if child.get_namespace_loc() == cur_path:
                    cur_loc = child
                    break
            else:
                vir_dp._config.logger.warn(f"File/Folder at {cur_path} does not seem to exist")
                return None  # This seems to link to a non-existent file
        if isinstance(cur_loc, VirMCHYFile):
            return cur_loc
        else:
            raise ConversionError(f"Path links to non-mchy file {type(cur_loc).__name__}(fs_name={cur_loc.fs_name})? (path: {cur_path})")

    def optimize(self, vir_dp: VirDP) -> Optional[VirDP]:
        # initialize file search
        finished_files: MutableSet[VirMCHYFile] = set()
        found_files: MutableSet[VirMCHYFile] = set()
        found_files.add(vir_dp.load_master_file)
        found_files.add(vir_dp.tick_master_file)
        for file in vir_dp.public_funcs_accessor_fld.children:
            if isinstance(file, VirMCHYFile):
                found_files.add(file)

        # parse all reachable files
        while len(found_files) >= 1:
            active_file = found_files.pop()
            for line in active_file.lines:
                if (found := CallableFilesOnly._REGEX_FUNC_LINE.match(line.cmd)) is not None:
                    file_link = self._parse_link(vir_dp, found.group(2))
                    if (file_link is not None) and (file_link not in finished_files):
                        found_files.add(file_link)
            finished_files.add(active_file)
        live_files = frozenset(finished_files)

        # regenerate generated filesystem
        dead_files = self._prune_tree(vir_dp.generated_root, live_files)

        if len(dead_files) == 0:
            return None
        else:
            if len((_isect := live_files.intersection(dead_files))) >= 1:
                raise VirtualRepError(f"Some files are both alive and dead? {repr(_isect)}")
            vir_dp._config.logger.very_verbose(f"VIR: {type(self).__name__}: Deleting `{len(dead_files)}` unreachable files (Preserved: `{len(live_files)}`)")
            return vir_dp

    def _prune_tree(self, tree: VirFolder, live_files: FrozenSet[VirMCHYFile]) -> List[VirMCHYFile]:
        """Visit the generated filesystem tree keeping only live_files and return any deleted files"""
        dead: List[VirMCHYFile] = []
        for child in tree.children:
            if isinstance(child, VirFolder):
                dead.extend(self._prune_tree(child, live_files))
            elif isinstance(child, VirMCHYFile):
                if child not in live_files:
                    dead.append(child)
                    tree.delete_child(child)
            else:
                pass  # Non-mchy files are implicitly preserved
        return dead


class DeleteEmptyFolders(VirOptimisation):

    def cost(self) -> int:
        return 2

    def level(self) -> Config.Optimize:
        return Config.Optimize.O1

    def optimize(self, vir_dp: VirDP) -> Optional[VirDP]:
        if (pcount := self._prune_empty(vir_dp.generated_root)) >= 1:
            vir_dp._config.logger.very_verbose(f"VIR: {type(self).__name__}: Deleting `{pcount}` empty folders")
            return vir_dp
        else:
            return None

    def _prune_empty(self, node: VirFolder) -> int:
        pruned: int = 0
        for child in node.children:
            if isinstance(child, VirFolder):
                pruned += self._prune_empty(child)
        if len(node.children) == 0:
            node.delete()
            pruned += 1
        return pruned
