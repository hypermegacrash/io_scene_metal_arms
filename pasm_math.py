# Various helpful math functions to help with converting from Blender formatting to PASM formatting

import bpy

from mathutils import Euler
from math import radians
import struct

def BRot2FRot(obj):
    # Rotation Matrix fun
    RMTXa = obj.rotation_euler
    RMTXb = RMTXa.to_matrix()
    
    #print("\nEuler Coordinates")
    #print(RMTXa)
    
    #print("\nBlender Rotation Matrix")
    #print(RMTXb)
    #print(obj.matrix_world.translation)
    
    #print("\nNegating column [2]")
    RMTXb[0][2] = -RMTXb[0][2]
    RMTXb[1][2] = -RMTXb[1][2]
    RMTXb[2][2] = -RMTXb[2][2]
    #print(RMTXb)
    
    #print("\nTranspose the matrix")
    RMTXb.transpose()
    #print(RMTXb)
    
    #print("\nSwap columns [1] and [2]")
    # temp buffer
    tempA = RMTXb[0][2]
    tempB = RMTXb[1][2]
    tempC = RMTXb[2][2]
    #print(tempA)
    #print(tempB)
    #print(tempC)
    
    # put Column [1] into [2]
    RMTXb[0][2] = RMTXb[0][1]
    RMTXb[1][2] = RMTXb[1][1]
    RMTXb[2][2] = RMTXb[2][1]
    
    # put temp into Column [1]
    RMTXb[0][1] = tempA
    RMTXb[1][1] = tempB
    RMTXb[2][1] = tempC
    
    # This is so stupid, should be a matrix not an array of floats
    outOrientation = [0.0 for i in range(12)]
    
    outOrientation[0] =  RMTXb[0][0]
    outOrientation[1] =  RMTXb[0][1]
    outOrientation[2] =  RMTXb[0][2]
    
    outOrientation[3] =  RMTXb[1][0]
    outOrientation[4] =  RMTXb[1][1]
    outOrientation[5] =  RMTXb[1][2]
    
    outOrientation[6] =  RMTXb[2][0]
    outOrientation[7] =  RMTXb[2][1]
    outOrientation[8] =  RMTXb[2][2]
    
    outOrientation[9] =   obj.matrix_world.translation[0]
    outOrientation[10] =  obj.matrix_world.translation[2]
    outOrientation[11] =  obj.matrix_world.translation[1]
    
    return outOrientation