import bpy 
from .armor_enums import ArmorPartEnum
from .... import utils


class ArmorModifierSetup:
    """
    Handles all modifier logic for armor obbjects:
    - armature modifiers
    - lattice modifiers
    - solidify
    - subdivision
    - taper
    - shape key muting
    - chestplate offsets
    """

    def __init__(self, rig, parent):
        self.rig = rig
        self.parent = parent

    # -------------------------------------------------------------------------
    # PUBLIC ENTRY POINT
    # -------------------------------------------------------------------------
    def apply_default_modifiers(
            self, 
            armor_object, 
            armor_part: ArmorPartEnum, 
            solidify=True, 
            chest_offset=True, 
            right=True, 
            left=True, 
            chestplate=True,
    ):
        """Apply all modifiers for a default armor piece"""
        VERTEX_GROUPS = {
            ArmorPartEnum.CHESTPLATE : ("Lattice.R", "Lattice.L"),
            ArmorPartEnum.LEGGINGS : ("Lattice_Right", "Lattice_Left"),
            ArmorPartEnum.BOOTS : ("Lattice_Right", "Lattice_Left"),
        }

        LATTICE_METHODS = {
            ArmorPartEnum.CHESTPLATE : (
                utils.add_modifier_lattice_arm_pose_R, 
                utils.add_modifier_lattice_arm_pose_L
            ),
            ArmorPartEnum.LEGGINGS : (
                utils.add_modifier_lattice_leg_pose_R,
                utils.add_modifier_lattice_leg_pose_L
            ),
            ArmorPartEnum.BOOTS : (
                utils.add_modifier_lattice_leg_pose_R,
                utils.add_modifier_lattice_leg_pose_L
            ),
        }

        FILTER_PARTS = (
            ArmorPartEnum.CHESTPLATE,
            ArmorPartEnum.LEGGINGS,
            ArmorPartEnum.BOOTS
        )
        
        if armor_part in FILTER_PARTS:
            if self.parent:
                chest_vertex_group = "UpperBodyMain"
                vertex_group_R, vertex_group_L = VERTEX_GROUPS.get(armor_part)
                method_R, method_L = LATTICE_METHODS.get(armor_part)

                if armor_part != ArmorPartEnum.BOOTS and chestplate:
                    # Chest Lattice
                    lattice_main = utils.add_modifier_lattice_chest_pose(
                        self.rig,
                        armor_object
                    )
                    lattice_main.vertex_group = chest_vertex_group

                if right:
                    lattice_R = method_R(self.rig, armor_object)
                    lattice_R.vertex_group = vertex_group_R

                if left:
                    lattice_L = method_L(self.rig, armor_object)
                    lattice_L.vertex_group = vertex_group_L

                if chest_offset:
                    for key in armor_object.data.shape_keys.key_blocks:
                        if "120" in key.name or "Bend" in key.name:
                            key.mute = True

            if armor_part == ArmorPartEnum.CHESTPLATE and chest_offset:
                armor_object.location[1] = 0.004265 # Chestplate offset
                shape_keys = armor_object.data.shape_keys
                shape_keys.key_blocks["chestplate.001"].value = 0

        # Handle helmet
        else:
            if self.parent:
                utils.add_modifier_armature(self.rig, armor_object)
                utils.add_modifier_lattice_smart_deform(self.rig, armor_object)
                utils.add_modifier_lattice_head(self.rig, armor_object)
            if solidify:
                utils.add_modifier_solidify(armor_object, -0.09)

            bpy.context.view_layer.objects.active = armor_object

        # Add taper lattice
        if self.parent:
            self.apply_taper(armor_object, armor_part, right, left, chestplate)
            
        # Add and move subdivisions to top
        bpy.context.view_layer.objects.active = armor_object
        utils.add_modifier_subdivision(armor_object, 0, 3, 'SIMPLE')
        last_index = len(armor_object.modifiers) - 1
        if solidify:
            bpy.ops.object.modifier_move_to_index(modifier="Solidify", index=0)
        bpy.ops.object.modifier_move_to_index(
            modifier="Auto Smooth",
            index=last_index
        )
        bpy.ops.object.modifier_move_to_index(modifier="subdivision", index=last_index)

        # Show solidify
        if solidify:
            solidify = armor_object.modifiers["Solidify"]
            solidify.show_viewport = True
            solidify.show_render = True

        for modifier in armor_object.modifiers:
            modifier.show_expanded = False
    
    def apply_custom_modifiers(self, objs, armor_part: ArmorPartEnum, armor_type: str):
        for idx, obj in enumerate(objs):
            # Add armature modifier
            utils.add_modifier_armature(self.rig, obj)

            # Lattice modifier
            if armor_part == ArmorPartEnum.HELMET:
                # Scuba: no need head lattice for 2nd helmet part but taper
                if armor_type == 'Scuba' and idx == 1:
                    self.apply_taper(obj, armor_part)
                    continue
                
                utils.add_modifier_lattice_smart_deform(self.rig, obj)
                utils.add_modifier_lattice_head(self.rig, obj)

            if (armor_type in {"Cultist", "ZombiePlate"} and armor_part == ArmorPartEnum.HELMET):
                self.rig.pose.bones["Main_Properties"]["No face"] = True

            # add subdivisions
            utils.add_modifier_subdivision(obj, 0, 3, "SIMPLE")
    
    def apply_taper(self, obj, armor_part: ArmorPartEnum, right=True, left=True, chestplate=True):
        # ------------------------------------------------------------
        # Helper: BOOTS + LEGGINGS taper
        # ------------------------------------------------------------
        def apply_leg_taper(obj):
            mat_obj = utils.get_mat_object(self.rig)
            # Right leg
            if right:
                lattice = mat_obj.modifiers["Lattice_R_Leg"].object
                obj.modifiers.new(name = "Taper.R", type = "LATTICE")
                obj.modifiers["Taper.R"].object = lattice
                obj.modifiers["Taper.R"].vertex_group = "Lattice_Right"

            # Left leg
            if left:
                lattice = mat_obj.modifiers["Lattice_L_Leg"].object
                obj.modifiers.new(name = "Taper.L", type = "LATTICE")
                obj.modifiers["Taper.L"].object = lattice
                obj.modifiers["Taper.L"].vertex_group = "Lattice_Left"

            # Move to top
            bpy.context.view_layer.objects.active = obj
            if right:
                bpy.ops.object.modifier_move_to_index(modifier="Taper.R", index=0   )
            if right:
                bpy.ops.object.modifier_move_to_index(modifier="Taper.L", index=1)

            if armor_part == ArmorPartEnum.LEGGINGS and chestplate:
                lattice = mat_obj.modifiers["Chest"].object
                obj.modifiers.new(name = "Chest", type = "LATTICE")
                obj.modifiers["Chest"].object = lattice
                obj.modifiers["Chest"].vertex_group = "UpperBodyMain"
                # Move to top
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.modifier_move_to_index(modifier="Chest",index=2)

        # ------------------------------------------------------------
        # Main logic
        # ------------------------------------------------------------
        if armor_part in {ArmorPartEnum.BOOTS, ArmorPartEnum.LEGGINGS}:
            apply_leg_taper(obj)
            return

        if armor_part == ArmorPartEnum.CHESTPLATE or "chest_lattice" in obj.name:
            # Chestplate
            if chestplate:
                utils.add_modifier_lattice_chest(self.rig, obj)

                # Move to top
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.modifier_move_to_index(modifier="Chest", index=0)
            return
