import bpy
import shutil
from .. import constants
from ..icons import IconReader

class THOMAS_RIG_CLEAR_IMPORTED_TEXTURES(bpy.types.Operator):
    bl_idname = "thomasriglegacy.clearimportedtextures"
    bl_label = ""
    bl_description = "Clears the importted textures."

    def execute(self, context):
        path = bpy.utils.extension_path_user(
            package=constants.PACKAGE,
            path="textures"
        )
        shutil.rmtree(path)

        from .. import utils
        preferences = utils.get_extension_preferences()

        preferences.mc_textures_ignore = True
        preferences.mc_textures_loaded = False
        preferences.previous_version = (0, 0, 0)

        IconReader.reload_icons()
        
        self.report({"INFO"}, "Textures cleared successfully")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.alert = True
        layout.label(text="Do you really want to remove the imported textures?", icon = "WARNING_LARGE")