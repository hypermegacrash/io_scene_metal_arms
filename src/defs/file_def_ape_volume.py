# Class Definitions for the PASM Volume Structures within the .wld file format

from .binary_writer import *

class PASMPortalFlag_e:
    APE_PORTAL_FLAG_MIRROR            = 0x00000001    # the portal is a mirror
    APE_PORTAL_FLAG_SOUND_ONLY        = 0x00000002    # the portal is for sound only
    APE_PORTAL_FLAG_ONE_WAY           = 0x00000004    # the portal is 1 way
    APE_PORTAL_FLAG_ANTI              = 0x00000008    # the portal is an anti portal

    APE_PORTAL_FLAG_NONE              = 0x00000000

@binary_dataclass(slots=True)
class PASMVisPoint(BinaryStruct):
    EXPECTED_SIZE = 12

    Pos: list[float] = array_field("f", 3)

@binary_dataclass(slots=True)
class PASMVisEdge(BinaryStruct):
    EXPECTED_SIZE = 16

    anVertIndices: list[int] = array_field("h", 2)
    nNumFaces:     int       = bin_field("i", default=0)
    anFaceIndices: list[int] = array_field("h", 2)
    PAD:           bytes     = bin_field("4s", default=b"\x00" * 4)

@binary_dataclass(slots=True)
class PASMVisFace(BinaryStruct):
    EXPECTED_SIZE = 56

    _MAX_VERT_INDICES = 6
    _MAX_EDGE_INDICES = 6

    nDegree:      int          = bin_field("i", default=0)
    aVertIndices: list[int]    = array_field("h", _MAX_VERT_INDICES)
    aEdgeIndices: list[int]    = array_field("h", _MAX_EDGE_INDICES)
    Normal:       list[float]  = array_field("f", 3)
    Centroid:     list[float]  = array_field("f", 3)
    PAD:          bytes        = bin_field("4s", default=b"\x00" * 4)

@binary_dataclass(slots=True)
class PASMVisPortal(BinaryStruct):
    EXPECTED_SIZE = 124

    _PORTAL_NAME_LEN = 32

    szName:   str                = str_field(_PORTAL_NAME_LEN)
    ACorners: list[PASMVisPoint] = struct_array_field(PASMVisPoint, 4, zero_bytes=b"\x00" * PASMVisPoint.EXPECTED_SIZE)
    Normal:   list[float]        = array_field("f", 3)
    Centroid: list[float]        = array_field("f", 3)
    nFlags:   int                = bin_field("i", default=0)
    PAD:      bytes              = bin_field("16s", default=b"\x00" * 16)

@binary_dataclass(slots=True)
class PASMCell(BinaryStruct):
    EXPECTED_SIZE = 4672

    _CELL_NAME_LEN  = 32
    _CELL_MAX_VERTS = 156
    _CELL_MAX_EDGES = 79
    _CELL_MAX_FACES = 26

    szCellName: str                = str_field(_CELL_NAME_LEN)
    nNumVerts:  int                = bin_field("i", default=0)
    aVisVerts:  list[PASMVisPoint] = struct_array_field(PASMVisPoint, _CELL_MAX_VERTS, zero_bytes=b"\x00" * PASMVisPoint.EXPECTED_SIZE)
    nNumEdges:  int                = bin_field("i", default=0)
    aVisEdges:  list[PASMVisEdge]  = struct_array_field(PASMVisEdge, _CELL_MAX_EDGES, zero_bytes=b"\x00" * PASMVisEdge.EXPECTED_SIZE)
    nNumFaces:  int                = bin_field("i", default=0)
    aVisFaces:  list[PASMVisFace]  = struct_array_field(PASMVisFace, _CELL_MAX_FACES, zero_bytes=b"\x00" * PASMVisFace.EXPECTED_SIZE)
    aSphere:    list[float]        = array_field("f", 4)
    nFlags:     int                = bin_field("i", default=0)
    PAD:        bytes              = bin_field("16s", default=b"\x00" * 16)

@binary_dataclass(slots=True)
class PASMVolume(BinaryStruct):
    EXPECTED_SIZE = 74792

    _VOLUME_MAX_CELLS = 16

    nNumCells: int           = bin_field("i", default=0)
    aCells:   list[PASMCell] = struct_array_field(PASMCell, _VOLUME_MAX_CELLS, zero_bytes=b"\x00" * PASMCell.EXPECTED_SIZE)
    Sphere:   list[float]    = array_field("f", 4)
    nFlags:   int            = bin_field("i", default=0)
    PAD:      bytes          = bin_field("16s", default=b"\x00" * 16)