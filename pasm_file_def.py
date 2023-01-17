# This file is a collection of classes that represents sections of the PASM file format
# Each of them contain a function to take the class contents and pack them into an array of bytes

import struct # For modifying vars into bytes

#################
# HEADER DEFINITION
# Flags for special material effect in Layers
# Size: 84h
class PASMHeader:
    def __init__(self):
        self.magic = "FANG"
        self.FVersion_Sub = 0
        self.FVersion_Minor = 5
        self.FVersion_Major = 1
        self.FVersion_Platform = 8
        self.fileSize = 132
        self.sceneName = ""
        self.bWld = 0
        self.nNumBones = 0
        self.nNumCells = 0
        self.nNumLights = 0
        self.nNumVisPortals = 0
        self.nNumObjects = 0
        self.nNumFogs = 0 # Deprecated
        self.nNumSegments = 0
        self.nNumShapes = 0
        self.nSizeOfBoneStruct = 176
        self.nSizeOfLightStruct = 228
        self.nSizeOfObjectStruct = 112
        self.nSizeOfFogStruct = 44
        self.nSizeOfSegmentStruct = 48
        self.nSizeOfMaterialStruct = 1692
        self.nSizeOfVertStruct = 188
        self.nSizeOfVertIndexStruct = 20
        self.nSizeOfShapeStruct = 88
        self.PAD = bytearray(66)

    def packBytes(self):
        import struct
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

        outBytes += struct.pack("<I", self.fileSize)
        
        size = bytearray(16)
        size[0:len(self.sceneName[0:15])] = bytes(self.sceneName, "utf-8")[0:15]
        outBytes += size
        
        # There was an issue on one person's Mac where the length of this was becoming 8 instead of 4, even with "<" format char
        # No idea why this happens but forcing struct.pack to return only the first 4 bytes fixes this
        outBytes += struct.pack("<i", self.bWld)[:4]

        outBytes += struct.pack("<h", self.nNumBones)
        outBytes += struct.pack("<h", self.nNumCells)
        outBytes += struct.pack("<h", self.nNumLights)
        outBytes += struct.pack("<h", self.nNumVisPortals)
        outBytes += struct.pack("<h", self.nNumObjects)
        outBytes += struct.pack("<h", self.nNumFogs)
        outBytes += struct.pack("<h", self.nNumSegments)
        outBytes += struct.pack("<h", self.nNumShapes)

        outBytes += struct.pack("<h", self.nSizeOfBoneStruct)
        outBytes += struct.pack("<h", self.nSizeOfLightStruct)
        outBytes += struct.pack("<h", self.nSizeOfObjectStruct)
        outBytes += struct.pack("<h", self.nSizeOfFogStruct)
        outBytes += struct.pack("<h", self.nSizeOfSegmentStruct)
        outBytes += struct.pack("<h", self.nSizeOfMaterialStruct)
        outBytes += struct.pack("<h", self.nSizeOfVertStruct)
        outBytes += struct.pack("<h", self.nSizeOfVertIndexStruct)
        outBytes += struct.pack("<h", self.nSizeOfShapeStruct)
        
        outBytes += self.PAD
        
        return outBytes
 
 ################# 
# BONE DEFINITIONS
# Bones only exist in .ape files, not in .wld files
class PASMBone:
    def __init__(self):
        self.szBoneName = ""
        self.nFlags = 0
        self.nBoneIndex = 0
        self.nParentIndex = -1
        self.mtxOrientation = [0.0 for i in range(12)]
        self.nNumChildren = 0
        self.auChildIndices = [0 for i in range(64)]
        self.PAD = bytearray(16)
        
    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
        
        size = bytearray(32)
        size[0:len(self.szBoneName[0:31])] = bytes(self.szBoneName, "utf-8")[0:31]
        outBytes += size
        
        outBytes += struct.pack("<i", self.nFlags)[:4]
        outBytes += struct.pack("<i", self.nBoneIndex)[:4]
        outBytes += struct.pack("<i", self.nParentIndex)[:4]
        
        for i in self.mtxOrientation:
            outBytes += struct.pack("<f", i)
            
        outBytes += struct.pack("<i", self.nNumChildren)[:4]
        
        for i in self.auChildIndices:
            outBytes += struct.pack("<b", i)

        outBytes += self.PAD
        
        return outBytes
        
