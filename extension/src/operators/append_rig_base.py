import bpy
import os

from ..utils import get_rig
from .. import constants


class ThomasRigLegacyAppendRigBase(bpy.types.Operator):
    bl_options = {'REGISTER', 'UNDO'}
    append_type:str = ""

    @classmethod
    def poll(cls, context):
        try:
            misc = get_rig().pose.bones["Misc_Properties"]
            return (misc[cls.append_type] is None)
        except (AttributeError, KeyError, TypeError):
            return False
    
    def execute(self, context):
        thomas_rig = get_rig()
        context.view_layer.objects.active = thomas_rig

        # appending
        file = os.path.join(constants.ARMOR_PATH, f"{self.append_type}.blend")
        directory = os.path.join(file, "Collection")
        filepath = os.path.join(directory, self.append_type.capitalize())

        bpy.ops.wm.append(
            filepath=filepath,
            filename=self.append_type.capitalize(),
            directory=directory,
            link=False,
            active_collection=True)
        
        # merging
        appended_items = bpy.context.selected_objects[0].children
        object = appended_items[0]

        thomas_rig.select_set(True)            
        bpy.ops.object.join()
        bpy.ops.object.select_all (action='DESELECT')

        # add correct armature target for append_type
        if self.append_type == 'cape':
            lattice = appended_items[1]
            lattice.modifiers[0].object = thomas_rig
        else: # elytra
            object.modifiers[0].object = thomas_rig
            # load texture IF Mc textures 
            preferences = context.preferences.addons[constants.PACKAGE].preferences 
            if preferences.mc_textures_loaded:
                res_path = bpy.utils.extension_path_user(package = constants.PACKAGE, path = "textures")
                material = object.material_slots[0].material
                nodes = material.node_tree.nodes
                texture = os.path.join(res_path, 'elytra.png')
                image = bpy.data.images.load(texture)
                nodes['Image Texture'].image = image

        # parenting append_type bone
        bpy.ops.object.mode_set (mode='EDIT', toggle=False)
        thomas_rig.data.edit_bones[f'{self.append_type.capitalize()}_Main'].parent = thomas_rig.data.edit_bones['Upper_Body']
        bpy.ops.object.mode_set (mode='POSE', toggle=False)

        # register append_type to rig
        thomas_rig.pose.bones["Misc_Properties"][self.append_type] = object.users_collection[0]
        return {'FINISHED'}
    

class THOMAS_RIG_LEGACY_APPEND_CAPE(ThomasRigLegacyAppendRigBase):
    bl_idname = "thomasriglegacy.appendcape"
    bl_label = "append cape"
    append_type = "cape"


class THOMAS_RIG_LEGACY_APPEND_ELYTRA(ThomasRigLegacyAppendRigBase):
    bl_idname = "thomasriglegacy.appendelytra"
    bl_label = "append elytra"
    append_type = "elytra"