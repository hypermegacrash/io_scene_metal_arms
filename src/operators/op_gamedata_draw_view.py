# Module for drawing 3D debug visualization for gamedata parameters

# BUILT IN
from mathutils import Vector
import math
# BLENDER
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
# FANG TOOLKIT
from ..process.process_gamedata import parse_gamedata_string

class MA_Gamedata_Draw_View_Mgr:
    """Singleton for managing the draw view handler"""
    handler       = None
    is_enabled    = False
    draw_distance = 350.0

    # Door Params
    door_color_act      = (1.0, 0.0, 1.0, 1.0)
    door_default_radius = 15.0

    # Lift Params
    lift_color_start_call = (1.0, 0.0, 0.0, 1.0)
    lift_color_start_act  = (1.0, 0.2, 0.2, 1.0)
    lift_color_end_call   = (0.0, 0.0, 1.0, 1.0)
    lift_color_end_act    = (0.2, 0.2, 1.0, 1.0)
    lift_default_start    = 15.0
    lift_default_act      = 20.0

    # Jumppad Params
    jumppad_color_parabola = (0.2, 0.8, 0.2, 1.0)

def gamedata_parse_int(data, key, default):
    try:
        value = int(data.get(key, 0))
        return value if value > 0 else default
    except:
        return default

def gamedata_parse_vector(data, key):
    if key not in data:
        return Vector( (0, 0, 0) )

    try:
        values = [ float(v.strip()) for v in data[key].split(",") ]

        if len(values) != 3: return Vector((0, 0, 0))

        return Vector(values)

    except:
        return Vector((0, 0, 0))

def gamedata_find_object_by_name(objects, in_name):
    """Find the first Blender object whose gamedata contains 'name=in_name'."""

    for obj in objects:
        if not obj.visible_get() or "ma" not in obj:
            continue

        if not obj["ma"]:
            continue

        data = parse_gamedata_string(obj["ma"])

        if data.get("name") == in_name:
            return obj

    return None

def draw_wire_sphere(location, radius, color):
    """Draw a wireframe sphere in 3D world space."""

    segments = 32
    verts    = []
    indices  = []

    def add_circle(get_pos):
        start = len(verts)

        for i in range(segments):
            angle = (2.0 * math.pi * i) / segments
            verts.append(get_pos(angle))

        for i in range(segments):
            indices.append( ( start + i, start + ((i + 1) % segments) ) )
    
    add_circle(lambda angle: ( location.x + radius * math.cos(angle), location.y + radius * math.sin(angle), location.z, ) ) # XY circle
    add_circle(lambda angle: ( location.x + radius * math.cos(angle), location.y, location.z + radius * math.sin(angle), ) ) # XZ circle
    add_circle(lambda angle: ( location.x, location.y + radius * math.cos(angle), location.z + radius * math.sin(angle), ) ) # YZ circle

    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    batch = batch_for_shader( shader, 'LINES', {"pos": verts}, indices=indices, )

    gpu.state.depth_test_set('LESS_EQUAL')
    gpu.state.blend_set('ALPHA')
    shader.bind()
    shader.uniform_float("color", color)
    gpu.state.line_width_set(2.0)

    batch.draw(shader)

    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')
    gpu.state.depth_test_set('NONE')

def draw_ballistic_trajectory(start, end, hangtime):

    segments = 48
    verts    = []
    indices  = []

    try:
        time_in_air = float(hangtime)
    except:
        return

    if time_in_air <= 0.0:
        return

    gravity = -64.0 # Pulled from b_glitch.csv

    # Horizontal displacement
    displacement_xy = Vector( ( end.x - start.x, end.y - start.y, 0.0 ) )
    distance_xy = displacement_xy.length

    if distance_xy < 0.001:
        return

    # Distance / time
    velocity_xy = displacement_xy / time_in_air
    velocity_z = ( (end.z - start.z) - (0.5 * gravity * time_in_air * time_in_air) ) / time_in_air

    velocity = Vector( ( velocity_xy.x, velocity_xy.y, velocity_z ) )

    # Sample trajectory
    for i in range(segments + 1):

        t = (i / segments) * time_in_air

        position = start + velocity * t

        # Apply gravity to Z only.
        position.z += 0.5 * gravity * t * t

        verts.append(position)

    indices = [ (i, i + 1) for i in range(segments) ]

    shader = gpu.shader.from_builtin('UNIFORM_COLOR')

    batch = batch_for_shader( shader, 'LINES', {"pos": verts}, indices=indices )

    gpu.state.depth_test_set('LESS_EQUAL')
    gpu.state.blend_set('ALPHA')
    gpu.state.line_width_set(3.0)

    shader.bind()
    shader.uniform_float( "color", MA_Gamedata_Draw_View_Mgr.jumppad_color_parabola )

    batch.draw(shader)

    gpu.state.line_width_set(1.0)
    gpu.state.blend_set('NONE')
    gpu.state.depth_test_set('NONE')