class PASMWeight:
    def __init__(self):
        self.fBoneIndex = 0.0
        self.fWeight = 0.0
        self.PAD = bytearray(16)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()

        outBytes += struct.pack("<f", self.fBoneIndex)
        outBytes += struct.pack("<f", self.fWeight)

        outBytes += self.PAD

        return outBytes
        
################# 
# LIGHT DEFINITIONS
# Flags for special material effect in Layers
# How does one properly enum in Python? Ehhh who cares put it all in a class
class PASMLightType_e():
    APE_LIGHT_TYPE_SPOT = 0
    APE_LIGHT_TYPE_OMNI = 1
    APE_LIGHT_TYPE_DIR = 2
    APE_LIGHT_TYPE_AMBIENT = 3

class PASMLightFlag_e():
    APE_LIGHT_FLAG_DONT_USE_RGB				= 0x00000001	# Disregard the light's rgb and only use the motif's color (default = off)
    APE_LIGHT_FLAG_LIGHT_SELF				= 0x00000002	# Light the object that the light is attached to (default = off)
    APE_LIGHT_FLAG_OBJ_DONT_LIGHT_TERRAIN	= 0x00000004	# Lights attached to this object don't light the terrain (default = off)

    APE_LIGHT_FLAG_PER_PIXEL				= 0x00000008	# This light casts a projection on the environment (may or may not have a texture)

    APE_LIGHT_FLAG_LIGHTMAP_ONLY_LIGHT		= 0x00000010	# This light will only be used in the lightmap portion of PASM and will not be exported to the engine.
    APE_LIGHT_FLAG_LIGHTMAP_LIGHT			= 0x00000020	# This light is to be used for generating lightmaps (If it is not dynamic, it can be discarded prior to the engine)
    APE_LIGHT_FLAG_UNIQUE_LIGHTMAP			= 0x00000040	# This light will generate its own unique lightmap in the lightmapping phase (it must also have a unique m_nLightID)

    APE_LIGHT_FLAG_CORONA					= 0x00000080	# This light has a corona
    APE_LIGHT_FLAG_CORONA_PROXFADE			= 0x00000100	# Fade the corona as the camera gets closer.

    APE_LIGHT_FLAG_CAST_SHADOWS				= 0x00000200	# This light will cast shadows (only relevant for engine lights)

    APE_LIGHT_FLAG_DYNAMIC_ONLY				= 0x00000400	# This light will not affect static objects

    APE_LIGHT_FLAG_MESH_MUST_BE_PER_PIXEL	= 0x00000800	# For per-pixel lights that have a projected texture.  If this flag is set, only objects that are flagged
                                                            # as per pixel lit will have the texture projected on them.  Others will just apply as a dynamic vertex light

class PASMLight:
    def __init__(self):
        self.nApeLightType = 0
        self.szLightName = ""
        self.Sphere = [0.0 for i in range(4)]
        self.Direction = [0.0 for i in range(3)]
        self.Color = [0.0 for i in range(3)]
        self.Intensity = 0.0
        self.fSpotInnerAngle = 0.0
        self.fSpotOuterAngle = 0.0
        self.nFlags = 0
        self.nMotifID = 0
        self.fCoronaScale = 1.0
        self.mtxOrientation = [0.0 for i in range(12)]
        self.szCoronaTexture = ""
        self.szPerPixelTexture = ""
        self.nLightID = -1
        self.szParentBoneName = "Scene Root"
        self.PAD = bytearray(30)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()

        outBytes += struct.pack("<i", self.nApeLightType)[:4]

        size = bytearray(16)
        size[0:len(self.szLightName[0:15])] = bytes(self.szLightName, "utf-8")[0:15]
        outBytes += size

        for i in self.Sphere:
            outBytes += struct.pack("<f", i)

        for i in self.Direction:
            outBytes += struct.pack("<f", i)

        for i in self.Color:
            outBytes += struct.pack("<f", i)

        outBytes += struct.pack("<f", self.Intensity)
        outBytes += struct.pack("<f", self.fSpotInnerAngle)
        outBytes += struct.pack("<f", self.fSpotOuterAngle)
        outBytes += struct.pack("<i", self.nFlags)[:4]
        outBytes += struct.pack("<i", self.nMotifID)[:4]
        outBytes += struct.pack("<f", self.fCoronaScale)

        for i in self.mtxOrientation:
            outBytes += struct.pack("<f", i)

        size = bytearray(16)
        size[0:len(self.szCoronaTexture[0:15])] = bytes(self.szCoronaTexture, "utf-8")[0:15]
        outBytes += size

        size = bytearray(16)
        size[0:len(self.szPerPixelTexture[0:15])] = bytes(self.szPerPixelTexture, "utf-8")[0:15]
        outBytes += size

        outBytes += struct.pack("<h", self.nLightID)

        size = bytearray(32)
        size[0:len(self.szParentBoneName[0:31])] = bytes(self.szParentBoneName, "utf-8")[0:31]
        outBytes += size

        outBytes += self.PAD
        
        return outBytes

