# Various helpful math functions to help with converting from Blender formatting to PASM formatting
# This module is outdated, update and/or merge functions based on BObj2F43MtxBONE

# BUILT IN
import copy
import math
#BLENDER
import mathutils

# Construct our left-handed matrix
left2RightMtx = mathutils.Matrix.Identity(4)
left2RightMtx[1][1] = 0.0
left2RightMtx[1][2] = 1.0
left2RightMtx[2][1] = 1.0
left2RightMtx[2][2] = 0.0

# Convert a Blender Object to a Fang Engine 4x3 Matrix with SCALING
def BObj2F43Mtx(obj):
    rotMtx = copy.deepcopy(obj.matrix_world)

    rotMtx = left2RightMtx @ rotMtx @ left2RightMtx
    
    # This is so stupid, should be a matrix not an array of floats
    outOrientation = [0.0 for i in range(12)]

    outOrientation[0]  = rotMtx[0][0]
    outOrientation[1]  = rotMtx[1][0]
    outOrientation[2]  = rotMtx[2][0]
     
    outOrientation[3]  = rotMtx[0][1]
    outOrientation[4]  = rotMtx[1][1]
    outOrientation[5]  = rotMtx[2][1]
     
    outOrientation[6]  = rotMtx[0][2]
    outOrientation[7]  = rotMtx[1][2]
    outOrientation[8]  = rotMtx[2][2]
    
    outOrientation[9]  =  obj.matrix_world.translation[0]
    outOrientation[10] =  obj.matrix_world.translation[2]
    outOrientation[11] =  obj.matrix_world.translation[1]
    
    return outOrientation

# Convert a Blender Object to a Fang Engine 4x3 Matrix with SCALING
def BObj2F43MtxCube(obj):
    loc = obj.matrix_local.to_translation()
    mat_loc = mathutils.Matrix.Translation(loc)

    rot = obj.matrix_local.to_quaternion()
    mat_rot = rot.to_matrix().to_4x4()

    rotMtx =  mat_loc @ mat_rot

    rotMtx = left2RightMtx @ rotMtx @ left2RightMtx
    
    # This is so stupid, should be a matrix not an array of floats
    outOrientation = [0.0 for i in range(12)]

    outOrientation[0]  = rotMtx[0][0]
    outOrientation[1]  = rotMtx[1][0]
    outOrientation[2]  = rotMtx[2][0]
     
    outOrientation[3]  = rotMtx[0][1]
    outOrientation[4]  = rotMtx[1][1]
    outOrientation[5]  = rotMtx[2][1]
     
    outOrientation[6]  = rotMtx[0][2]
    outOrientation[7]  = rotMtx[1][2]
    outOrientation[8]  = rotMtx[2][2]
    
    outOrientation[9]  =  obj.matrix_world.translation[0]
    outOrientation[10] =  obj.matrix_world.translation[2]
    outOrientation[11] =  obj.matrix_world.translation[1]
    
    return outOrientation
    
# PASM Lights are special and calculate their 4x3 matrix in a different way
def BObj2F43MtxLIGHT(obj):
    # Grab the rotation matrix
    rotMtx = obj.matrix_world.to_3x3()
    
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

# DONT TOUCH IT
def BObj2F43MtxBONE(obj):
    # This is so stupid, should be a matrix not an array of floats
    outOrientation = [0.0 for i in range(12)]
    
    hArmature = obj.id_data
    
    if obj.parent: rotMtx = obj.parent.matrix.inverted() @ obj.matrix
    else:          rotMtx = hArmature.matrix_world @ obj.matrix
    
    # Convert matrix from Blender's right-handed to PASM's left-handed
    rotMtx = left2RightMtx @ rotMtx @ left2RightMtx
    
    # Write out the rotation matrix
    outOrientation[0]  = rotMtx[0][0]
    outOrientation[1]  = rotMtx[1][0]
    outOrientation[2]  = rotMtx[2][0]
                       
    outOrientation[3]  = rotMtx[0][1]
    outOrientation[4]  = rotMtx[1][1]
    outOrientation[5]  = rotMtx[2][1]
                       
    outOrientation[6]  = rotMtx[0][2]
    outOrientation[7]  = rotMtx[1][2]
    outOrientation[8]  = rotMtx[2][2]
    
    # Assign Position
    outOrientation[9]  = rotMtx[0][3]
    outOrientation[10] = rotMtx[1][3]
    outOrientation[11] = rotMtx[2][3]
    
    return outOrientation

# This WORKS, DO NOT TOUCH UNLESS YOU ARE CRAZY!!!!!
def BObj2F43MtxHIERARCHY(inBone):
    # Convert pose bone matrix from object-space of the armature to world-space of the scene
    outOrientation = [0.0 for i in range(12)]

    rotMtx = copy.deepcopy(inBone.matrix)
    
    # Convert matrix from Blender's right-handed to PASM's left-handed
    rotMtx = left2RightMtx @ rotMtx @ left2RightMtx
    
    # Invert it
    rotMtx.invert()
    
    # Write out the rotation matrix
    outOrientation[0]  = rotMtx[0][0]
    outOrientation[1]  = rotMtx[1][0]
    outOrientation[2]  = rotMtx[2][0]
                       
    outOrientation[3]  = rotMtx[0][1]
    outOrientation[4]  = rotMtx[1][1]
    outOrientation[5]  = rotMtx[2][1]
                       
    outOrientation[6]  = rotMtx[0][2]
    outOrientation[7]  = rotMtx[1][2]
    outOrientation[8]  = rotMtx[2][2]
    
    # Assign Position
    outOrientation[9]  = rotMtx[0][3]
    outOrientation[10] = rotMtx[1][3]
    outOrientation[11] = rotMtx[2][3]
    
    return outOrientation
    
# Variation function for exporting cylinder so it faces +z instead of +y
def BObj2F43MtxCylinder(obj):

    mat_rot_x = mathutils.Matrix.Rotation(math.radians(90.0), 4, 'X')
    rotMtx = obj.matrix_world @ mat_rot_x

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