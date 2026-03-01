import os
import re
import zipfile
import PIL.Image
import PIL.ImageChops
import bpy
import PIL

from pkg_resources import parse_version
from enum import Enum, auto
from bpy_extras.io_utils import ImportHelper

from .. import icons
from .. import constants
from .. import constants

class Errors(Enum):
    MC_NOT_FOUND = auto()
    NO_VERSION_INSTALLED = auto()
    MIN_VERSION_EXCEEDED = auto()
    VERSION_FILE_NOT_FOUND = auto()
    NOT_ALL_TEXTURES = auto()
    ENCHANTED_BOOK = auto()


    def error_text(self):
        descriptions = {
            Errors.MC_NOT_FOUND: "Minecraft could not be found",
            Errors.NO_VERSION_INSTALLED: "No Minecraft version installed",
            Errors.MIN_VERSION_EXCEEDED: f'Minimum version requirement [{MC_TEXTURES_LOAD_OT_SET.MIN_VERSION}] not met',
            Errors.VERSION_FILE_NOT_FOUND: "MC Version.jar file not found",
            Errors.NOT_ALL_TEXTURES: "Not all needed textures found",
            Errors.ENCHANTED_BOOK: "Could not create enchanted book icon"  
        }
        return descriptions.get(self, "Unknown error.")


class MC_TEXTURES_LOAD_OT_SET(bpy.types.Operator):
    bl_idname = "thomasriglegacy.mc_textures_import"
    bl_label = "load mc textures"
    bl_description = ""

    MIN_VERSION = [1, 21]
    error = None
    jar_path = None

    def execute(self, context):
        preferences = context.preferences.addons[constants.PACKAGE].preferences

        status = self.get_jar_path()
        if status:
            try:
                self.extract_from_zip()
                if self.error:
                    preferences.mc_textures_ignore = True
                    self.report({"WARNING"}, self.error.error_text())
                    bpy.ops.wm.save_userpref()
                    return{'CANCELLED'}
            except FileNotFoundError:
                preferences.mc_textures_ignore = True
                self.error = Errors.VERSION_FILE_NOT_FOUND
                self.report({"WARNING"}, self.error.error_text())
                bpy.ops.wm.save_userpref()
                return{'CANCELLED'}
        else:
            preferences.mc_textures_ignore = True
            self.report({"WARNING"}, self.error.error_text())
            bpy.ops.wm.save_userpref()
            return{'CANCELLED'}
        
        # set addon preferences texture loaded property
        preferences.mc_textures_loaded = True
        bpy.ops.wm.save_userpref()

        # reload icons
        icons.IconReader.reload_icons()

        version = os.path.splitext(os.path.basename(self.jar_path))[0]
        self.report({"INFO"}, version + " MC textures loaded successfully")
        return{'FINISHED'}
    
    def get_jar_path(self) -> bool:
        # Minecraft jar files directory
        if os.name == 'nt':  # Windows
            minecraft_dir = os.path.join(os.getenv('APPDATA'), '.minecraft', 'versions')
        elif os.name == 'posix':  # macOS and Linux
            if 'darwin' in os.uname().sysname.lower():  # macOS
                minecraft_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'minecraft', 'versions')
            else:  # Linux
                minecraft_dir = os.path.join(os.path.expanduser('~'), '.minecraft', 'versions')

        if not os.path.exists(minecraft_dir): # MC not found
            self.error = Errors.MC_NOT_FOUND
            return False
        
        # get latest "normal" minecraft versions
        versions = os.listdir(minecraft_dir)
        if len(versions) == 0:
            self.error = Errors.NO_VERSION_INSTALLED
            return False
        
        # filter out snapshots and mods
        versions = [version for version in versions if not re.search('[a-zA-Z]', version)]
        # sort versions from low to high
        versions = sorted(versions, key=parse_version)
        for version in reversed(versions):
            # check min version
            int_version = [int(v) for v in version.split('.')]
            not_sufficient = int_version[0] < self.MIN_VERSION[0] or int_version[1] < self.MIN_VERSION[1]

            if not_sufficient:
                self.error = Errors.MIN_VERSION_EXCEEDED
                return False

            # check if version.jar exists
            file_name = version + '.jar'
            jar_path = os.path.join(minecraft_dir, version, file_name)
            if os.path.exists(jar_path):
                self.jar_path = jar_path
                return True
        return False

    def extract_from_zip(self) -> bool:
        texture_path = bpy.utils.extension_path_user(package = constants.PACKAGE, path = "textures", create=True)
        textures, extracted_textures, enchanted_book = extract_from_zip(texture_path, self.jar_path)

        if not textures == extracted_textures:
            self.error = Errors.NOT_ALL_TEXTURES
            return False
        
        if not enchanted_book:
            self.error = Errors.ENCHANTED_BOOK
            return False
        
        return True


