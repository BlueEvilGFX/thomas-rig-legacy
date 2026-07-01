import bpy
from bpy.props import BoolProperty

from ... import utils
from ... import constants
from .logic.armor_enums import TrimEnum, MaterialEnum, ArmorPartEnum, ArmorTypeEnum
from .property_creator import PropertyCreator
from .node_setup import ShaderNodeHandler

from .logic.armor_loader import ArmorLoader
from .logic.armor_modifiers import ArmorModifierSetup
from .logic.armor_drivers import ArmorDriverSetup
from .logic.armor_cleanup import ArmorCleanup

class THOMAS_RIG_ARMOR_ADD(bpy.types.Operator):
    bl_idname = "thomasriglegacy.addarmor"
    bl_label = "add armor"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    # -------------------- CALLBACKS -----------------------
    def filepath_refresh(self, context):
        if context.area:
            context.area.tag_redraw()

    # -------------------- GLOBAL --------------------
    loaded: BoolProperty(default=False)  # type: ignore
    parent: BoolProperty(default=False, options={'SKIP_PRESET'})  # type: ignore
    filepath_1: bpy.props.StringProperty(subtype="FILE_PATH", update=filepath_refresh, options={'SKIP_PRESET'})  # type: ignore
    filepath_2: bpy.props.StringProperty(subtype="FILE_PATH", update=filepath_refresh, options={'SKIP_PRESET'})  # type: ignore

    # -------------------- ARMOR PARTS --------------------
    helmet: PropertyCreator.boolean()  # type: ignore
    chestplate: PropertyCreator.boolean()  # type: ignore
    leggings: PropertyCreator.boolean()  # type: ignore
    boots: PropertyCreator.boolean()  # type: ignore

    # -------------------- ARMOR TYPE --------------------
    armor_type: PropertyCreator.armor_type()  # type: ignore

    # -------------------- MATERIALS --------------------
    helmet_material: PropertyCreator.material(True)  # type: ignore
    chestplate_material: PropertyCreator.material()  # type: ignore
    leggings_material: PropertyCreator.material()  # type: ignore
    boots_material: PropertyCreator.material()  # type: ignore

    # -------------------- TRIMS --------------------
    helmet_trim: PropertyCreator.trim_type()  # type: ignore
    chestplate_trim: PropertyCreator.trim_type()  # type: ignore
    leggings_trim: PropertyCreator.trim_type()  # type: ignore
    boots_trim: PropertyCreator.trim_type()  # type: ignore

    # -------------------- TRIM COLORS --------------------
    helmet_trim_colour: PropertyCreator.colour()  # type: ignore
    chestplate_trim_colour: PropertyCreator.colour()  # type: ignore
    leggings_trim_colour: PropertyCreator.colour()  # type: ignore
    boots_trim_colour: PropertyCreator.colour()  # type: ignore

    # -------------------- ALT TEXTURES --------------------
    helmet_alt_texture: PropertyCreator.boolean()  # type: ignore
    chestplate_alt_texture: PropertyCreator.boolean()  # type: ignore
    leggings_alt_texture: PropertyCreator.boolean()  # type: ignore
    boots_alt_texture: PropertyCreator.boolean()  # type: ignore

    # -------------------- LEATHER COLORS --------------------
    helmet_leather_colour: PropertyCreator.colour(MaterialEnum.LEATHER)  # type: ignore
    chestplate_leather_colour: PropertyCreator.colour(MaterialEnum.LEATHER)  # type: ignore
    leggings_leather_colour: PropertyCreator.colour(MaterialEnum.LEATHER)  # type: ignore
    boots_leather_colour: PropertyCreator.colour(MaterialEnum.LEATHER)  # type: ignore

    # -------------------- ENCHANTMENTS --------------------
    helmet_enchantment: PropertyCreator.boolean()  # type: ignore
    chestplate_enchantment: PropertyCreator.boolean()  # type: ignore
    leggings_enchantment: PropertyCreator.boolean()  # type: ignore
    boots_enchantment: PropertyCreator.boolean()  # type: ignore

    # -------------------- TRIMS EMISSION ------------------
    helmet_trim_emission: PropertyCreator.boolean()  # type: ignore
    chestplate_trim_emission: PropertyCreator.boolean()  # type: ignore
    leggings_trim_emission: PropertyCreator.boolean()  # type: ignore
    boots_trim_emission: PropertyCreator.boolean()  # type: ignore

    def _rig_is_valid(self):
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
        from .armor_ui import draw_armor_ui
        draw_armor_ui(self, context)

    def execute(self, context):
        if not any([self.helmet, self.chestplate, self.leggings, self.boots]):
            self.report({'INFO'}, 'No armor part selected')
            return {'FINISHED'}

        if self._rig_is_valid() is False and self.parent is True:
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
        else:
            self.rig = None

        # armor type
        wm = bpy.context.window_manager
        armor_type = wm.thomas_rig_legacy.custom_armor[:-4]

        loader = ArmorLoader(self)
        modifiers = ArmorModifierSetup(self.rig, self.parent)
        drivers = ArmorDriverSetup(self)
        cleanup = ArmorCleanup(self)
        node_handler = ShaderNodeHandler()

        # -------------------- CUSTOM ARMOR --------------------
        if self.armor_type == ArmorTypeEnum.CUSTOM.value:
            for armor_part in ArmorPartEnum:
                # Armor part not accesible
                if not getattr(self, armor_part.value):
                    continue

                objs = loader.load_custom(armor_part, armor_type)

                if not self.parent:
                    continue

                modifiers.apply_custom_modifiers(objs, armor_part, armor_type)

                for obj in objs:
                    if armor_type in {'Scuba'}:
                        drivers.apply_default_drivers(obj, armor_part)
                    elif (
                        armor_type == 'Samurai_2'
                        and armor_part == 'leggings'
                        and 'leggings' in obj.name
                    ):
                        drivers.apply_default_drivers(obj, armor_part)                

        # -------------------- DEFAULT ARMOR --------------------
        elif self.armor_type == ArmorTypeEnum.DEFAULT.value:
            for armor_part in ArmorPartEnum:
                material = MaterialEnum(getattr(self, f"{armor_part.value}_material"))
                self._process_armor_part(
                    armor_part, context, loader, modifiers, drivers, cleanup, node_handler,
                    original_textures=not self.boots_alt_texture,
                    material=material,
                    filepath=None
                )


        # -------------------- TEXTURE ARMOR --------------------
        elif self.armor_type == ArmorTypeEnum.TEXTURE.value:
            for armor_part in ArmorPartEnum:

                if armor_part in {ArmorPartEnum.HELMET, ArmorPartEnum.CHESTPLATE}:
                    filepath = self.filepath_1
                    print("FILEPATH", filepath)
                    if not filepath:
                        self.helmet = False
                        self.chestplate = False
                else:
                    filepath = self.filepath_2
                    if not filepath:
                        self.leggings = False
                        self.boots = False

                self._process_armor_part(
                    armor_part, context, loader, modifiers, drivers, cleanup, node_handler,
                    original_textures=False,
                    material=None,
                    filepath=filepath
                )
        
        # -------------------- FINISH -------------------
        bpy.ops.object.select_all (action='DESELECT')
        if mode and self.parent:
            context.view_layer.objects.active = self.rig
            bpy.ops.object.mode_set(mode=mode, toggle=False)
        
        # Force update no face mode
        if self.parent:
            self.rig.data.update_tag()
            self.rig.data.pose_position = 'POSE'
        return {'FINISHED'}
    
    def _process_armor_part(self, armor_part, context, loader, modifiers, drivers, cleanup, node_handler,*, original_textures, material,filepath=None):
        # Armor part not accessible
        if not getattr(self, armor_part.value):
            return

        if self.parent:
            context.view_layer.objects.active = self.rig

        armor_object = loader.load_default(armor_part)
        modifiers.apply_default_modifiers(armor_object, armor_part)
        drivers.apply_default_drivers(armor_object, armor_part)

        trim_property = f"{armor_part.value}_trim"
        has_trim = getattr(self, trim_property) != TrimEnum.NONE.value

        node_handler.initialize(
            armor_obj=armor_object,
            original_textures=original_textures,
            armor_material=material,
            armor_part=armor_part,
            armor_trim=TrimEnum(getattr(self, trim_property)),
            trim_colour=getattr(self, f"{armor_part.value}_trim_colour"),
            trim_emission=getattr(self, f"{armor_part.value}_trim_emission"),
            leather_colour=getattr(self, f"{armor_part.value}_leather_colour", None),
            enchantment=getattr(self, f"{armor_part.value}_enchantment"),
            filepath=filepath
        )

        node_handler.execute()
        cleanup.remove_alpha_faces(armor_object, has_trim)
