# Module that processes an shape object and returns byte data

# FANG TOOLKIT
from . import file_def_ape  # Get our PASM file classes
from . import g_class       # Get our global variables for the header data
from . import pasm_math     # PASM helper defs

def ExportObjShape(obj):
    bExitEarly = False
    
    if obj.name[:4].lower() == "off_": return               # Doesn't matter it's off bail early
    if obj.type             != "EMPTY": bExitEarly = True   # Objects are EMTPY or CURVE objects
    if obj.type             == "CURVE": bExitEarly = False  # Lines are shapes so must be excluded
    if obj.name[:4].lower() == "obj_":  bExitEarly = True   # objs could be ANY DATATYPE, so check for that
    if obj.name[:5].lower() == "port_": bExitEarly = True   # portals should be skipped
    if obj.name[:7].lower() == "ambient" and obj.type == "EMPTY": bExitEarly = True  # Ambient cubes are lights, not shapes
    if obj.name[:6].lower() == "start_"  and obj.type == "MESH":  bExitEarly = False # Little hack for Vissova so a mesh can represent a player start
        
    if(bExitEarly): return
        
    print(obj.name, "is a shape object")
    
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
        outShape.typeData.fLength = obj.scale[1]
        outShape.typeData.fWidth  = obj.scale[0]
        outShape.typeData.fHeight = obj.scale[2]
        
    if outShape.nType == file_def_ape.PASMShapeType_e.APE_SHAPE_TYPE_SPHERE:
        outShape.typeData.fRadius = obj.empty_display_size
        
    if outShape.nType == file_def_ape.PASMShapeType_e.APE_SHAPE_TYPE_SPLINE:
        outShape.typeData.nNumPts = len(obj.data.splines[0].points)
        # Actually check this
        outShape.typeData.bClosed = 0 
        # I think you can have multiple seperate chains of splines
        # in a single node, must be tested but assume 1 for now
        outShape.typeData.nNumSegments = 1
        
        for point in obj.data.splines[0].points:
            # Multiply our world position matrix by the vertex position X Y Z to get world space position of verts
            PosAfterWTM = obj.matrix_world @ point.co
            outShape.userData.append(PosAfterWTM[0])
            outShape.userData.append(PosAfterWTM[2])
            outShape.userData.append(PosAfterWTM[1])
    
    # Rotation Matrix fun
    outShape.mtxOrientation = pasm_math.BObj2F43Mtx(obj)
    
    # Grab custom properties from the object
    try:
        cmds = obj["ma"].split('\n')
        x = 0
        for index in cmds:
            if index == "" or index.isspace(): continue # Check if string is empty
            if index[0] == "#":                continue # Check if comment line
            x += 1
            a = index.find("=")
            i = a - 1
            j = a + 1
            while index[i] == " ":
                i = i - 1
            while index[j] == " ":
                j = j + 1
            outShape.userData.append(index[:i + 1] + "=" + index[j:])
            if x < len(cmds):
                outShape.userData.append(str('\x0D\x0A'))
    except:
        print("No Custom Properties")
    
    # Go back and patch up userData length
    dataLen = 0
    for data in outShape.userData:
        if type(data) == float:
            dataLen = dataLen + 4
        else:
            dataLen = dataLen + len(data)
    outShape.nBytesOfUserData = dataLen
    
    # Finally, write data to the file, and our header
    g_class.file.write(outShape.packBytes())
    g_class.gApeHeader.fileSize += len(outShape.packBytes())
    g_class.gApeHeader.nNumShapes += 1