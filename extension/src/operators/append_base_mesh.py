import bpy
import os
from bpy.props import IntProperty

from .. import utils
from .. import constants
from .armor.logic.armor_modifiers import ArmorModifierSetup, ArmorPartEnum

class THOMAS_RIG_LEGACY_APPEND_BASE_MESH(bpy.types.Operator):
    """
    Appends the base mesh to the rig. 3x3, Alex or Steve Arms are determined
    automatically
    """
    bl_options = {'REGISTER', 'UNDO'}
    bl_idname = "thomasriglegacy.appendbasemesh"
    bl_label = "append base mesh"

    layer: IntProperty() # type: ignore


    def execute(self, context):
        self.rig = rig = utils.get_rig()

        main_propteries = rig.pose.bones["Main_Properties"]
        
        # encoding for arm type
        ARM_STEVE = "Arms_Steve"
        ARM_SLIM = "Arms_Alex"
        ARM_3X3 = "Arms_3x3"

        arm_slim = main_propteries["Slim main"]
        arm_3x3 = main_propteries["3x3"]
        arm_type = ARM_STEVE if arm_slim is False\
            else ARM_SLIM if arm_3x3 is False\
            else ARM_3X3
        
        context.view_layer.objects.active = rig

        # save the mode state
        try:
            mode = context.object.mode
        except:
            mode = False
        bpy.ops.object.mode_set(mode = "OBJECT")

        # appending
        blend_file = os.path.join(constants.RIGS_PATH, "Mesh_Layers.blend")

        # base 
        bpy.ops.wm.append(
            filepath=os.path.join(blend_file, "Collection", "Base"),
            directory=os.path.join(blend_file, "Collection"),
            filename="Base",
            link=False,
            active_collection=True
        )
        base_meshes = bpy.context.selected_objects

        # arms
        bpy.ops.wm.append(
            filepath=os.path.join(blend_file, "Collection", arm_type),
            directory=os.path.join(blend_file, "Collection"),
            filename=arm_type,
            link=False,
            active_collection=True
        )
        arm_meshes = bpy.context.selected_objects

        all_meshes = set(base_meshes) | set(arm_meshes)

        # parenting
        self.rig.data.pose_position = 'REST'
        mat_obj = utils.get_mat_object(self.rig)
        for mesh in all_meshes:
            modifiers = ArmorModifierSetup(rig, parent=True)

            if "Head" in mesh.name:
                modifiers.apply_default_modifiers(mesh, ArmorPartEnum.HELMET, solidify=False)
            elif "Chest_Layer" in mesh.name:
                modifiers.apply_default_modifiers(
                    mesh, ArmorPartEnum.CHESTPLATE, solidify=False, chest_offset=False,
                    right=False, left=False, chestplate=True
                )
            elif "Arm" in mesh.name: 
                # taper lattice
                name = "Taper_Arm.R" if ".R" in mesh.name else "Taper_Arm.L"
                lattice = mat_obj.modifiers[name].object
                mesh.modifiers.new(name = name, type = "LATTICE")
                mesh.modifiers[name].object = lattice

                modifiers.apply_default_modifiers(
                    mesh, ArmorPartEnum.CHESTPLATE, solidify=False, chest_offset=False,
                    right=".R" in mesh.name, left=".L" in mesh.name, chestplate=False
                )

            elif "Leg" in mesh.name:
                modifiers.apply_default_modifiers(
                    mesh, ArmorPartEnum.LEGGINGS, solidify=False, chest_offset=False,
                    right=".R" in mesh.name, left=".L" in mesh.name, chestplate=False
                )

        # auto smooth & set material
        for obj in bpy.context.view_layer.objects: 
            obj.select_set(False)

        for obj in all_meshes: 
            obj.select_set(True)
            material = mat_obj.material_slots[3].material
            obj.data.materials.append(material)
            if self.layer == 2:
                obj.data.uv_layers["2nd_Layer"].active_render = True

        bpy.ops.object.shade_auto_smooth()

        self.rig.data.pose_position = 'POSE'

        # reset the mode state
        bpy.ops.object.select_all (action='DESELECT')
        if mode:
            context.view_layer.objects.active = self.rig
            bpy.ops.object.mode_set(mode=mode, toggle=False)
        
        return {'FINISHED'}