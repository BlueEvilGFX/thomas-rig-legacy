import os
import bpy
from bpy.types import PropertyGroup
from bpy.props import PointerProperty, BoolProperty, EnumProperty, FloatProperty
from bpy.types import WindowManager

from . import constants

preview_collections = {}

bpy.types.Object.ui_tab = bpy.props.EnumProperty(
    items = [
        ("DESIGN", "Design", 'Design'),
        ("MATERIALS", "Material", 'Material'),
        ("POSING", "Posing", 'Posing')
    ]
) # type: ignore

class SceneProperty(PropertyGroup):
    def update_reference(self, context):
        if context.scene.thomas_rig_legacy.reference == None:
            return
        if context.scene.thomas_rig_legacy.reference.get("Rig_ID") != constants.RIG_ID:
            context.scene.thomas_rig_legacy.reference = None

    def update_reference_toggle(self, context):
        # add / remove based on the state
        if context.scene.thomas_rig_legacy.reference_toggle:
            # only add if not already added
            if thomas_rig_reference_handler not in bpy.app.handlers.depsgraph_update_post:
                bpy.app.handlers.depsgraph_update_post.append(thomas_rig_reference_handler)
        # remove if not already removed
        elif thomas_rig_reference_handler in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.remove(thomas_rig_reference_handler)

    reference : PointerProperty(type=bpy.types.Object, update = update_reference) # type: ignore
    reference_toggle : BoolProperty(default=True, update=update_reference_toggle) # type: ignore

    progress_bar : FloatProperty(min=0.0, max=1.0) # type: ignore


class PreviewsProperty(PropertyGroup):
    def callback_base(self, context, directory, entry):
        enum_items = []

        if context is None:
            return enum_items
        
        pcoll = preview_collections['thomas_rig_legacy']
        
        if directory and os.path.exists(directory):
            image_paths = [fn for fn in os.listdir(directory) if fn.lower().endswith('.png')]

            for i, name in enumerate(image_paths):
                filepath = os.path.join(directory, name)

                thumb = pcoll.get(name)
                if not thumb:
                    thumb = pcoll.load(name, filepath, 'IMAGE')
                    
                enum_items.append((name, name, '', thumb.icon_id, i))

        setattr(pcoll, entry, enum_items)
        return enum_items
    
    def callback_custom_armor(self, context):
        return self.callback_base(context, constants.ARMOR_PATH_PREVIEWS, "custom_armor")

    def callback_misc(self, context):
        return self.callback_base(context, constants.MISC_PATH_PREVIEWS, "misc")

    custom_armor : EnumProperty(items = callback_custom_armor) # type: ignore
    misc : EnumProperty(items=callback_misc) # type: ignore

def thomas_rig_reference_handler(scene):
    scn_prop = scene.thomas_rig_legacy

    # Check if an object is selected
    if bpy.context.active_object is None:
        if scn_prop.reference is not None and scn_prop.reference.users < 2:
            scn_prop.reference = None
        return

    # Check for rig
    if (bpy.context.active_object is not None and 
        bpy.context.active_object.get('Rig_ID') == constants.RIG_ID):
        scn_prop.reference = bpy.context.active_object

def register():
    bpy.utils.register_class(SceneProperty)
    bpy.utils.register_class(PreviewsProperty)

    bpy.types.Scene.thomas_rig_legacy = PointerProperty(type=SceneProperty)
    WindowManager.thomas_rig_legacy = PointerProperty(type=PreviewsProperty)

    pcoll = bpy.utils.previews.new()
    pcoll.custom_armor = ()
    preview_collections['thomas_rig_legacy'] = pcoll

    try:
        bpy.app.handlers.depsgraph_update_post.append(thomas_rig_reference_handler)
    except Exception as e:
        print(">>>>", e)
    # bpy.context.scene.thomas_rig_legacy.reference_toggle = True

def unregister():
    if thomas_rig_reference_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(thomas_rig_reference_handler)

    del WindowManager.thomas_rig_legacy
    del bpy.types.Scene.thomas_rig_legacy

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    bpy.utils.unregister_class(PreviewsProperty)
    bpy.utils.unregister_class(SceneProperty)