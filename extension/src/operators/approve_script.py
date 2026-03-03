import bpy

from ..utils import get_rig, hash_string


class THOMAS_RIG_ASSETS_APPROVE_SCRIPT_OT_SET(bpy.types.Operator):
    """
    Description:
        Approves the script and stores the text hash to the APPROVED_SCRIPTS set.
        Uses the script of the referenced rig (rig selector)
    """
    bl_idname = "thomasriglegacy.approve_script"
    bl_label = "approve script"
    bl_description = ""

    def execute(self, context):
        rig = get_rig()
        source = rig.pose.bones["Misc_Properties"]['UI_Script']
        source_string = source.as_string()
        hash = hash_string(source_string)
        
        from ... import APPROVED_SCRIPTS
        APPROVED_SCRIPTS.add(hash)

        return{'FINISHED'}