class MC_TEXTURES_IMPORT_OT_SET(bpy.types.Operator, ImportHelper):
    bl_idname = "thomasriglegacy.mc_textures_import_manually" 
    bl_label = "import mc textures"

    filter_glob : bpy.props.StringProperty(
        default = "*.zip;*.rar;*.jar",
        options = {"HIDDEN"}
        ) # type: ignore

    def execute(self, context):
        filepath = self.filepath
        preferences = context.preferences.addons[constants.PACKAGE].preferences

        texture_path = bpy.utils.extension_path_user(package = constants.PACKAGE, path = "textures", create=True)
        textures, extracted_textures, enchanted_book = extract_from_zip(texture_path, filepath)

        if not textures == extracted_textures:
            self.error = Errors.NOT_ALL_TEXTURES
            preferences.mc_textures_ignore = True
            self.report({"WARNING"}, self.error.error_text())
            bpy.ops.wm.save_userpref()
            return{'CANCELLED'}
        
        if not enchanted_book:
            self.error = Errors.ENCHANTED_BOOK
            preferences.mc_textures_ignore = True
            self.report({"WARNING"}, self.error.error_text())
            bpy.ops.wm.save_userpref()
            return{'CANCELLED'}
        
        # set addon preferences texture loaded property
        preferences.mc_textures_loaded = True
        bpy.ops.wm.save_userpref()

        # reload icons
        icons.unregister()
        icons.register()
        version = os.path.splitext(os.path.basename(filepath))[0]
        icons.IconReader.reload_icons()
        self.report({"INFO"}, version + " MC textures loaded successfully")
        return{'FINISHED'}


class MC_TEXTURES_SKIP_OT_SET(bpy.types.Operator):
    bl_idname = "thomasriglegacy.mc_textures_skip"
    bl_label = "skip"
    bl_description = ""

    def execute(self, context):
        preferences = context.preferences.addons[constants.PACKAGE].preferences
        preferences.mc_textures_ignore = True
        bpy.ops.wm.save_userpref()
        icons.IconReader.reload_icons()
        return{'FINISHED'}