def draw_jumppad_parabola(obj, data, objects):

    if data.get("type") != "jumppad":
        return

    target_name = data.get("target")
    hangtime = data.get("hangtime")

    if not target_name or not hangtime:
        return

    target_obj = gamedata_find_object_by_name( objects, target_name )

    if not target_obj:
        return

    draw_ballistic_trajectory( obj.location, target_obj.location, hangtime )

def draw_gamedata_view(self, context):
    """Draw 3D gamedata visualization in the viewport."""

    for obj in context.view_layer.objects:
        if not obj.visible_get() or "ma" not in obj:
            continue

        # Empty string
        if not obj["ma"]:
            continue

        # Skip if too far away.
        rv3d = context.space_data.region_3d

        view_location = rv3d.view_matrix.inverted().translation

        if ( obj.location - view_location ).length > MA_Gamedata_Draw_View_Mgr.draw_distance:
            continue
     
        data = parse_gamedata_string((obj["ma"]))

        data = { key.lower(): value.lower() for key, value in data.items() }

        if data.get("type") == "lift":
            radius = gamedata_parse_int(data, "activeradius", MA_Gamedata_Draw_View_Mgr.lift_default_start)
            draw_wire_sphere( obj.location, radius, MA_Gamedata_Draw_View_Mgr.lift_color_start_call ) 

            radius = gamedata_parse_int(data, "activeradius2", MA_Gamedata_Draw_View_Mgr.lift_default_act)
            draw_wire_sphere( obj.location, radius, MA_Gamedata_Draw_View_Mgr.lift_color_start_act ) 

            if "displace" in data:
                displace = gamedata_parse_vector(data, "displace")

                radius = gamedata_parse_int(data, "activeradius", MA_Gamedata_Draw_View_Mgr.lift_default_start)
                draw_wire_sphere( obj.location + displace, radius, MA_Gamedata_Draw_View_Mgr.lift_color_end_call ) 

                radius = gamedata_parse_int(data, "activeradius2", MA_Gamedata_Draw_View_Mgr.lift_default_act)
                draw_wire_sphere( obj.location + displace, radius, MA_Gamedata_Draw_View_Mgr.lift_color_end_act )

        elif data.get("type") == "door":
            radius = gamedata_parse_int(data, "activeradius", MA_Gamedata_Draw_View_Mgr.door_default_radius)
            draw_wire_sphere( obj.location, radius, MA_Gamedata_Draw_View_Mgr.door_color_act ) 

        elif data.get("type") == "jumppad":
            draw_jumppad_parabola( obj, data, context.view_layer.objects )

class MA_Gamedata_Draw_View(bpy.types.Operator):
    """Toggle viewing gamedata in the 3D viewport"""

    bl_idname = "object.ma_gd_draw_view"
    bl_label = "Debug Visualization"

    def execute(self, context):
        if not MA_Gamedata_Draw_View_Mgr.is_enabled:

            MA_Gamedata_Draw_View_Mgr.handler_view = bpy.types.SpaceView3D.draw_handler_add( draw_gamedata_view, (self, context), 'WINDOW', 'POST_VIEW'  )

            MA_Gamedata_Draw_View_Mgr.is_enabled = True

            self.report( {'INFO'}, "Gamedata Debug Visualization enabled" )

        else:
            if MA_Gamedata_Draw_View_Mgr.handler_view: bpy.types.SpaceView3D.draw_handler_remove( MA_Gamedata_Draw_View_Mgr.handler_view, 'WINDOW' )

            MA_Gamedata_Draw_View_Mgr.handler_view = None

            MA_Gamedata_Draw_View_Mgr.is_enabled = False

            self.report( {'INFO'}, "Gamedata 3D Debug Visualization disabled" )

        return {'FINISHED'}