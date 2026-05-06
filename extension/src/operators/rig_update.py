import bpy

from .. import utils
from .. import constants

MAX_VERSION = (1, 2, 5)
MIN_VERSION =  (1, 2, 0)

class THOMAS_RIG_UPDATE_RIG(bpy.types.Operator):
    bl_idname = "thomasriglegacy.update_rig"
    bl_label = "update"
    bl_options = {'REGISTER', 'UNDO'}

    rig = None
    rig_version = None
    ext_version = None
    
    @classmethod
    def poll(cls, context):
        rig = utils.get_rig()
        if rig is None:
            return False
        rig_version = rig.get("rig_version", "unknown")

        if not rig or not rig.get("Rig_ID") == constants.RIG_ID:
            return False

        if tuple(rig_version) >= MIN_VERSION and tuple(rig_version) < MAX_VERSION:
            return True
                
        return rig_version == "unknown" or tuple(rig_version) < utils.get_ext_version()
    
    @classmethod
    def manual_update_poll(cls) -> bool | tuple[str]:
        rig = utils.get_rig()
        rig_version = rig.get("rig_version", "unknown")

        if rig_version != "unknown" and tuple(rig_version) >= MIN_VERSION:
            return False
        
        return ("manual update required.", "can result in unexpected errors.")

    def execute(self, context):
        rig = utils.get_rig()
        rig_version = rig.get("rig_version", None)
        ext_version = utils.get_ext_version()

        # example of use

        #if tuple(rig_version) < (1, 1, 9):
        #    Updater.update_to_1_1_9(self)

        if tuple(rig_version) < (1, 2, 1):
            Updater.update_to_1_2_1(self)

        if tuple(rig_version) < (1, 2 ,2):
            Updater.update_to_1_2_2(self)

        if tuple(rig_version) < (1, 2 ,3):
            Updater.update_to_1_2_3(self)

        if tuple(rig_version) < (1, 2 ,4):
            Updater.update_to_1_2_4(self)

        if tuple(rig_version) < (1, 2 ,5):
            Updater.update_to_1_2_4(self)

        # set rig version to newest
        rig["rig_version"] = ext_version
        rig.data.update_tag()
        bpy.context.view_layer.update()
        self.report({"INFO"}, "Rig updated to v" + '.'.join(map(str, ext_version)))
        return {'FINISHED'}
    

class Updater():
    def update_to_1_2_1(self):
        rig = utils.get_rig()
        for obj in rig.children_recursive:
            if obj.name == "Head_NoDeform":
                obj.data.uv_layers['UVMap.001'].active = True
                return
            
    def update_to_1_2_2(self):
        return
    
    def update_to_1_2_3(self):
        return
    
    def update_to_1_2_4(self):
        return
    
    def update_to_1_2_5(self):
        return

    # this is one example how to use this class

    # def update_to_1_1_9(self):
    #     # reset location & deactivate "Transformation" displace constraint 
    #     rig = utils.get_rig()
    #     rig.location = (0, 0, 0)
    #     rig.pose.bones["Root"].constraints["Transformation"].enabled = False
    # 
    #     # move subdiv modifier under armature
    #     for obj in rig.children_recursive:
    #         if "Head_Boolean_Eyes" not in obj.name:
    #             continue
    #         mod = obj.modifiers["Armature"]
    #         idx = list(obj.modifiers).index(mod)
    #         obj.modifiers.move(idx, 0)