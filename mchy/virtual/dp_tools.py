

from mchy.common.com_constants import DebugObjectives
from mchy.common.config import Config
from mchy.stmnt.struct.module import SmtModule
from mchy.virtual.vir_dirs import VirFolder, VirRawFile
from mchy.virtual.vir_dp import VirDP


def generate_tools(smt_module: SmtModule, vir_dp: VirDP, config: Config):
    tools_fld = VirFolder("tools", vir_dp.generated_root)

    if config.debug_mode:
        debug_tools_fld = VirFolder("debug", tools_fld)

        # debug tool: print_entity_source
        # | Prints the line the executing entity was created on if known
        VirRawFile("print_entity_source.mcfunction", debug_tools_fld, "\n".join([
            (
                r'''execute if score @s ''' +
                vir_dp.linker.get_debug_obj(DebugObjectives.SUMMON_LINE_COUNT.value) +
                r''' = @s ''' +
                vir_dp.linker.get_debug_obj(DebugObjectives.SUMMON_LINE_COUNT.value) +
                r''' run tellraw @a ["",''' +
                r'''{"text":"The entity `","color":"blue"},''' +
                r'''{"selector":"@s","color":"light_purple"},''' +
                r'''{"text":"` was created on line `","color":"blue"},''' +
                r'''{"score":{"name":"@s","objective":"''' +
                vir_dp.linker.get_debug_obj(DebugObjectives.SUMMON_LINE_COUNT.value) +
                r'''"},"color":"light_purple"},''' +
                r'''{"text":"`","color":"blue"}]'''
            ),
            (
                r'''execute unless score @s ''' +
                vir_dp.linker.get_debug_obj(DebugObjectives.SUMMON_LINE_COUNT.value) +
                r''' = @s ''' +
                vir_dp.linker.get_debug_obj(DebugObjectives.SUMMON_LINE_COUNT.value) +
                r''' run tellraw @a ["",''' +
                r'''{"text":"The entity `","color":"blue"},''' +
                r'''{"selector":"@s","color":"light_purple"},''' +
                r'''{"text":"` was not created by the datapack `","color":"blue"},''' +
                r'''{"text":"''' + config.project_name + r'''","italic":true,"color":"#3636CE"},''' +
                r'''{"text":"`","color":"blue"}]'''
            ),
        ]))

        # debug tool: scan_for_leaked_markers
        # | Looks for marker entities created by this datapacks with no tags and prints
        # | a message indicating the likely source of the leak based on the first such match.
        # |
        # | Markers we made now without no tags implies the user has no way to reference them
        # | and thus they have been leaked.  Only markers are tested as other entities may
        # | have been intentionally leaked such as zombies for combat or armor stands to display items.
        VirRawFile("scan_for_leaked_markers.mcfunction", debug_tools_fld, "\n".join([
            (
                r'''execute as @e[type=minecraft:marker,limit=1,sort=arbitrary,scores={''' +
                vir_dp.linker.get_debug_obj(DebugObjectives.SUMMON_LINE_COUNT.value) +
                r'''=-2147483648..},tag=] run function ''' +
                f"{debug_tools_fld.get_namespace_loc()}/print_entity_source"
            ),
            (
                r'''tellraw @a ["",{"text":"Scan complete!","color":"blue"}]'''
            ),
        ]))
