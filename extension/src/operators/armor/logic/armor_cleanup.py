from ..logic.armor_enums import ShaderNodeEnum


class ArmorCleanup:
    def __init__(self, op):
        self.op = op
        self.rig = op.rig

    def remove_alpha_faces(self, armor_obj, has_trim: bool = False):
        import bmesh
        # Get the object and its mesh data
        mesh = armor_obj.data

        # Create a BMesh from the mesh data
        bm = bmesh.new()
        bm.from_mesh(mesh)

        # Get the UV layer
        uv_layer = bm.loops.layers.uv.verify()

        # Get the image
        nodes = armor_obj.data.materials[0].node_tree.nodes
        base = nodes[str(ShaderNodeEnum.BASE)].image
        trim_node = nodes.get(str(ShaderNodeEnum.TRIM))
        if trim_node:
            trim_img = trim_node.image

        # Calculate the width and height
        width, height = base.size

        def get_pixel_alpha(image, uv):
            pixel_index = 4 * (
                int(uv[1] * height) * width
                + int(uv[0] * width)
            )
            return image.pixels[pixel_index + 3]

        # Loop through the faces of the BMesh
        for face in bm.faces:
            for loop in face.loops:
                uv_data = loop[uv_layer].uv
                alpha = get_pixel_alpha(base, uv_data)

                if has_trim:
                    uv_data_trim = loop[uv_layer].uv
                    alpha_trim = get_pixel_alpha(trim_img, uv_data_trim)
                    if alpha == 0 and alpha_trim == 0:
                        bmesh.ops.delete(bm, geom=[face], context='FACES')
                        break
                else:
                    if alpha == 0:
                        bmesh.ops.delete(bm, geom=[face], context='FACES')
                        break

        # Update the mesh data with the new BMesh data
        bm.to_mesh(mesh)
        bm.free()