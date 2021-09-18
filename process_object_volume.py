# Module that processes a volume object and returns byte data

from mathutils import Vector # Need Vector for computing bounding box

from . import pasm_file_def # Get our PASM file classes

from . import g_class # Get our global variables for the header data

def ExportObjVolume(obj):
    if obj.type != "MESH":
        return
    if(obj.name.find("cell_", 0, 5) == -1):
        return
        
    print(obj.name, "is a cell object")    
    
    if(len(obj.data.polygons) != 6):
        #print("The cell", obj.name, "isn't a non-triangulated cube with 6 faces. While convex shapes ARE supported for cells" +
        #" in the PASM .wld format. That functionality is not currently supported in this itteration of the tool")
        return
    #print("CELL NAME:", obj.name, "is a cube with 6 faces, good")   
    
    outCell = pasm_file_def.PASMCell()
    
    outCell.szCellName = obj.name
    
    # This returns a new instance of the vertex data
    # Whatever modifed here won't affect the scene
    testM = obj.to_mesh()
    
    # Dump the verts
    VisVerts = []
    for index in testM.vertices:
        tempVisVert = pasm_file_def.PASMVisPoint()
        
        #Thx stackexchange! https://blender.stackexchange.com/questions/6155/how-to-convert-coordinates-from-vertex-to-world-space
           
        vertPosAfterWTM = obj.matrix_world @ index.co
        tempVisVert.Pos[0] = vertPosAfterWTM[0]
        tempVisVert.Pos[1] = vertPosAfterWTM[2]
        tempVisVert.Pos[2] = vertPosAfterWTM[1]
        
        VisVerts.append(tempVisVert)
    
    outCell.nNumVerts = len(VisVerts)
    for x in range(len(VisVerts)):
        outCell.aVisVerts[x] = VisVerts[x]
    
    # Dump the edges
    VisEdges = []
    for index in testM.edges:
        tempVisEdge = pasm_file_def.PASMVisEdge()
        
        for x in range(len(index.vertices)):
            tempVisEdge.anVertIndices[x] = index.vertices[x]
        # Don't believe there can BE an instance of a convex shape with an edge sharing more than 2 faces
        tempVisEdge.nNumFaces = 2
        # Given two verts in an edge, find the two faces that share those verts
        aFaceIndices = []
        for y in testM.polygons:
            if tempVisEdge.anVertIndices[0] in y.vertices and tempVisEdge.anVertIndices[1] in y.vertices:
                aFaceIndices.append(y.index)
        #print("EDGE:", index, "connects to FACES:", aFaceIndices)
        for x in range(len(aFaceIndices)):
            tempVisEdge.anFaceIndices[x] = aFaceIndices[x]
            
        VisEdges.append(tempVisEdge)
    
    outCell.nNumEdges = len(VisEdges)
    for x in range(len(VisEdges)):
        outCell.aVisEdges[x] = VisEdges[x]
    
    # Dump the faces
    VisFaces = []
    for index in testM.polygons:
        tempVisFace = pasm_file_def.PASMVisFace()
        
        # We're hardcoding cubes for now, cubes always got 4 edges and verts per face
        tempVisFace.nDegree = 4
        
        # Should be 4 in here b/c CUBE
        for vertex in range(len(index.vertices)):
              tempVisFace.aVertIndices[vertex] = index.vertices[vertex]
              
        # We already got a list of edges, use them to find pattern
        aEdgeIndices = []
        for y in VisEdges:
            if y.anFaceIndices[0] == index.index or y.anFaceIndices[1] == index.index:
                aEdgeIndices.append(VisEdges.index(y))
        #print("FACE:", index, "connects to EDGES:", aEdgeIndices)
        for x in range(len(aEdgeIndices)):
            tempVisFace.aEdgeIndices[x] = aEdgeIndices[x]
        
        tempVisFace.Normal[0] = index.normal[0]
        tempVisFace.Normal[1] = index.normal[2]
        tempVisFace.Normal[2] = index.normal[1]
        
        faceCenterAfterWTM = obj.matrix_world @ index.center
        tempVisFace.Centroid[0] = faceCenterAfterWTM[0]
        tempVisFace.Centroid[1] = faceCenterAfterWTM[2]
        tempVisFace.Centroid[2] = faceCenterAfterWTM[1]
             
        VisFaces.append(tempVisFace)
    
    outCell.nNumFaces = len(VisFaces)
    for x in range(len(VisFaces)):
        outCell.aVisFaces[x] = VisFaces[x]
    
    # outCell Sphere
    # It goes [Radius, X, Y, Z]
    # Need to swap Y and Z
    # Sphere is a bounding sphere used for computing viewport frustrum culling
    # https://stackoverflow.com/questions/41529743/computing-the-bounding-sphere-for-a-3d-mesh-in-python
    
    # Thx StackExchange! https://blender.stackexchange.com/questions/62040/get-center-of-geometry-of-an-object
    # There was a syntax change from <2.79 -> 2.8+, fix here
    # https://blender.stackexchange.com/questions/129473/typeerror-element-wise-multiplication-not-supported-between-matrix-and-vect/129474
    local_bbox_center = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
    global_bbox_center = obj.matrix_world @ local_bbox_center
    #print("local_bbox_center:", local_bbox_center)
    #print("global_bbox_center:", global_bbox_center)
    
    # Probably inefficient as all hell since we're itterating over every vertex but it works
    # https://sinestesia.co/blog/tutorials/calculating-distances-in-blender-with-python/
    radius = 0
    for vert in testM.vertices:
        #print((vert.co - local_bbox_center).length)
        if (vert.co - local_bbox_center).length > radius:
            radius = (vert.co - local_bbox_center).length
    #print("RADIUS:", radius)
    
    outCell.aSphere[0] = radius
    # Hey dummy this is local space not world space
    outCell.aSphere[1] = local_bbox_center[0]
    outCell.aSphere[2] = local_bbox_center[1]
    outCell.aSphere[3] = local_bbox_center[2]
    
    testVolume = pasm_file_def.PASMVolume()
    
     # For the moment Volumes are hardcoded to only be 1 cell
    testVolume.nNumCells = 1   
    testVolume.aCells[0] = outCell
    testVolume.Sphere = outCell.aSphere
    
    # Finally, write data to the file, and our header
    g_class.file.write(testVolume.packBytes())
    g_class.gWldHeader.fileSize += len(testVolume.packBytes())
    g_class.gWldHeader.nNumCells += 1
    
    
    
    