# This file is a collection of classes that represents sections of the PASM .mtx file format
# Each of them contain a function to take the class contents and pack them into an array of bytes

import struct # For modifying vars into bytes

class MTXHeader:
    """Header for the MTX file"""
    def __init__(self):
        self.nNumBones = 0
        self.nDataType = 0

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
        
        outBytes += struct.pack("<i", self.nNumBones)[:4]
        outBytes += struct.pack("<i", self.nDataType)[:4]
        
        return outBytes
        
class MTXBone:
    """Bone with all offsets to their orientations"""
    def __init__(self):
        self.szBoneName = ""
        self.nNumFrames = 0
        self.nFrameArrayOffset = 0

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()

        #string
        size = bytearray(32)
        size[0:len(self.szBoneName[0:31])] = bytes(self.szBoneName, "utf-8")[0:31]
        outBytes += size
        
        outBytes += struct.pack("<i", self.nNumFrames)[:4]
        outBytes += struct.pack("<i", self.nFrameArrayOffset)[:4]
        
        return outBytes
        
class MTXFrame:
    """Matrix data for x bone at y time from first frame"""
    def __init__(self):
        self.fStartingSecs = 0
        self.mtxOrientation = [0.0 for i in range(12)]

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
        
        outBytes += struct.pack("<f", self.fStartingSecs)[:4]
        
        for i in self.mtxOrientation:
            outBytes += struct.pack("<f", i)
        
        return outBytes