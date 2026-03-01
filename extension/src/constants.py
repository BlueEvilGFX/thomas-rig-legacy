import os
from pathlib import Path

RIG_ID = 'Thomas_Rig_Legacy'

# info
INFO_TEXT = "To use the original Minecraft textures, you need to have a legal copy of Minecraft installed (min. ver. 1.21, no snapshot). If you do not own one, please proceed with the `skip` operator. The addon will use alternative textures in the meantime. You can still load the original textures later in the addon preferences once you have Minecraft installed."
INFO_TEXT_PREFERENCES = "To use the original Minecraft textures, you need to have a legal copy of Minecraft installed (min. ver. 1.21, no snapshot). If you do not own one, the addon will use alternative textures."
INFO_TEXT_PREFERENCES_IMPORT = "To manually import the textures, you need to have either the jar or zip file of the game version that contains the game files. This requires also a min. ver. of 1.21."

# main
PACKAGE = '.'.join(__package__.split('.')[:-1])
ADDON_PATH = Path(os.path.dirname(__file__)).parent
ASSETS_PATH = os.path.join(ADDON_PATH, "assets")
SRC_PATH = os.path.join(ADDON_PATH, "src")

# icons
ADDON_PATH_ICONS = os.path.join(ASSETS_PATH, "icons")

# rigs
RIGS_PATH = os.path.join(ASSETS_PATH, "rigs")
RIGS_PATH_ICONS = os.path.join(RIGS_PATH, "icons")

# misc
MISC_PATH = os.path.join(ASSETS_PATH, "misc")
MISC_PATH_PREVIEWS = os.path.join(MISC_PATH, "previews")
MISC_PATH_TEXTURES = os.path.join(MISC_PATH, "textures")

# armor
ARMOR_PATH = os.path.join(ASSETS_PATH, "armor")
ARMOR_PATH_PREVIEWS = os.path.join(ARMOR_PATH, "Custom_Armor_Previews")
ARMOR_PATH_TEXTURES = os.path.join(ARMOR_PATH, "textures")
ARMOR_PATH_VANILLA = os.path.join(ARMOR_PATH_TEXTURES, "vanilla")

# skin downloader
UUID_URL = r"https://api.mojang.com/users/profiles/minecraft/"
SKIN_URL = r"https://sessionserver.mojang.com/session/minecraft/profile/"

# extension version
EXT_VERSION = None # set and read by addon directly

# Minecraft Version
MIN_VERSION = [1, 21, 11]

# preferences
SECOND_LAYER_ALTERNATIVE_HEAD_POSITION_Z = 2.8

# values
DEFAULT_EMISSION_VALUE = 5