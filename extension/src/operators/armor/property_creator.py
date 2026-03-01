from bpy.props import EnumProperty, FloatVectorProperty, BoolProperty
from .logic.armor_enums import TrimEnum, MaterialEnum, ArmorTypeEnum
from ... import utils

# Custom type alias
from typing import Any
EnumPropertyType = Any
ColourPropertyType = Any
BooleanPropertyType = Any


class PropertyCreator:
    @staticmethod
    def armor_type() -> EnumPropertyType:
        values = ArmorTypeEnum.values()
        entry_list = [utils.create_item(value) for value in values]
        return EnumProperty(
            default = ArmorTypeEnum.DEFAULT.value,
            items = entry_list
        )

    @staticmethod
    def material(helmet: bool = False) -> EnumPropertyType:
        values = MaterialEnum.values()

        if not helmet:
            values.remove(MaterialEnum.TURTLE.value)

        entry_list = [utils.create_item(value) for value in values]

        return EnumProperty(
            name="",
            default=MaterialEnum.DIAMOND.value,
            items=entry_list
        )

    @staticmethod
    def trim_type() -> EnumPropertyType:
        values = TrimEnum.values()
        entry_list = [utils.create_item(value) for value in values]
        return EnumProperty(
            name="",
            default=TrimEnum.NONE.value,
            items=entry_list
        )

    @staticmethod
    def colour(mat: MaterialEnum = None) -> ColourPropertyType:
        colour = (1, 1, 1, 1)
        if mat == MaterialEnum.LEATHER:
            colour = (0.132891, 0.072269, 0.033102, 1)

        return FloatVectorProperty(
            name="",
            subtype="COLOR",
            size=4,
            default=colour,
            max=1,
            min=0
        )
    
    @staticmethod
    def boolean() -> BooleanPropertyType:
        return BoolProperty()