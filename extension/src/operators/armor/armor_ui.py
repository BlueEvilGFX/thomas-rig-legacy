from ...utils import UI_Utils, get_image_size
from ... import constants
from .logic.armor_enums import TrimEnum, MaterialEnum, ArmorPartEnum, ArmorTypeEnum

def draw_armor_ui(op, context):
    from ... import icons

    # -------------------- ICONS ---------------------
    pcoll = icons.thomas_icons["thomas_legacy"]
    loaded = getattr(
        context.preferences.addons[constants.PACKAGE].preferences,
        "mc_textures_loaded",
        False
    )

    icon_dict = {
        ArmorPartEnum.HELMET : pcoll["helmet_iron"].icon_id,
        ArmorPartEnum.CHESTPLATE : pcoll["chestplate_iron"].icon_id,
        ArmorPartEnum.LEGGINGS : pcoll["leggings_iron"].icon_id,
        ArmorPartEnum.BOOTS : pcoll["boots_iron"].icon_id,
    }

    # -------------------- UI ------------------------
    column = op.layout.column()
    column.row().prop(op, "armor_type", expand = True)

    # store on operator
    op.loaded = loaded

    # -------------------------------------------------------------------------
    # DEFAULT ARMOR UI
    # -------------------------------------------------------------------------
    if op.armor_type == ArmorTypeEnum.DEFAULT.value:
        _draw_default(op, column, icon_dict, pcoll)

    # -------------------------------------------------------------------------
    # CUSTOM ARMOR UI
    # -------------------------------------------------------------------------
    elif op.armor_type == ArmorTypeEnum.CUSTOM.value:
        column.template_icon_view(
            context.window_manager.thomas_rig_legacy,
            "custom_armor"
        )
        
        UI_Utils.spacer(column, 0.3)
        
        column.prop(op, ArmorPartEnum.HELMET.value)
        column.prop(op, ArmorPartEnum.CHESTPLATE.value)
        column.prop(op, ArmorPartEnum.LEGGINGS.value)
        
        wm = context.window_manager
        custom_armor = wm.thomas_rig_legacy.custom_armor[:-4]
        
        if custom_armor in {'Scuba'}:
            column.prop(op, ArmorPartEnum.BOOTS.value)

    # -------------------------------------------------------------------------
    # TEXTURE ARMOR UI
    # -------------------------------------------------------------------------
    elif op.armor_type == ArmorTypeEnum.TEXTURE.value:
        # -------------------- TEXTURE -----------------------
        size_1 = get_image_size(op.filepath_1)
        size_2 = get_image_size(op.filepath_2)

        correct_size_1 = size_1 == (64, 32) if size_1 else True
        correct_size_2 = size_2 == (64, 32) if size_2 else True
        file_ending_1 = op.filepath_1.split('.')[-1]
        file_ending_2 = op.filepath_2.split('.')[-1]

        row = column.row()
        row.alert = not correct_size_1
        row.prop(op, "filepath_1")

        row = column.row()
        row.alert = not correct_size_2
        row.prop(op, "filepath_2")

        layer_1 = size_1 is not None
        layer_2 = size_2 is not None

        # -------------------- SETTINGS -----------------------
        _draw_default(op, column, icon_dict, pcoll, False, layer_1, layer_2)
        
        # -------------------- WARNING ------------------------
        wrong_format = (file_ending_1.lower() != "png" and file_ending_1 != "") \
                    or (file_ending_2.lower() != "png" and file_ending_2 != "")

        if not correct_size_1 or not correct_size_2 or wrong_format:
            UI_Utils.spacer(op.layout, 0.3)
            box = op.layout.box()
            box.alignment = "CENTER"
            box.alert = True
            box.label(text="Wrong format or texture size.", icon="WARNING_LARGE")


def _draw_default(op, column, icon_dict, pcoll, is_default=True, layer_1=True, layer_2=True):
    UI_Utils.spacer(column, 0.3)

    # Naming text info
    row = column.row()
    split = row.split(factor=0.4)
    split.column().label(text="armor part")

    if is_default:
        split = split.split(factor=0.4)
        split.column().label(text="material")
    
    col = split.column()
    col.enabled = op.loaded
    col.label(text="trim")

    row.label(text = "", icon="BLANK1") # enchantment column

    for part in ArmorPartEnum:
        element = part.value

        row = column.row()
        if part in {ArmorPartEnum.HELMET, ArmorPartEnum.CHESTPLATE}:
            row.enabled = layer_1
        else:
            row.enabled = layer_2

        split = row.split(factor = 0.4)

        # Armor part toggle + icon
        col = split.column()
        type_row = col.row()
        type_row.label(text="", icon_value=icon_dict.get(part))
        type_row.prop(op, element)

        if not getattr(op, element, False):
            continue

        if is_default:
            # Alternative tetures
            alt_texture = type_row.split()
            alt_texture.enabled = op.loaded
            alt_texture.prop(
                op,
                f"{element}_alt_texture",
                icon="UV_SYNC_SELECT",
                text=""
            )

            # Material
            split = split.split(factor = 0.4)
            col = split.column()
            material_row = col.row(align = True)
            material_row.prop(op, f"{element}_material")

            # Leather armor color
            if getattr(op, f"{element}_material") == MaterialEnum.LEATHER.value:
                material_row.scale_x = 0.4
                material_row.prop(op, element + "_leather_colour")

        # Trims
        col = split.column()
        trim_row = col.row(align = True)
        trim_row.enabled = op.loaded

        trim_type = trim_row.split(align = True)
        trim_type.prop(op, f"{element}_trim")

        trim_value = getattr(op, f"{element}_trim")
        trim_colour = trim_row.split(align = True)
        trim_colour.enabled = (trim_value != TrimEnum.NONE.value)
        trim_colour.scale_x = 0.4
        trim_colour.prop(op, element + "_trim_colour")
        
        trim_enchantment = trim_colour.split(align=True)
        trim_enchantment.scale_x = 0.4
        trim_enchantment.enabled = (trim_value != TrimEnum.NONE.value)
        icon = "OUTLINER_OB_LIGHT" if getattr(op, f"{element}_trim_emission") else "OUTLINER_DATA_LIGHT"
        trim_enchantment.prop(op, element + "_trim_emission", icon=icon, text="")

        # Enchantment
        enchantment_row = row.split().row()
        enchantment_row.enabled = op.loaded
        enchanted_book = pcoll.get("enchanted_book", False)
        icon_value = enchanted_book.icon_id if enchanted_book else 0
        enchantment_row.prop(
            op,
            f"{element}_enchantment",
            icon_value = icon_value,
            icon="EVENT_E" if "enchanted_book" not in pcoll else 'NONE',
                text="",
                toggle=True
            )