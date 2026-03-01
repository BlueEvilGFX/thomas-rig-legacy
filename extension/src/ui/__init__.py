import bpy
import textwrap

from .. import utils
from ..constants import PACKAGE, RIG_ID, INFO_TEXT
from ..operators import rig_update
from . import design_settings, material_settings, posing_settings


class THOMASRIGLEGACY_OT_PANEL(bpy.types.Panel):
    bl_label = "Thomas Rig Legacy"
    bl_idname = "SCENE_PT_THOMAS_RIG_LEGACY"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Thomas Rig Legacy"

    @classmethod
    def poll(cls, context):
        rig = utils.get_rig()
        preferences = context.preferences.addons[PACKAGE].preferences 
        loaded = preferences.mc_textures_loaded
        ignore = preferences.mc_textures_ignore

        if not loaded and not ignore:
            return True

        if not rig or not rig.get("Rig_ID") == RIG_ID:
            return False
        
        return True

    def draw(self, context):
        from .. import icons
        pcoll = icons.thomas_icons["thomas_legacy"]
        preferences = context.preferences.addons[PACKAGE].preferences 
        loaded = preferences.mc_textures_loaded
        ignore = preferences.mc_textures_ignore

        # check if textures loaded / skipped
        if not loaded and not ignore:
            icon = pcoll["Thomas Rig Legacy"].icon_id
            layout = self.layout
            box = layout.box()

            split = box.split(factor=0.8)
            split.scale_y = 1.5
            split.alert = True
            split.operator("thomasriglegacy.mc_textures_import", icon_value = icon)
            split.alert = False
            split.operator("thomasriglegacy.mc_textures_skip")

            # info text
            # Get the 3D View area
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    break
            # Calculate the width of the panel
            for region in area.regions:
                if region.type == 'UI':
                    panel_width = region.width
                    break

            # Calculate the maximum width of the label
            uifontscale = 9 * context.preferences.view.ui_scale
            max_label_width = max(1, int(panel_width // uifontscale))

            # Split the text into lines and format each line
            box = layout.box()
            col = box.column()
            for line in INFO_TEXT.splitlines():
                # Remove leading and trailing whitespace
                line = line.strip()

                # Split the line into chunks that fit within the maximum label width
                for chunk in textwrap.wrap(line, width=max_label_width):
                    col.label(text=chunk)
            return
        
        # normal UI
        icon = pcoll["automatic"].icon_id
        row = self.layout.row(align=True)
        row.prop(context.scene.thomas_rig_legacy, 'reference', text = "")
        row.prop(context.scene.thomas_rig_legacy, 'reference_toggle', toggle=True, text="", icon_value = icon)

        rig = utils.get_rig()
        if not rig:
            return
        if not rig.get("Rig_ID") == RIG_ID:
            self.layout.label(text="Thomas Rig Legacy is not selected")
            return

        # ------------

        # UPDATE rig
        if rig_update.THOMAS_RIG_UPDATE_RIG.poll(context):
            utils.UI_Utils.spacer(self.layout, 1)
            layout_update = self.layout.column()
            box = layout_update.box()
            box.alert = True
            box.scale_y = 1.5
            box.operator("thomasriglegacy.update_rig", icon = "ERROR")
            row = self.layout.row()
            row.alignment = 'CENTER'
            row.label(text="oudated rig version, please update.")

            response = rig_update.THOMAS_RIG_UPDATE_RIG.manual_update_poll()
            if isinstance(response, tuple):
                for text in response:
                    row = self.layout.row()
                    row.alignment = 'CENTER'
                    row.label(text=text)

            # NO UPDATE IMPLEMENTED
            layout_update.enabled = isinstance(response, bool)

            utils.UI_Utils.spacer(self.layout, 1)

        # ------------

        layout = self.layout

        main_props  = rig.pose.bones["Main_Properties"]
        misc_props  = rig.pose.bones["Misc_Properties"]

        r_arm_props = rig.pose.bones["R.Arm_Properties"]
        l_arm_props = rig.pose.bones["L.Arm_Properties"]
        r_leg_props = rig.pose.bones["R.Leg_Properties"]
        l_leg_props = rig.pose.bones["L.Leg_Properties"]
        pupil_props = rig.pose.bones["Pupils_controller"]


        # search function
        layout.prop(misc_props, '["search"]')
        if misc_props["search"] != "":
            column = layout.box().column()
            utils.UI_Utils.check_search(column, main_props)
            utils.UI_Utils.check_search(column, r_arm_props, True)
            utils.UI_Utils.check_search(column, l_arm_props, True)
            utils.UI_Utils.check_search(column, r_leg_props)
            utils.UI_Utils.check_search(column, l_leg_props)
            utils.UI_Utils.check_search(column, pupil_props)
            return
        
        # AntiLag
        row = layout.row()
        row.prop(main_props, '["AntiLag"]', toggle = True)
        render = context.scene.render
        row = row.row(align=True)
        row.prop(render, "use_simplify", toggle = True, text = "simplify")
        row = row.row(align = True)
        row.enabled = render.use_simplify
        row.prop(render, "simplify_subdivision", text="")

        # normal UI
        header = layout.row(align=True)
        header.scale_y = 1.2
        header.prop(rig, "ui_tab", expand = True)
        tab = rig.ui_tab

        if tab == "DESIGN":
            design_settings.draw(main_props, misc_props, layout, context, rig)
        elif tab == "MATERIALS":
            material_settings.draw(rig, layout, main_props)
        else:
            posing_settings.draw(layout, rig, main_props)

        # rig /addon version number
        row = layout.row()
        row.enabled = False
        row.alignment = 'RIGHT'

        rig_version = rig.get("rig_version", "unknown")
        if rig_version != "unknown": 
            rig_version = f'v{".".join(map(str, rig_version))}'

        ext_version = 'v' + '.'.join(map(str, utils.get_ext_version()))

        if rig_version == ext_version:
            text = rig_version
        else:
            text = f'{rig_version} | {ext_version}'
        row.label(text = text)



def register():
    bpy.utils.register_class(THOMASRIGLEGACY_OT_PANEL)
  
def unregister():
    bpy.utils.unregister_class(THOMASRIGLEGACY_OT_PANEL)