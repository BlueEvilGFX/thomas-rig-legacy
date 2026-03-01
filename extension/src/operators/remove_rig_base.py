import bpy

from ..utils import get_rig


class ThomasRigLegacyRemoveRigBase(bpy.types.Operator):
    bl_options = {'REGISTER', 'UNDO'}
    append_type:str = ""
    bone_names:list = []

    @classmethod
    def poll(cls, context):
        try:            
            misc = get_rig().pose.bones["Misc_Properties"]
            return (misc[cls.append_type] is not None)
        except (AttributeError, KeyError, TypeError):
            return False
    
    def execute(self, context):
        thomas_rig = get_rig()
        context.view_layer.objects.active = thomas_rig

        # remove objects and material
        collection = thomas_rig.pose.bones["Misc_Properties"][self.append_type]
        for obj in collection.objects:
            if obj.type == 'MESH' and obj.material_slots:
                material = obj.material_slots[0].material
                if material:
                    break

        image = material.node_tree.nodes['Image Texture'].image
        bpy.data.images.remove(image)
        bpy.data.materials.remove(material)
        bpy.data.collections.remove(collection)

        # removing bones
        bpy.ops.object.mode_set (mode='EDIT', toggle=False)
        edit_bones = thomas_rig.data.edit_bones
        bones = [edit_bones[bone] for bone in self.bone_names if bone in edit_bones]
        for bone in bones:
            edit_bones.remove(bone)
        bpy.ops.object.mode_set (mode='POSE', toggle=False)
        
        # unregister append_type 
        thomas_rig.pose.bones["Misc_Properties"][self.append_type] = None
        return {'FINISHED'}

    def get_bone_names(self):
        return []


class THOMAS_RIG_LEGACY_REMOVE_CAPE(ThomasRigLegacyRemoveRigBase):
    bl_idname = "thomasriglegacy.removecape"
    bl_label = "remove cape"
    append_type = "cape"
    bone_names = ["Cape_Main", "Cape_Bendy", "Cape_Controller"]


class THOMAS_RIG_LEGACY_REMOVE_ELYTRA(ThomasRigLegacyRemoveRigBase):
    bl_idname = "thomasriglegacy.removeelytra"
    bl_label = "remove elytra"
    append_type = "elytra"
    bone_names = [
        "Elytra_Main",
        "Elytra_1.R", "Elytra_2.R", "Elytra_3.R", "Elytra_4.R",
        "Elytra_5.R", "Elytra_6.R", "Elytra_7.R",
        "Elytra_1.L", "Elytra_2.L", "Elytra_3.L", "Elytra_4.L",
        "Elytra_5.L", "Elytra_6.L", "Elytra_7.L"
    ]