import bpy
import os
import math

from .. import utils
from .. import constants


class THOMAS_RIG_LEGACY_APPEND_MISC(bpy.types.Operator):
    bl_options = {'REGISTER', 'UNDO'}
    bl_idname = "thomasriglegacy.appendmisc"
    bl_label = "append misc"

    def execute(self, context):
        # get misc name wihtout extension
        self.misc = os.path.splitext(context.window_manager.thomas_rig_legacy.misc)[0]
        self.rig = utils.get_rig()
        # append misc
        self.add()
        return {'FINISHED'}

    def add(self) -> None:
        # set rest position
        self.rig.data.pose_position = 'REST'

        if self.misc in {"blush", "blush_1", "blood_splatter"}:
            img_path = os.path.join(constants.MISC_PATH_TEXTURES, self.misc + ".png")

            if "blush" in self.misc: # if a blush, use following settings
                location = (0, -0.401, 2.64)
                rotation = (math.radians(90), 0, 0)
                ratio = 2/3
            else: # bloodsplatter
                location = (-0.235, -0.401, 2.62)
                rotation = (math.radians(90), math.radians(-90), 0)
                ratio =  1/5
            
            # append, add modifier and parent
            asset = self.add_image_as_plane(img_path, location, rotation, ratio)
            utils.add_modifier_subdivision(asset, 2, 3)
            self.parent_to_head(asset)
        
        elif self.misc in {"eye_lashes_1", "eye_lashes_2", "eye_lashes_3"}:
            eye_lashes_file = os.path.join(constants.MISC_PATH , "eye_lashes.blend")

            # append
            directory = os.path.join(eye_lashes_file, "Object")
            filepath = os.path.join(directory, self.misc)
            bpy.ops.wm.append(
                filepath=filepath,
                filename=self.misc,
                directory=directory,
                link=False,
                active_collection=True
            )

            eye_lash_R = bpy.context.selected_objects[0]
            eye_lash_R.location = (-0.231, -0.4, 2.76756)

            # duplicating & mirror
            bpy.context.view_layer.objects.active = eye_lash_R
            eye_lash_R.select_set(True)
            bpy.ops.object.duplicate(linked=0,mode='TRANSLATION')
            eye_lash_L = bpy.context.active_object
            bpy.ops.transform.mirror(orient_type="LOCAL", constraint_axis=(True, False, False))

            # lattice eyelash
            mat_obj = utils.get_mat_object(self.rig)
            lattice =mat_obj.modifiers["Lattice_R.Eyebrow"].object
            eye_lash_R.modifiers.new(name = "eyelash", type = "LATTICE")
            eye_lash_R.modifiers["eyelash"].object = lattice

            lattice = mat_obj.modifiers["Lattice_L.Eyebrow"].object
            eye_lash_L.modifiers.new(name = "eyelash", type = "LATTICE")
            eye_lash_L.modifiers["eyelash"].object = lattice

            # smart deform
            utils.add_modifier_lattice_smart_deform(self.rig, eye_lash_R)
            utils.add_modifier_lattice_smart_deform(self.rig, eye_lash_L)

            # squash stretch
            utils.add_modifier_lattice_head(self.rig, eye_lash_R)
            utils.add_modifier_lattice_head(self.rig, eye_lash_L)

            # driver
            if "1" in self.misc:
                self.eye_lash_driver(eye_lash_R, "iUI_Blink.r")
                self.eye_lash_driver(eye_lash_L, "iUI_Blink.L")
            eye_lash_L.location[0] = 0.223813

        # select only the rig
        bpy.ops.object.select_all (action='DESELECT')
        self.rig.select_set(True)
        bpy.context.view_layer.objects.active = self.rig
        bpy.context.view_layer.update()
        self.rig.location = self.rig.location

        # set rest position
        self.rig.data.pose_position = 'POSE'

    def eye_lash_driver(self, item, bone) -> None:
        driver = item.data.shape_keys.key_blocks["UP"].driver_add("value").driver
        driver.type = "SCRIPTED"

        var = driver.variables.new()
        var.type = "TRANSFORMS"
        var.name = "location"

        driver.variables[0].targets[0].id = self.rig
        driver.variables[0].targets[0].bone_target = bone
        driver.variables[0].targets[0].transform_type = "LOC_Y"
        driver.variables[0].targets[0].transform_space = "LOCAL_SPACE"
        driver.expression = "-location / 0.0525"

    def add_image_as_plane(self, img_path, location=(0,0,0), rotation=(0,0,0), ratio=1) -> bpy.types.Object:
        img = bpy.data.images.load(img_path)

        bpy.ops.mesh.primitive_plane_add(
            size=1,
            location=location,
            rotation=rotation
        )
        plane = bpy.context.object
        plane.name = self.misc
        plane.scale.x = img.size[0] / max(img.size) * ratio
        plane.scale.y = img.size[1] / max(img.size) * ratio

        # create material
        material = bpy.data.materials.new(name=self.misc)
        material.use_nodes = True
        material.blend_method = "BLEND"
        plane.data.materials.append(material)

        nodes = material.node_tree.nodes

        img_node = nodes.new("ShaderNodeTexImage")
        img_node.location = (-400, 300)
        img_node.interpolation = "Closest"
        img_node.image = img

        links = material.node_tree.links
        links.new(img_node.outputs['Color'], nodes['Principled BSDF'].inputs['Base Color'])
        links.new(img_node.outputs['Alpha'], nodes['Principled BSDF'].inputs['Alpha'])
        return plane

    def parent_to_head(self, obj) -> None:
        child_of = obj.constraints.new(type="CHILD_OF")
        child_of.target = self.rig
        child_of.subtarget = "Head"

        utils.add_modifier_lattice_smart_deform(self.rig, obj)
        utils.add_modifier_lattice_head(self.rig, obj)