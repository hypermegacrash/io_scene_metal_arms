# Module for drawing gamedata parameters in viewport space.

# BLENDER
import bpy
import blf
from bpy_extras.view3d_utils import location_3d_to_region_2d
import gpu
from gpu_extras.batch import batch_for_shader

class MA_Gamedata_Draw_Mgr:
    """Singleton for managing the draw handler"""
    handler       = None
    is_enabled    = False

    draw_distance_min  = 250.0
    draw_distance_full = 100.0

    font_size     = 16
    line_height   = 18
    color_name    = (0.8, 0.8, 1.0, 1.0)
    color_comment = (0.8, 1.0, 1.0, 1.0)
    color_default = (1.0, 1.0, 1.0, 1.0)

def draw_rect(x, y, w, h, color):
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    verts = (
        (x,     y),
        (x + w, y),
        (x + w, y + h),
        (x,     y + h),
    )
    indices = ((0, 1, 2), (2, 3, 0))
    batch = batch_for_shader(shader, 'TRIS', {"pos": verts}, indices=indices)

    gpu.state.blend_set('ALPHA')
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)
    gpu.state.blend_set('NONE')

def get_lod_lines(lines, distance):
    important_lines = []

    important_keys = {
        "name",
        "type",
        "tripwirebuild",
    }

    for line in lines:
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip().lower()

        if key in important_keys:
            important_lines.append(line)

    if distance <= MA_Gamedata_Draw_Mgr.draw_distance_full:
        return lines
    else:
        return important_lines


def draw_gamedata_px(self, context):
    """Draw gamedata labels in the 3D viewport"""
    font_id = 0
    blf.size(font_id, MA_Gamedata_Draw_Mgr.font_size)
    blf.enable(font_id, 4)  # shadow
    blf.shadow_offset(font_id, 1, -1)

    region = context.region
    rv3d   = context.space_data.region_3d

    for obj in context.view_layer.objects:
        if not obj.visible_get() or "ma" not in obj:
            continue

        if not obj["ma"]:
            continue

        # Skip if too far
        if (obj.location - rv3d.view_matrix.inverted().translation).length > MA_Gamedata_Draw_Mgr.draw_distance_min:
            continue

        coord_2d = location_3d_to_region_2d(region, rv3d, obj.location)
        if not coord_2d:
            continue

        distance = ( obj.location - rv3d.view_matrix.inverted().translation ).length

        lines = obj["ma"].split("\n")
        lines = get_lod_lines(lines, distance)

        if not lines:
            continue
        
        x = coord_2d[0]
        y = coord_2d[1]

        # Textbox Size
        max_width = 0
        for line in lines:
            w, h = blf.dimensions(font_id, line)
            max_width = max(max_width, w)

        total_height = ( len(lines) - 1 ) * MA_Gamedata_Draw_Mgr.line_height

        padding = 20

        # Draw Background
        draw_rect(
            x - padding,
            y - total_height - padding,
            max_width + padding * 2,
            total_height + padding * 2,
            (0.0, 0.0, 0.0, 0.5)  # black, 50% alpha
        )

        for line in lines:
            blf.position(font_id, coord_2d[0], y, 0)

            if line.lower().startswith("name"): blf.color(font_id, *MA_Gamedata_Draw_Mgr.color_name)
            elif line.startswith("#"):          blf.color(font_id, *MA_Gamedata_Draw_Mgr.color_comment)
            else:                               blf.color(font_id, *MA_Gamedata_Draw_Mgr.color_default)

            blf.draw(font_id, line)
            y -= MA_Gamedata_Draw_Mgr.line_height

class MA_Gamedata_Draw_Px(bpy.types.Operator):
    """Toggle viewing gamedata in the 3D viewport"""

    bl_idname = "object.ma_gd_view"
    bl_label  = "View Gamedata in World Space"

    def execute(self, context):
        if not MA_Gamedata_Draw_Mgr.is_enabled:
            MA_Gamedata_Draw_Mgr.handler_px = bpy.types.SpaceView3D.draw_handler_add( draw_gamedata_px,   (self, context), 'WINDOW', 'POST_PIXEL' )

            MA_Gamedata_Draw_Mgr.is_enabled = True

            self.report( {'INFO'}, "Gamedata screen view enabled" )

        else:
            if MA_Gamedata_Draw_Mgr.handler_px:   bpy.types.SpaceView3D.draw_handler_remove( MA_Gamedata_Draw_Mgr.handler_px,   'WINDOW' )

            MA_Gamedata_Draw_Mgr.handler_px = None

            MA_Gamedata_Draw_Mgr.is_enabled = False

            self.report( {'INFO'}, "Gamedata screen view disabled" )

        return {'FINISHED'}