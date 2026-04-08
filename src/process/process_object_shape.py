# Module that processes an shape object and returns byte data

# FANG TOOLKIT
from ..defs import file_def_ape_shape
from . import g_class
from . import pasm_math
from .process_gamedata import ProcessGamedata

def ExportObjShape(obj):
    # Precompute lowercase name and common attributes
    name       = obj.name.lower()
    obj_type   = obj.type
    scale      = obj.scale
    empty_type = getattr(obj, "empty_display_type", None)

    bExitEarly  = False
    bIsParticle = False
    if name.startswith("off_"):  return              # Doesn't matter it's off bail early
    if obj_type != "EMPTY":      bExitEarly = True   # Objects are EMTPY or CURVE objects
    if obj_type == "CURVE":      bExitEarly = False  # Lines are shapes so must be excluded
    if name.startswith("obj_"):  bExitEarly = True   # objs could be ANY DATATYPE, so check for that
    if name.startswith("port_"): bExitEarly = True   # portals should be skipped
    if name.startswith("ambient") and obj_type == "EMPTY": bExitEarly = True  # Ambient cubes are lights, not shapes
    if name.startswith("start_")  and obj_type == "MESH":  bExitEarly = False # Little hack for Vissova so a mesh can represent a player start
    if name.startswith("part_")   and obj_type == "EMPTY": bIsParticle = True # Particles can be represented as a sphere, box or cylinder (Cone in Blender)
        
    if bExitEarly: return

    # Uniform scale check
    if round(scale.x, 5) != round(scale.y, 5) != round(scale.z, 5):
        if empty_type != "CUBE" and not bIsParticle:
            g_class.logError(
                f"OBJECT ERROR: The object {obj.name} does not have a uniform scale! "
                f"Found {scale[0]:.3f}, {scale[1]:.3f}, {scale[2]:.3f}... Skipping"
            )
            return
    
    # Init shape object
    outShape = file_def_ape_shape.PASMShape()
    
    # Handle "start_" hack for player start
    if name.startswith("start_") and obj_type == "MESH":
        outShape.nType = file_def_ape_shape.PASMShapeType_e.APE_SHAPE_TYPE_START_POINT
        outShape.typeData = file_def_ape_shape.PASMShapeStartPoint()
    
    # Determine shape type based on object type / empty display type
    if obj_type == "EMPTY":
        if empty_type == "CUBE":
            if name.startswith("start_"):
                outShape.nType = file_def_ape_shape.PASMShapeType_e.APE_SHAPE_TYPE_START_POINT
                outShape.typeData = file_def_ape_shape.PASMShapeStartPoint()
            else:
                outShape.nType = file_def_ape_shape.PASMShapeType_e.APE_SHAPE_TYPE_BOX
                outShape.typeData = file_def_ape_shape.PASMShapeBox()
        elif empty_type == "SPHERE":
            outShape.nType = file_def_ape_shape.PASMShapeType_e.APE_SHAPE_TYPE_SPHERE
            outShape.typeData = file_def_ape_shape.PASMShapeSphere()
        elif empty_type == "CONE":
            outShape.nType = file_def_ape_shape.PASMShapeType_e.APE_SHAPE_TYPE_CYLINDER
            outShape.typeData = file_def_ape_shape.PASMShapeCylinder()
            
    elif obj.type == "CURVE":
        spline = obj.data.splines[0]
        if spline.type != "POLY":
            g_class.logError(
                f"SPLINE ERROR: The spline object {obj.name} is a {spline.type} spline but only POLY splines are supported.\n"
                f"FIX: Select type in OBJECT mode > EDIT mode > Object Context Menu (Default is right click) > Set Spline Type > Poly"
            )
            return
        outShape.nType = file_def_ape_shape.PASMShapeType_e.APE_SHAPE_TYPE_SPLINE
        outShape.typeData = file_def_ape_shape.PASMShapeSpline()
    
    if outShape.nType == -1:
        return # Couldn't associate our object with any shape
    
    # Populate shape data       
    if outShape.nType == file_def_ape_shape.PASMShapeType_e.APE_SHAPE_TYPE_BOX:
        if obj.empty_display_size != 0.5:
            g_class.logError(
                f"TRIPWIRE ERROR: The empty object {obj.name} has a display size of "
                f"{obj.empty_display_size} which MUST be set to 0.5m.\n"
                f"FIX: Set Size in OBJECT mode > Properties > Object Data Properties > Set Size to 0.5"
            )
            return
        outShape.typeData.fLength = obj.scale[1]
        outShape.typeData.fWidth  = obj.scale[0]
        outShape.typeData.fHeight = obj.scale[2]
        
    elif outShape.nType == file_def_ape_shape.PASMShapeType_e.APE_SHAPE_TYPE_SPHERE:
        outShape.typeData.fRadius = obj.empty_display_size
        
    elif outShape.nType == file_def_ape_shape.PASMShapeType_e.APE_SHAPE_TYPE_CYLINDER:
        outShape.typeData.fRadius = obj.ma_ob_props.fCylinderWidth
        outShape.typeData.fHeight = obj.ma_ob_props.fCylinderHeight
        
    elif outShape.nType == file_def_ape_shape.PASMShapeType_e.APE_SHAPE_TYPE_SPLINE:
        spline = obj.data.splines[0]
        outShape.typeData.nNumPts = len(spline.points)
        outShape.typeData.bClosed = 1 if spline.use_cyclic_u else 0
        outShape.typeData.nNumSegments = 1 # Metal Arms only supports one chain of splines

        # Compute world-space coordinates directly (no duplication needed)
        world_matrix = obj.matrix_world
        for point in spline.points:
            co_world = world_matrix @ point.co
            outShape.userData.extend([co_world[0], co_world[2], co_world[1]])
    
    # Rotation Matrix fun
    
    # The cone tip is pointed towards +y but cylinder particles emit towards the +z direction in FANG
    # As an artist it's intuitive to see the cone tip as the emit direction
    # We can accomidate by rotating the object -90 degrees on the x-axis before converting to FANG Matrix
    if (outShape.nType == file_def_ape_shape.PASMShapeType_e.APE_SHAPE_TYPE_CYLINDER):
        outShape.mtxOrientation = pasm_math.BObj2F43MtxCylinder(obj)
    elif (outShape.nType == file_def_ape_shape.PASMShapeType_e.APE_SHAPE_TYPE_BOX):
        outShape.mtxOrientation = pasm_math.BObj2F43MtxCube(obj)
    else:
        outShape.mtxOrientation = pasm_math.BObj2F43Mtx(obj)
    
    # Determine entity type
    entity_type_map = {
        file_def_ape_shape.PASMShapeType_e.APE_SHAPE_TYPE_SPHERE:      "Sphere",
        file_def_ape_shape.PASMShapeType_e.APE_SHAPE_TYPE_CYLINDER:    "Cylinder",
        file_def_ape_shape.PASMShapeType_e.APE_SHAPE_TYPE_BOX:         "Box",
        file_def_ape_shape.PASMShapeType_e.APE_SHAPE_TYPE_START_POINT: "Sphere",
        file_def_ape_shape.PASMShapeType_e.APE_SHAPE_TYPE_SPLINE:      "Spline",
    }
    entityType = entity_type_map.get(outShape.nType, None)

    ProcessGamedata(obj, entityType, outShape)

    # Go back and patch up userData length
    dataLen = 0
    for data in outShape.userData:
        if type(data) == float:
            dataLen = dataLen + 4
        else:
            dataLen = dataLen + len(data)
    outShape.nBytesOfUserData = dataLen
    
    # Finally, write data to the file
    data = outShape.pack()
    g_class.g_FileOut.write(data)
    g_class.g_ApeHeader.fileSize += len(data)
    g_class.g_ApeHeader.nNumShapes += 1