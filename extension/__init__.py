from .src import preferences, icons, properties, operators, append_ui, ui

# For the UI users can add custom UI scripts.
# Users must approve them first to be displayed.
# Using hashes to detect change in file etc.
# -> script hashes of user ui scripts
# APPROVED_SCRIPTS = set()

def register():
    preferences.register()
    icons.register()
    properties.register()
    operators.register()
    append_ui.register()
    ui.register()

def unregister():
    ui.unregister()
    append_ui.unregister()
    operators.unregister()
    properties.unregister()
    icons.unregister()
    preferences.unregister()
