# Module that processes a volume object and returns byte data

# BUILT IN
import math
# BLENDER
import bmesh  # Needed to triangulate the mesh
import mathutils
# FANG TOOLKIT
from ..defs import file_def_ape_volume
from . import g_class
    
def ProcessCell(obj):
    name = obj.name.lower()
    if name.startswith("off_"):      return False
    if obj.type != "MESH":           return False
    if not name.startswith("cell_"): return False

    outCell = file_def_ape_volume.PASMCell()
    outCell.szCellName = obj.name

    # Create evaluated mesh copy
    testM = obj.to_mesh()
    bm = bmesh.new()
    bm.from_mesh(testM)
    bm.faces.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    try:
        # Manifold check
        for e in bm.edges:
            if not e.is_manifold:
                g_class.logError(f"VOLUME / CELL ERROR: The cell {obj.name} is not manifold, skipping cell.")
                return False

        # TODO: Fix the false positives
        # Convexity test
        # for face in bm.faces:
        #     p = face.verts[0].co
        #     n = face.normal
        #     for v in bm.verts:
        #         if (v.co - p).dot(n) > 1e-6:
        #             g_class.logError(
        #                 f"VOLUME / CELL ERROR: The cell {obj.name} is not convex, skipping cell."
        #             )
        #             return False

        # Enforce max 6 verts per face
        for face in list(bm.faces):
            if len(face.verts) > 6:
                bmesh.ops.connect_verts(
                    bm, verts=list(face.verts[:6])
                )

        bm.to_mesh(testM)

    finally:
        bm.free()

    # Transform & normals
    if obj.matrix_world.determinant() < 0.0:
        testM.flip_normals()

    testM.transform(obj.matrix_world)
    testM.calc_loop_triangles()

    # Export vertices
    VisVerts = []
    for v in testM.vertices:
        p = file_def_ape_volume.PASMVisPoint()
        p.Pos[0] = v.co.x
        p.Pos[1] = v.co.z
        p.Pos[2] = v.co.y
        VisVerts.append(p)

    if( len(VisVerts) > file_def_ape_volume.PASMCell._CELL_MAX_VERTS ):
        g_class.logError(f"VOLUME / CELL ERROR: The cell {obj.name} contains {len(VisVerts)} vertices, max is {file_def_ape_volume.PASMCell._CELL_MAX_VERTS}.")
        return False

    outCell.nNumVerts = len(VisVerts)
    for i, v in enumerate(VisVerts):
        outCell.aVisVerts[i] = v

    # Build edge-face lookup
    edge_faces = {tuple(sorted(e.vertices)): [] for e in testM.edges}

    for poly in testM.polygons:
        verts = poly.vertices
        for i in range(len(verts)):
            key = tuple(sorted((verts[i], verts[(i + 1) % len(verts)])))
            edge_faces[key].append(poly.index)

    # Export edges
    VisEdges = []
    for e in testM.edges:
        ve = file_def_ape_volume.PASMVisEdge()
        ve.anVertIndices[0], ve.anVertIndices[1] = e.vertices

        faces = edge_faces[tuple(sorted(e.vertices))]
        ve.nNumFaces = len(faces)

        for i, fi in enumerate(faces):
            ve.anFaceIndices[i] = fi

        VisEdges.append(ve)

    if( len(VisEdges) > file_def_ape_volume.PASMCell._CELL_MAX_EDGES ):
        g_class.logError(f"VOLUME / CELL ERROR: The cell {obj.name} contains {len(VisEdges)} edges, max is {file_def_ape_volume.PASMCell._CELL_MAX_EDGES}.")
        return False

    outCell.nNumEdges = len(VisEdges)
    for i, e in enumerate(VisEdges):
        outCell.aVisEdges[i] = e

    # Build face-edge lookup
    face_edges = [[] for _ in testM.polygons]
    for ei, edge in enumerate(VisEdges):
        for fi in edge.anFaceIndices[:edge.nNumFaces]:
            face_edges[fi].append(ei)

    # Export faces
    VisFaces = []
    for poly in testM.polygons:
        vf = file_def_ape_volume.PASMVisFace()

        vf.nDegree = len(poly.vertices)
        for i, vi in enumerate(poly.vertices):
            vf.aVertIndices[i] = vi

        for i, ei in enumerate(face_edges[poly.index]):
            vf.aEdgeIndices[i] = ei

        n = poly.normal
        vf.Normal[0] = n.x
        vf.Normal[1] = n.z
        vf.Normal[2] = n.y

        c = poly.center
        vf.Centroid[0] = c.x
        vf.Centroid[1] = c.z
        vf.Centroid[2] = c.y

        VisFaces.append(vf)

    if( len(VisFaces) > file_def_ape_volume.PASMCell._CELL_MAX_FACES ):
        g_class.logError(f"VOLUME / CELL ERROR: The cell {obj.name} contains {len(VisFaces)} faces, max is {file_def_ape_volume.PASMCell._CELL_MAX_FACES}.")
        return False

    outCell.nNumFaces = len(VisFaces)
    for i, f in enumerate(VisFaces):
        outCell.aVisFaces[i] = f

    # Bounding sphere
    bbox = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
    center = sum(bbox, mathutils.Vector()) / 8.0
    radius = max((v - center).length for v in bbox)

    outCell.aSphere = ( radius, center.x, center.z, center.y )

    # Cleanup
    obj.to_mesh_clear()

    return outCell

def ExportObjVolume(aVolumes):
    outVolume = file_def_ape_volume.PASMVolume()

    cells = aVolumes if isinstance(aVolumes, list) else [aVolumes]

    cx = cy = cz = 0.0
    radius_sq = 0.0

    for cell_obj in cells:
        outCell = ProcessCell(cell_obj)
        if not outCell:
            return

        outVolume.aCells[outVolume.nNumCells] = outCell

        # First cell initializes sphere
        if outVolume.nNumCells == 0:
            r, cx, cz, cy = outCell.aSphere
            radius_sq = r * r
        else:
            # Move center to midpoint
            cx = (cx + outCell.aSphere[1]) * 0.5
            cy = (cy + outCell.aSphere[3]) * 0.5
            cz = (cz + outCell.aSphere[2]) * 0.5

            # Expand radius if needed
            for cell in outVolume.aCells[:outVolume.nNumCells + 1]:
                for i in range(cell.nNumVerts):
                    vx, vy, vz = cell.aVisVerts[i].Pos
                    dx = vx - cx
                    dy = vy - cy
                    dz = vz - cz
                    d = dx*dx + dy*dy + dz*dz
                    if d > radius_sq:
                        radius_sq = d

        outVolume.nNumCells += 1

    outVolume.Sphere[0] = math.sqrt(radius_sq)
    outVolume.Sphere[1] = cx
    outVolume.Sphere[2] = cz
    outVolume.Sphere[3] = cy

    # Finally, write data to the file
    data = outVolume.pack()
    g_class.g_FileOut.write(data)
    g_class.g_ApeHeader.fileSize += len(data)
    g_class.g_ApeHeader.nNumCells += 1
    
    
    
    