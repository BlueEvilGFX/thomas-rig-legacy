from .. import utils

def draw(main_props, misc_props, layout, context, rig):
    from .. import icons

    box = layout.box()
    col = box.column()

    # misc design
    col.prop(main_props, '["Second layer"]', toggle = True, text = "2nd Layer")
    col.prop(main_props, '["Smooth bends"]', toggle = True, text = "Smooth Bends")

    # neck
    row = col.row(align = True)
    row.prop(main_props, '["neck"]', toggle = True, text = "Neck")
    row = row.split(align = True)
    row.enabled = main_props["neck"]
    row.prop(main_props, '["neck_bendy"]', toggle = True, text = "Bendy")

    # chibi
    row = col.row(align = True)
    row.prop(misc_props, '["Chibi"]', toggle = True, text = "Chibi")

    # head
    icon = "CHECKBOX_HLT" if main_props["No face"] else "CHECKBOX_DEHLT"
    col.prop(main_props, '["No face"]', toggle = True, text = "No Face", icon = icon)
    c_head = col.column(align = True)
    c_head.enabled = not main_props["No face"]
    row = c_head.row(align = True)
    row.label(icon = "BLANK1")
    row.scale_x = 0.5
    row.prop(main_props, '["Texture deform"]', toggle = True, text = "Texture Deform")
    row = c_head.row(align = True)
    row.label(icon = "BLANK1")
    row.scale_x = 0.5
    row.prop(main_props, '["Eyebrow thickness"]', text = "Brow Height")
    utils.UI_Utils.spacer(col, factor = 0.3)

    # arms
    row = col.row(align=True)
    row.prop(main_props, '["Slim main"]', toggle = True, text = "Slim Arms")
    arms = row.row(align = True)
    arms.enabled = main_props["Slim main"]
    arms.prop(main_props, '["3x3"]', toggle = True, text = "3x3")

    # fingers
    row = col.row(align = True)
    row.prop(main_props, '["Finger main"]', toggle = True, text = "", icon = "VIEW_PAN")
    row = row.split(align = True)
    row.enabled = main_props["Finger main"]
    row.prop(main_props, '["Finger+ main"]', toggle = True, text = "Finger+")

    # deforms
    box = layout.box()
    col = box.column()
    icon = "DOWNARROW_HLT" if misc_props["Mesh_Deforms"] else "RIGHTARROW"
    col.prop(misc_props, '["Mesh_Deforms"]', toggle = True, text = "Mesh Deforms", icon = icon)
    if misc_props["Mesh_Deforms"]:
        row = col.row(align = True)
        row.label(icon = "BLANK1")
        row.scale_x = 0.5
        col = row.column()
        col.prop(misc_props, '["Leg_Taper"]', toggle = True, text = "Leg Taper", slider = True)
        waist_lattice = utils.get_mat_object(rig).modifiers["Chest"].object
        col.prop(waist_lattice.data.shape_keys.key_blocks["Breast"], "value", text = "Breast")
        col.prop(waist_lattice.data.shape_keys.key_blocks["Waist"], "value", text = "Waist")

    # new assets
    col = layout.column()
    utils.UI_Utils.spacer(col, factor = 0.3)
    split = col.row(align=True)
    left = split.box().column()
    right = split.box().column()

    pcoll = icons.thomas_icons["thomas_legacy"]
    sub_tab = rig.pose.bones["Main_Properties"]["Assets_Tab"]

    # check for minecraft original icons
    if pcoll.get("elytra") is None:
        sub_tabs = {
            0 : "MOD_CLOTH",
            1 : pcoll["cape"].icon_id,
            2 : "MOD_MIRROR",
            3 : "ADD"
        }
    else:
        sub_tabs = {
            0 : pcoll["iron_chestplate"].icon_id,
            1 : pcoll["cape"].icon_id,
            2 : pcoll["elytra"].icon_id,
            3 : pcoll["glow_item_frame"].icon_id
        }

    for i in range(4):
        # icon check
        
        r = left.row()
        r.alert = (sub_tab == i)
        if isinstance(sub_tabs[i], int):
            r.operator("thomasriglegacy.change_armor_tab", text = "", icon_value = sub_tabs.get(i)).tab = i
        else:
            r.operator("thomasriglegacy.change_armor_tab", text = "", icon = sub_tabs.get(i)).tab = i

    # armor
    if main_props['Assets_Tab'] == 0:
        col = right.column()
        col.operator("thomasriglegacy.addarmor", text = "Armor", icon = "ADD").parent = True
        col.operator("thomasriglegacy.parenttool", text = "Parent", icon = "CON_CHILDOF")
        # space
        col.label(text="")
        col.label(text="")

    # cape
    if main_props['Assets_Tab'] == 1:
        row = right.row(align = True)
        row.label(text="Cape")
        row.operator("thomasriglegacy.appendcape", text = "", icon = "ADD")
        row.operator("thomasriglegacy.removecape", text = "", icon = "REMOVE")

        if misc_props['cape']:
            try:
                img_node = misc_props['cape'].objects[2].material_slots[0].material.node_tree.nodes['Image Texture'].image
                left = right.row(align = True)
                left.operator("thomasriglegacy.imgpack" , text="",
                            icon="PACKAGE" if utils.is_packed(img_node) else "UGLYPACKAGE"
                    ).id_name = img_node.name 

                main = left.row(align=True) 
                main.enabled = not utils.is_packed(img_node)
                main.prop(img_node, "filepath", text="")  
                main.operator("thomasriglegacy.imgreload", text = "", icon = "FILE_REFRESH"
                    ).id_name = img_node.name
            except:
                row = right.row()
                row.scale_y = 0.67
                row.label(text="material error", icon = "ERROR")
            row = right.row(align = True)
            row.scale_x = 10
            row.prop(misc_props['cape'], "hide_viewport", text="")
            row.prop(misc_props['cape'], "hide_render", text="")
        else:
            # space
            right.label(text="")
            right.label(text="")
            right.label(text="")

    # elytra
    if main_props['Assets_Tab'] == 2:
        row = right.row(align = True)
        row.label(text="Elytra")
        row.operator("thomasriglegacy.appendelytra", text = "", icon = "ADD")
        row.operator("thomasriglegacy.removeelytra", text = "", icon = "REMOVE")

        if misc_props['elytra']:
            try:
                img_node = misc_props['elytra'].objects[0].material_slots[0].material.node_tree.nodes['Image Texture'].image
                left = right.row(align = True)
                left.operator("thomasriglegacy.imgpack" , text="",
                            icon="PACKAGE" if utils.is_packed(img_node) else "UGLYPACKAGE"
                    ).id_name = img_node.name 

                main = left.row(align=True) 
                main.enabled = not utils.is_packed(img_node)
                main.prop(img_node, "filepath", text="")  
                main.operator("thomasriglegacy.imgreload", text = "", icon = "FILE_REFRESH"
                    ).id_name = img_node.name
            except:
                row = right.row()
                row.scale_y = 0.67
                row.label(text="material error", icon = "ERROR")
            row = right.row(align = True)
            row.scale_x = 10
            row.prop(misc_props['elytra'], "hide_viewport", text="")
            row.prop(misc_props['elytra'], "hide_render", text="")
        else:
            # space
            right.label(text="")
            right.label(text="")
            right.label(text="")
    
    # miscs
    if main_props['Assets_Tab'] == 3:
        col = right.column()
        enum = col.row()
        enum.scale_y = 0.54
        th_prev = context.window_manager.thomas_rig_legacy
        enum.template_icon_view(th_prev, "misc")
        col.operator("thomasriglegacy.appendmisc", icon="ADD", text = f'<{th_prev.misc[:-4]}>')