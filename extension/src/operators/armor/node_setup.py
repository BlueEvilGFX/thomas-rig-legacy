import bpy
import os
import random

from .logic.armor_enums import TrimEnum, MaterialEnum, ArmorPartEnum, ShaderNodeEnum
from ... import constants

ENCHANTMENT_VALUE: float = 3.8
ENCHANTMENT_SPEED: int = 400


class ShaderNodeHandler:
    armor_obj: bpy.types.Object
    original_textures: bool
    armor_material: MaterialEnum
    armor_part: ArmorPartEnum
    armor_trim: TrimEnum 
    trim_colour: tuple[float, float, float]
    leather_colour: tuple[float, float, float]
    enchantment: bool
    trim_emission: bool

    material: bpy.types.Material
    node_tree: bpy.types.NodeTree
    nodes: list[bpy.types.Node]
    node_links: list[bpy.types.NodeLinks]

    filepath: str # optional

    loaded_textures = {} # texturepath : image

    def initialize(
            self,
            armor_obj: bpy.types.Object,
            original_textures: bool,
            armor_material: MaterialEnum,
            armor_part: ArmorPartEnum,
            armor_trim: TrimEnum,
            trim_colour: tuple[float, float, float],
            leather_colour: tuple[float, float, float],
            enchantment: bool,
            trim_emission: bool,
            filepath: str = None
    ):
        self.armor_obj = armor_obj
        self.original_textures = original_textures
        self.armor_material = armor_material
        self.armor_part = armor_part
        self.armor_trim = armor_trim
        self.trim_colour = trim_colour
        self.leather_colour = leather_colour
        self.enchantment = enchantment
        self.trim_emission = trim_emission

        self.material = armor_obj.data.materials[0]
        self.node_tree = self.material.node_tree
        self.nodes = self.node_tree.nodes
        self.node_links = self.node_tree.links

        layer_idx = "2" if self.armor_part == ArmorPartEnum.LEGGINGS else "1"
        self.layer = f"layer_{layer_idx}"

        self.armor_texture_dir = self._get_extension_armor_dir() \
            if self.original_textures else constants.ARMOR_PATH_VANILLA
        
        self.filepath = filepath

    def execute(self):
        """takes care of all needed node changes"""
        self._clear_nodes()
        self._set_base_nodes()
        
        if self.armor_material == MaterialEnum.LEATHER:
            self._handle_leather()

        if self.armor_trim != TrimEnum.NONE:
            self._handle_trim()

            if self.trim_emission:
                self._handle_trim_emission()
        
        if self.enchantment:    
            self._handle_enchantment()

    def _get_extension_textures_dir(self) -> str:
        return bpy.utils.extension_path_user(
            package=constants.PACKAGE,
            path="textures"
        )

    def _get_extension_armor_dir(self) -> str:
        return os.path.join(
            self._get_extension_textures_dir(),
            "armor"
        )
    
    def _get_extension_trims_dir(self) -> str:
        return os.path.join(
            self._get_extension_textures_dir(),
            "trims"
        )

    def _set_base_nodes(self):
        # Add nodes
        image_node = self.nodes.new("ShaderNodeTexImage")
        image_node.interpolation = "Closest"
        image_node.location = (-360, 0)
        image_node.hide = True
        self._set_naming(image_node, ShaderNodeEnum.BASE)

        bsdf_node = self.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf_node.location = (0, 0)
        self._set_naming(bsdf_node, ShaderNodeEnum.BSDF)
        bsdf_node.inputs[2].default_value = 0.745
        bsdf_node.inputs[3].default_value = 1.45

        output_node = self.nodes.new("ShaderNodeOutputMaterial")
        output_node.location = (300, 0)
        self._set_naming(output_node, ShaderNodeEnum.OUTPUT)

        # Link nodes
        self._create_link(image_node, 'Alpha', bsdf_node, 4)
        self._create_link(image_node, 'Color', bsdf_node, 0)
        self._create_link(bsdf_node, 0, output_node, 0)

        # Set texture
        # use custom texture if filepath is given
        if self.filepath:
            texture =  self.filepath
        else:
            material = self.armor_material.value
            texture = os.path.join(self.armor_texture_dir,  f"{material}_{self.layer}.png")

        if not texture in self.loaded_textures.keys():
            image = bpy.data.images.load(texture)
            self.loaded_textures[texture] = image
        else:
            image = self.loaded_textures[texture]

        image_node.image = image

    def _handle_leather(self):
        # Move nodes
        self._mass_move_nodes_(-200, 0)

        # Add nodes
        base_location = self._get_node(ShaderNodeEnum.BASE).location
        
        leather_color_node = self.nodes.new("ShaderNodeMixRGB")
        self._set_naming(leather_color_node, ShaderNodeEnum.LEATHER_COLOUR)
        leather_color_node.blend_type = "MULTIPLY"
        leather_color_node.inputs['Fac'].default_value = 1
        leather_color_node.location = (-200, 0)

        leather_rgb_node = self.nodes.new("ShaderNodeRGB")
        self._set_naming(leather_rgb_node, ShaderNodeEnum.LEATHER_RGB)
        leather_rgb_node.outputs[0].default_value = self.leather_colour
        offset = (-160 , -80)
        new_location = tuple(x + y for x, y in zip(base_location, offset))
        leather_rgb_node.location =  new_location

        # Link Nodes
        self._create_link(
            self._get_node(ShaderNodeEnum.BASE), 'Color',
            leather_color_node, 'Color1'
        )

        self._create_link(
            leather_color_node, 'Color',
            self._get_node(ShaderNodeEnum.BSDF), 'Base Color'
        )

        self._create_link(leather_rgb_node, 0, leather_color_node, 'Color2')

        # overlay only avaialable if original MC textures loaded -> Guard clause
        if not self.original_textures:
            return
        
        # reposition nodes
        self._mass_move_nodes_(-200, 0)

        # overlay - brown and already coloured
        leather_overlay_node = self.nodes.new("ShaderNodeTexImage")
        leather_overlay_node.interpolation = "Closest"
        leather_overlay_node.hide = True
        self._set_naming(leather_overlay_node, ShaderNodeEnum.LEATHER_OVERLAY)

        # mix node
        overlay_mix_node = self.nodes.new("ShaderNodeMixRGB")
        overlay_mix_node.blend_type = "MIX"
        overlay_mix_node.inputs['Fac'].default_value = 1
        overlay_mix_node.location = (-200, 0)
        self._set_naming(overlay_mix_node, ShaderNodeEnum.LEATHER_OVERLAY_MIX)

        # Load overlay texture
        material = self.armor_material.value
        texture = os.path.join(self.armor_texture_dir,  f"{material}_overlay_{self.layer}.png")

        if not texture in self.loaded_textures.keys():
            image = bpy.data.images.load(texture)
            self.loaded_textures[texture] = image
        else:
            image = self.loaded_textures[texture]
        
        leather_overlay_node.image = image

        # repostion and connect
        leather_overlay_node.location = (base_location[0], base_location[1] + 40)
        self._create_link(
            leather_color_node, 'Color',
            overlay_mix_node, 'Color1'
        )

        self._create_link(
            leather_overlay_node, 'Color',
            overlay_mix_node, 'Color2'
        )

        self._create_link(
            leather_overlay_node, 'Alpha',
            overlay_mix_node, 'Fac'
        )

        self._create_link(
            overlay_mix_node, 'Color',
            self._get_node(ShaderNodeEnum.BSDF), 'Base Color'
        )

    def _handle_trim(self):
        # Move nodes
        self._mass_move_nodes_(-400, 0)

        # Add nodes
        base_location = self._get_node(ShaderNodeEnum.BASE).location

        trim_node = self.nodes.new("ShaderNodeTexImage")
        trim_node.interpolation = "Closest"
        trim_node.hide = True
        self._set_naming(trim_node, ShaderNodeEnum.TRIM)
        
        offset = (0 , -40)
        new_location = tuple(x + y for x, y in zip(base_location, offset))
        trim_node.location =  new_location

        colour_node = self.nodes.new("ShaderNodeMixRGB")
        self._set_naming(colour_node, ShaderNodeEnum.TRIM_COLOUR)
        colour_node.inputs['Fac'].default_value = 1
        colour_node.blend_type = "MULTIPLY"
        colour_node.location = (-400, 0)

        mix_node = self.nodes.new("ShaderNodeMixRGB")
        mix_node.hide = True
        self._set_naming(mix_node, ShaderNodeEnum.TRIM_MIX)
        mix_node.blend_type = "MIX"
        mix_node.location = (-200, 0)

        add_alpha_node = self.nodes.new("ShaderNodeMath")
        add_alpha_node.hide = True
        add_alpha_node.location = (-200, -40)
        self._set_naming(add_alpha_node, ShaderNodeEnum.TRIM_ADD_ALPHA)

        trim_rgb_node = self.nodes.new("ShaderNodeRGB")
        self._set_naming(trim_rgb_node, ShaderNodeEnum.TRIM_RGB)
        trim_rgb_node.outputs[0].default_value = self.trim_colour
        offset = (0 , -80)
        new_location = tuple(x + y for x, y in zip(base_location, offset))
        trim_rgb_node.location =  new_location

        # Link nodes
        bsdf_node = self._get_node(ShaderNodeEnum.BSDF)
        input_socket = bsdf_node.inputs.get('Base Color')
        link = input_socket.links[0] 
        linked_node = link.from_node
        linked_output = link.from_socket

        base_node = self._get_node(ShaderNodeEnum.BASE)

        self._create_link(linked_node, linked_output.name, mix_node, 'Color1')
        self._create_link(trim_node, 'Color', colour_node, 'Color1')
        self._create_link(colour_node, 'Color', mix_node, 'Color2')
        self._create_link(mix_node, 'Color', bsdf_node, 'Base Color')
        self._create_link(trim_node, 'Alpha', mix_node, 'Fac')
        self._create_link(base_node, 'Alpha', add_alpha_node, 0)
        self._create_link(trim_node, 'Alpha', add_alpha_node, 1)
        self._create_link(add_alpha_node, 0, bsdf_node, 4)
        self._create_link(trim_rgb_node, 0, colour_node, 'Color2')

        # Load trim texture
        texture = os.path.join(
            self._get_extension_trims_dir(),
            f"{self.armor_trim.value}_layer_2.png" \
                if self.armor_part in {ArmorPartEnum.LEGGINGS}
                else f"{self.armor_trim.value}.png"
        )
        

        if not texture in self.loaded_textures.keys():
            image = bpy.data.images.load(texture)
            self.loaded_textures[texture] = image
        else:
            image = self.loaded_textures[texture]

        trim_node.image = image 

    def _handle_trim_emission(self):
        # Add nodes
        base_location = self._get_node(ShaderNodeEnum.BSDF).location

        # emission shader
        shader_emission = self.nodes.new("ShaderNodeEmission")
        self._set_naming(shader_emission, ShaderNodeEnum.TRIM_EMISSION_SHADER)
        offset = (0 , -350)
        new_location = tuple(x + y for x, y in zip(base_location, offset))
        shader_emission.location = new_location

        # emission value
        emission_value_node = self.nodes.new("ShaderNodeValue")
        self._set_naming(emission_value_node, ShaderNodeEnum.TRIM_EMISSION_VALUE)
        emission_value_node.outputs[0].default_value = constants.DEFAULT_EMISSION_VALUE
        offset = (-400 , -650)
        new_location = tuple(x + y for x, y in zip(base_location, offset))
        emission_value_node.location = new_location

        # mix shader
        shader_mix = self.nodes.new("ShaderNodeMixShader")
        self._set_naming(shader_mix, ShaderNodeEnum.TRIM_MIX_SHADER)
        offset = (350 , 0)
        new_location = tuple(x + y for x, y in zip(base_location, offset))
        shader_mix.location = new_location

        # light path | camera ray
        ligh_path = self.nodes.new("ShaderNodeLightPath")
        self._set_naming(ligh_path, ShaderNodeEnum.TRIM_EMISSION_CAMERA_RAY)
        ligh_path.hide = True
        offset = (-400 , -550)
        new_location = tuple(x + y for x, y in zip(base_location, offset))
        ligh_path.location = new_location

        # blow out value
        blow_out_value_node = self.nodes.new("ShaderNodeValue")
        self._set_naming(blow_out_value_node, ShaderNodeEnum.TRIM_EMISSION_BLOW_OUT)
        blow_out_value_node.outputs[0].default_value = 0.1
        offset = (-400 , -700)
        new_location = tuple(x + y for x, y in zip(base_location, offset))
        blow_out_value_node.location = new_location

        # blow out math mix
        blow_out_mix_node = self.nodes.new("ShaderNodeMix")
        self._set_naming(blow_out_mix_node, ShaderNodeEnum.TRIM_EMISSION_MIX_BLOW_OUT)
        offset = (-200 , -500)
        new_location = tuple(x + y for x, y in zip(base_location, offset))
        blow_out_mix_node.location = new_location

        # blow out colour mix
        blow_out_mix_colour_node = self.nodes.new("ShaderNodeMixRGB")
        self._set_naming(blow_out_mix_colour_node, ShaderNodeEnum.TRIM_EMISSION_MIX_Colour_BLOW_OUT)
        blow_out_mix_colour_node.inputs[2].default_value = [0, 0, 0, 1] # set to black
        offset = (0 , -500)
        new_location = tuple(x + y for x, y in zip(base_location, offset))
        blow_out_mix_colour_node.location = new_location

        # move output node
        output = self.nodes["output"]
        output.location[0] = output.location[0] + 200

        # link nodes
        bsdf_node = self._get_node(ShaderNodeEnum.BSDF)
        trim_colour_node = self._get_node(ShaderNodeEnum.TRIM_COLOUR)

        self._create_link(trim_colour_node, "Color", shader_emission, "Color")
        self._create_link(shader_emission, 0, shader_mix, 2)
        self._create_link(bsdf_node, 0, shader_mix, 1)
        self._create_link(shader_mix, 0, output, 0)
        self._create_link(ligh_path, "Is Camera Ray", blow_out_mix_node, 'A')
        self._create_link(emission_value_node, 0, blow_out_mix_colour_node, 1)
        self._create_link(blow_out_value_node, 0, blow_out_mix_node, 0)
        self._create_link(blow_out_mix_node, 0, blow_out_mix_colour_node, 0)
        self._create_link(blow_out_mix_colour_node, 0, shader_emission, 1)

    def _handle_enchantment(self):
        # Move nodes
        self._mass_move_nodes_(-200, 0)

        # Add nodes
        base_location = self._get_node(ShaderNodeEnum.BASE).location

        enchantment_node = self.nodes.new("ShaderNodeTexImage")
        enchantment_node.interpolation = "Cubic"
        enchantment_node.hide = True
        self._set_naming(enchantment_node, ShaderNodeEnum.ENCHANTMENT)
        offset = (0 , 40)
        new_location = tuple(x + y for x, y in zip(base_location, offset))
        enchantment_node.location =  new_location

        mix_node = self.nodes.new("ShaderNodeMixRGB")
        self._set_naming(mix_node, ShaderNodeEnum.ENCHANTMENT_MIX)
        mix_node.hide = True
        mix_node.inputs['Fac'].default_value = 1
        mix_node.blend_type = "ADD"
        mix_node.location = (-200, 0)

        hue_node = self.nodes.new("ShaderNodeHueSaturation")
        self._set_naming(hue_node, ShaderNodeEnum.ENCHANTMENT_HUE)
        hue_node.location = (-200, -80)
        hue_node.inputs[1].default_value = 0
        hue_node.inputs[2].default_value = ENCHANTMENT_VALUE

        offset_node = self.nodes.new("ShaderNodeValue")
        self._set_naming(offset_node, ShaderNodeEnum.ENCHANTMENT_VALUE_OFFSET)
        offset = (-160 , -270)
        new_location = tuple(x + y for x, y in zip(base_location, offset))
        offset_node.location = new_location
        value = random.randint(0, ENCHANTMENT_SPEED)
        offset_node.outputs[0].default_value = value

        speed_node = self.nodes.new("ShaderNodeValue")
        self._set_naming(speed_node, ShaderNodeEnum.ENCHANTMENT_VALUE_SPEED)
        offset = (0 , -270)
        new_location = tuple(x + y for x, y in zip(base_location, offset))
        speed_node.location = new_location
        speed_node.outputs[0].default_value = ENCHANTMENT_SPEED

        add_node = self.nodes.new("ShaderNodeMath")
        self._set_naming(add_node, ShaderNodeEnum.ENCHANTMENT_ADD)
        add_node.operation = "ADD"
        add_node.location = (-400, -270)
        add_node.hide = True
        # create a driver : current frame
        driver = add_node.inputs[1].driver_add("default_value").driver
        driver.type = 'SCRIPTED'
        driver.expression = "frame"
        # Add a variable to the driver for the frame
        var = driver.variables.new()
        var.name = "frame"
        var.targets[0].id_type = 'SCENE'
        var.targets[0].id = bpy.context.scene
        var.targets[0].data_path = "frame_current"

        divide_node = self.nodes.new("ShaderNodeMath")
        self._set_naming(divide_node, ShaderNodeEnum.ENCHANTMENT_DIV)
        divide_node.operation = "DIVIDE"
        divide_node.location = (-400, -310)
        divide_node.hide = True

        mul_node = self.nodes.new("ShaderNodeVectorMath")
        self._set_naming(mul_node, ShaderNodeEnum.ENCHANTMENT_MUL)
        mul_node.operation = "MULTIPLY"
        mul_node.location = (-200, -270)
        mul_node.inputs[1].default_value = (1, 1, 0)
        mul_node.hide = True

        map_node = self.nodes.new("ShaderNodeMapping")
        self._set_naming(map_node, ShaderNodeEnum.ENCHANTMENT_MAP)
        map_node.location = (-200, -310)
        map_node.hide = True

        tco_node = self.nodes.new("ShaderNodeTexCoord")
        tco_node.location = (-400, -370)
        tco_node.hide = True
    
        # routing nodes
        rout_node_1 = self.nodes.new("NodeReroute")
        rout_node_1.location = (-40, -320)
        self._create_link(map_node, 0, rout_node_1, 0)

        rout_node_2 = self.nodes.new("NodeReroute")
        rout_node_2.location = (-40, 60)
        self._create_link(rout_node_1, 0, rout_node_2, 0)

        rout_node_3 = self.nodes.new("NodeReroute")
        offset = (-40 , 60)
        new_location = tuple(x + y for x, y in zip(base_location, offset))
        rout_node_3.location = new_location
        self._create_link(rout_node_2, 0, rout_node_3, 0)

        rout_node_4 = self.nodes.new("NodeReroute")
        offset = (-40 , 30)
        new_location = tuple(x + y for x, y in zip(base_location, offset))
        rout_node_4.location = new_location
        self._create_link(rout_node_3, 0, rout_node_4, 0)
        self._create_link(rout_node_4, 0, enchantment_node, 0)

        # Link nodes
        bsdf_node = self._get_node(ShaderNodeEnum.BSDF)
        input_socket = bsdf_node.inputs.get('Base Color')
        link = input_socket.links[0] 
        linked_node = link.from_node
        linked_output = link.from_socket

        self._create_link(linked_node, linked_output.name, mix_node, 'Color1')
        self._create_link(mix_node, 'Color', bsdf_node, 'Base Color')
        self._create_link(enchantment_node, 'Color', hue_node, 'Color')
        self._create_link(hue_node, 'Color', bsdf_node, 28)
        self._create_link(enchantment_node, 'Color', bsdf_node, 27)
        self._create_link(enchantment_node, 'Color', mix_node, 'Color2')
        self._create_link(offset_node, 0, add_node, 0)
        self._create_link(speed_node, 0, divide_node, 1)
        self._create_link(add_node, 0, divide_node, 0)
        self._create_link(divide_node, 0, mul_node, 0)
        self._create_link(mul_node, 0, map_node, 1)
        self._create_link(tco_node, 2, map_node, 0)

        # Load enchantment texture
        texture = os.path.join(
            self._get_extension_armor_dir(),
            "enchanted_glint_armor.png"
        )

        if not texture in self.loaded_textures.keys():
            image = bpy.data.images.load(texture)
            self.loaded_textures[texture] = image
        else:
            image = self.loaded_textures[texture]
            
        enchantment_node.image = image

    def _clear_nodes(self):
        for node in list(self.nodes):
            self.nodes.remove(node)

    def _set_naming(
            self, node: bpy.types.ShaderNode,
            key: ShaderNodeEnum
    ):
        """sets the label and the name of a ShaderNode"""
        node.name = str(key)
        node.label = key.value

    def _get_node(self, node_type: ShaderNodeEnum) -> bpy.types.ShaderNode:
        return self.nodes[str(node_type)]

    def _create_link(
        self,
        src_node: bpy.types.ShaderNode,
        src_socket: str | int,
        target_node: bpy.types.ShaderNode,
        target_socket: str | int      
    ):
        self.node_links.new(
            src_node.outputs[src_socket],
            target_node.inputs[target_socket]
        )
    
    def _mass_move_nodes_(self, x_offset: int, splitpoint: 0):
        """moves the nodes in X which are left to splitpoint"""
        for node in list(self.nodes):
            if node.location[0] < splitpoint:
                offset:tuple = (x_offset , 0)
                location = node.location
                node.location = tuple(x + y for x, y in zip(location, offset))