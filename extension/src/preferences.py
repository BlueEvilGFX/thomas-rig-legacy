import bpy
from bpy.props import BoolProperty, IntVectorProperty, StringProperty
import textwrap

from . import icons
from .constants import INFO_TEXT_PREFERENCES,INFO_TEXT_PREFERENCES_IMPORT, PACKAGE
from . import utils

class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = PACKAGE
    
    # -------------------- INTERNAL --------------------
    mc_textures_ignore : BoolProperty(default=False) #type: ignore
    mc_textures_loaded : BoolProperty(default=False) #type: ignore
    previous_version : IntVectorProperty(default=(0, 0, 0), size=3) #type: ignore

    # -------------------- SETTINGS --------------------
    second_layer_alternative_placement : BoolProperty(
        default=False,
        description="If turned on, the head will spawn above the head and not on the head."
    ) #type: ignore

    show_pose_mode: BoolProperty(
        default=True,
        description="If active the rest pose toggle will be displayed in the rig UI."
    ) #type: ignore

    default_player_rig_scale: BoolProperty(default=False) #type: ignore

    verbose: BoolProperty(
        default=False,
        description="Printing debugging information to the terminal for operators."
    ) #type: ignore

    loaded_version: StringProperty() # type: ignore


    def draw(self, context):
        pcoll = icons.thomas_icons["thomas_legacy"]
        layout = self.layout

        # box for general settings
        box = layout.box()
        box.label(text="Rig & Extension Settings")
        col = box.column()
        col.prop(
            self, "second_layer_alternative_placement",
            text = "2nd Layer Head Offset",
            toggle=-1
        )

        col.prop(
            self, "show_pose_mode",
            text="Toggle rest pose setting in UI"
        )
        
        row_scale = box.row(align=True)
        scale_toggles = row_scale.row(align=True)
        scale_toggles.prop(self, "default_player_rig_scale", text="Minecraft Scale", toggle=True)
        scale_toggles.prop(self, "default_player_rig_scale", text="Original Scale", toggle=True, invert_checkbox=True)
        scale_toggles.label(text="Player Rig Scale", icon="BLANK1")

        col.prop(
            self, "verbose",
            text="Verbose Operator Settings"
        )

        # -----------------------
        # box for texture loading
        box = layout.box()
        box.label(text="Texture Management")
        col = box.column()

        box.operator

        # import operator with progress bar
        row = col.row(align=True)
        progress = context.scene.thomas_rig_legacy.progress_bar
        if progress == 0:
            row.operator("thomasriglegacy.mc_textures_import_manually", text = "import textures", icon = "IMPORT")
        else:
            row.progress( text="Loading Files", factor=progress, type='BAR')

        split = row.row(align=True)
        split.enabled = self.mc_textures_loaded
        split.operator("thomasriglegacy.clearimportedtextures", text="", icon="TRASH")

        if self.mc_textures_loaded:
            col.label(text=f"Active Textures: Minecraft {self.loaded_version}", icon="CHECKBOX_HLT")
        else:
            col.label(text="No Active Textures", icon="PANEL_CLOSE")

        col.separator()

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
        row = col.row()
        for text in [INFO_TEXT_PREFERENCES, INFO_TEXT_PREFERENCES_IMPORT]:
            box = row.box()
            col = box.column()
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
        preferences.mc_textures_loaded = False
        preferences.previous_version = ext_version


def unregister():
    bpy.utils.unregister_class(AddonPreferences)