################# 
# OBJECT DEFINITIONS
class PASMObject:
    def __init__(self):
        self.szObjectName = ""
        self.nFlags = 0
        self.mtxOrientation = [0.0 for i in range(12)]
        self.nBytesOfUserData = 0
        self.fCullDistance = 0
        self.nParentIndex = 0
        self.TintRGB = [0.0 for i in range(3)]
        self.PAD = bytearray(20)
        self.userData = [] # User Data is gonna be an array of string commands

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
        
        size = bytearray(16)
        size[0:len(self.szObjectName[0:11])] = bytes(self.szObjectName, "utf-8")[0:11]
        outBytes += size
        
        outBytes += struct.pack("<i", self.nFlags)[:4]
        
        for i in self.mtxOrientation:
            outBytes += struct.pack("<f", i)
            
        outBytes += struct.pack("<i", self.nBytesOfUserData)[:4]
        outBytes += struct.pack("<i", self.fCullDistance)[:4]
        outBytes += struct.pack("<i", self.nParentIndex)[:4]
        
        for i in self.TintRGB:
            outBytes += struct.pack("<f", i)
        
        outBytes += self.PAD
        
        for data in self.userData:
            outBytes += bytes(data, "utf-8")
        
        return outBytes

################# 
# SHAPE DEFINITIONS      
class PASMShapeType_e:
    APE_SHAPE_TYPE_SPHERE            = 0
    APE_SHAPE_TYPE_CYLINDER          = 1
    APE_SHAPE_TYPE_BOX               = 2
    APE_SHAPE_TYPE_CAMERA            = 3
    APE_SHAPE_TYPE_SPEAKER           = 4
    #APE_SHAPE_TYPE_SPAWN_POINT       = 5
    APE_SHAPE_TYPE_START_POINT       = 6
    #APE_SHAPE_TYPE_ROOM              = 7
    #APE_SHAPE_TYPE_ARENA             = 8
    APE_SHAPE_TYPE_PARTICLE_BOX      = 9
    APE_SHAPE_TYPE_PARTICLE_SPHERE   = 10
    APE_SHAPE_TYPE_PARTICLE_CYLINDER = 11
    APE_SHAPE_TYPE_SPLINE            = 12
        
class PASMShapeSphere:
    def __init__(self):
        self.fRadius = 0
        self.PAD = bytearray(12)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
   
        outBytes += struct.pack("<f", self.fRadius)
        outBytes += self.PAD
        
        return outBytes

class PASMShapeCylinder:
    def __init__(self):
        self.PAD = bytearray(16)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
   
        outBytes += self.PAD
        
        return outBytes
        
class PASMShapeBox:
    def __init__(self):
        self.PAD = bytearray(4)
        self.fLength = 0
        self.fWidth = 0
        self.fHeight = 0

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
   
        outBytes += self.PAD
        outBytes += struct.pack("<f", self.fLength)
        outBytes += struct.pack("<f", self.fWidth)
        outBytes += struct.pack("<f", self.fHeight)
        
        return outBytes
        
class PASMShapeCamera:
    def __init__(self):
        self.PAD = bytearray(16)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
   
        outBytes += self.PAD
        
        return outBytes
        
class PASMShapeSpeaker:
    def __init__(self):
        self.PAD = bytearray(16)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
   
        outBytes += self.PAD
        
        return outBytes
        
# Deprecated
class PASMShapeSpawnPoint:
    def __init__(self):
        self.PAD = bytearray(16)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
   
        outBytes += self.PAD
        
        return outBytes

class PASMShapeStartPoint:
    def __init__(self):
        self.PAD = bytearray(16)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
   
        outBytes += self.PAD
        
        return outBytes
        
