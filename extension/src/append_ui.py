import bpy
import os

from .icons import Icons
from . import constants
from . import utils

def menu_func(self, context):
    layout = self.layout
    custom_icon = Icons.Thomas_Rig_Legacy

    preferences = utils.get_extension_preferences()
    loaded = preferences.mc_textures_loaded

    layout.operator("view3d.thomasriglegacyappend", icon_value = custom_icon)
    armor_op = layout.operator(
        "thomasriglegacy.addarmor",
        text = "Add Minecraft Armor",
        icon = "MATCLOTH" if not Icons.iron_chestplate else 'NONE',
        icon_value = Icons.iron_chestplate
    )
    armor_op.parent = False
    armor_op.parent_possibility = False
    # armor_op.helmet = True
    # armor_op.chestplate = True
    # armor_op.leggings = True
    # armor_op.boots = True
    armor_op.loaded = loaded

class OBJECT_MT_APPEND(bpy.types.Operator):
    bl_idname = "view3d.thomasriglegacyappend"
    bl_label = "Thomas Rig Legacy"

    def execute(self, context):
        existing_collections = set(bpy.data.collections.keys())
        preferences = utils.get_extension_preferences()

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

        # rename appended collection
        # delete top level appended collection
        new_collections = [col for col in bpy.data.collections.keys() if col not in existing_collections]
        
        if new_collections:
            active_col = context.collection
            new_cols = [bpy.data.collections.get(name) for name in new_collections if bpy.data.collections.get(name)]
            
            root_to_remove = None
            
            # find true top level collection, rename and safe
            for collection in new_cols:
                if collection.name.startswith("Rig [only append this]"):
                    collection.name = "Thomas Rig Legacy"
                    
                    # link collection
                    if collection.name not in active_col.children.keys():
                        try:
                            active_col.children.link(collection)
                        except Exception:
                            pass # if already on first layer
                            
                # unwanted embracing appended collection
                elif collection.name.startswith("Appended"):
                    root_to_remove = collection

            if root_to_remove:
                # save content
                for obj in root_to_remove.objects:
                    if obj.name not in active_col.objects.keys():
                        active_col.objects.link(obj)
                
                # delete collection enclosure
                bpy.data.collections.remove(root_to_remove)

        return {'FINISHED'}



#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                   (un)register
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def register():
    bpy.utils.register_class(OBJECT_MT_APPEND)
    bpy.types.VIEW3D_MT_add.append(menu_func)

def unregister():
    bpy.types.VIEW3D_MT_add.remove(menu_func)
    bpy.utils.unregister_class(OBJECT_MT_APPEND)