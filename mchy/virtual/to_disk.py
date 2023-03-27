
from mchy.common.com_cmd import ComCmd
from mchy.errors import UnreachableError
from mchy.virtual.vir_dirs import VirFolder, VirMCHYFile, VirRawFile
import os


def disk_line(ln: ComCmd) -> str:
    return ln.cmd


def to_disk(cur_folder: VirFolder, cur_path: str) -> None:
    # create the current directory
    os.mkdir(cur_path)

    # Write the children to disk
    for child in cur_folder.children:
        if isinstance(child, VirFolder):
            to_disk(child, os.path.join(cur_path, child.fs_name))
        elif isinstance(child, VirMCHYFile):
            content = "\n".join([disk_line(line) for line in child.lines])+"\n"
            with open(os.path.join(cur_path, child.fs_name), mode="w") as file:
                file.write(content)
        elif isinstance(child, VirRawFile):
            with open(os.path.join(cur_path, child.fs_name), mode="w") as file:
                file.write(child.content)
        else:
            raise UnreachableError(f"Unknown child of VirFSNode `{type(child).__name__}`")