# Deprecated
class PASMShapeRoom:
    def __init__(self):
        self.PAD = bytearray(16)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
   
        outBytes += self.PAD
        
        return outBytes
        
# Deprecated
class PASMShapeArena:
    def __init__(self):
        self.PAD = bytearray(16)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
   
        outBytes += self.PAD
        
        return outBytes
        
class PASMShapeParticleBox:
    def __init__(self):
        self.PAD = bytearray(16)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
   
        outBytes += self.PAD
        
        return outBytes
        
class PASMShapeParticleSphere:
    def __init__(self):
        self.PAD = bytearray(16)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
   
        outBytes += self.PAD
        
        return outBytes
        
class PASMShapeParticleCylinder:
    def __init__(self):
        self.PAD = bytearray(16)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
   
        outBytes += self.PAD
        
        return outBytes
        
class PASMShapeSpline:
    def __init__(self):
        self.nNumPts = 0
        self.bClosed = 0
        self.nNumSegments = 0
        self.PAD = bytearray(4)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
   
        outBytes += struct.pack("<i", self.nNumPts)[:4]
        outBytes += struct.pack("<i", self.bClosed)[:4]
        outBytes += struct.pack("<i", self.nNumSegments)[:4]
        outBytes += self.PAD
        
        return outBytes
        
# Included at start of userData in PASMShape.userData when typeData = APE_SHAPE_TYPE_SPLINE
class PASMSplinePt:
    def __init__(self):
        self.Pos = [0.0 for i in range(3)]

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
   
        for i in self.Pos:
            outBytes += struct.pack("<f", i)
        
        return outBytes

class PASMShape:
    def __init__(self):
        self.nType = -1
        # This type data will become one of the classes defined above based on nType
        self.typeData = None
        self.mtxOrientation = [0.0 for i in range(12)]
        self.nBytesOfUserData = 0
        self.PAD = bytearray(16)
        self.userData = [] # User Data is gonna be an array of string commands

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
        
        outBytes += struct.pack("<i", self.nType)[:4]
        
        outBytes += self.typeData.packBytes()
        
        for i in self.mtxOrientation:
            outBytes += struct.pack("<f", i)
            
        outBytes += struct.pack("<i", self.nBytesOfUserData)[:4]
        
        outBytes += self.PAD
        
        for data in self.userData:
            if type(data) == float:
                outBytes += struct.pack("<f", data)[:4]
            else:
                outBytes += bytes(data, "utf-8")
        
        return outBytes
        
################# 
# VOLUME DEFINITIONS
class PASMVisPoint:
    def __init__(self):
        self.Pos = [0.0, 0.0, 0.0]

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
        for i in self.Pos:
            outBytes += struct.pack("<f", i)
        
        return outBytes

class PASMVisEdge:
    def __init__(self):
        self.anVertIndices = [0,0]

        # How could an edge be connected to more than 2 faces in a convex shape???
        self.nNumFaces = 0  
        self.anFaceIndices = [0,0]

        self.PAD = bytearray(4)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
        
        for i in self.anVertIndices:
            outBytes += struct.pack("<h", i)

        outBytes += struct.pack("<i", self.nNumFaces)[:4]

        for i in self.anFaceIndices:
            outBytes += struct.pack("<h", i)

        outBytes += self.PAD
        
        return outBytes

class PASMVisFace:
    def __init__(self):
        self.nDegree = 0 # Number of aVertIndicies / aEdgeIndicies used, usually 4
        # Not all these values have to be filled out, EX: cube only needs 4
        self.aVertIndices = [0 for i in range(6)]
        self.aEdgeIndices = [0 for i in range(6)]

        self.Normal = [0.0, 0.0, 0.0]
        self.Centroid = [0.0, 0.0, 0.0]

        self.PAD = bytearray(4)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()

        outBytes += struct.pack("<i", self.nDegree)[:4]

        for i in self.aVertIndices:
            outBytes += struct.pack("<h", i)
        for i in self.aEdgeIndices:
            outBytes += struct.pack("<h", i)
        for i in self.Normal:
            outBytes += struct.pack("<f", i)
        for i in self.Centroid:
            outBytes += struct.pack("<f", i)
        outBytes += self.PAD
             
        return outBytes

