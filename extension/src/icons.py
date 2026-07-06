import os
import bpy
import bpy.utils.previews
from bpy.app.handlers import persistent

from . import constants
from . import utils


class IconReader:
    @staticmethod
    def load_icons(pcoll) -> None:
        # base thomas legacy icons
        for icon in os.listdir(constants.ADDON_PATH_ICONS):
            path = os.path.join(constants.ADDON_PATH_ICONS, icon)
            pcoll.load(os.path.splitext(icon)[0], path, "IMAGE")

        # rig thomas legacy icons
        for icon in os.listdir(constants.RIGS_PATH_ICONS):
            path = os.path.join(constants.RIGS_PATH_ICONS, icon)
            pcoll.load(os.path.splitext(icon)[0], path, "IMAGE") 

        # loaded mc icons
        preferences = utils.get_extension_preferences()
        loaded = preferences.mc_textures_loaded
        if loaded:
            texture_path = bpy.utils.extension_path_user(package = constants.PACKAGE, path = "textures")
            dir = os.path.join(texture_path, "icons")
            for icon in os.listdir(dir):
                path = os.path.join(dir, icon)
                pcoll.load(os.path.splitext(icon)[0], path, "IMAGE") 

    @staticmethod
    def reload_icons() -> None:
        # clears icons from pcoll
        for pcoll in thomas_icons.values():
            bpy.utils.previews.remove(pcoll)

        pcoll = bpy.utils.previews.new()

        IconReader.load_icons(pcoll)
        thomas_icons["thomas_legacy"] = pcoll


@persistent
def load_icons_handler(dummy):
    IconReader.reload_icons()

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#                   (un)register
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━s

thomas_icons = {}

def register():
    pcoll = bpy.utils.previews.new()
    IconReader.load_icons(pcoll)
    thomas_icons["thomas_legacy"] = pcoll
    bpy.app.handlers.load_post.append(load_icons_handler)

def unregister():
    bpy.app.handlers.load_post.remove(load_icons_handler)
    for pcoll in thomas_icons.values():
        bpy.utils.previews.remove(pcoll)
    thomas_icons.clear()