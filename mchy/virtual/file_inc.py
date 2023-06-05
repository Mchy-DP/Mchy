from mchy.common.com_inclusion import FileInclusion
from mchy.common.config import Config
from mchy.errors import ConversionError
from mchy.virtual.vir_dirs import VirFSNode, VirFolder, VirRawFile
from mchy.virtual.vir_dp import VirDP
import os


def include_file(vir_dp: VirDP, inclusion: FileInclusion, config: Config):
    resource_path = os.path.abspath(config.inclusion_path + os.path.sep + os.path.join(*inclusion.resource_path.split("/")))
    if not os.path.exists(resource_path):
        raise ConversionError(f"The included resource targeting `{'/'.join(inclusion.output_path)}` cannot be found at {resource_path}").with_loc(inclusion.loc)

    target_folder = vir_dp.top_data_fld
    for tar_name in inclusion.output_path:
        for child in target_folder.children:
            if child.fs_name == tar_name:
                if not isinstance(child, VirFolder):
                    raise ConversionError(f"Included target `{tar_name}` appears to be a file, directory/folder expected?").with_loc(inclusion.loc)
                target_folder = child
                break
        else:
            target_folder = VirFolder(tar_name, target_folder)

    vir_resource = vir_dp_from_fs(resource_path)

    if (existing_child := target_folder.get_child_with_name(vir_resource.fs_name)) is not None:
        raise ConversionError(f"Included resource `{vir_resource.fs_name}` clashes with existing resource at `{existing_child.path}`").with_loc(inclusion.loc)

    target_folder.add_child(vir_resource)


def vir_dp_from_fs(path: str) -> VirFSNode:
    fs_name = os.path.basename(path)
    if os.path.isdir(path):
        return VirFolder(fs_name, initial_children=[vir_dp_from_fs(os.path.join(path, child)) for child in os.listdir(path)])
    else:
        with open(path, "r") as f:
            return VirRawFile(fs_name, initial_contents=f.read())
