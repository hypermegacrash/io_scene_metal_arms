# Various helpful math functions to help with converting from Blender formatting to PASM formatting

import mathutils # Need to work with matrix math

# Convert a Blender Object to a Fand Engine 4x3 Matrix
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
    
    
    
    