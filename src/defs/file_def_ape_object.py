# Class Definitions for the PASM Object Structures within the .wld file format

from .binary_writer import *

class PASMObjectFlag_e:
    APE_OB_FLAG_STATIC              = 0x00000001    # Object's bounding sphere has a static footprint in 3D space
    APE_OB_FLAG_POSTER_Y            = 0x00000002    # Poster object around it's Y axis to always face the camera (neg-Z axis of object toward viewer)
    APE_OB_FLAG_NO_COLL             = 0x00000004    # Don't collide with this object

    APE_OB_FLAG_NO_LIGHT            = 0x00000010    # Don't light this object

    APE_OB_FLAG_POSTER_X            = 0x00000040    # Poster object around it's X axis
    APE_OB_FLAG_POSTER_Z            = 0x00000080    # Poster object around it's Z axis
    APE_OB_FLAG_NO_DRAW             = 0x00000100   
    APE_OB_FLAG_LM                  = 0x00000200    # This (static) object will receive light maps
    APE_OB_FLAG_PER_PIXEL           = 0x00000400   
    APE_OB_FLAG_VERT_RADIOSITY      = 0x00000800    # This (static) object will receive vertex radiosity
    APE_OB_FLAG_ACCEPT_SHADOWS      = 0x00001000    # This object will receive shadows
    APE_OB_FLAG_CAST_SHADOWS        = 0x00002000    # This object will cast shadows
    APE_OB_FLAG_TINT                = 0x00004000    # This object will be tinted
    APE_OB_FLAG_NO_LM_USE           = 0x00008000    # This object will not be considered when generating lightmaps (even if static)

    APE_OB_FLAG_NONE                = 0x00000000

@binary_dataclass(slots=True)
class PASMObjectHeader(BinaryStruct):
    EXPECTED_SIZE = 112  # adjust based on exact byte size

    _OBJECT_NAME_LEN = 12

    szObjectName:     str         = str_field(_OBJECT_NAME_LEN)
    PAD_0x04:         bytes       = bin_field("4s", default=b"\x00" * 4)
    nFlags:           int         = bin_field("i", default=0)
    mtxOrientation:   list[float] = array_field("f", 12, default=lambda: [0.0]*12)
    nBytesOfUserData: int         = bin_field("i", default=0)
    fCullDistance:    float       = bin_field("f", default=0.0)
    nParentIndex:     int         = bin_field("i", default=0)
    TintRGB:          list[float] = array_field("f", 3, default=lambda: [0.0]*3)
    PAD:              bytes       = bin_field("20s", default=b"\x00" * 20)

class PASMObject:
    __slots__ = ("header", "userData")

    def __init__(self):
        self.header = PASMObjectHeader()
        self.userData: list[str] = []  # variable length string data

    def pack(self) -> bytes:
        # pack fixed-size header
        out = self.header.pack()

        # pack variable-length userdata
        for data in self.userData:
            if isinstance(data, float):
                out += struct.pack("<f", data)
            else:
                out += data.encode("utf-8")

        return out