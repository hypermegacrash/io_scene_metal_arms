# Module that processes an shape object and returns byte data

# FANG TOOLKIT
from . import file_def_ape  # Get our PASM file classes
from . import g_class       # Get our global variables for the header data
from . import pasm_math     # PASM helper defs
from .process_gamedata import ProcessGamedata # Import just the Gamedata Parser
import bpy

def ExportObjShape(obj):
    bExitEarly = False
    bIsParticle = False
    
    if obj.name[:4].lower() == "off_": return               # Doesn't matter it's off bail early
    if obj.type             != "EMPTY": bExitEarly = True   # Objects are EMTPY or CURVE objects
    if obj.type             == "CURVE": bExitEarly = False  # Lines are shapes so must be excluded
    if obj.name[:4].lower() == "obj_":  bExitEarly = True   # objs could be ANY DATATYPE, so check for that
    if obj.name[:5].lower() == "port_": bExitEarly = True   # portals should be skipped
    if obj.name[:7].lower() == "ambient" and obj.type == "EMPTY": bExitEarly = True  # Ambient cubes are lights, not shapes
    if obj.name[:6].lower() == "start_"  and obj.type == "MESH":  bExitEarly = False # Little hack for Vissova so a mesh can represent a player start
    if obj.name[:5].lower() == "part_"   and obj.type == "EMPTY": bIsParticle = True # Particles can be represented as a sphere, box or cylinder (Cone in Blender)
        
    if(bExitEarly): return
        
    # print(obj.name, "is a shape object")

    if round(obj.scale.x, 5) != round(obj.scale.y, 5) != round(obj.scale.z, 5):
        if obj.empty_display_type != "CUBE" and not bIsParticle:
            g_class.logError(f"OBJECT ERROR: The object object {obj.name} does not have a uniform scale! Found {obj.scale[0]:.3f}, {obj.scale[1]:.3f}, {obj.scale[2]:.3f}... Skipping")
            return
    
    outShape = file_def_ape.PASMShape()
    
    # Little hack PT 2 for Vissova so a mesh can represent a player start
    if obj.name[:6].lower() == "start_" and obj.type == "MESH":
        outShape.nType = file_def_ape.PASMShapeType_e.APE_SHAPE_TYPE_START_POINT
        outShape.typeData = file_def_ape.PASMShapeStartPoint()
    
    # Because we deal with shapes that aren't always empties
    if obj.type == "EMPTY":
        if obj.empty_display_type == "CUBE":
            if(obj.name.find("start_", 0, 6) != -1):
                outShape.nType = file_def_ape.PASMShapeType_e.APE_SHAPE_TYPE_START_POINT
                outShape.typeData = file_def_ape.PASMShapeStartPoint()
            else:
                # Making an assumption by process of elimination it must be a box volume
                outShape.nType = file_def_ape.PASMShapeType_e.APE_SHAPE_TYPE_BOX
                outShape.typeData = file_def_ape.PASMShapeBox()
        if obj.empty_display_type == "SPHERE":
            outShape.nType = file_def_ape.PASMShapeType_e.APE_SHAPE_TYPE_SPHERE
            outShape.typeData = file_def_ape.PASMShapeSphere()
        if obj.empty_display_type == "CONE":
            outShape.nType = file_def_ape.PASMShapeType_e.APE_SHAPE_TYPE_CYLINDER
            outShape.typeData = file_def_ape.PASMShapeCylinder()    
            #bIsParticle = True
            
    if obj.type == "CURVE":
        if obj.data.splines[0].type != "POLY":
            g_class.logError("SPLINE ERROR: The spline object " + obj.name + " is a " + obj.data.splines[0].type + " spline but only POLY splines are supported.\n" +
                             "FIX: Select " + obj.name + " in OBJECT mode > EDIT mode > Object Context Menu (Default is right click) > Set Spline Type > Poly")
            return
        outShape.nType = file_def_ape.PASMShapeType_e.APE_SHAPE_TYPE_SPLINE
        outShape.typeData = file_def_ape.PASMShapeSpline()
    
    if outShape.nType == -1:
        # Couldn't associate our object with any shape
        return
        
    if outShape.nType == file_def_ape.PASMShapeType_e.APE_SHAPE_TYPE_BOX:
        if obj.empty_display_size != 0.5:
            g_class.logError("TRIPWIRE ERROR: The empty object " + obj.name + " has a display size of " + str(obj.empty_display_size) + " which MUST be set to 0.5m to show dimensions of the tripwire as it will appear ingame.\n" +
                             "FIX: Select " + obj.name + " in OBJECT mode > Properties > Object Data Properties > Set Size to 0.5")
            return
        outShape.typeData.fLength = obj.scale[1]
        outShape.typeData.fWidth  = obj.scale[0]
        outShape.typeData.fHeight = obj.scale[2]
        
    if outShape.nType == file_def_ape.PASMShapeType_e.APE_SHAPE_TYPE_SPHERE:
        outShape.typeData.fRadius = obj.empty_display_size
        
    if outShape.nType == file_def_ape.PASMShapeType_e.APE_SHAPE_TYPE_CYLINDER:
        outShape.typeData.fRadius = obj.ma_ob_props.fCylinderWidth
        outShape.typeData.fHeight = obj.ma_ob_props.fCylinderHeight
        
    if outShape.nType == file_def_ape.PASMShapeType_e.APE_SHAPE_TYPE_SPLINE:
        outShape.typeData.nNumPts = len(obj.data.splines[0].points)
        
        if obj.data.splines[0].use_cyclic_u:
            outShape.typeData.bClosed = 1
        else:
            outShape.typeData.bClosed = 0
            
        # Metal Arms only supports one chain of splines
        outShape.typeData.nNumSegments = 1


        # To not destroy the existing scene, we will duplicate the input object
        # we want to modify then delete after we finish exporting segments
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.duplicate()

        # Assign a handle to our new work object
        workObj = bpy.context.view_layer.objects.active

        # Apply transformation, rotation, scale, etc
        bpy.ops.object.select_all(action="DESELECT")
        workObj.select_set(True)
        bpy.context.view_layer.objects.active = workObj
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True, properties=False)
        
        for point in workObj.data.splines[0].points:
            # Multiply our world position matrix by the vertex position X Y Z to get world space position of verts
            PosAfterWTM = workObj.matrix_world @ point.co
            outShape.userData.append(PosAfterWTM[0])
            outShape.userData.append(PosAfterWTM[2])
            outShape.userData.append(PosAfterWTM[1])

        bpy.ops.object.select_all(action="DESELECT")
        workObj.select_set(True)
        bpy.ops.object.delete()
    
    # Rotation Matrix fun
    
    # The cone tip is pointed towards +y but cylinder particles emit towards the +z direction in FANG
    # As an artist it's intuitive to see the cone tip as the emit direction
    # We can accomidate by rotating the object -90 degrees on the x-axis before converting to FANG Matrix
    if (outShape.nType == file_def_ape.PASMShapeType_e.APE_SHAPE_TYPE_CYLINDER):
        outShape.mtxOrientation = pasm_math.BObj2F43MtxCylinder(obj)
    elif (outShape.nType == file_def_ape.PASMShapeType_e.APE_SHAPE_TYPE_BOX):
        outShape.mtxOrientation = pasm_math.BObj2F43MtxCube(obj)
    else:
        outShape.mtxOrientation = pasm_math.BObj2F43Mtx(obj)
    
    # Get the current gamedata type to pass along
    entityType = None
    match outShape.nType:
        case file_def_ape.PASMShapeType_e.APE_SHAPE_TYPE_SPHERE:      entityType = "Sphere"
        case file_def_ape.PASMShapeType_e.APE_SHAPE_TYPE_CYLINDER:    entityType = "Cylinder"
        case file_def_ape.PASMShapeType_e.APE_SHAPE_TYPE_BOX:         entityType = "Box"
        case file_def_ape.PASMShapeType_e.APE_SHAPE_TYPE_SPAWN_POINT: entityType = "Sphere"
        case file_def_ape.PASMShapeType_e.APE_SHAPE_TYPE_START_POINT: entityType = "Sphere"
        case file_def_ape.PASMShapeType_e.APE_SHAPE_TYPE_SPLINE:      entityType = "Spline"

    ProcessGamedata(obj, entityType, outShape)
    
    # Finally, write data to the file, and our header
    g_class.file.write(outShape.packBytes())
    g_class.gApeHeader.fileSize += len(outShape.packBytes())
    g_class.gApeHeader.nNumShapes += 1