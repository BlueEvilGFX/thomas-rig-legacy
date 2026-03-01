import bpy

from .src import preferences
from .src import icons
from .src import properties
from .src import operators
from .src import append_ui
from .src import ui

modules = (
    "preferences",
    "icons",
    "properties",
    "operators",
    "append_ui",
    "ui",
)

register, unregister = bpy.utils.register_submodule_factory(
    module_name =  __name__,
    submodule_names = modules
)