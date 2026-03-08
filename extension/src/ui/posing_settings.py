from .. import utils

def draw(layout, rig, main_props):

    r_arm_props = rig.pose.bones["R.Arm_Properties"]
    l_arm_props = rig.pose.bones["L.Arm_Properties"]
    r_leg_props = rig.pose.bones["R.Leg_Properties"]
    l_leg_props = rig.pose.bones["L.Leg_Properties"]
    pupil_props = rig.pose.bones["Pupils_controller"]

    layout.box().prop(rig, "show_in_front", toggle = True, icon="BONE_DATA")

    box = layout.box()
    col = box.column()

    # arms/legs
    split = col.split(factor=3/11)
    left = split.column()
    right = split.column()

    # arms
    left.label(text="Arm IK")
    Arms = right.row()
    # left
    arms = Arms.row(align=True)
    arms.prop(l_arm_props, '["L.Arm_FK/IK"]', toggle = True, text = "L")
    l = arms.split(align=True)
    l.enabled = l_arm_props["L.Arm_FK/IK"]
    l.prop(rig.pose.bones["L.arm_stretch"].constraints["Stretch To"], "enabled",  text ="", icon = "CON_STRETCHTO", invert_checkbox = True)
    l.prop(l_arm_props, '["L.Arm_World"]', toggle = True, text = "", icon = "WORLD")
    # right
    arms = Arms.row(align=True)
    arms.prop(r_arm_props, '["R.Arm_FK/IK"]', toggle = True, text = "R")
    r = arms.split(align=True)
    r.enabled = r_arm_props["R.Arm_FK/IK"]
    r.prop(rig.pose.bones["R.arm_stretch"].constraints["Stretch To"], "enabled", text ="", icon = "CON_STRETCHTO", invert_checkbox = True)
    r.prop(r_arm_props, '["R.Arm_World"]', toggle = True, text = "", icon = "WORLD")

    # legs
    left.label(text="Leg IK")
    Legs = right.row()
    # left
    legs = Legs.row(align=True)
    legs.prop(l_leg_props, '["L.IK/FK"]', toggle = True, text = "L")
    l = legs.split(align=True)
    l.enabled = not l_leg_props["L.IK/FK"]
    l.prop(rig.pose.bones["Leg_IK.L"].constraints["Stretch To"], "enabled", text ="", icon = "CON_STRETCHTO", invert_checkbox = True, toggle = True)
    # mid
    mid = Legs.row()
    mid.enabled = not (r_leg_props["R.IK/FK"] or l_leg_props["L.IK/FK"])
    mid.prop(main_props, '["Leg body deform"]', toggle = True, icon = "CONSTRAINT_BONE", text = "")
    # right
    legs = Legs.row(align=True)
    legs.prop(r_leg_props, '["R.IK/FK"]', toggle = True, text = "R")
    r = legs.split(align=True)
    r.enabled = not r_leg_props["R.IK/FK"]
    r.prop(rig.pose.bones["Leg_IK.R"].constraints["Stretch To"], "enabled", text ="", icon = "CON_STRETCHTO", invert_checkbox = True, toggle = True)

    utils.UI_Utils.spacer(col, factor = 0.3)
    col.prop(main_props, '["Full rigged face"]', toggle = True, text = "Full rigged face")

    utils.UI_Utils.spacer(col, factor = 0.3)
    col.prop(main_props, '["Head world"]', toggle = True, text = "Head World")

    # eyes
    row = col.row(align = True)
    row.enabled = main_props["Head world"]
    row.prop(main_props, '["Eyes tracker"]', toggle = True, text = "Eyes Tracker")
    r = row.row(align = True)
    r.enabled = main_props["Eyes tracker"]
    r.prop(pupil_props, '["Easy look head"]', icon = "MONKEY", text = "")
    r.prop(pupil_props, '["Easy look mouth"]', icon = "MOD_SIMPLIFY", text = "")
    r.prop(pupil_props, '["Easy look upper body"]', icon = "MATCLOTH", text = "")
    col.prop(main_props, '["Eyes follow"]', toggle = True, text = "Eyes Follow")

    # smart deform
    row = col.row(align = True)
    row.prop(main_props, '["Smart deform"]', toggle = True, text = "Smart Deform")
    r = row.row(align = True)
    r.enabled = main_props["Smart deform"]
    r.prop(main_props, '["Smart deform strength"]', text = "")
    r.prop(main_props, '["Bone shape smart deform"]', toggle = True, text = "", icon = "BONE_DATA")

    utils.UI_Utils.spacer(col, 0.3)
    col.prop(main_props, '["Flip bone"]', toggle = True, text = "Flip Bone")

    # finger
    col = layout.box().column()
    row = col.row(align = True)
    row.prop(main_props, '["Finger main"]', toggle = True, text = "", icon = "VIEW_PAN")
    row = row.split(align = True)
    row.enabled = main_props["Finger main"]
    row.prop(main_props, '["Finger+ main"]', toggle = True, text = "Finger+")