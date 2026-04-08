# Class Definitions for the PASM Mesh Structures within the .ape / .wld file format

from .binary_writer import *
 
class PASMMaterialFlag_e:
    APE_MAT_FLAGS_NO_DRAW            = 0x01    # Polys with this material will not be drawn
    APE_MAT_FLAGS_APPLY_TINT         = 0x02    # This tint is modulated into the texture color in the surface pass
    APE_MAT_FLAGS_DO_NOT_LM          = 0x04    # These polys should not be light mapped, though they can obscure light
    APE_MAT_FLAGS_ZWRITE_ON          = 0x08    # Relevant for translucent materials, only. When rendering this material, write to the zbuffer (default for translucent materials is not to)
    APE_MAT_FLAGS_DO_NOT_TINT        = 0x10    # If tint is applied to the mesh, this material will not receive tint
    APE_MAT_FLAGS_NO_LM_USE          = 0x20    # These polys should not be used in the lightmap phase (to receive or obscure light)
    APE_MAT_FLAGS_DO_NOT_BLOCK_LM    = 0x40    # These polys will not block light during lightmap application
    APE_MAT_FLAGS_VERT_RADIOSITY     = 0x80    # These polys will receive vertex radiosity
    APE_MAT_FLAGS_NONE               = 0x00

class PASMMatCollFlag_e:
    APE_MAT_COLL_FLAGS_COLL_WITH_PLAYER              = 0x0001
    APE_MAT_COLL_FLAGS_COLL_WITH_NPCS                = 0x0002
    APE_MAT_COLL_FLAGS_OBSTRUCT_LINE_OF_SIGHT        = 0x0004
    APE_MAT_COLL_FLAGS_COLL_WITH_THIN_PROJECTILES    = 0x0008
    APE_MAT_COLL_FLAGS_COLL_WITH_THICK_PROJECTILTES  = 0x0010
    APE_MAT_COLL_FLAGS_COLL_WITH_CAMERA              = 0x0020
    APE_MAT_COLL_FLAGS_COLL_WITH_OBJECTS             = 0x0040
    APE_MAT_COLL_FLAGS_WALKABLE                      = 0x0080
    APE_MAT_COLL_FLAGS_OBSTRUCT_SPLASH_DAMAGE        = 0x0100
    APE_MAT_COLL_FLAGS_COLLIDE_WITH_DEBRIS           = 0x0200
    APE_MAT_COLL_FLAGS_COLLIDE_WITH_VEHICLES         = 0x0400
    APE_MAT_COLL_FLAGS_HOVER_COLLIDABLE              = 0x0800
    APE_MAT_COLL_FLAGS_COLL_WITH_NOTHING             = 0x0000
    APE_MAT_COLL_FLAGS_COLL_WITH_EVERYTHING          = 0xFFFF

class PASMLayerFlag_e:
    APE_LAYER_FLAGS_DO_NOT_CAST_SHADOWS              = 0x00000100
    APE_LAYER_FLAGS_INVERT_EMISSIVE_MASK             = 0x00000200
    APE_LAYER_FLAGS_ANGULAR_EMISSIVE                 = 0x00000400
    APE_LAYER_FLAGS_ANGULAR_TRANSLUCENCY             = 0x00000800
    APE_LAYER_FLAGS_NO_ALPHA_SCROLL                  = 0x00001000
    APE_LAYER_FLAGS_NONE                             = 0x00000000

