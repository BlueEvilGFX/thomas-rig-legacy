import os
import re
import zipfile
import bpy
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import platform

from bpy_extras.io_utils import ImportHelper

from ... import icons
from ... import constants
from ... import constants
from .errors import Errors

from ...constants import MIN_VERSION


def parse_version(v: str):
    return tuple(int(x) for x in v.split('.')) 


@dataclass
class LauncherPaths:
    mojang: list[Path]
    prism: list[Path]
    curseforge: list[Path]
    modrinth: list[Path]


class Launchers(Enum):
    MOJANG = "Mojang"
    PRISM = "Prism"
    CURSEFORGE = "CurseForge"
    MODRINTH = "Modrinth"


class MC_TEXTURES_LOAD_OT_SET(bpy.types.Operator):
    bl_idname = "thomasriglegacy.mc_textures_import"
    bl_label = "load mc textures"
    bl_description = ""

    error: Errors = None
    jar_path: str = None

    _timer = None
    _step = 0
    _version = -1
    _launcher = None
    _preferences = None

    def execute(self, context):
        self._preferences = context.preferences.addons[constants.PACKAGE].preferences
        self._preferences.mc_textures_ignore = True
        
        # Reset progress
        context.scene.thomas_rig_legacy.progress_bar = 0
        self._step = 0
        
        # Start modal timer
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)

        # Loading Steps
        self.steps = [
            self.get_jar_path_step,
            self.extract_from_zip_step,
            self.reload_icons_step,
            self.finish_step
        ]

        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        if event.type == 'TIMER':
            # Finished?
            if self._step >= len(self.steps):
                context.window_manager.event_timer_remove(self._timer)
                context.scene.thomas_rig_legacy.progress_bar = 0 # reset timer
                self.report({"INFO"}, str(self._version) + " MC textures loaded successfully with " + self._launcher.value)
                self._preferences.mc_textures_ignore = False

                return {'FINISHED'}

            # Run next step
            # every error should be cought in the steps and saved to self.error
            self.steps[self._step](context)
            if self.error:
                self._preferences.mc_textures_ignore = True
                self.report({'WARNING'}, self.error.error_text())
                bpy.ops.wm.save_userpref()
                context.scene.thomas_rig_legacy.progress_bar = 0
                return {'CANCELLED'}

            # Update progress
            context.scene.thomas_rig_legacy.progress_bar = (self._step + 1) / len(self.steps)
            self._step += 1

            # Redraw UI
            for area in context.screen.areas:
                area.tag_redraw()

        return {'RUNNING_MODAL'}

    # --- Steps ---
    def get_jar_path_step(self, context):
        self._launcher = self.get_jar_path()

    def extract_from_zip_step(self, context):
        try:
            self.extract_from_zip()
        except FileNotFoundError:
            self.error = Errors.VERSION_FILE_NOT_FOUND

    def reload_icons_step(self, context):
        icons.IconReader.reload_icons()

    def finish_step(self, context):
        preferences = context.preferences.addons[constants.PACKAGE].preferences
        preferences.mc_textures_loaded = True
        self._version = os.path.splitext(os.path.basename(self.jar_path))[0]
        bpy.ops.wm.save_userpref()

    # --- calls / logic ---    
    def get_jar_path(self) -> bool | Launchers:
        launchers = self.get_launcher_paths()
        if not launchers: 
            return False

        _error = None
        for launcher, paths in launchers.items():   # installed launchers
            for path in paths:                      # launcher installations
                versions = os.listdir(path)

                if len(versions) == 0:
                    _error = Errors.NO_VERSION_INSTALLED
                    continue
                
                # filter out snapshots and mods
                versions = [version for version in versions if not re.search('[a-zA-Z]', version)]
                # sort versions
                versions = sorted(versions, key=parse_version)
                for version in reversed(versions):
                    # check min version
                    int_version = [int(v) for v in version.split('.')]

                    if len(int_version) < 3:
                        int_version.append(0)

                    #not sufficient mc version
                    if tuple(int_version) < tuple(MIN_VERSION):
                        _error = Errors.MIN_VERSION_EXCEEDED
                        continue

                    # check if version.jar exists
                    # filename is <version>.jar for original launcher
                    # different for other launchers
                    # only one jar file though
                    version_dir = os.path.join(path, version)
                    for file in os.listdir(version_dir):
                        if '.jar' in file:
                            self.jar_path = os.path.join(version_dir, file)
                            # found correct version
                            return launcher
        self.error = _error
        return False
    
    def get_launcher_paths(self) -> dict[Launchers, list[str]]:
        """Returns a list of paths of the launchers version directory"""
        launcher_paths: LauncherPaths = PathProvider().get_paths()

        launcher_map = {
            Launchers.MOJANG: launcher_paths.mojang,
            Launchers.PRISM: launcher_paths.prism,
            Launchers.CURSEFORGE: launcher_paths.curseforge,
            Launchers.PRISM: launcher_paths.modrinth
        }

        # Keep only existing directories
        existing = {}
        for launcher, path_list in launcher_map.items():
            valid_paths = [p for p in path_list if p and os.path.isdir(p)]

            if valid_paths:
                existing[launcher] = valid_paths

        # Error Handling
        if not existing:
            self.error = Errors.MC_NOT_FOUND
            return {}
        
        return existing

    def extract_from_zip(self) -> bool:
        texture_path = bpy.utils.extension_path_user(package = constants.PACKAGE, path = "textures", create=True)
        textures, extracted_textures = extract_from_zip(texture_path, self.jar_path)

        if not textures == extracted_textures:
            self.error = Errors.NOT_ALL_TEXTURES
            return False
        
        return True
    

