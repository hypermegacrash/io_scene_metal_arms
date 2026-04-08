# Class Definitions for the PASM Light Structures within the .ape file format

from .binary_writer import *
                
class PASMLightType_e():
    APE_LIGHT_TYPE_SPOT    = 0
    APE_LIGHT_TYPE_OMNI    = 1
    APE_LIGHT_TYPE_DIR     = 2
    APE_LIGHT_TYPE_AMBIENT = 3

class PASMLightFlag_e():
    APE_LIGHT_FLAG_DONT_USE_RGB              = 0x00000001   # Disregard the light's rgb and only use the motif's color (default = off)
    APE_LIGHT_FLAG_LIGHT_SELF                = 0x00000002   # Light the object that the light is attached to (default = off)
    APE_LIGHT_FLAG_OBJ_DONT_LIGHT_TERRAIN    = 0x00000004   # Lights attached to this object don't light the terrain (default = off)

    APE_LIGHT_FLAG_PER_PIXEL                 = 0x00000008   # This light casts a projection on the environment (may or may not have a texture)

    APE_LIGHT_FLAG_LIGHTMAP_ONLY_LIGHT       = 0x00000010   # This light will only be used in the lightmap portion of PASM and will not be exported to the engine.
    APE_LIGHT_FLAG_LIGHTMAP_LIGHT            = 0x00000020   # This light is to be used for generating lightmaps (If it is not dynamic, it can be discarded prior to the engine)
    APE_LIGHT_FLAG_UNIQUE_LIGHTMAP           = 0x00000040   # This light will generate its own unique lightmap in the lightmapping phase (it must also have a unique m_nLightID)

    APE_LIGHT_FLAG_CORONA                    = 0x00000080   # This light has a corona
    APE_LIGHT_FLAG_CORONA_PROXFADE           = 0x00000100   # Fade the corona as the camera gets closer.

    APE_LIGHT_FLAG_CAST_SHADOWS              = 0x00000200   # This light will cast shadows (only relevant for engine lights)

    APE_LIGHT_FLAG_DYNAMIC_ONLY              = 0x00000400   # This light will not affect static objects

    APE_LIGHT_FLAG_MESH_MUST_BE_PER_PIXEL    = 0x00000800   # For per-pixel lights that have a projected texture.  If this flag is set, only objects that are flagged
                                                            # as per pixel lit will have the texture projected on them.  Others will just apply as a dynamic vertex light

@binary_dataclass(slots=True)
class PASMLight(BinaryStruct):
    EXPECTED_SIZE = 228

    _LIGHT_NAME_LEN             = 16
    _LIGHT_CORONA_NAME_LEN      = 16
    _LIGHT_PERPIXEL_NAME_LEN    = 16
    _LIGHT_PARENT_BONE_NAME_LEN = 32

    nApeLightType:     int         = bin_field("i", default=0)
    szLightName:       str         = str_field(_LIGHT_NAME_LEN, default="")
    Sphere:            list[float] = array_field("f", 4, default=lambda: [0.0] * 4)
    Direction:         list[float] = array_field("f", 3, default=lambda: [0.0] * 3)
    Color:             list[float] = array_field("f", 3, default=lambda: [0.0] * 3)
    Intensity:         float       = bin_field("f", default=0.0)
    fSpotInnerAngle:   float       = bin_field("f", default=0.0)
    fSpotOuterAngle:   float       = bin_field("f", default=0.0)
    nFlags:            int         = bin_field("i", default=0)
    nMotifID:          int         = bin_field("i", default=0)
    fCoronaScale:      float       = bin_field("f", default=1.0)
    mtxOrientation:    list[float] = array_field("f", 12, default=lambda: [0.0] * 12)
    szCoronaTexture:   str         = str_field(_LIGHT_CORONA_NAME_LEN, default="")
    szPerPixelTexture: str         = str_field(_LIGHT_PERPIXEL_NAME_LEN, default="")
    nLightID:          int         = bin_field("h", default=-1)
    szParentBoneName:  str         = str_field(_LIGHT_PARENT_BONE_NAME_LEN, default="Scene Root")
    PAD:               bytes       = bin_field("30s", default=b"\x00" * 30)