@binary_dataclass(slots=True)
class PASMCommands(BinaryStruct):
    EXPECTED_SIZE = 128

    bSort:                  int         = bin_field("i", default=0)
    nOrderNum:              int         = bin_field("i", default=0)
    nShaderNum:             int         = bin_field("i", default=0)
    nEmissiveMotifID:       int         = bin_field("i", default=0)
    nSpecularMotifID:       int         = bin_field("i", default=0)
    nDiffuseMotifID:        int         = bin_field("i", default=0)
    bUseEmissiveColor:      int         = bin_field("i", default=0)
    bUseSpecularColor:      int         = bin_field("i", default=0)
    bUseDiffuseColor:       int         = bin_field("i", default=0)
    nNumTexFrames:          int         = bin_field("i", default=0)
    fFramesPerSec:          float       = bin_field("f", default=0.0)
    fDeltaUPerSec:          float       = bin_field("f", default=0.0)
    fDeltaVPerSec:          float       = bin_field("f", default=0.0)
    nZTugValue:             int         = bin_field("i", default=0)
    nID:                    int         = bin_field("b", default=0)
    bNoColl:                int         = bin_field("b", default=0)
    nCollID:                int         = bin_field("B", default=0)
    nFlags:                 int         = bin_field("B", default=0)
    nCollMask:              int         = bin_field("H", default=0)
    nReactType:             int         = bin_field("h", default=0)
    nSurfaceType:           int         = bin_field("h", default=0)
    _null_bytes:            bytes       = bin_field("2s", default=b"\x00\x00")
    TintRGB:                list[float] = array_field("f", 3, default=lambda: [0.0] * 3)
    LightRGBI:              list[float] = array_field("f", 4, default=lambda: [0.0] * 4)
    fBumpMapTileFactor:     float       = bin_field("f", default=0.0)
    fDetailMapTileFactor:   float       = bin_field("f", default=0.0)
    fDeltaUVRotationPerSec: float       = bin_field("f", default=0.0)
    vRotateUVAround:        list[float] = array_field("f", 2, default=lambda: [0.0] * 2)
    PAD:                    bytes       = bin_field("12s", default=b"\x00" * 12)

class PASMLayerIndex_e():
    APE_LAYER_TEXTURE_DIFFUSE       = 0
    APE_LAYER_TEXTURE_SPECULAR_MASK = 1
    APE_LAYER_TEXTURE_EMISSIVE_MASK = 2
    APE_LAYER_TEXTURE_ALPHA_MASK    = 3
    APE_LAYER_TEXTURE_BUMP          = 4
    APE_LAYER_TEXTURE_DETAIL        = 5
    APE_LAYER_TEXTURE_ENVIRONMENT   = 6
    APE_LAYER_TEXTURE_UNUSED_3      = 7
    APE_LAYER_TEXTURE_UNUSED_2      = 8
    APE_LAYER_TEXTURE_UNUSED_1      = 9

    APE_LAYER_TEXTURE_MAX           = 10

@binary_dataclass(slots=True)
class PASMLayer(BinaryStruct):
    EXPECTED_SIZE = 380

    _TEX_NAME_COUNT = 10
    _TEX_NAME_LEN   = 16

    bTextured:            int          = bin_field("i", default=0)
    szTexName:            list[str]    = fixed_str_array_field(_TEX_NAME_COUNT, _TEX_NAME_LEN)
    fUnitAlphaMultiplier: float        = bin_field("f", default=0.0)
    bDrawAsWire:          int          = bin_field("b", default=0)
    bTwoSided:            int          = bin_field("b", default=0)
    bTileU:               int          = bin_field("b", default=1)
    bTileV:               int          = bin_field("b", default=1)
    SpecularRGB:          list[float]  = array_field("f", 3, default=lambda: [0.0] * 3)
    IllumRGB:             list[float]  = array_field("f", 3, default=lambda: [0.0] * 3)
    DiffuseRGB:           list[float]  = array_field("f", 3, default=lambda: [0.0] * 3)
    fShininess:           float        = bin_field("f", default=0.0)
    fShinStr:             float        = bin_field("f", default=0.0)
    StarCommands:         PASMCommands = struct_field(PASMCommands)
    PAD:                  bytes        = bin_field("36s", default=b"\x00" * 36)

