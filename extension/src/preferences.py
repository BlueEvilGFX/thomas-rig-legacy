import bpy
from bpy.props import BoolProperty, IntVectorProperty
import textwrap

from . import icons
from .constants import INFO_TEXT_PREFERENCES,INFO_TEXT_PREFERENCES_IMPORT, PACKAGE
from . import utils

class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = PACKAGE

    mc_textures_loaded : BoolProperty(default=False) #type: ignore
    mc_textures_ignore : BoolProperty(default=False) #type: ignore
    previous_version : IntVectorProperty(default=(0, 0, 0), size=3) #type: ignore

    def draw(self, context):
        pcoll = icons.thomas_icons["thomas_legacy"]

        layout = self.layout
        col = layout.column()
        if not self.mc_textures_loaded:
            row = col.row()
            row.label(text="Textures not loaded", icon = "CANCEL")
            row.label(text="Using fallback textures", icon = "ERROR")
        
        alert = (self.mc_textures_loaded == False and self.mc_textures_ignore == False)

        icon = pcoll["Thomas Rig Legacy"].icon_id
        if alert:
            split = col.split(factor=0.8)
            split.alert = True
            split.operator("thomasriglegacy.mc_textures_import", text = "(re)load MC textures", icon_value = icon)
            split.alert = False
            split.operator("thomasriglegacy.mc_textures_skip")

            split = col.split(factor=0.8)
            split.alert = True
            split.operator("thomasriglegacy.mc_textures_import_manually", text = "import textures", icon = "IMPORT")
            split.alert = False
            split.operator("thomasriglegacy.mc_textures_skip")
        
        else:
            row = col.row()
            row.operator("thomasriglegacy.mc_textures_import", text = "(re)load MC textures", icon_value = icon)
            row.operator("thomasriglegacy.mc_textures_import_manually", text = "import textures", icon = "IMPORT")

        # info text
        # Get the 3D View area
        for area in context.screen.areas:
            if area.type == 'PREFERENCES':
                break
        # Calculate the width of the panel
        for region in area.regions:
            if region.type == 'WINDOW':
                panel_width = region.width
                break

        # Calculate the maximum width of the label
        uifontscale = 9 * context.preferences.view.ui_scale
        max_label_width = int(panel_width // uifontscale) / 2 + 8

        # Split the text into lines and format each line
        row = layout.row()
        for text in [INFO_TEXT_PREFERENCES, INFO_TEXT_PREFERENCES_IMPORT]:
            col = row.column()
            for line in text.splitlines():
                # Remove leading and trailing whitespace
                line = line.strip()

                # Split the line into chunks that fit within the maximum label width
                for chunk in textwrap.wrap(line, width=max_label_width):
                    col.label(text=chunk)

def register():
    bpy.utils.register_class(AddonPreferences)

    preferences = bpy.context.preferences.addons[PACKAGE].preferences
    previous_version = tuple(preferences.previous_version)
    ext_version = utils.get_ext_version()

    if previous_version != ext_version:
        preferences.mc_textures_ignore = False
        preferences.mc_textures_loaded = False
        preferences.previous_version = ext_version

  
def unregister():
    bpy.utils.unregister_class(AddonPreferences)