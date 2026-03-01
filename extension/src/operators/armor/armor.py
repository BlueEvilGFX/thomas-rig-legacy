import bpy
from bpy.props import BoolProperty, EnumProperty,FloatVectorProperty
import bmesh
import os

from ... import utils
from ... import constants
from .armor_enums import TrimEnum, MaterialEnum, ShaderNodeEnum, ArmorPartEnum
from .property_creator import PropertyCreator
from .node_setup import ShaderNodeHandler


class THOMAS_RIG_ARMOR_ADD(bpy.types.Operator):
    bl_idname = "thomasriglegacy.addarmor"
    bl_label = "add armor"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    # Loaded mc textures
    loaded: BoolProperty(default=False) # type: ignore

    # parent to rig (Thomas Rig Legacy)
    parent: BoolProperty(default=False) # type: ignore
    
    # Armor parts : Boolean
    helmet : PropertyCreator.boolean() # type: ignore
    chestplate : PropertyCreator.boolean() # type: ignore
    leggings : PropertyCreator.boolean() # type: ignore
    boots : PropertyCreator.boolean() # type: ignore

    # Armor select : Enum
    armor_type : PropertyCreator.armor_type() # type: ignore

    # Default armor materials : Enum
    helmet_material : PropertyCreator.material(True) # type: ignore
    chestplate_material : PropertyCreator.material() # type: ignore
    leggings_material : PropertyCreator.material() # type: ignore
    boots_material : PropertyCreator.material() # type: ignore

    # Armor trims : Enum
    helmet_trim : PropertyCreator.trim_type() # type: ignore
    chestplate_trim : PropertyCreator.trim_type() # type: ignore
    leggings_trim : PropertyCreator.trim_type() # type: ignore
    boots_trim : PropertyCreator.trim_type() # type: ignore

    # Armor trims : Colour
    helmet_trim_colour : PropertyCreator.colour() # type: ignore
    chestplate_trim_colour : PropertyCreator.colour() # type: ignore
    leggings_trim_colour : PropertyCreator.colour() # type: ignore
    boots_trim_colour : PropertyCreator.colour() # type: ignore

    # Alternative textures : Boolean
    helmet_alt_texture : PropertyCreator.boolean() # type: ignore
    chestplate_alt_texture : PropertyCreator.boolean() # type: ignore
    leggings_alt_texture : PropertyCreator.boolean() # type: ignore
    boots_alt_texture : PropertyCreator.boolean() # type: ignore
    
    # Leather armor : Colour
    helmet_leather_colour : PropertyCreator.colour(MaterialEnum.LEATHER) # type: ignore
    chestplate_leather_colour : PropertyCreator.colour(MaterialEnum.LEATHER) # type: ignore
    leggings_leather_colour : PropertyCreator.colour(MaterialEnum.LEATHER) # type: ignore
    boots_leather_colour : PropertyCreator.colour(MaterialEnum.LEATHER) # type: ignore

    # Enchantments : Boolean
    helmet_enchantment : PropertyCreator.boolean() # type: ignore
    chestplate_enchantment :PropertyCreator.boolean() # type: ignore
    leggings_enchantment : PropertyCreator.boolean() # type: ignore
    boots_enchantment : PropertyCreator.boolean() # type: ignore

    def rig_poll(self):
        rig = utils.get_rig()

        if not rig or not rig.get("Rig_ID") == constants.RIG_ID:
            return False
        
        rig_version = rig.get("rig_version", "unknown")

        if rig_version == "unknown":
            return False

        return list(rig_version) >= [0, 2, 2]
    
    def reapply_lock(self):
        if self.loaded:
            return
        
        self.helmet_alt_texture = True
        self.chestplate_alt_texture = True
        self.leggings_alt_texture = True
        self.boots_alt_texture = True

        self.helmet_trim = TrimEnum.NONE.value
        self.chestplate_trim = TrimEnum.NONE.value
        self.leggings_trim = TrimEnum.NONE.value
        self.boots_trim = TrimEnum.NONE.value

        self.helmet_enchantment = False
        self.chestplate_enchantment = False
        self.leggings_enchantment = False
        self.boots_enchantment = False

    def invoke(self, context, event):
        # Set mc textures loaded property and default for alternative textures
        preferences = context.preferences.addons[constants.PACKAGE].preferences
        self.loaded = preferences.mc_textures_loaded

        self.helmet_alt_texture = not self.loaded
        self.chestplate_alt_texture = not self.loaded
        self.leggings_alt_texture = not self.loaded
        self.boots_alt_texture = not self.loaded

        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        from ... import icons

        column = self.layout.column()
        column.row().prop(self, "armor_type", expand = True)

        pcoll = icons.thomas_icons["thomas_legacy"]
        self.loaded = getattr(context.preferences.addons[constants.PACKAGE].preferences, "mc_textures_loaded", False)

        if self.armor_type == "default":
            utils.UI_Utils.spacer(column, 0.3)

            icon_dict = {
                ArmorPartEnum.HELMET : pcoll["helmet_iron"].icon_id,
                ArmorPartEnum.CHESTPLATE : pcoll["chestplate_iron"].icon_id,
                ArmorPartEnum.LEGGINGS : pcoll["leggings_iron"].icon_id,
                ArmorPartEnum.BOOTS : pcoll["boots_iron"].icon_id,
            }

            # Naming text info
            row = column.row()
            split = row.split(factor=0.4)

            # Armor, Material (, Trim, Enchantment)
            split.column().label(text="armor part")
            split = split.split(factor=0.5)
            split.column().label(text="material")
            
            col = split.column()
            col.enabled = self.loaded
            col.label(text="trim")

            row.label(text = "", icon="BLANK1") # Enchantment

            for key in ArmorPartEnum:
                element = key.value
                row = column.row()
                split = row.split(factor = 0.4)

                # Armor type
                col = split.column()
                type_row = col.row()
                type_row.label(text="", icon_value=icon_dict.get(key))
                type_row.prop(self, element)

                if not getattr(self, element, False):
                    continue

                # Alternative tetures
                alt_texture = type_row.split()
                alt_texture.enabled = self.loaded
                alt_texture.prop(
                    self,
                    f"{element}_alt_texture",
                    icon="UV_SYNC_SELECT",
                    text=""
                )

                # Material
                split = split.split(factor = 0.5)
                col = split.column()
                material_row = col.row(align = True)
                material_row.prop(self, element + "_material")

                # Leather armor coloring
                if getattr(self, f"{element}_material") == MaterialEnum.LEATHER.value:
                    material_row.scale_x = 0.4
                    material_row.prop(self, element + "_leather_colour")

                # Trims
                col = split.column()
                trim_row = col.row(align = True)
                trim_row.enabled = self.loaded

                trim_type = trim_row.split(align = True)
                trim_type.prop(self, element + "_trim")

                trim_colour = trim_row.split(align = True)
                trim_value = getattr(self, f"{element}_trim")
                trim_colour.enabled = (trim_value != TrimEnum.NONE.value)
                trim_colour.scale_x = 0.4
                trim_colour.prop(self, element + "_trim_colour")

                # Enchantment
                enchantment_row = row.split().row()
                enchantment_row.enabled = self.loaded
                enchanted_book = pcoll.get("enchanted_book", False)
                icon_value = enchanted_book.icon_id if enchanted_book else 0
                enchantment_row.prop(
                    self,
                    f"{element}_enchantment",
                    icon_value = icon_value,
                    icon="EVENT_E" if "enchanted_book" not in pcoll else 'NONE',
                    text="",
                    toggle=True
                )
        else:
            column.template_icon_view(
                context.window_manager.thomas_rig_legacy,
                "custom_armor"
            )
            
            utils.UI_Utils.spacer(column, 0.3)
            column.prop(self, ArmorPartEnum.HELMET.value)
            column.prop(self, ArmorPartEnum.CHESTPLATE.value)
            column.prop(self, ArmorPartEnum.LEGGINGS.value)
            
            wm = context.window_manager
            custom_armor = wm.thomas_rig_legacy.custom_armor[:-4]
            
            if custom_armor in {'Scuba'}:
                column.prop(self, ArmorPartEnum.BOOTS.value)

    def execute(self, context):
        if not any([self.helmet, self.chestplate, self.leggings, self.boots]):
            self.report({'INFO'}, 'No armor part selected')
            return {'FINISHED'}
        
        if self.rig_poll() is False and self.parent is True:
            self.report({'WARNING'}, 'Rig not selected')
            return {'FINISHED'}
        
        # If preset selected: not loaded can be cicumvented
        self.reapply_lock()

        try:
            mode = context.object.mode
        except:
            mode = False

        if self.parent:
            self.rig = utils.get_rig()
            context.view_layer.objects.active = self.rig
            self.rig.data.pose_position = 'REST'

        for armor_part in ArmorPartEnum:
            # Armor part not accesible
            if not getattr(self, armor_part.value):
                continue
            
            # Add custom armor piece
            if self.armor_type == "custom":
                self.add_custom_armor(armor_part)
                continue

            # Add default armor piece
            if self.parent:
                context.view_layer.objects.active = self.rig
            armor_object = self.add_default_armor(armor_part)

            # Add trim 
            trim_property = f"{armor_part.value}_trim"
            has_trim = getattr(self, trim_property) != TrimEnum.NONE.value

            node_handler = ShaderNodeHandler(
                armor_object,
                not self.boots_alt_texture,
                MaterialEnum(getattr(self, f"{armor_part.value}_material")),
                armor_part,
                TrimEnum(getattr(self, trim_property)),
                getattr(self,  f'{armor_part.value}_trim_colour'),
                getattr(self,  f'{armor_part.value}_leather_colour'),
                getattr(self,  f'{armor_part.value}_enchantment')                
            )

            node_handler.initialize()

            self.remove_alpha_faces(armor_object, has_trim)

        bpy.ops.object.select_all (action='DESELECT')
        if mode:
            context.view_layer.objects.active = self.rig
            bpy.ops.object.mode_set(mode=mode, toggle=False)
        
        # Force update no face mode
        if self.parent:
            self.rig.data.update_tag()
            self.rig.data.pose_position = 'POSE'
        return {'FINISHED'}
    
    def add_default_armor(self, armor_part: ArmorPartEnum) -> bpy.types.Object:
        armor_dir = constants.ARMOR_PATH 
        default_armor_file = os.path.join(armor_dir, "armor_default.blend")

        # Append armor part
        directory = os.path.join(default_armor_file, "Object")
        filepath = os.path.join(directory, armor_part.value)
        bpy.ops.wm.append(
            filepath=filepath,
            filename=armor_part.value,
            directory=directory,
            link=False,
            active_collection=True
        )
        if self.parent:
            bpy.ops.object.mode_set(mode = "OBJECT")
        armor_object = bpy.context.selected_objects[0]
        armor_object.location.x = 0
        armor_object.location.y = 0
        # armor_object.location.z = 0

        # Modifiers
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
        
        if any(part == armor_part for part in FILTER_PARTS):
            if self.parent:
                chest_vertex_group = "UpperBodyMain"
                vertex_group_R, vertex_group_L = VERTEX_GROUPS.get(armor_part)
                method_R, method_L = LATTICE_METHODS.get(armor_part)

                if armor_part != ArmorPartEnum.BOOTS:
                    # Chest Lattice
                    lattice_main = utils.add_modifier_lattice_chest_pose(
                        self.rig,
                        armor_object
                    )
                    lattice_main.vertex_group = chest_vertex_group

                lattice_R = method_R(self.rig, armor_object)
                lattice_R.vertex_group = vertex_group_R

                lattice_L = method_L(self.rig, armor_object)
                lattice_L.vertex_group = vertex_group_L

                for key in armor_object.data.shape_keys.key_blocks:
                    if "120" in key.name or "Bend" in key.name:
                        key.mute = True
                        
                self.add_drivers_default_armor(armor_object, self.rig, armor_part)

            if armor_part == ArmorPartEnum.CHESTPLATE:
                armor_object.location[1] = 0.004265 # Chestplate offset
                shape_keys = armor_object.data.shape_keys
                shape_keys.key_blocks["chestplate.001"].value = 0

        # Handle helmet
        else:
            if self.parent:
                utils.add_modifier_armature(self.rig, armor_object)
                utils.add_modifier_lattice_smart_deform(self.rig, armor_object)
                utils.add_modifier_lattice_head(self.rig, armor_object)
            utils.add_modifier_solidify(armor_object, -0.045)

            bpy.context.view_layer.objects.active = armor_object

        # Add taper lattice
        if self.parent:
            self.add_taper(armor_object, armor_part)
            
        # Add and move subdivisions to top
        bpy.context.view_layer.objects.active = armor_object
        utils.add_modifier_subdivision(armor_object, 0, 3, 'SIMPLE')
        last_index = len(armor_object.modifiers) - 1
        bpy.ops.object.modifier_move_to_index(modifier="Solidify", index=last_index)
        bpy.ops.object.modifier_move_to_index(
            modifier="Auto Smooth",
            index=last_index
        )
        bpy.ops.object.modifier_move_to_index(modifier="subdivision", index=last_index)

        # Show solidify
        solidify = armor_object.modifiers["Solidify"]
        solidify.show_viewport = True
        solidify.show_render = True

        for modifier in armor_object.modifiers:
            modifier.show_expanded = False

        return armor_object

    def add_custom_armor(self, armor_part: ArmorPartEnum):
        wm = bpy.context.window_manager
        armor_type = wm.thomas_rig_legacy.custom_armor[:-4]
        armor_file = os.path.join(constants.ARMOR_PATH, f"{armor_type}.blend")

        # Append
        directory = os.path.join(armor_file, "Collection")
        filepath = os.path.join(directory, armor_part.value)
        bpy.ops.wm.append(
            filepath=filepath,
            filename=armor_part.value,
            directory=directory,
            link=False,
            active_collection=True
        )
        if not self.parent:
            return
        
        bpy.ops.object.mode_set(mode = "OBJECT")
        appended_objects = bpy.context.selected_objects
        
        for idx, obj in enumerate(appended_objects):
            # Add armature modifier
            utils.add_modifier_armature(self.rig, obj)

            # Lattice modifier
            if armor_part == ArmorPartEnum.HELMET:
                # Scuba: no need head lattice for 2nd helmet part but taper
                if armor_type == 'Scuba' and idx == 1:
                    self.add_taper(obj, armor_part)
                    continue
                
                utils.add_modifier_lattice_smart_deform(self.rig, obj)
                utils.add_modifier_lattice_head(self.rig, obj)

            if (
                armor_type in {"Cultist", "ZombiePlate"}
                and armor_part == ArmorPartEnum.HELMET
            ):
                self.rig.pose.bones["Main_Properties"]["No face"] = True
            elif armor_type in {'Scuba'}:
                self.add_taper(obj, armor_part)
                self.add_drivers_default_armor(obj, self.rig, armor_part)
            elif (
                armor_type == 'Samurai_2'
                and armor_part == 'leggings'
                and 'leggings' in obj.name
            ):
                self.add_drivers_default_armor(obj, self.rig, armor_part)

            # add subdivisions
            utils.add_modifier_subdivision(obj, 0, 3, "SIMPLE")

    def add_taper(self, armor_obj, armor_part: ArmorPartEnum):
        if (armor_part == ArmorPartEnum.BOOTS
                or armor_part == ArmorPartEnum.LEGGINGS):
        
            mat_obj = utils.get_mat_object(self.rig)
            # Right leg
            lattice = mat_obj.modifiers["Lattice_R_Leg"].object
            armor_obj.modifiers.new(name = "Taper.R", type = "LATTICE")
            armor_obj.modifiers["Taper.R"].object = lattice
            armor_obj.modifiers["Taper.R"].vertex_group = "Lattice_Right"

            # Left leg
            lattice = mat_obj.modifiers["Lattice_L_Leg"].object
            armor_obj.modifiers.new(name = "Taper.L", type = "LATTICE")
            armor_obj.modifiers["Taper.L"].object = lattice
            armor_obj.modifiers["Taper.L"].vertex_group = "Lattice_Left"

            # Move to top
            bpy.context.view_layer.objects.active = armor_obj
            bpy.ops.object.modifier_move_to_index(modifier="Taper.R", index=0)
            bpy.ops.object.modifier_move_to_index(modifier="Taper.L", index=1)

            if armor_part == ArmorPartEnum.LEGGINGS:
                lattice = mat_obj.modifiers["Chest"].object
                armor_obj.modifiers.new(name = "Chest", type = "LATTICE")
                armor_obj.modifiers["Chest"].object = lattice
                armor_obj.modifiers["Chest"].vertex_group = "UpperBodyMain"
                # Move to top
                bpy.context.view_layer.objects.active = armor_obj
                bpy.ops.object.modifier_move_to_index(
                    modifier="Chest",
                    index=2
                )

        elif (
            armor_part == ArmorPartEnum.CHESTPLATE
                or "chest_lattice" in armor_obj.name
        ):
            # Chestplate
            utils.add_modifier_lattice_chest(self.rig, armor_obj)
            # Move to top
            bpy.context.view_layer.objects.active = armor_obj
            bpy.ops.object.modifier_move_to_index(modifier="Chest", index=0)

    def add_drivers_default_armor(
        self, armor_obj, rig, armor_part: ArmorPartEnum
    ):
        if armor_part == ArmorPartEnum.CHESTPLATE:
            joint = "Arm_Lower_Driver"
        elif (
            armor_part == ArmorPartEnum.BOOTS
            or armor_part == ArmorPartEnum.LEGGINGS
        ):
            joint = "Leg_knee_Driver"
        else:
            return
        self.add_driver_bend_120(armor_obj, rig, ".R", "Bend.R", joint, "a")
        self.add_driver_bend_120(armor_obj, rig, ".R", "120.R", joint, "b")
        self.add_driver_bend_120(armor_obj, rig, ".L", "Bend.L", joint, "a")
        self.add_driver_bend_120(armor_obj, rig, ".L", "120.L", joint, "b")

    def add_driver_bend_120(
            self, armor_obj,
            rig, side,
            shapeKeyName,
            boneTarget, ab
        ):
        if ab == "a":
            expression = (
                "tan(value*0.5) if tan(value*0.5) >= 0 "
                "else -tan(value*0.5)"
            )
        elif ab == "b":
            expression = (
                "tan(value*0.5)-1 if tan(value*0.5) >= 0 "
                "else -tan(value*0.5)-1"
            )

        key_block = armor_obj.data.shape_keys.key_blocks[shapeKeyName]
        driver = key_block.driver_add("value").driver
        driver.type = "SCRIPTED"

        var = driver.variables.new()
        var.type = "TRANSFORMS"
        var.name = "value"

        target = driver.variables[0].targets[0]
        target.id = rig
        target.bone_target = boneTarget + side
        target.transform_type = "ROT_X"
        target.transform_space = "LOCAL_SPACE"
        driver.expression = expression

    def remove_alpha_faces(self, armor_obj, has_trim: bool = False):
        # Get the object and its mesh data
        mesh = armor_obj.data

        # Create a BMesh from the mesh data
        bm = bmesh.new()
        bm.from_mesh(mesh)

        # Get the UV layer
        uv_layer = bm.loops.layers.uv.verify()

        # Get the image
        nodes = armor_obj.data.materials[0].node_tree.nodes
        base = nodes[str(ShaderNodeEnum.BASE)].image
        trim_node = nodes.get(str(ShaderNodeEnum.TRIM))
        if trim_node:
            trim_img = trim_node.image

        # Calculate the width and height
        width, height = base.size

        def get_pixel_alpha(image, uv):
            pixel_index = 4 * (
                int(uv[1] * height) * width
                + int(uv[0] * width)
            )
            return image.pixels[pixel_index + 3]

        # Loop through the faces of the BMesh
        for face in bm.faces:
            for loop in face.loops:
                uv_data = loop[uv_layer].uv
                alpha = get_pixel_alpha(base, uv_data)

                if has_trim:
                    uv_data_trim = loop[uv_layer].uv
                    alpha_trim = get_pixel_alpha(trim_img, uv_data_trim)
                    if alpha == 0 and alpha_trim == 0:
                        bmesh.ops.delete(bm, geom=[face], context='FACES')
                        break
                else:
                    if alpha == 0:
                        bmesh.ops.delete(bm, geom=[face], context='FACES')
                        break

        # Update the mesh data with the new BMesh data
        bm.to_mesh(mesh)
        bm.free()