# Custom UI TOML Guide

If you want to display your custom properties not as a default list like the extension would do you can define how they should be displayed. For this we use a custom `TOML` system. This is a restricted system with limited functionality.
This guide explains how to format and structure TOML files to generate UI elements in the rig ui panel.

## The Component Hierarchy
Every UI element is treated as an item in a list (`[[layout]]`). Elements that group other elements (like `row`, `column`, `box`, or `split`) must contain a `children` array holding nested elements.

## Property Types
When generating UI properties (`type = "prop"`), the configuration changes depending on whether you are targeting **Rig/Bone Custom Properties** or **Native Blender Settings**.

### 1. Rig / Bone Custom Properties (`#user_props`)
Use this when you want to display custom properties assigned to your rig's bones.

* **`data`**: Must be set to `"#user_props"`
* **`property`**: Must include brackets and quotes: `"['your_prop_name']"`

**Example:**
```toml
[[layout]]
type = "row"
align = true
children = [
    { type = "prop", data = "#user_props", property = "['ik_fk_switch']", text = "IK/FK Switch", toggle = true },
    { type = "prop", data = "#user_props", property = "['stretch_amount']", slider = true }
]
```

### 2. Native Blender Settings (`context`)
Use this to expose global Blender settings directly in your custom panel.
- `data`: Must be set to `"context"`
- `property`: Write the native Python path, ommiting `bpy.context.`.
- _Note_: Do not use brackets here unless targeting specific collection items

**Example**
```toml
[[layout]]
type = "split"
factor = 0.6
children = [
    # Adjusting Render Settings (automatically resolved to scene.render)
    { type = "prop", data = "context", property = "render.engine", text = "Render Engine" },
    # Adjusting Viewport Raytracing
    { type = "prop", data = "context", property = "scene.eevee.use_raytracing", text = "Raytracing" }
]
```

## Supported Layout And Optional Attributes
| Layout (`type`) | Optional Attribute |
|-------|-------|
| `box` ||
| `column` | `align` |
| `row` | `align` |
| `split` | `align`, `factor` |
| `label` | `text`, `icon` |
| `prop` | `text`, `icon`, `expand`, `slider`, `toggle`, `icon_only`, `emboss`, `invert_checkbox` |

**Note on Booleans:** Ensure all toggle options like `align`, `slider`, or `toggle` are written as native TOML booleans (`true`/`false`), NOT as strings (`"true"`/`"false"`).^


## Fulll Example
```toml
# 1st element on the main layout
[[layout]]
type = "label"
text = "Label1 test"
icon = "INFO"

# 2nd element on the main layout
[[layout]]
type = "row"
align = true
children = [
    { type = "prop", data = "#user_props", property = "['prop1']", text = "1", toggle = true },
    { type = "prop", data = "#user_props", property = "['prop2']", text = "2", toggle = true },
    { type = "prop", data = "#user_props", property = "['prop3']", text = "3", toggle = true },
    { type = "prop", data = "#user_props", property = "['prop5']", text = "5", toggle = true }
]

# 3d element on the main layout
[[layout]]
type = "row"
align = false
children = [
    { type = "prop", data = "#user_props", property = "['prop4']", toggle = true }
]

# 4th element on the main layout
[[layout]]
type = "split"
align = false
factor = 0.6
children = [
    { type = "prop", data = "context", property = "render.resolution_x", text="vec3 bool"}
]
```