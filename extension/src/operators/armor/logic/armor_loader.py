import bpy
import os

from .armor_enums import TrimEnum, MaterialEnum, ArmorPartEnum, ArmorTypeEnum
from .... import utils
from .... import constants



class ArmorLoader:
    def __init__(self, op):
        self.op = op
        self.rig = op.rig
        self.parent = op.parent

    def load_default(self, armor_part: ArmorPartEnum) -> bpy.types.Object:
        armor_dir = constants.ARMOR_PATH 
        default_armor_file = os.path.join(armor_dir, "armor_default.blend")

        # Append armor part
        directory = os.path.join(default_armor_file, "Object")
        filepath = os.path.join(directory, armor_part.value)
        bpy.ops.wm.append(
            filepath=filepath,
            filename=armor_part.value,
            directory=directory,
            link=False,
            active_collection=True
        )
        if self.parent:
            bpy.ops.object.mode_set(mode = "OBJECT")
        armor_object = bpy.context.selected_objects[0]
        armor_object.location.x = 0
        armor_object.location.y = 0
        # armor_object.location.z = 0

        return armor_object        
    
    def load_custom(self, armor_part: ArmorPartEnum, armor_type: str) -> list[bpy.types.Object]:
        armor_file = os.path.join(constants.ARMOR_PATH, f"{armor_type}.blend")

        # Append
        directory = os.path.join(armor_file, "Collection")
        filepath = os.path.join(directory, armor_part.value)
        bpy.ops.wm.append(
            filepath=filepath,
            filename=armor_part.value,
            directory=directory,
            link=False,
            active_collection=True
        )
        if not self.parent:
            return
        
        bpy.ops.object.mode_set(mode = "OBJECT")
        return bpy.context.selected_objects
