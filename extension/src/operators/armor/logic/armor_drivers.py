from .armor_enums import ArmorPartEnum

class ArmorDriverSetup:
    def __init__(self, op):
        self.op = op
        self.rig = op.rig

    def apply_default_drivers(self, armor_obj, armor_part: ArmorPartEnum):
        """Apply bend/120 drivers for default armor."""
        if armor_part == ArmorPartEnum.CHESTPLATE:
            joint = "Arm_Lower_Driver"
        elif armor_part in {ArmorPartEnum.BOOTS, ArmorPartEnum.LEGGINGS}:
            joint = "Leg_knee_Driver"
        else:
            return

        self._add_driver_bend_120(armor_obj, ".R", "Bend.R", joint, "a")
        self._add_driver_bend_120(armor_obj, ".R", "120.R", joint, "b")
        self._add_driver_bend_120(armor_obj, ".L", "Bend.L", joint, "a")
        self._add_driver_bend_120(armor_obj, ".L", "120.L", joint, "b")

    def _add_driver_bend_120(self, armor_obj, side, shape_key, bone, ab):
        """Internal helper for creating bend/120 drivers."""
        if ab == "a":
            expression = (
                "tan(value*0.5) if tan(value*0.5) >= 0 "
                "else -tan(value*0.5)"
            )
        else:  # ab == "b"
            expression = (
                "tan(value*0.5)-1 if tan(value*0.5) >= 0 "
                "else -tan(value*0.5)-1"
            )

        key_block = armor_obj.data.shape_keys.key_blocks[shape_key]
        driver = key_block.driver_add("value").driver
        driver.type = "SCRIPTED"

        var = driver.variables.new()
        var.type = "TRANSFORMS"
        var.name = "value"

        target = var.targets[0]
        target.id = self.rig
        target.bone_target = bone + side
        target.transform_type = "ROT_X"
        target.transform_space = "LOCAL_SPACE"

        driver.expression = expression