#Size :1240h
class PASMCell:
    def __init__(self):
        self.szCellName = ""
        
        self.nNumVerts = 0
        self.aVisVerts = [PASMVisPoint() for i in range(156)]

        self.nNumEdges = 0
        self.aVisEdges = [PASMVisEdge() for i in range(79)]

        self.nNumFaces = 0
        self.aVisFaces = [PASMVisFace() for i in range(26)]

        self.aSphere = [0.0, 0.0, 0.0, 0.0]
        self.nFlags = 0
        self.PAD = bytearray(16)
        
    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
        
        size = bytearray(32)
        size[0:len(self.szCellName[0:31])] = bytes(self.szCellName, "utf-8")[0:31]
        outBytes += size

        outBytes += struct.pack("<i", self.nNumVerts)[:4]
        for i in self.aVisVerts:
            outBytes += i.packBytes()

        outBytes += struct.pack("<i", self.nNumEdges)[:4]
        for i in self.aVisEdges:
            outBytes += i.packBytes()

        outBytes += struct.pack("<i", self.nNumFaces)[:4]
        for i in self.aVisFaces:
            outBytes += i.packBytes()

        for i in self.aSphere:
            outBytes += struct.pack("<f", i)

        outBytes += struct.pack("<i", self.nFlags)[:4]
        outBytes += self.PAD
        
        return outBytes

class PASMVolume:
    def __init__(self):
        self.nNumCells = 0
        self.aCells = [PASMCell() for i in range(16)]
        self.Sphere = [0.0, 0.0, 0.0, 0.0]
        self.nFlags = 0
        self.PAD = bytearray(16)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()

        outBytes += struct.pack("<i", self.nNumCells)[:4]

        for i in self.aCells:
            outBytes += i.packBytes()

        for i in self.Sphere:
            outBytes += struct.pack("<f", i)

        outBytes += struct.pack("<i", self.nFlags)[:4]

        outBytes += self.PAD

        return outBytes

#################
# PORTAL DEFINITIONS
# Visibilty Portal definition for designer placed sightline planes between volumes
class PASMVisPortal:
    def __init__(self):
        self.szName = ""
        self.ACorners = [PASMVisPoint() for i in range(4)]
        self.Normal = [0.0, 0.0, 0.0]
        self.Centroid = [0.0, 0.0, 0.0]

        self.nFlags = 0

        self.PAD = bytearray(16)

    def packBytes(self):
        outBytes = bytearray() # init our bytearray
        
        size = bytearray(32)
        size[0:len(self.szName[0:31])] = bytes(self.szName, "utf-8")[0:31]
        outBytes += size
        
        for i in self.ACorners:
            outBytes += i.packBytes()
        for i in self.Normal:
            outBytes += struct.pack("<f", i)
        for i in self.Centroid:
            outBytes += struct.pack("<f", i)
        
        outBytes += struct.pack("<i", self.nFlags)[:4]
            
        outBytes += self.PAD
             
        return outBytes

