# Module that processes an shape object and returns byte data

from . import pasm_file_def # Get our PASM file classes

from . import g_class # Get our global variables for the header data

from . import pasm_math # PASM helper defs

def ExportObjShape(obj):
    # Ugly temp hack to let Vissova use a mesh of Glitch to represent a player start
    if(obj.name.find("start_", 0, 6) != -1) and obj.type == "MESH":
        outShape = pasm_file_def.PASMShape()
        outShape.nType = pasm_file_def.PASMShapeType_e.APE_SHAPE_TYPE_START_POINT
        outShape.typeData = pasm_file_def.PASMShapeStartPoint()
        
        # Rotation Matrix fun
        outShape.mtxOrientation = pasm_math.BObj2F43Mtx(obj)
    
        # Grab custom properties from the object
        if len(obj.keys()) > 1:
            # First item is _RNA_UI
            index = 2
            for K in obj.keys():        
                if K not in '_RNA_UI':
                    outShape.userData.append(str(K) + "=" + str(obj[K]))
                    if index < len(obj.keys()):
                        index += 1
                        outShape.userData.append(str('\x0D\x0A'))
     
        # Go back and patch up userData length
        dataLen = 0
        for data in outShape.userData:
            dataLen = dataLen + len(data)
        outShape.nBytesOfUserData = dataLen
    
        # Finally, write data to the file, and our header
        g_class.file.write(outShape.packBytes())
        g_class.gWldHeader.fileSize += len(outShape.packBytes())
        g_class.gWldHeader.nNumShapes += 1
        
        return

    if obj.type != "EMPTY":
        return
    #objs could be ANY DATATYPE, so check for that
    if(obj.name.find("obj_", 0, 4) != -1):
        return
        
    print(obj.name, "is a shape object")
    
    outShape = pasm_file_def.PASMShape()
    
    if obj.empty_display_type == "CUBE":
        if(obj.name.find("start_", 0, 6) != -1):
            outShape.nType = pasm_file_def.PASMShapeType_e.APE_SHAPE_TYPE_START_POINT
            outShape.typeData = pasm_file_def.PASMShapeStartPoint()
        else:
            # Making an assumption by process of elimination it must be a box volume
            outShape.nType = pasm_file_def.PASMShapeType_e.APE_SHAPE_TYPE_BOX
            outShape.typeData = pasm_file_def.PASMShapeBox()
    if obj.empty_display_type == "SPHERE":
        outShape.nType = pasm_file_def.PASMShapeType_e.APE_SHAPE_TYPE_SPHERE
        outShape.typeData = pasm_file_def.PASMShapeSphere()
    
    if outShape.nType == -1:
        # Couldn't associate empty with shape, just return
        return
        
    if outShape.nType == pasm_file_def.PASMShapeType_e.APE_SHAPE_TYPE_BOX:
        outShape.typeData.fLength = obj.scale[1]
        outShape.typeData.fWidth = obj.scale[0]
        outShape.typeData.fHeight = obj.scale[2]
        
    if outShape.nType == pasm_file_def.PASMShapeType_e.APE_SHAPE_TYPE_SPHERE:
        outShape.typeData.fRadius = obj.empty_display_size
    
    # Rotation Matrix fun
    outShape.mtxOrientation = pasm_math.BObj2F43Mtx(obj)
    
    # Grab custom properties from the object
    if len(obj.keys()) > 1:
        # First item is _RNA_UI
        index = 2
        for K in obj.keys():        
            if K not in '_RNA_UI':
                outShape.userData.append(str(K) + "=" + str(obj[K]))
                if index < len(obj.keys()):
                    index += 1
                    outShape.userData.append(str('\x0D\x0A'))
     
    # Go back and patch up userData length
    dataLen = 0
    for data in outShape.userData:
        dataLen = dataLen + len(data)
    outShape.nBytesOfUserData = dataLen
    
    # Finally, write data to the file, and our header
    g_class.file.write(outShape.packBytes())
    g_class.gWldHeader.fileSize += len(outShape.packBytes())
    g_class.gWldHeader.nNumShapes += 1