class PathProvider:
    def __init__(self):
        self.home = Path(os.path.expanduser('~'))
        self.appdata = Path(os.getenv('APPDATA', self.home))

    def get_paths(self) -> LauncherPaths:
        # Map the system names to your internal methods
        systems = {
            'Windows': self._build_windows,
            'Darwin':  self._build_darwin,
            'Linux':   self._build_linux
        }
        
        # Get the current OS
        current = platform.system()

        return systems[current]()

        
    def _build_windows(self) -> LauncherPaths:
        return LauncherPaths(
            mojang      = [self.appdata / ".minecraft/versions"],
            prism       = [self.appdata / "PrismLauncher/libraries/com/mojang/minecraft/Install/versions"],
            curseforge  = [self.home / "curseforge/minecraft/Install/versions"],
            modrinth    = [self.appdata / "modrinth-app/minecraft/versions"]
        )
    
    def _build_darwin(self) -> LauncherPaths:
        support = self.home / "Library/Application Support"
        return LauncherPaths(
            mojang      = [support / "minecraft/versions"],
            prism       = [support / "PrismLauncher/libraries/com/mojang/minecraft"],
            curseforge  = [self.home / "Documents/Curseforge/Minecraft/Install/versions"],
            modrinth    = [support / "modrinth-app/minecraft/versions"]
        )
    
    def _build_linux(self) -> LauncherPaths:
        local_share = self.home / ".local/share"
        flatpak_bin = self.home / ".var/app"

        return LauncherPaths(
            mojang = [self.home / ".minecraft/versions"],
            prism = [
                local_share / "PrismLauncher/libraries/com/mojang/minecraft",
                flatpak_bin / "org.prismlauncher.PrismLauncher/data/PrismLauncher/libraries/com/mojang/minecraft"
            ],
            curseforge = [
                self.home / "Documents/curseforge/Minecraft/Install/versions",
                flatpak_bin / "org.overwolf.CurseForge/data/curseforge/minecraft/versions"
            ],
            modrinth = [
                local_share / "PrismLauncher/libraries/com/mojang/minecraft",
                flatpak_bin / "app.modrinth.ModrinthApp/data/modrinth-app/minecraft/versions"
            ]
        )


class MC_TEXTURES_IMPORT_OT_SET(bpy.types.Operator, ImportHelper):
    bl_idname = "thomasriglegacy.mc_textures_import_manually" 
    bl_label = "import mc textures"

    filter_glob : bpy.props.StringProperty(
        default = "*.zip;*.rar;*.jar",
        options = {"HIDDEN"}
        ) # type: ignore

    def execute(self, context):
        filepath = self.filepath

        if os.path.isdir(filepath):
            self.report({"WARNING"}, Errors.WRONG_FILE_FORMAT.error_text())
            return {'CANCELLED'}

        preferences = context.preferences.addons[constants.PACKAGE].preferences

        texture_path = bpy.utils.extension_path_user(package = constants.PACKAGE, path = "textures", create=True)
        textures, extracted_textures = extract_from_zip(texture_path, filepath)

        if not textures == extracted_textures:
            self.error = Errors.NOT_ALL_TEXTURES
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
    # version = os.path.splitext(os.path.basename(jar_path))[0]

    # 1.21.11
    textures = {
        trims_zip_dir : {
            "textures/trims/entity/humanoid/",
            "textures/trims/entity/humanoid_leggings/"
            },
        armor_dir : {
            "textures/entity/equipment/humanoid/",
            "textures/entity/equipment/humanoid_leggings/",
            "textures/misc/enchanted_glint_armor.png"
            },
        icon_dir : {
            "textures/item/iron_chestplate.png",
            "textures/item/elytra.png",
            "textures/item/glow_item_frame.png",
            "enchanted_book.png"
            },
        texture_path : {
            "textures/entity/equipment/wings/elytra.png"
            }
    }

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
                    # armor layer handling
                    elif ("_leggings" in file or "equipment/humanoid" in file):
                        target_name = os.path.splitext(os.path.basename(file))[0] + ('_layer_2.png' if '_leggings' in file else '_layer_1.png')
                    # filter the leather overlay
                    elif "overlay" in file:
                        if "1" in file: # layer 1
                            target_name = "leather_overlay_layer_1.png"
                        else: # layer 2
                            target_name = "leather_overlay_layer_2.png"
                    # default case
                    else:
                        target_name = os.path.basename(file)

                    target_path = os.path.join(dir, target_name)  # output path

                    # Create target dummy file
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with open(target_path, "wb") as f:
                        f.write(archive.read(file))  # Write file to target

                    # Extracted textures (optimized with `.setdefault()`)
                    extracted_textures.setdefault(dir, set()).add(matched_texture)
                    break  # Stop after first match
    
    return textures, extracted_textures
