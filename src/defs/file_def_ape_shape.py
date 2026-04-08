# Class Definitions for the PASM Shape Structures within the .wld file format

from .binary_writer import *
                     
class PASMShapeType_e:
    APE_SHAPE_TYPE_SPHERE            = 0
    APE_SHAPE_TYPE_CYLINDER          = 1
    APE_SHAPE_TYPE_BOX               = 2
    #APE_SHAPE_TYPE_CAMERA            = 3  # Deprecated baking into .wld, replaced by .cam files
    #APE_SHAPE_TYPE_SPEAKER           = 4  # Deprecated, superseded by sound_ambient_* gamedata in entities
    #APE_SHAPE_TYPE_SPAWN_POINT       = 5  # Functionally equivalent as APE_SHAPE_TYPE_START_POINT
    APE_SHAPE_TYPE_START_POINT       = 6
    #APE_SHAPE_TYPE_ROOM              = 7  # AIRooms module deprecated, treated by PASM as APE_SHAPE_TYPE_BOX
    #APE_SHAPE_TYPE_ARENA             = 8  # Deprecated, treated by PASM as APE_SHAPE_TYPE_BOX
    #APE_SHAPE_TYPE_PARTICLE_BOX      = 9  # Unimplimented in max exporter and treated by PASM as APE_SHAPE_TYPE_BOX
    #APE_SHAPE_TYPE_PARTICLE_SPHERE   = 10 # Unimplimented in max exporter and treated by PASM as APE_SHAPE_TYPE_SPHERE
    #APE_SHAPE_TYPE_PARTICLE_CYLINDER = 11 # Unimplimented in max exporter and treated by PASM as APE_SHAPE_TYPE_CYLINDER
    APE_SHAPE_TYPE_SPLINE            = 12

@binary_dataclass(slots=True)
class PASMShapeSphere(BinaryStruct):
    EXPECTED_SIZE = 16

    fRadius: float = bin_field("f", default=0.0)
    PAD:     bytes = bin_field("12s", default=b"\x00" * 12)

@binary_dataclass(slots=True)
class PASMShapeCylinder(BinaryStruct):
    EXPECTED_SIZE = 16

    fRadius: float = bin_field("f", default=0.0)
    fHeight: float = bin_field("f", default=0.0)
    PAD:     bytes = bin_field("8s", default=b"\x00" * 8)

@binary_dataclass(slots=True)
class PASMShapeBox(BinaryStruct):
    EXPECTED_SIZE = 16

    PAD:     bytes = bin_field("4s", default=b"\x00" * 4)
    fLength: float = bin_field("f", default=0.0)
    fWidth:  float = bin_field("f", default=0.0)
    fHeight: float = bin_field("f", default=0.0)

@binary_dataclass(slots=True)
class PASMShapeStartPoint(BinaryStruct):
    EXPECTED_SIZE = 16

    PAD: bytes = bin_field("16s", default=b"\x00" * 16)

@binary_dataclass(slots=True)
class PASMShapeSpline(BinaryStruct):
    EXPECTED_SIZE = 16

    nNumPts:      int   = bin_field("i", default=0)
    bClosed:      int   = bin_field("i", default=0)
    nNumSegments: int   = bin_field("i", default=0)
    PAD:          bytes = bin_field("4s", default=b"\x00" * 4)

@binary_dataclass(slots=True)
class PASMSplinePt(BinaryStruct):
    """Included at start of userData in PASMShape.userData when typeData = APE_SHAPE_TYPE_SPLINE"""
    EXPECTED_SIZE = 12

    Pos: list[float] = array_field("f", 3, default=lambda: [0.0, 0.0, 0.0])

class PASMShape:
    __slots__ = ("nType", "typeData", "mtxOrientation", "nBytesOfUserData", "nParentIndex", "PAD", "userData")

    EXPECTED_SIZE = 88

    def __init__(self):
        self.nType:            int          = -1
        self.typeData:         BinaryStruct = None  # one of the above headers
        self.mtxOrientation:   list[float]  = [0.0] * 12
        self.nBytesOfUserData: int          = 0
        self.nParentIndex:     int          = 0
        self.PAD:              bytes        = b"\x00" * 12
        self.userData:         list         = []  # floats or strings

    def pack(self) -> bytes:
        out = bytearray()

        out += struct.pack("<i", self.nType)
        out += self.typeData.pack()
            
        for f in self.mtxOrientation:
            out += struct.pack("<f", f)
        out += struct.pack("<i", self.nBytesOfUserData)
        out += struct.pack("<i", self.nParentIndex)
        out += self.PAD

        for data in self.userData:
            if isinstance(data, float):
                out += struct.pack("<f", data)
            else:
                out += data.encode("utf-8")

        return out