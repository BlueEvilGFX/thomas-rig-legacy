import bpy
import addon_utils

from . import constants

from typing import List, Optional, Tuple

def add_modifier_armature(rig, obj) -> bpy.types.Modifier:
    modifier = obj.modifiers.new(name = "Skeleton", type = "ARMATURE")
    modifier.object = rig
    return modifier

def add_modifier_lattice_chest_pose(rig, obj) -> bpy.types.Modifier:
    lattice = get_mat_object(rig).modifiers["Chest_Pose"].object
    modifier = obj.modifiers.new(name = "Chest_Pose", type = "LATTICE")
    modifier.object = lattice
    return modifier

def add_modifier_lattice_arm_pose_R(rig, obj) -> bpy.types.Modifier:
    lattice = get_mat_object(rig).modifiers["Arm_R"].object
    modifier = obj.modifiers.new(name = "Arm_R", type = "LATTICE")
    modifier.object = lattice
    return modifier

def add_modifier_lattice_arm_pose_L(rig, obj) -> bpy.types.Modifier:
    lattice = get_mat_object(rig).modifiers["Arm_L"].object
    modifier = obj.modifiers.new(name = "Arm_L", type = "LATTICE")
    modifier.object = lattice
    return modifier

def add_modifier_lattice_leg_pose_R(rig, obj) -> bpy.types.Modifier:
    lattice = get_mat_object(rig).modifiers["Leg_R"].object
    modifier = obj.modifiers.new(name = "Leg_R", type = "LATTICE")
    modifier.object = lattice
    return modifier

def add_modifier_lattice_leg_pose_L(rig, obj) -> bpy.types.Modifier:
    lattice = get_mat_object(rig).modifiers["Leg_L"].object
    modifier = obj.modifiers.new(name = "Leg_L", type = "LATTICE")
    modifier.object = lattice
    return modifier

def add_modifier_lattice_smart_deform(rig, obj) -> None:
    lattice = get_mat_object(rig).modifiers["Lattice_Smart_Deform"].object
    obj.modifiers.new(name = "deform", type = "LATTICE")
    obj.modifiers["deform"].object = lattice

def add_modifier_lattice_head(rig, obj) -> None:
    lattice = get_mat_object(rig).modifiers["Lattice_Head"].object
    obj.modifiers.new(name = "squash stretch", type = "LATTICE")   
    obj.modifiers["squash stretch"].object = lattice

def add_modifier_solidify(obj, thickness) -> None:
    obj.modifiers.new(name = "Solidify", type = "SOLIDIFY")
    obj.modifiers["Solidify"].thickness = thickness
    obj.modifiers["Solidify"].use_even_offset = True
    obj.modifiers["Solidify"].use_quality_normals = True

def add_modifier_subdivision(obj, viewport_level, render_level, sub_type="CATMULL_CLARK") -> None:
    obj.modifiers.new(name = "subdivision", type = "SUBSURF")
    obj.modifiers['subdivision'].levels = viewport_level
    obj.modifiers['subdivision'].render_levels = render_level
    obj.modifiers['subdivision'].subdivision_type = sub_type

def add_modifier_lattice_chest(rig, obj) -> None:
    lattice = get_mat_object(rig).modifiers["Chest"].object
    obj.modifiers.new(name = "Chest", type = "LATTICE")
    obj.modifiers["Chest"].object = lattice
    obj.modifiers["Chest"].vertex_group = "UpperBodyMain"

def create_item(key):
    return (key, key, "")

def get_rig():
    scn = bpy.context.scene
    try:
        if scn.thomas_rig_legacy.get('reference'):
            return scn.thomas_rig_legacy.reference
    except:
        return bpy.context.active_object
    return bpy.context.active_object

def get_mat_object(rig) -> bpy.types.Object:
    return rig.children[0]

def is_packed(img):
    try:
        return img.packed_files.values() != []
    except (AttributeError, KeyError, TypeError):
        return False

def safe_unpack(img): #unpacks relative to the file ONLY if the file is saved
    if img.packed_files:
        if bpy.data.is_saved:
            return img.unpack()
        else:
            return img.unpack(method='USE_ORIGINAL')
        

class UI_Utils:
    def spacer(layout, factor):
        spacer = layout.row()
        spacer.label(text="")
        spacer.scale_y = factor

    def check_search(display, prop_src, arm_filter=False) -> bool:
        search = get_rig().pose.bones["Misc_Properties"]["search"].lower()
        if arm_filter:
            arm_props = {"L.Arm_FK/IK", "R.Arm_FK/IK", "L.Arm_World", "R.Arm_World"}

            for prop in prop_src.keys():
                if prop in arm_props and search in prop.lower():
                    display.prop(prop_src, f'["{prop}"]', toggle = True)
            return

        for prop in prop_src.keys():
            if(search in prop.lower() and search != ""):
                display.prop(prop_src, f'["{prop}"]', toggle = True)


def get_ext_version() -> List[int]:
    # if already once loaded, return EXT_VERSION
    if constants.EXT_VERSION is not None:
        return constants.EXT_VERSION
    
    modules = addon_utils.modules()
    # iterate through all modules and get one with the rig name as the name
    result = next((ext for ext in modules if "Thomas Rig Legacy" == ext.bl_info['name']))
    version = result.bl_info['version']
    constants.EXT_VERSION = version
    return version

def get_image_size(filepath: str) -> Optional[Tuple[int, int]]:
    """returns the size of the image (width, height)"""
    import OpenImageIO as oiio
    
    inp = oiio.ImageInput.open(filepath)
    if inp:
        spec = inp.spec()
        xres = spec.width
        yres = spec.height
        inp.close()

        return [xres, yres]
    return None