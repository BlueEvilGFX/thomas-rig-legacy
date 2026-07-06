import os
import bpy
import bpy.utils.previews
from bpy.app.handlers import persistent

from . import constants
from . import utils


class IconsMeta(type):
    def __getattr__(cls, name: str) -> int:
        # cls is the class 'Icons'
        pcoll = cls.get_pcoll()
        return pcoll[name].icon_id if name in pcoll else False

class Icons(metaclass=IconsMeta):
    """
    Class for icon access via IconSet.<icon_name>.
    """
    automatic: int
    cape: int
    helmet_iron: int
    chestplate_iron: int
    leggings_iron: int
    boots_iron: int
    Thomas_Rig_Legacy: int
    
    _pcoll = None

    @classmethod
    def get_pcoll(cls):
        if cls._pcoll is None:
            cls._pcoll = bpy.utils.previews.new()
        return cls._pcoll
    

class IconReader:
    @staticmethod
    def load_icons() -> None:
        pcoll = Icons.get_pcoll()

        # base thomas legacy icons
        for icon in os.listdir(constants.ADDON_PATH_ICONS):
            path = os.path.join(constants.ADDON_PATH_ICONS, icon)
            clean_name = os.path.splitext(icon)[0].replace(" ", "_")
            pcoll.load(clean_name, path, "IMAGE")

        # rig thomas legacy icons
        for icon in os.listdir(constants.RIGS_PATH_ICONS):
            path = os.path.join(constants.RIGS_PATH_ICONS, icon)
            clean_name = os.path.splitext(icon)[0].replace(" ", "_")
            pcoll.load(clean_name, path, "IMAGE")

        # loaded mc icons
        preferences = utils.get_extension_preferences()
        loaded = preferences.mc_textures_loaded
        if loaded:
            texture_path = bpy.utils.extension_path_user(package = constants.PACKAGE, path = "textures")
            dir = os.path.join(texture_path, "icons")
            for icon in os.listdir(dir):
                path = os.path.join(dir, icon)
                clean_name = os.path.splitext(icon)[0].replace(" ", "_")
                pcoll.load(clean_name, path, "IMAGE")

    @staticmethod
    def reload_icons() -> None:
        if Icons._pcoll is not None:
            bpy.utils.previews.remove(Icons._pcoll)
            Icons._pcoll = None
        IconReader.load_icons()


@persistent
def load_icons_handler(dummy):
    IconReader.reload_icons()

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                   (un)register
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━s

def register():
    IconReader.load_icons()
    bpy.app.handlers.load_post.append(load_icons_handler)

def unregister():
    if load_icons_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_icons_handler)

    if Icons._pcoll is not None:
        bpy.utils.previews.remove(Icons._pcoll)
        Icons._pcoll = None