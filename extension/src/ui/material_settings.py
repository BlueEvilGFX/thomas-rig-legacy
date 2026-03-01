from .. import utils

# ------------------------------------------------------------
# MATERIAL ACCESS HELPERS 
# ------------------------------------------------------------


def get_skin_image(mat_obj): 
    return mat_obj.material_slots[0].material.node_tree.nodes['Skin'].image

def get_eye_inputs(mat_obj):
    return mat_obj.material_slots[1].material.node_tree.nodes['Eyes'].inputs

def get_eyebrow_inputs(mat_obj):
    return mat_obj.material_slots[2].material.node_tree.nodes['Mix'].inputs


# ------------------------------------------------------------
# UI HELPERS 
# ------------------------------------------------------------


def draw_prop(col, socket, text="", icon=None):
    if type(icon) == int:
        col.prop(socket, "default_value", text=text, icon_id=icon)
    elif icon:
        col.prop(socket, "default_value", text=text, icon=icon)
    else:
        col.prop(socket, "default_value", text=text)


# ------------------------------------------------------------
# SKIN UI
# ------------------------------------------------------------


def draw_skin_section(col, img):
    row = col.row(align=True)

    # pack/unpack operator
    row.operator(
        "thomasriglegacy.imgpack", 
        text="",
        icon="PACKAGE" if utils.is_packed(img) else "UGLYPACKAGE"
    ).id_name = img.name 

    # filepath + reload + download
    main = row.row(align=True)
    main.enabled = not utils.is_packed(img)
    main.prop(img, "filepath", text="")  
    main.operator(
        "thomasriglegacy.imgreload",
        text = "",
        icon = "FILE_REFRESH"
    ).id_name = img.name
    main.operator("thomasriglegacy.downloadskin", icon = 'SORT_ASC')


# ------------------------------------------------------------
# EYE UI
# ------------------------------------------------------------


def draw_eye_type_selector(col, main_props):
    row = col.row(align=True)
    row.label(text="Eye Type:")
    row.prop(main_props, '["Eye type"]', text="")
    row.prop(main_props, '["Different eyes colour"]', 
             toggle=True, text="", icon="PHYSICS")

def draw_eye_solid(col, eye_node, two_colour):
    row = col.row()
    draw_prop(row, eye_node["1_EyeSC"])
    if two_colour:
        draw_prop(row, eye_node["2_EyeSC"])

def draw_eye_original(col, eye_node, two_colour):
    row = col.row() 
    block = row.row(align=True)

    # left column 
    left = block.column(align=True) 
    draw_prop(left, eye_node["1_Color1"]) 
    draw_prop(left, eye_node["1_Color2"]) 

    # right column 
    right = block.column(align=True)
    draw_prop(right, eye_node["1_Reflection"])
    draw_prop(right, eye_node["1_Pupil"]) 

    # second eye 
    if two_colour: 
        second = block.split() 
        col2 = second.row(align=True) 
        left2 = col2.column(align=True) 
        draw_prop(left2, eye_node["2_Color1"]) 
        draw_prop(left2, eye_node["2_Color2"]) 
        right2 = col2.column(align=True) 
        draw_prop(right2, eye_node["2_Reflection"])
        draw_prop(right2, eye_node["2_Pupil"]) 

    # rim size 
    rim = col.row() 
    draw_prop(rim, eye_node["1_RimSize"], text="Rim Size") 
    if two_colour: 
        draw_prop(rim, eye_node["2_RimSize"], text="Rim Size")

def draw_eye_emission(col, eye_node, two_colour):
    row = col.row()
    icon = "OUTLINER_OB_LIGHT" if eye_node["1_Emission"].default_value else "LIGHT" 
    row.label(text="", icon=icon) 

    draw_prop(row, eye_node["1_Emission"])
    cell = row.row(align=True)
    cell.enabled = eye_node["1_Emission"].default_value > 0 
    if two_colour:
        cell.enabled = cell.enabled or eye_node["2_Emission"].default_value > 0 

    draw_prop(cell, eye_node["Blow_Out"], text="Blow Out") 

    if two_colour: 
        draw_prop(row, eye_node["2_Emission"])


# ------------------------------------------------------------
# EYEBROW UI
# ------------------------------------------------------------ 


def draw_eyebrow_section(layout, eyebrow_node, main_props, enabled):
    row = layout.box().row(align=True)
    row.enabled = enabled

    row.prop(main_props, '["CC eyebrow"]', toggle=True, text="Eyebrow")

    split = row.split(align=True)
    split.enabled = main_props["CC eyebrow"]
    draw_prop(split, eyebrow_node[7])


# ------------------------------------------------------------
# MAIN DRAW
# ------------------------------------------------------------


def draw(rig, layout, main_props):
    mat_obj = utils.get_mat_object(rig)

    col = layout.box().column()
            
    # ---------------- SKIN ----------------
    try:
        img = get_skin_image(mat_obj)
        draw_skin_section(col, img)
    except Exception as e:
        col.label(text="Skin error", icon="ERROR")
        print(e)

    enabled = not main_props["No face"]

    # ---------------- EYES ----------------
    try:
        eye_node = get_eye_inputs(mat_obj)
        col = layout.box().column()
        col.enabled = enabled

        draw_eye_type_selector(col, main_props)
        
        eye_type = main_props["Eye type"]
        two_colour = main_props["Different eyes colour"]

        if eye_type == 2:
            col.prop(main_props, '["Eye texture type"]', text = "texture type")

        utils.UI_Utils.spacer(col, factor = 0.3)

        if eye_type != 1:
            draw_eye_solid(col, eye_node, two_colour)
        else:
            draw_eye_original(col, eye_node, two_colour)

        if eye_node.get("1_Emission"):
            utils.UI_Utils.spacer(col, factor = 0.3)
            draw_eye_emission(col, eye_node, two_colour)

        utils.UI_Utils.spacer(col, factor = 0.3)
        draw_prop(col, eye_node["Roughness"], text="Roughness")

    except Exception as e:
        col.label(text="eye material error", icon="ERROR")
        print(e)

    # ---------------- EYEBROW ----------------
    try:
        eyebrow_node = get_eyebrow_inputs(mat_obj)
        draw_eyebrow_section(layout, eyebrow_node, main_props, enabled)
    except Exception as e: 
        col.label(text="eyebrow material not found", icon="ERROR")
        print(e)