# Various helpful math functions to help with converting from Blender formatting to PASM formatting

import mathutils # Need to work with matrix math

# Convert a Blender Object to a Fang Engine 4x3 Matrix
def BObj2F43Mtx(obj):
    rotMtx = obj.rotation_euler
    rotMtx = rotMtx.to_matrix()

    rotMtx.transpose()

    left2RightMtx = mathutils.Matrix.Identity(3)
    left2RightMtx[1][1] = 0.0
    left2RightMtx[1][2] = 1.0
    left2RightMtx[2][1] = 1.0
    left2RightMtx[2][2] = 0.0

    rotMtx = left2RightMtx @ rotMtx @ left2RightMtx
    
    # This is so stupid, should be a matrix not an array of floats
    outOrientation = [0.0 for i in range(12)]
    
    outOrientation[0] =  rotMtx[0][0]
    outOrientation[1] =  rotMtx[0][1]
    outOrientation[2] =  rotMtx[0][2]
    
    outOrientation[3] =  rotMtx[1][0]
    outOrientation[4] =  rotMtx[1][1]
    outOrientation[5] =  rotMtx[1][2]
    
    outOrientation[6] =  rotMtx[2][0]
    outOrientation[7] =  rotMtx[2][1]
    outOrientation[8] =  rotMtx[2][2]
    
    outOrientation[9] =   obj.matrix_world.translation[0]
    outOrientation[10] =  obj.matrix_world.translation[2]
    outOrientation[11] =  obj.matrix_world.translation[1]
    
    return outOrientation
    
# Convert a Blender Object to a Fang Engine 4x3 Matrix with SCALING
def BObj2F43MtxSCALE(obj):
    rotMtx = obj.rotation_euler
    rotMtx = rotMtx.to_matrix()

    rotMtx.transpose()

    left2RightMtx = mathutils.Matrix.Identity(3)
    left2RightMtx[1][1] = 0.0
    left2RightMtx[1][2] = 1.0
    left2RightMtx[2][1] = 1.0
    left2RightMtx[2][2] = 0.0
    
    # We only apply scale if it is uniform
    if(obj.scale[0] == obj.scale[1] == obj.scale[2]):
        pass
        #print("SCALE UNIFORM")
        rotMtx[0][0] = obj.scale[0] * rotMtx[0][0]
        rotMtx[0][1] = obj.scale[0] * rotMtx[0][1]
        rotMtx[0][2] = obj.scale[0] * rotMtx[0][2]
        
        rotMtx[1][0] = obj.scale[0] * rotMtx[1][0]
        rotMtx[1][1] = obj.scale[0] * rotMtx[1][1]
        rotMtx[1][2] = obj.scale[0] * rotMtx[1][2]
        
        rotMtx[2][0] = obj.scale[0] * rotMtx[2][0]
        rotMtx[2][1] = obj.scale[0] * rotMtx[2][1]
        rotMtx[2][2] = obj.scale[0] * rotMtx[2][2]
    else:
        pass
        #print("SCALE NOT UNIFORM")

    rotMtx = left2RightMtx @ rotMtx @ left2RightMtx
    
    # This is so stupid, should be a matrix not an array of floats
    outOrientation = [0.0 for i in range(12)]
    
    outOrientation[0] =  rotMtx[0][0]
    outOrientation[1] =  rotMtx[0][1]
    outOrientation[2] =  rotMtx[0][2]
    
    outOrientation[3] =  rotMtx[1][0]
    outOrientation[4] =  rotMtx[1][1]
    outOrientation[5] =  rotMtx[1][2]
    
    outOrientation[6] =  rotMtx[2][0]
    outOrientation[7] =  rotMtx[2][1]
    outOrientation[8] =  rotMtx[2][2]
    
    outOrientation[9] =   obj.matrix_world.translation[0]
    outOrientation[10] =  obj.matrix_world.translation[2]
    outOrientation[11] =  obj.matrix_world.translation[1]
    
    return outOrientation
    
