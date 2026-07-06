from enum import Enum
import tomllib
import bpy

from .. import constants
from .. import utils


class UIType(Enum):
    BOX = "box"
    COLUMN = "column"
    ROW = "row"
    SPLIT = "split"

    LABEL = "label"
    PROP = "prop"

    @classmethod
    def from_str(cls, value: str):
        try:
            return cls(value)
        except ValueError:
            return None
        
def draw_toml(context, rig, layout, toml: str) -> dict:
    """
    Parses the toml file and then displays it
    """
    verbose = utils.get_extension_preferences().verbose
    try:
        data = tomllib.loads(toml)
    except Exception as e:
        if verbose:
            print(f"Error when parsing TOML file: {e}")
            layout.label(text="Error", icon="ERROR")
        return
        
    for element in data.get("layout", []):
        draw_element(context, rig, layout, element, verbose)

def draw_element(context, rig, layout, element: dict, verbose):
    user_props  = rig.pose.bones.get("User_Properties", None)
    el_type = UIType.from_str(element.get("type", ""))
    current_layout = layout

    # container types
    if el_type == UIType.BOX:
        current_layout = layout.box()

    elif el_type == UIType.COLUMN:
        align = element.get("align", False)
        current_layout = layout.column(align=align)

    elif el_type == UIType.ROW:
        align = element.get("align", False)
        current_layout = layout.row(align=align)

    elif el_type == UIType.SPLIT:
        align = element.get("align", False)
        factor = element.get("factor", 0.5)
        current_layout = layout.split(align=align, factor=factor)

    # display types
    elif el_type == UIType.LABEL:
        text = element.get("text", "")
        icon = element.get("icon", "NONE")
        current_layout.label(text=text, icon=icon)

    elif el_type == UIType.PROP:       
        # determine data source
        data_source = element.get("data")
        if data_source == "#user_props":
            data_source = user_props
        elif data_source == "context":
            data_source = context
        
        prop = element.get("property", "")
        is_context_source = (data_source == context)

        # split String and path
        if '[' in prop:
            # bone property '["prop"]'
            clean_prop_name = prop[2:-2]
            is_custom_prop = True
        else:
            # native property
            clean_prop_name = prop
            is_custom_prop = False

        # nested context paths
        if is_context_source and not is_custom_prop and "." in clean_prop_name:
            path_parts = clean_prop_name.split(".")
            parent_path = ".".join(path_parts[:-1])
            
            # if user forgot scene in TOML
            if not parent_path.startswith("scene") and hasattr(context.scene, parent_path.split(".")[0]):
                parent_path = f"scene.{parent_path}"

            final_prop = path_parts[-1]              # e.g. "engine"
            
            try:
                data_source = context.path_resolve(parent_path)
                prop = final_prop
                clean_prop_name = final_prop
            except (ValueError, AttributeError):
                data_source = None
        
        # exist check
        source_keys = []
        if data_source and hasattr(data_source, "keys"):
            try: source_keys = data_source.keys()
            except TypeError: source_keys = []

        if is_custom_prop:
            prop_exists = clean_prop_name in source_keys
        else:
            prop_exists = hasattr(data_source, clean_prop_name) if data_source else False

        # draw
        if data_source and prop_exists:
            kwargs = {}
            if "text" in element: kwargs["text"] = element["text"]
            if "icon" in element: kwargs["icon"] = element["icon"]
            if "expand" in element: kwargs["expand"] = element["expand"]
            if "slider" in element: kwargs["slider"] = element["slider"]
            if "toggle" in element: kwargs["toggle"] = element["toggle"]
            if "icon_only" in element: kwargs["icon_only"] = element["icon_only"]
            if "emboss" in element: kwargs["emboss"] = element["emboss"]
            if "invert_checkbox" in element: kwargs["invert_checkbox"] = element["invert_checkbox"]

            # final prop formatting
            if is_custom_prop:
                blender_path = f'["{clean_prop_name}"]'
            else:
                blender_path = clean_prop_name

            current_layout.prop(data_source, blender_path, **kwargs)
        else:
            current_layout.label(text=f"Missing Prop: {prop}", icon='ERROR')
            if verbose:
                print(f"Property '{prop}' not found on source '{data_source}'")

    # recursion
    if "children" in element:
        for child in element["children"]:
            draw_element(context, rig, current_layout, child, verbose)