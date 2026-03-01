import bpy
from bpy.props import IntProperty

from ..utils import get_rig


class THOMAS_RIG_ASSETS_ARMOR_TAB_OT_SET(bpy.types.Operator):
    """
    description:
        operator which changes the assets_tab int -> mimic enum property
    args:
        asset_type : armor | cape | elytra
    """
    bl_idname = "thomasriglegacy.change_armor_tab"
    bl_label = "change setting tab to $()"
    bl_description = ""

    tab : IntProperty() # type: ignore

    def execute(self, context):
        rig = get_rig()
        rig.pose.bones["Main_Properties"]["Assets_Tab"] = self.tab
        return{'FINISHED'}