#################
# MESH DEFINITIONS
# Flags for special material effect in Layers
# Size: 80h
class PASMCommands:
    def __init__(self):
        self.bSort = 0
        self.nOrderNum = 0
        self.nShaderNum = 0
        self.nEmissiveMotifID = 0
        self.nSpecularMotifID = 0
        self.nDiffuseMotifID = 0
        self.bUseEmissiveColor = 0
        self.bUseSpecularColor = 0
        self.bUseDiffuseColor = 0
        self.nNumTexFrames = 0
        self.fFramesPerSec = 0
        self.fDeltaUPerSec = 0
        self.fDeltaVPerSec = 0
        self.nZTugValue = 0
        self.nID = 0
        self.bNoColl = 0
        self.nCollID = 0
        self.nFlags = 0
        self.nCollMask = 0
        self.nReactType = 0
        self.nSurfaceType = 0
        self.TintRGB = [0.0, 0.0, 0.0]
        self.LightRGBI = [0.0, 0.0, 0.0, 0.0]
        self.fBumpMapTileFactor = 0
        self.fDetailMapTileFactor = 0
        self.fDeltaUVRotationPerSec = 0
        self.vRotateUVAround = [0.0, 0.0]
        self.PAD = bytearray(12)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()

        outBytes += struct.pack("<i", self.bSort)[:4]
        outBytes += struct.pack("<i", self.nOrderNum)[:4]
        outBytes += struct.pack("<i", self.nShaderNum)[:4]
        outBytes += struct.pack("<i", self.nEmissiveMotifID)[:4]
        outBytes += struct.pack("<i", self.nSpecularMotifID)[:4]
        outBytes += struct.pack("<i", self.nDiffuseMotifID)[:4]
        outBytes += struct.pack("<i", self.bUseEmissiveColor)[:4]
        outBytes += struct.pack("<i", self.bUseSpecularColor)[:4]
        outBytes += struct.pack("<i", self.bUseDiffuseColor)[:4]
        outBytes += struct.pack("<i", self.nNumTexFrames)[:4]
        outBytes += struct.pack("<f", self.fFramesPerSec)
        outBytes += struct.pack("<f", self.fDeltaUPerSec)
        outBytes += struct.pack("<f", self.fDeltaVPerSec)
        outBytes += struct.pack("<i", self.nZTugValue)[:4]
        
        outBytes += struct.pack("<b", self.nID)
        outBytes += struct.pack("<b", self.bNoColl)
        outBytes += struct.pack("<b", self.nCollID)
        outBytes += struct.pack("<B", self.nFlags)

        outBytes += struct.pack("<H", self.nCollMask)
        outBytes += struct.pack("<h", self.nReactType)
        outBytes += struct.pack("<h", self.nSurfaceType)

        # Strange null bytes
        outBytes += bytearray(2)

        for i in self.TintRGB:
            outBytes += struct.pack("<f", i)
        for i in self.LightRGBI:
            outBytes += struct.pack("<f", i)

        outBytes += struct.pack("<f", self.fBumpMapTileFactor)
        outBytes += struct.pack("<f", self.fDetailMapTileFactor)
        outBytes += struct.pack("<f", self.fDeltaUVRotationPerSec)

        for i in self.vRotateUVAround:
            outBytes += struct.pack("<f", i)

        outBytes += self.PAD

        return outBytes
 
class PASMLayerIndex_e():
    APE_LAYER_TEXTURE_DIFFUSE = 0	
    APE_LAYER_TEXTURE_SPECULAR_MASK = 1	
    APE_LAYER_TEXTURE_EMISSIVE_MASK = 2	
    APE_LAYER_TEXTURE_ALPHA_MASK = 3	
    APE_LAYER_TEXTURE_BUMP = 4		
    APE_LAYER_TEXTURE_DETAIL = 5		
    APE_LAYER_TEXTURE_ENVIRONMENT = 6
    APE_LAYER_TEXTURE_UNUSED_3 = 7
    APE_LAYER_TEXTURE_UNUSED_2 = 8
    APE_LAYER_TEXTURE_UNUSED_1 = 9	

    APE_LAYER_TEXTURE_MAX = 10
        
# A Material is made up of either 1 or 2 layers, base and layer1 respectfully
# Size: 17Ch
class PASMLayer:
    def __init__(self):
        self.bTextured = 0
        self.szTexName = ["" for i in range(10)]
        self.fUnitAlphaMultiplier = 0.0
        self.bDrawAsWire = 0
        self.bTwoSided = 0
        self.bTileU = 1
        self.bTileV = 1
        self.SpecularRGB = [0.0, 0.0, 0.0]
        self.IllumRGB = [0.0, 0.0, 0.0]
        self.DiffuseRGB = [0.0, 0.0, 0.0]
        self.fShininess = 0.0
        self.fShinStr = 0.0
        self.StarCommands = PASMCommands()
        self.PAD = bytearray(36)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()

        outBytes += struct.pack("<i", self.bTextured)[:4]

        for i in self.szTexName:
            size = bytearray(16)
            try:
                size[0:len(i)] = bytes(i, "utf-8")
            except:
                pass
            outBytes += size

        outBytes += struct.pack("<f", self.fUnitAlphaMultiplier)
        
        outBytes += struct.pack("<b", self.bDrawAsWire)
        outBytes += struct.pack("<b", self.bTwoSided)
        outBytes += struct.pack("<b", self.bTileU)
        outBytes += struct.pack("<b", self.bTileV)

        for i in self.SpecularRGB:
            outBytes += struct.pack("<f", i)
        for i in self.IllumRGB:
            outBytes += struct.pack("<f", i)
        for i in self.DiffuseRGB:
            outBytes += struct.pack("<f", i)

        outBytes += struct.pack("<f", self.fShininess)
        outBytes += struct.pack("<f", self.fShinStr)

        outBytes += self.StarCommands.packBytes()

        outBytes += self.PAD

        return outBytes

