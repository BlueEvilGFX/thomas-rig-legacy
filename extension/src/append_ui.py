import bpy
import os

from . import icons
from . import constants

def menu_func(self, context):
    layout = self.layout
    pcoll = icons.thomas_icons["thomas_legacy"]
    custom_icon = pcoll["Thomas Rig Legacy"].icon_id

    preferences = context.preferences.addons[constants.PACKAGE].preferences 
    loaded = preferences.mc_textures_loaded

    layout.operator("view3d.thomasriglegacyappend", icon_value = custom_icon)
    armor_op = layout.operator("thomasriglegacy.addarmor", text = "Add Minecraft Armor", icon = "MATCLOTH")
    armor_op.parent = False
    # armor_op.helmet = True
    # armor_op.chestplate = True
    # armor_op.leggings = True
    # armor_op.boots = True
    armor_op.loaded = loaded

class OBJECT_MT_APPEND(bpy.types.Operator):
    bl_idname = "view3d.thomasriglegacyappend"
    bl_label = "Thomas Rig Legacy"

    def execute(self, context):
        preferences = context.preferences.addons[constants.PACKAGE].preferences 

        blendfile = os.path.join(constants.RIGS_PATH, "Thomas Rig Legacy.blend")
        section = "Collection"
        obj = "Rig [only append this]"
        filepath  = os.path.join(blendfile,section,obj)
        directory = os.path.join(blendfile,section)
        filename  = obj
        bpy.ops.wm.append(filepath=filepath,filename=filename,directory=directory,link=False,active_collection=False)

        # move 2nd Layer Head to alternative position
        alternative = preferences.second_layer_alternative_placement
        if alternative:
            for obj in context.selected_objects:
                if "2_Layer_Extrusion" in obj.name:
                    obj.location[2] = constants.SECOND_LAYER_ALTERNATIVE_HEAD_POSITION_Z

        # select the rig
        rig = [obj for obj in context.selected_objects if obj.type == 'ARMATURE'][0]
        if rig:
            bpy.ops.object.select_all(action='DESELECT')
            context.view_layer.objects.active = rig

            # move to cursor location
            bpy.ops.object.mode_set(mode = 'POSE')
            cursor_position = bpy.context.scene.cursor.location
            rig.pose.bones['Root'].matrix.translation = cursor_position
            rig.pose.bones['Root'].scale = (1, 1, 1)

        # set default size
        default_size = preferences.default_player_rig_scale # False: Minecraft, True: Original -> show constraint
        rig.pose.bones["Root"].constraints["pre-scale"].enabled = default_size
        return{'FINISHED'}


#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                   (un)register
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def register():
    bpy.utils.register_class(OBJECT_MT_APPEND)
    bpy.types.VIEW3D_MT_add.append(menu_func)

def unregister():
    bpy.types.VIEW3D_MT_add.remove(menu_func)
    bpy.utils.unregister_class(OBJECT_MT_APPEND)