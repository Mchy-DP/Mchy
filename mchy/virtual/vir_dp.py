
import shutil
import sys
from mchy.common.com_cmd import ComCmd
from mchy.common.config import Config
from mchy.stmnt.struct.linker import SmtLinker
from mchy.virtual.helpers import json_dump
from mchy.virtual.to_disk import to_disk
from mchy.virtual.vir_dirs import VirFolder, VirMCHYFile, VirNSFolder, VirRawFile
from os import path as os_path
import os


def _make_archive(source, destination):
    # Taken From: https://stackoverflow.com/questions/32640053 -- Make42
    base_name = '.'.join(destination.split('.')[:-1])
    format = destination.split('.')[-1]
    root_dir = os_path.dirname(source)
    base_dir = os_path.basename(source.strip(os_path.sep))
    shutil.make_archive(base_name, format, root_dir, base_dir)


class VirDP:

    def __init__(self, config: Config):
        self._config: Config = config
        self._linker: SmtLinker = SmtLinker(config.project_namespace, config.recursion_limit)

        # Virtual structure
        self._dp_superroot = VirFolder("datapacks")
        self._root = VirFolder(config.project_name, self._dp_superroot)
        self._mcmeta = VirRawFile("pack.mcmeta", self._root, self._get_pack_dot_mcmeta())
        self._generated_proof_file = VirRawFile("generated.txt", self._root, "Datapack generated by the MCHY datapack generator (https://github.com/jacobbox/mchy)")
        fs_fld_data = VirFolder("data", self._root)
        fs_fld_functags = VirFolder("functions", VirFolder("tags", VirFolder("minecraft", fs_fld_data)))
        VirRawFile("load.json", fs_fld_functags, json_dump({"values": [f"{config.project_namespace}:generated/internal_root/load_master"]}))
        VirRawFile("tick.json", fs_fld_functags, json_dump({"values": [f"{config.project_namespace}:generated/internal_root/tick_master"]}))
        self._prj_ns = VirFolder(config.project_namespace, fs_fld_data)
        self._generated = VirNSFolder(f"{config.project_namespace}:generated", "generated", VirFolder("functions", self._prj_ns))
        fs_fld_internal_func_root = VirFolder("internal_root", self._generated)
        fs_fld_imported_func_root = VirFolder("imported_root", self._generated)
        self._public_funcs = VirFolder("public", self._generated)
        self._import_param_default_init = VirMCHYFile("default_param_init.mcfunction", fs_fld_imported_func_root)
        self._load_master = VirMCHYFile("load_master.mcfunction", fs_fld_internal_func_root)
        self._tick_master = VirMCHYFile("tick_master.mcfunction", fs_fld_internal_func_root)
        self._mchy_func = VirFolder("mchy_func", fs_fld_internal_func_root)
        fs_fld_extra = VirFolder("extra", fs_fld_internal_func_root)
        self._extra_compiler_util = VirFolder("compiler_util", fs_fld_extra)
        fs_fld_extra_frags = VirFolder("frags", fs_fld_extra)
        self._extra_frags_init = VirFolder("init_master_load", fs_fld_extra_frags)
        self._extra_frags_tick = VirFolder("tick_master_load", fs_fld_extra_frags)
        self._extra_frags_setup = VirFolder("setup", fs_fld_extra_frags)
        self._extra_frags_import_ns = VirFolder("import_ns", fs_fld_extra_frags)
        self._extra_frags_public = VirFolder("public", fs_fld_extra_frags)

    def _get_pack_format(self) -> int:
        return 12  # TODO: update to reflect config target version

    def _get_pack_dot_mcmeta(self) -> str:
        return json_dump(
            {"pack": {"pack_format": self._get_pack_format(), "description": f"{self._config.project_name} - generated by MCHY"}}
        )

    @property
    def extra_frags_init(self) -> VirFolder:
        return self._extra_frags_init

    @property
    def generated_root(self) -> VirNSFolder:
        return self._generated

    @property
    def extra_frags_tick(self) -> VirFolder:
        return self._extra_frags_tick

    @property
    def extra_frags_setup(self) -> VirFolder:
        return self._extra_frags_setup

    @property
    def extra_frags_import_ns(self) -> VirFolder:
        return self._extra_frags_import_ns

    @property
    def extra_frags_public_fld(self) -> VirFolder:
        return self._extra_frags_public

    @property
    def public_funcs_accessor_fld(self) -> VirFolder:
        return self._public_funcs

    @property
    def mchy_func_fld(self) -> VirFolder:
        return self._mchy_func

    @property
    def load_master_file(self) -> VirMCHYFile:
        return self._load_master

    @property
    def tick_master_file(self) -> VirMCHYFile:
        return self._tick_master

    @property
    def import_param_default_file(self) -> VirMCHYFile:
        return self._import_param_default_init

    @property
    def compiler_util_fld(self) -> VirFolder:
        return self._extra_compiler_util

    @property
    def linker(self) -> SmtLinker:
        return self._linker

    def write_to_disk(self):
        prj_path = os_path.join(self._config.output_path, self._config.project_name)
        if os_path.exists(prj_path):
            self._config.logger.very_verbose("DISK: Output path already exists, checking if we can overwrite")
            # check file is what we think it is:
            if os_path.exists(os_path.join(prj_path, "pack.mcmeta")) and os_path.exists(os_path.join(prj_path, "generated.txt")):  # Is a datapack that we generated
                if self._config.do_backup:
                    self._config.logger.very_verbose("DISK: We made this, backing up old datapack")
                    _make_archive(prj_path, prj_path+".zip")
                    self._config.logger.very_verbose("DISK: Backed up existing datapack")
                else:
                    self._config.logger.very_verbose("DISK: We made this, skipping backup due to config")
                shutil.rmtree(prj_path)
                self._config.logger.very_verbose("DISK: Deleted old datapack")
            else:
                self._config.logger.error(
                    f"File-Exists: Attempted to write to output file '{prj_path}' however it already exists and was missing generated markers that would imply " +
                    f"it can safely be overwritten.  Program stopping to prevent damage, please delete/move output folder and try again"
                )
                sys.exit(1)
        self._config.logger.very_verbose("DISK: Writing files to disk")
        to_disk(self._root, prj_path)
        self._config.logger.very_verbose("DISK: Done!")