@binary_dataclass(slots=True)
class PASMMaterial(BinaryStruct):
    EXPECTED_SIZE = 1692

    _NUM_LAYERS = 4

    nLayerCount:  int             = bin_field("i", default=0)
    aMatLayers:   list[PASMLayer] = struct_array_field(PASMLayer, _NUM_LAYERS, zero_bytes=b"\x00" * PASMLayer.EXPECTED_SIZE)
    nFirstIndex:  int             = bin_field("i", default=0)
    nNumIndices:  int             = bin_field("i", default=0)
    StarCommands: PASMCommands    = struct_field(PASMCommands)
    nLODIndex:    int             = bin_field("h", default=0)
    nAffectAngle: int             = bin_field("h", default=0)
    nFlags:       int             = bin_field("i", default=0)
    PAD:          bytes           = bin_field("24s", default=b"\x00" * 24)

@binary_dataclass(slots=True)
class PASMWeight(BinaryStruct):
    EXPECTED_SIZE = 24

    fBoneIndex: float = bin_field("f", default=0.0)
    fWeight:    float = bin_field("f", default=0.0)
    PAD:        bytes = bin_field("16s", default=b"\x00" * 16)

@binary_dataclass(slots=True)
class PASMVert(BinaryStruct):
    EXPECTED_SIZE = 188

    _NUM_UVS     = 4
    _NUM_WEIGHTS = 4

    Pos:         list[float]       = array_field("f", 3, default=lambda: [0.0] * 3)
    Norm:        list[float]       = array_field("f", 3, default=lambda: [0.0] * 3)
    Color:       list[float]       = array_field("f", 4, default=lambda: [0.0, 0.0, 0.0, 1.0])
    aUVs:        list[list[float]] = vec2_array_field(_NUM_UVS)
    fNumWeights: float             = bin_field("f", default=0.0)
    aWeights:    list[PASMWeight]  = struct_array_field(PASMWeight, _NUM_WEIGHTS, zero_bytes=b"\x00" * PASMWeight.EXPECTED_SIZE)
    PAD:         bytes             = bin_field("16s", default=b"\x00" * 16)

    def __hash__(self):
        uv_flat = tuple( tuple(uv) for uv in self.aUVs )
        weights_flat = tuple( (w.fBoneIndex, w.fWeight) if w is not None else (None, None) for w in self.aWeights )

        return hash((
            tuple(self.Pos),
            tuple(self.Norm),
            tuple(self.Color),
            uv_flat,
            self.fNumWeights,
            weights_flat,
        ))
    
    # Class comparison doesn't work by default b/c it doesn't know what to compare so we do this
    # which is followed by the real test which is the hash comparison above
    def __eq__(self, other): 
        return self.Pos == other.Pos

@binary_dataclass(slots=True)
class PASMVertIndex(BinaryStruct):
    EXPECTED_SIZE = 20

    nVertIndex: int   = bin_field("i", default=0)
    PAD:        bytes = bin_field("16s", default=b"\x00" * 16)

@binary_dataclass(slots=True)
class PASMSegmentHeader(BinaryStruct):
    EXPECTED_SIZE = 48

    _SEGMENT_NAME_LEN = 16

    szMeshName:    str   = str_field(_SEGMENT_NAME_LEN)
    bSkinned:      int   = bin_field("i", default=0)
    nNumMaterials: int   = bin_field("i", default=0)
    nNumVerts:     int   = bin_field("i", default=0)
    nNumIndices:   int   = bin_field("i", default=0)
    PAD:           bytes = bin_field("16s", default=b"\x00" * 16)

class PASMSegment:
    __slots__ = ("header", "aMaterials", "aVertices", "aIndicies")
    
    def __init__(self):
        self.header = PASMSegmentHeader()
        self.aMaterials: list[PASMMaterial]  = []
        self.aVertices:  list[PASMVert]      = []
        self.aIndicies:  list[PASMVertIndex] = []

    def pack(self) -> bytes:
        # update counts in header
        self.header.nNumMaterials = len(self.aMaterials)
        self.header.nNumVerts     = len(self.aVertices)
        self.header.nNumIndices   = len(self.aIndicies)

        # pack header
        data = self.header.pack()

        # pack arrays
        data += b"".join(m.pack() for m in self.aMaterials)
        data += b"".join(v.pack() for v in self.aVertices)
        data += b"".join(i.pack() for i in self.aIndicies)
        return data