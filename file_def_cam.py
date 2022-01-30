# This file is a collection of classes that represents sections of the PASM .cam file format
# Each of them contain a function to take the class contents and pack them into an array of bytes

import struct # For modifying vars into bytes

class PASMCamHeader:
    def __init__(self):
        self.fRadius = 0
        self.PAD = bytearray(12)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
   
        outBytes += struct.pack("<f", self.fRadius)
        outBytes += self.PAD
        
        return outBytes
        
class PASMCamInfo:
    def __init__(self):
        self.magic = "FANG"
        self.FVersion_Sub = 0
        self.FVersion_Minor = 5
        self.FVersion_Major = 1
        self.FVersion_Platform = 8
        
        self.nBytesInFile = 0
    
        self.szCameraName = ""
        self.nFrames = 0
        self.nBytesOfUserData = 0
        self.nOffsetToString = 0
    
        self.PAD = bytearray(64)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
        
        #string
        size = bytearray(4)
        size = bytes(str(self.magic), "utf-8")
        outBytes += size
        
        #uint8_t
        # Using "<" format char because struct.pack returns incorrect length if unspecified on one person's Mac
        outBytes += struct.pack("<b", self.FVersion_Sub)
        outBytes += struct.pack("<b", self.FVersion_Minor)
        outBytes += struct.pack("<b", self.FVersion_Major)
        outBytes += struct.pack("<b", self.FVersion_Platform)
   
        outBytes += struct.pack("<i", self.nBytesInFile)
        
        size = bytearray(16)
        size[0:len(self.szBoneName[0:11])] = bytes(self.szBoneName, "utf-8")[0:11]
        outBytes += size
        
        outBytes += struct.pack("<i", self.nFrames)
        outBytes += struct.pack("<i", self.nBytesOfUserData)
        outBytes += struct.pack("<i", self.nOffsetToString)
        
        outBytes += self.PAD
        
        return outBytes
        
class PASMCamFrame:
    def __init__(self):
        self.fSecsFromStart = 0
        self.fFOV = 0;
        self.mtxOrientation = [0.0 for i in range(12)]

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
        
        outBytes += struct.pack("<f", self.fSecsFromStart)
        outBytes += struct.pack("<f", self.fFOV)
        
        for i in self.mtxOrientation:
            outBytes += struct.pack("<f", i)
        
        return outBytes
        
        
