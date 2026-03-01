from enum import Enum, auto

class BaseEnum(Enum):
    @classmethod
    def values(cls) -> list[str]:
        return [item.value for item in cls]
    

class TrimEnum(BaseEnum):
    NONE = "None"
    BOLT = "bolt"
    COAST = "coast"
    DUNE = "dune"
    EYE = "eye"
    FLOW = "flow"
    HOST = "host"
    RAISER = "raiser"
    RIB = "rib"
    SENTRY = "sentry"
    SHAPER = "shaper"
    SILENCE = "silence"
    SNOUT = "snout"
    SPIRE = "spire"
    TIDE = "tide"
    VEX = "vex"
    WARD = "ward"
    WAYFINDER = "wayfinder"
    WILD = "wild"


class MaterialEnum(BaseEnum):
    LEATHER = "leather"
    CHAINMAIL = "chainmail"
    IRON = "iron"
    GOLD = "gold"
    DIAMOND = "diamond"
    NETHERITE = "netherite"
    TURTLE = "turtle"
    

class ArmorTypeEnum(BaseEnum):
    """Default / Custom"""
    DEFAULT = "default"
    CUSTOM = "custom"


class ArmorPartEnum(BaseEnum):
    HELMET = "helmet"
    CHESTPLATE = "chestplate"
    LEGGINGS = "leggings"
    BOOTS = "boots"

class ShaderNodeEnum(Enum):
    """returns always the key lowercase and in string in str()"""
    BASE = "Base"
    BSDF = "Bsdf"
    OUTPUT = "Output"

    LEATHER_COLOUR = "Leather: Colour"
    LEATHER_RGB = "Leather: Colour"
    LEATHER_OVERLAY = "Leather: Overlay"
    LEATHER_OVERLAY_MIX = "Leather: Overlay"

    TRIM ="Trim"
    TRIM_COLOUR = "Trim: Colour"
    TRIM_MIX = "Trim: Colour"
    TRIM_ADD_ALPHA = "Trim: Add Alpha"
    TRIM_RGB = "Trim: Colour"

    ENCHANTMENT = "Enchantment"
    ENCHANTMENT_MIX = "Enchantment: Mix"
    ENCHANTMENT_HUE = "Enchantment: Hue/Sat/Value"
    ENCHANTMENT_MAP = "Enchantment: Mapping"
    ENCHANTMENT_MUL = "Enchantment: Multiply"
    ENCHANTMENT_DIV = "Enchantment: Divide"
    ENCHANTMENT_ADD = "Enchantment: Add"
    ENCHANTMENT_TCO = "Enchantment: Texture Coordinate"
    ENCHANTMENT_VALUE_SPEED = "Enchantment: Speed"
    ENCHANTMENT_VALUE_OFFSET = "Enchantment: Offset"

    def __str__(self):
        """returns the lower key"""
        return  self.name.lower()