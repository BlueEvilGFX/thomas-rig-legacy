import bpy
from bpy.props import EnumProperty

from ..utils import get_rig


class THOMAS_RIG_TOOL_PARENT(bpy.types.Operator):
    bl_idname = "thomasriglegacy.parenttool"
    bl_label = "parent"
    bl_options = {'REGISTER', 'UNDO'}

    arm_side : EnumProperty(
        default = 'wrist.R',
        items = [
            ('wrist.R', 'wrist.R', ''),
            ('wrist.L', 'wrist.L', '')
            ]) # type: ignore
    
    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 1
    
    def draw(self, context):
        self.layout.row().prop(self, "arm_side", expand = True)
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        rig = get_rig()
        item = context.selected_objects[0]

        constraint = item.constraints.new(type="CHILD_OF")
        constraint.target = rig
        constraint.subtarget = self.arm_side
        return {'FINISHED'}