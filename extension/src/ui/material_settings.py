from .. import utils

def draw(rig, layout, main_props):
    mat_obj = utils.get_mat_object(rig)

    box = layout.box()
    col = box.column()
            
    # skin
    try:
        img = mat_obj.material_slots[0].material.node_tree.nodes['Skin'].image

        left = col.row(align = True)  
        left.operator("thomasriglegacy.imgpack" , text="",
                    icon="PACKAGE" if utils.is_packed(img) else "UGLYPACKAGE"
            ).id_name = img.name 

        main = left.row(align=True) 
        main.enabled = not utils.is_packed(img)
        main.prop(img, "filepath", text="")  
        main.operator("thomasriglegacy.imgreload", text = "", icon = "FILE_REFRESH"
            ).id_name = img.name
        main.operator("thomasriglegacy.downloadskin", icon = 'SORT_ASC')
    except:
        col.label(text="material error", icon = "ERROR")

    # disable further material settings due disabled face
    enabled = not main_props["No face"]
    # eyes
    try:
        eye_node = mat_obj.material_slots[1].material.node_tree.nodes['Eyes'].inputs
        
        col = layout.box().column()
        col.enabled = enabled
        row = col.row(align = True)
        row.label(text = "Eye Type:")
        # row.prop(eye_node["Type"], "default_value", text = "")
        row.prop(main_props, '["Eye type"]', text = "")
        row.prop(main_props, '["Different eyes colour"]', toggle = True, text = "", icon = "PHYSICS")

        settings = col.row()
        # eye_type = eye_node["Type"].default_value
        eye_type = rig.pose.bones["Main_Properties"]["Eye type"]
        two_colour = rig.pose.bones["Main_Properties"]["Different eyes colour"]

        # eye type texture
        if eye_type == 2:
            # settings.prop(eye_node["TextureType"], "default_value", text = "texture type")
            settings.prop(main_props, '["Eye texture type"]', text = "texture type")

        utils.UI_Utils.spacer(col, factor = 0.3)
        colour = col.row()

        # eye type solid
        if eye_type != 1:
            colour = col.row()
            colour.prop(eye_node["1_EyeSC"], "default_value", text = "")
            if two_colour:
                colour.prop(eye_node["2_EyeSC"], "default_value", text = "")

        # eye type original 
        if eye_type == 1:
            main = colour.row()

            a = main.row(align = True)
            c = a.column(align = True)
            c.prop(eye_node["1_Color1"], "default_value", text = "")
            c.prop(eye_node["1_Color2"], "default_value", text = "")

            c = a.column(align = True)
            c.prop(eye_node["1_Reflection"], "default_value", text = "")
            c.prop(eye_node["1_Pupil"], "default_value", text = "")

            if two_colour:
                second = main.split()
                a = second.row(align = True)
                c = a.column(align = True)
                c.prop(eye_node["2_Color1"], "default_value", text = "")
                c.prop(eye_node["2_Color2"], "default_value", text = "")

                c = a.column(align = True)
                c.prop(eye_node["2_Reflection"], "default_value", text = "")
                c.prop(eye_node["2_Pupil"], "default_value", text = "")
            
            row = col.row()
            row.prop(eye_node["1_RimSize"], "default_value", text = "Rim Size")
            if two_colour:
                row.prop(eye_node["2_RimSize"], "default_value", text = "Rim Size")

        utils.UI_Utils.spacer(col, factor = 0.3)
        
        col.prop(eye_node["Roughness"], "default_value", text = "Roughness")
    except:
        col.label(text="eye material not found", icon="ERROR")

    try:
        # eyebrow
        eyebrow_node = mat_obj.material_slots[2].material.node_tree.nodes['Mix'].inputs
        row = layout.box().row(align = True)
        row.enabled = enabled
        row.prop(main_props, '["CC eyebrow"]', toggle = True, text = "Eyebrow")
        split = row.split(align = True)
        split.enabled = main_props["CC eyebrow"]
        split.prop(eyebrow_node[7], "default_value", text = "")
    except:
        col.label(text="eyebrow material not found", icon="ERROR")