def extract_from_zip(texture_path, jar_path):
    trims_zip_dir = os.path.join(texture_path, "trims")
    armor_dir = os.path.join(texture_path, "armor")
    icon_dir = os.path.join(texture_path, "icons")
    version = os.path.splitext(os.path.basename(jar_path))[0]

    # 1.21 or 1.21.1
    if version in ['1.21', '1.21.1']:
        textures = {
            trims_zip_dir : {"textures/trims/models/armor/"},
            armor_dir : {"textures/models/armor/", "textures/misc/enchanted_glint_entity.png"},
            icon_dir : {"textures/item/iron_chestplate.png", "textures/item/elytra.png", "textures/item/glow_item_frame.png", "enchanted_book.png"},
            texture_path : {"entity/elytra.png", "textures/misc/enchanted_glint_item.png"}
        }
    else: # newer versions
        textures = {
            trims_zip_dir : {"textures/trims/entity/humanoid/", "textures/trims/entity/humanoid_leggings/"},
            armor_dir : {"textures/entity/equipment/humanoid/", "textures/entity/equipment/humanoid_leggings/", "textures/misc/enchanted_glint_entity.png"},
            icon_dir : {"textures/item/iron_chestplate.png", "textures/item/elytra.png", "textures/item/glow_item_frame.png", "enchanted_book.png"},
            texture_path : {"textures/entity/equipment/wings/elytra.png", "textures/misc/enchanted_glint_item.png"}
        }

    parsed_version = parse_version(version)
    parsed_compare_version = parse_version("1.21.5")

    if parsed_version >= parsed_compare_version:
        textures[armor_dir].remove("textures/misc/enchanted_glint_entity.png")
        textures[armor_dir].add("textures/misc/enchanted_glint_armor.png")

    extracted_textures = {}

    with zipfile.ZipFile(jar_path) as archive:
        for file in archive.namelist():
            if not file.endswith(".png"):
                continue  # Skip non-PNG files early
            
            for dir, values in textures.items():
                matched_texture = next((texture for texture in values if texture in file), None)
                if matched_texture:
                    # Determine target filename
                    if "turtle" in file:
                        target_name = "turtle_layer_1.png"
                    elif version not in ["1.21", "1.21.1"] and ("_leggings" in file or "equipment/humanoid" in file):
                        target_name = os.path.splitext(os.path.basename(file))[0] + ('_layer_2.png' if '_leggings' in file else '_layer_1.png')
                    elif "_leggings" in file:   
                        target_name = os.path.splitext(os.path.basename(file))[0][:-len("_leggings")] + "_layer_2.png"
                    # filter the leather overlay
                    elif "overlay" in file:
                        if "1" in file: # layer 1
                            target_name = "leather_overlay_layer_1.png"
                        else: # layer 2
                            target_name = "leather_overlay_layer_2.png"
                    else:
                        target_name = os.path.basename(file)

                    # Special handling for enchanted_glint_armor
                    if "enchanted_glint_armor.png" in file:
                        target_name = "enchanted_glint_entity.png"

                    target_path = os.path.join(dir, target_name)  # output path

                    # Create target dummy file
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with open(target_path, "wb") as f:
                        f.write(archive.read(file))  # Write file to target

                    # Extracted textures (optimized with `.setdefault()`)
                    extracted_textures.setdefault(dir, set()).add(matched_texture)
                    break  # Stop after first match

    # enchanted book -> overlay with enchanted texture
    try:
        book_path = os.path.join(bpy.utils.extension_path_user(package = constants.PACKAGE, path = "textures"),"icons" , "enchanted_book.png")
        book = PIL.Image.open(book_path).convert("RGBA")
        enchant_glint = PIL.Image.open(os.path.join(bpy.utils.extension_path_user(package = constants.PACKAGE, path = "textures"), "enchanted_glint_item.png")).convert("RGBA")

        enchant_glint = enchant_glint.resize(book.size, PIL.Image.Resampling.BILINEAR)

        # overlay using "add" and combine alpha channel
        added = PIL.ImageChops.add(book, enchant_glint)
        result = PIL.Image.new("RGBA", book.size)
        result.paste(added, mask=book.split()[3])

        result.save(book_path)
        enchanted_book = True
    except:
        enchanted_book = False
    
    return textures, extracted_textures, enchanted_book

def register():
    bpy.utils.register_class(MC_TEXTURES_LOAD_OT_SET)
    bpy.utils.register_class(MC_TEXTURES_IMPORT_OT_SET)
    bpy.utils.register_class(MC_TEXTURES_SKIP_OT_SET)

def unregister():
    bpy.utils.unregister_class(MC_TEXTURES_SKIP_OT_SET)
    bpy.utils.unregister_class(MC_TEXTURES_IMPORT_OT_SET)
    bpy.utils.unregister_class(MC_TEXTURES_LOAD_OT_SET)