# PASM Lights are special and calculate their 4x3 matrix in a different way
def BObj2F43MtxLIGHT(obj):
    # Rotation Matrix fun
    rotMtx = obj.rotation_euler
    rotMtx = rotMtx.to_matrix()
    
    # Negating column [2]
    rotMtx[0][2] = -rotMtx[0][2]
    rotMtx[1][2] = -rotMtx[1][2]
    rotMtx[2][2] = -rotMtx[2][2]
    
    rotMtx.transpose()
    
    # Swap columns [1] and [2]
    tempA = rotMtx[0][2]
    tempB = rotMtx[1][2]
    tempC = rotMtx[2][2]
    
    # put Column [1] into [2]
    rotMtx[0][2] = rotMtx[0][1]
    rotMtx[1][2] = rotMtx[1][1]
    rotMtx[2][2] = rotMtx[2][1]
    
    # put temp into Column [1]
    rotMtx[0][1] = tempA
    rotMtx[1][1] = tempB
    rotMtx[2][1] = tempC
    
    # This is so stupid, should be a matrix not an array of floats
    outOrientation = [0.0 for i in range(12)]
    
    outOrientation[0] =  rotMtx[0][0]
    outOrientation[1] =  rotMtx[0][1]
    outOrientation[2] =  rotMtx[0][2]
    
    outOrientation[3] =  rotMtx[1][0]
    outOrientation[4] =  rotMtx[1][1]
    outOrientation[5] =  rotMtx[1][2]
    
    outOrientation[6] =  rotMtx[2][0]
    outOrientation[7] =  rotMtx[2][1]
    outOrientation[8] =  rotMtx[2][2]
    
    outOrientation[9] =   obj.matrix_world.translation[0]
    outOrientation[10] =  obj.matrix_world.translation[2]
    outOrientation[11] =  obj.matrix_world.translation[1]
    
    return outOrientation
    
def BObj2F43MtxBONE(obj):
    rotMtx = obj.matrix.to_euler()
    # We need the bone rotation in local space
    # Since we inherit the parent bone's rotation
    # we must subtract that to get this bone's own rotation
    try:
        rotMtxParent = obj.parent.matrix.to_euler()
        #print("rotMtx: ", rotMtx)
        #print("rotMtx Parent: ", rotMtxParent)
        rotMtx[0] = rotMtx[0] - rotMtxParent[0]
        rotMtx[1] = rotMtx[1] - rotMtxParent[1]
        rotMtx[2] = rotMtx[2] - rotMtxParent[2]
        #print(rotMtx)
    except:
        None
    rotMtx = rotMtx.to_matrix()
    
    rotMtx.transpose()

    left2RightMtx = mathutils.Matrix.Identity(3)
    left2RightMtx[1][1] = 0.0
    left2RightMtx[1][2] = 1.0
    left2RightMtx[2][1] = 1.0
    left2RightMtx[2][2] = 0.0

    rotMtx = left2RightMtx @ rotMtx @ left2RightMtx
    
    # This is so stupid, should be a matrix not an array of floats
    outOrientation = [0.0 for i in range(12)]
    
    outOrientation[0] =  rotMtx[0][0]
    outOrientation[1] =  rotMtx[0][1]
    outOrientation[2] =  rotMtx[0][2]
    
    outOrientation[3] =  rotMtx[1][0]
    outOrientation[4] =  rotMtx[1][1]
    outOrientation[5] =  rotMtx[1][2]
    
    outOrientation[6] =  rotMtx[2][0]
    outOrientation[7] =  rotMtx[2][1]
    outOrientation[8] =  rotMtx[2][2]
    
    # Bone position is relative to it's parent as a starting position
    try:
        Translation = obj.head - obj.parent.head
    except:
        Translation = obj.head
    
    outOrientation[9] =   Translation[0]
    outOrientation[10] =  Translation[2]
    outOrientation[11] =  Translation[1]
    
    return outOrientation
    
# Blender stores Color RGB values from UI in scene color, PASM expects them in sRGB format
# https://blender.stackexchange.com/questions/218312/python-how-to-color-accurately-convert-from-rgb-0-255-format-to-values-in-0-0f
def color_scene_linear_to_srgb(c):
  if (c < 0.0031308):
    if (c < 0.0):
        return 0.0
    else:
        return c * 12.92
  else:
    return 1.055 * pow(c, 1.0 / 2.4) - 0.055   
    
    
    
    
    
    