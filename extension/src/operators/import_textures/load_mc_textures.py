import os
import zipfile
import bpy
import json

from bpy_extras.io_utils import ImportHelper
from ... import utils
from ... import icons
from ... import constants
from ... import constants
from .errors import Errors

from ...constants import MIN_VERSION


def parse_version(v: str):
    return tuple(int(x) for x in v.split('.')) 

class MC_TEXTURES_SKIP_OT_SET(bpy.types.Operator):
    bl_idname = "thomasriglegacy.mc_textures_skip"
    bl_label = "skip"
    bl_description = ""

    def execute(self, context):
        preferences = utils.get_extension_preferences()
        preferences.mc_textures_ignore = True
        bpy.ops.wm.save_userpref()
        icons.IconReader.reload_icons()
        return{'FINISHED'}
        
class MC_TEXTURES_IMPORT_OT_SET(bpy.types.Operator, ImportHelper):
    bl_idname = "thomasriglegacy.mc_textures_import_manually" 
    bl_label = "import textures"
    bl_description = "This will load the textures into the extensions storage. It can take a small amount of time to process it."

    filter_glob : bpy.props.StringProperty(
        default = "*.zip;*.rar;*.jar",
        options = {"HIDDEN"}
        ) # type: ignore
    
    loaded_version: bpy.props.IntVectorProperty(options={'HIDDEN'}) # type: ignore

    def execute(self, context):
        filepath = self.filepath

        if os.path.isdir(filepath):
            self.report({"WARNING"}, Errors.WRONG_FILE_FORMAT.error_text())
            return {'CANCELLED'}

        preferences = utils.get_extension_preferences()

        texture_path = bpy.utils.extension_path_user(package = constants.PACKAGE, path = "textures", create=True)
        extraction_map, extracted_textures, version = extract_from_zip(texture_path, filepath)

        if not verify_extraction_complete(extraction_map, extracted_textures):
            self.error = Errors.NOT_ALL_TEXTURES
            self.report({"WARNING"}, self.error.error_text())
            bpy.ops.wm.save_userpref()
            return{'CANCELLED'}
                
        # set addon preferences texture loaded property
        preferences.mc_textures_loaded = True
        preferences.loaded_version = version
        bpy.ops.wm.save_userpref()

        # reload iconsz
        icons.unregister()
        icons.register()
        icons.IconReader.reload_icons()
        self.report({"INFO"}, version + " MC textures loaded successfully")
        return{'FINISHED'}

def extract_from_zip(texture_path, jar_path):
    trims_zip_dir = os.path.join(texture_path, "trims")
    armor_dir = os.path.join(texture_path, "armor")
    icon_dir = os.path.join(texture_path, "icons")
    # version = os.path.splitext(os.path.basename(jar_path))[0]

    extraction_map = {
        "textures/trims/entity/humanoid/"                   : trims_zip_dir,
        "textures/trims/entity/humanoid_leggings/"          : trims_zip_dir,

        "textures/entity/equipment/humanoid/"               : armor_dir,
        "textures/entity/equipment/humanoid_leggings/"      : armor_dir,
        "textures/misc/enchanted_glint_armor.png"           : armor_dir,

        "textures/item/iron_chestplate.png"                 : icon_dir,
        "textures/item/elytra.png"                          : icon_dir,
        "textures/item/glow_item_frame.png"                 : icon_dir,
        "enchanted_book.png"                                : icon_dir,

        "textures/entity/equipment/wings/elytra.png"        : texture_path
    }

    extracted_textures = {}
    version = "None"

    with zipfile.ZipFile(jar_path, 'r') as archive:
        verbose = utils.get_extension_preferences().verbose


        # read version identifier
        if "version.json" in archive.namelist():
            try:
                with archive.open("version.json") as json_file:
                    json_data = json.loads(json_file.read().decode("utf-8"))
                    version = json_data.get("id", "-1.-1.-1")

            except Exception as e:
                if verbose:
                    print(f"Error reading version.json when importing textures. {e}")


        # extract textures
        for jar_file in archive.namelist():
            # Only look at PNGs
            if not jar_file.endswith(".png"):
                continue
            
            # Check for match
            for source_prefix, target_folder in extraction_map.items():
                if source_prefix in jar_file:
                    # 1. Determine file name
                    if "turtle" in jar_file:
                        target_name = "turtle_layer_1.png"
                    # armor layer handling
                    elif ("_leggings" in jar_file or "equipment/humanoid" in jar_file):
                        target_name = os.path.splitext(os.path.basename(jar_file))[0] + ('_layer_2.png' if '_leggings' in jar_file else '_layer_1.png')
                    # filter the leather overlay
                    elif "overlay" in jar_file:
                        if "1" in jar_file: # layer 1
                            target_name = "leather_overlay_layer_1.png"
                        else: # layer 2
                            target_name = "leather_overlay_layer_2.png"
                    # default case
                    else:
                        target_name = os.path.basename(jar_file)

                    # 2. Build target path
                    os.makedirs(target_folder, exist_ok=True)
                    dest_path = os.path.join(target_folder, target_name)

                    # 3. Extract
                    with archive.open(jar_file) as source, open(dest_path, "wb") as target:
                        target.write(source.read())

                    # Found a match -> no need to check other prefixes
                    extracted_textures.setdefault(source_prefix, []).append(target_name)
                    break

    return extraction_map, extracted_textures, version

def verify_extraction_complete(extraction_map, extracted_textures) -> bool:
    """
    Returns True if every rule in the extraction map was satisfied.
    Returns False if even one prefix/file failed to extract.
    """
    all_successful = True
    verbose = utils.get_extension_preferences().verbose

    if verbose:
        print("Verify File Extraction:")

    for source_prefix, target_folder in extraction_map.items():
        # Get the files that were saved to the folder associated with this prefix
        found_files = extracted_textures.get(source_prefix, [])

        # Logic: If it's a specific file (ends in .png), check for that specific name.
        # If it's a folder prefix, check if the folder got ANY files.
        if source_prefix.endswith(".png"):
            expected_name = os.path.basename(source_prefix)
            # We use 'any' because the file might have been renamed (e.g., _layer_1)
            # or just exists plainly in the list.
            match = any(expected_name in f or f == expected_name for f in found_files)
        else:
            # It's a folder prefix; we just need at least one file to have been found
            match = len(found_files) > 0

        if verbose:
            if not match:
                print(f"    ✖    Extraction Failed for: {source_prefix}")
                all_successful = False
            else:
                print(f"    ✔    Extraction Success for: {source_prefix}")

    if verbose:
        print("\n")

    return all_successful