# A Material is a container for up to 2 layers
class PASMMaterial:
    def __init__(self):
        self.nLayerCount = 0
        self.aMatLayers = [PASMLayer() for i in range(4)]
        self.nFirstIndex = 0
        self.nNumIndices = 0
        self.StarCommands = PASMCommands()
        self.nLODIndex = 0
        self.nAffectAngle = 0
        self.nFlags = 0
        self.PAD = bytearray(24)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()

        outBytes += struct.pack("<i", self.nLayerCount)[:4]

        for i in self.aMatLayers:
            outBytes += i.packBytes()

        outBytes += struct.pack("<i", self.nFirstIndex)[:4]
        outBytes += struct.pack("<i", self.nNumIndices)[:4]

        outBytes += self.StarCommands.packBytes()
        outBytes += struct.pack("<h", self.nLODIndex)
        outBytes += struct.pack("<h", self.nAffectAngle)
        outBytes += struct.pack("<i", self.nFlags)[:4]
        
        outBytes += self.PAD

        return outBytes

class PASMVert:
    def __init__(self):
        self.Pos = [0.0, 0.0, 0.0]
        self.Norm = [0.0, 0.0, 0.0]
        self.Color = [0.0, 0.0, 0.0, 0.0]
        self.aUVs = [[0.0, 0.0] for i in range(4)]
        self.fNumWeights = 0
        self.aWeights = [PASMWeight() for i in range(4)]
        self.PAD = bytearray(16)
        
    def __hash__(self):
        return hash( (tuple(self.Pos), tuple(self.Norm), tuple(self.Color), tuple(self.aUVs[0]), tuple(self.aUVs[1]), self.fNumWeights, tuple(self.aWeights) ) )
        
    # Class comparison doesn't work by default b/c it doesn't know what to compare so we do this
    # Stupid, half assed function, blah
    def __eq__(self, other) : 
        return self.Pos == other.Pos and self.Norm == other.Norm and self.Color == other.Color and self.aUVs[0] == other.aUVs[0] and self.aUVs[1] == other.aUVs[1]
        
    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()

        for i in self.Pos:
            outBytes += struct.pack("<f", i)
        for i in self.Norm:
            outBytes += struct.pack("<f", i)
        for i in self.Color:
            outBytes += struct.pack("<f", i)
        for i in self.aUVs:
            for j in i:
                outBytes += struct.pack("<f", j)

        outBytes += struct.pack("<f", self.fNumWeights)

        for i in self.aWeights:
            outBytes += i.packBytes()

        outBytes += self.PAD

        return outBytes

class PASMVertIndex:
    def __init__(self):
        self.nVertIndex = 0
        self.PAD = bytearray(16)

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()

        outBytes += struct.pack("<i", self.nVertIndex)[:4]
        outBytes += self.PAD

        return outBytes

class PASMSegment:
    def __init__(self):
        self.szMeshName = ""
        self.bSkinned = 0
        self.nNumMaterials = 0
        self.nNumVerts = 0
        self.nNumIndices = 0
        self.PAD = bytearray(16)

        # NORMALLY in the ape exporter the mats, verts and indices are seperated
        # WELL... we're gonna pack them with the segment / mesh

        self.aMaterials = []
        self.aVertices = []
        self.aIndicies =  []

    def packBytes(self):
        #init our bytearray
        outBytes = bytearray()
        
        size = bytearray(16)
        size[0:len(self.szMeshName[0:15])] = bytes(self.szMeshName, "utf-8")[0:15]
        outBytes += size
        
        outBytes += struct.pack("<i", self.bSkinned)[:4]
        outBytes += struct.pack("<i", self.nNumMaterials)[:4]
        outBytes += struct.pack("<i", self.nNumVerts)[:4]
        outBytes += struct.pack("<i", self.nNumIndices)[:4]
        outBytes += self.PAD
        
        for i in self.aMaterials:
            outBytes += i.packBytes()
        for i in self.aVertices:
            outBytes += i.packBytes()
        for i in self.aIndicies:
            outBytes += i.packBytes()
     
        return outBytes