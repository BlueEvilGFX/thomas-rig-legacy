import bpy
from bpy.props import StringProperty

from ..utils import get_rig, is_packed, safe_unpack


class THOMAS_RIG_IMG_PACK(bpy.types.Operator):
    bl_idname = "thomasriglegacy.imgpack"
    bl_label = ""
    bl_description = "Pack/Unpack the skin texture"

    id_name: StringProperty() # type: ignore

    @classmethod
    def poll(cls, context):
        rig = get_rig()
        return rig is not None

    def execute(self, context):
        img = bpy.data.images[self.id_name]
        if is_packed(img):
            safe_unpack(img)
        else:
            img.pack()
        return {'FINISHED'}
    

class THOMAS_RIG_IMAGERELOAD(bpy.types.Operator):
    bl_idname = "thomasriglegacy.imgreload"
    bl_label = ""
    bl_description = "reload the skin texture"

    id_name: StringProperty() # type: ignore

    @classmethod
    def poll(cls, context):
        rig = get_rig()
        return rig is not None

    def execute(self, context):
        img = bpy.data.images[self.id_name]
        img.reload()
        return {'FINISHED'}