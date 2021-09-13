# Module that processes a geo object and returns byte data

import struct # Work with bytes

import bpy # Work with Blender data types
import bmesh # Work with Blender mesh data
import math # Do we use this again?

from . import pasm_file_def # Get our PASM file classes

from . import g_class # Get our global variables for the header data

def ExportObjGeo(obj):
    # Validate we're working with mesh data and not other stuff
    if obj.type != "MESH":
        return
    # We don't do cells
    if(obj.name.find("cell_", 0, 5) != -1):
        return
    #objs could be ANY DATATYPE, so check for that
    if(obj.name.find("obj_", 0, 4) != -1):
        return
        
    print(obj.name, "is a geo object")

    outSegment = pasm_file_def.PASMSegment()
    
    #outSegment.szMeshName = obj.name
    
    outSegment.szMeshName = "segment" + str(g_class.gWldHeader.nNumSegments)
    
    # Layer based on Floor & Wall Mesh
    # Would these be good as default values?
    layer = pasm_file_def.PASMLayer()
    layer.bTextured = 1
    layer.fUnitAlphaMultiplier = 1.0
    layer.SpecularRGB = [0.8, 0.8, 0.8]
    layer.fShininess = 58.5
    layer.fShinStr = 0.25
    # Layer uses a special nShaderNum compared to Material
    # are the starcommands from the Material used as a starting base?
    layer.StarCommands.bUseDiffuseColor = 1
    layer.StarCommands.bUseSpecularColor = 1
    layer.StarCommands.TintRGB = [1.0, 1.0, 1.0]
    layer.StarCommands.nShaderNum = -1  # Difference between Layer & Material
    layer.StarCommands.fBumpMapTileFactor = 1
    layer.StarCommands.fDetailMapTileFactor = 4
    layer.StarCommands.nCollMask = 255
    layer.StarCommands.nReactType = 0
    layer.StarCommands.nSurfaceType = -1
    
    
    # Do a little hack here to get a diffuse texture out of the mesh   
    try:
        mat = obj.data.materials[0]
        # Get the nodes in the material node tree
        nodes = mat.node_tree.nodes
        # Get a principled node (If there is 2 of these we should probably freak out and assert or some shit)
        bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
        # Get the NodeLink from the base color node
        base_color = bsdf.inputs['Base Color'].links[0]
        # Print the image connecting to this node
        outTex = base_color.from_node.image.name
        outTex = outTex[:len(outTex)-4]
        layer.szTexName[0] = outTex
    except:
        #print("Unable to extract texture from", obj.name)
        layer.szTexName[0] = "grid_64_pur"
    
    mat = pasm_file_def.PASMMaterial()
    mat.nLayerCount = 1
    mat.aMatLayers[0] = layer
    mat.nNumIndices = 36 # This is for a triangulated cube
    mat.StarCommands.bUseDiffuseColor = 1
    mat.StarCommands.bUseSpecularColor = 1
    mat.StarCommands.TintRGB = [1.0, 1.0, 1.0]
    mat.StarCommands.nShaderNum = 0
    mat.StarCommands.fBumpMapTileFactor = 1
    mat.StarCommands.fDetailMapTileFactor = 4
    mat.StarCommands.nCollMask = 255
    mat.StarCommands.nReactType = 0
    mat.StarCommands.nSurfaceType = -1
     
    # This returns a new instance of the vertex data
    # Whatever modifed here won't affect the scene
    test = obj.to_mesh()
        
    # We're gonna triangulate the mesh first before we work with it further
    bm = bmesh.new()
    bm.from_mesh(test)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(test)
    bm.free()
    
    UVLAYER = test.uv_layers[0] # Hardcoded reference to UV MAP
    # Flip UVs vertically across (0.5, 0.5) point
    reflectionPoint = 0.500
    for uv in UVLAYER.data:
        VBuffer = uv.uv[1]
        VBuffer = VBuffer - reflectionPoint
        VBuffer = -VBuffer
        VBuffer = VBuffer + reflectionPoint
        uv.uv[1] = VBuffer
        
    aVertexBuffer = [] # Buffer to hold all unique PASMVerts
    aIndexBuffer = [] # New PASMVertIndex buffer for remapped indices
    indexIndex = 0 # my brain is melting
    
    # Get the faces of the mesh
    for face in test.polygons:
        for index in (range(len(face.vertices))):
            #Sanity Print
            #print("VERTEX INDEX:", face.vertices[index], "POS:", test.vertices[face.vertices[index]].co, "  \tNORMAL:", test.vertices[face.vertices[index]].normal, "  \tLOOP INDEX:", face.loop_indices[index], "  \tUV:", UVLAYER.data[face.loop_indices[index]].uv)
    
            # Assemble a PASMVert with this vertex info
            tempVertex = pasm_file_def.PASMVert()
            
            # Multiply our world position matrix by the vertex position X Y Z to get world space position of verts
            vertPosAfterWTM = obj.matrix_world @ test.vertices[face.vertices[index]].co
            tempVertex.Pos[0] = vertPosAfterWTM[0]
            tempVertex.Pos[1] = vertPosAfterWTM[2]
            tempVertex.Pos[2] = vertPosAfterWTM[1]
            
            # This deserves a bit of history...
            # For the longest time I tried making tempVertex.Norm = "test.vertices[face.vertices[index]].normal" work
            # But this doesn't work since a single vert can be shared across multiple polygons
            # However on a whim I decided each of the verts of a single polygon share the same normal...
            # And it worked!
            tempVertex.Norm[0] = face.normal[0]
            tempVertex.Norm[1] = face.normal[2]
            tempVertex.Norm[2] = face.normal[1]
            
            tempVertex.aUVs[0] = UVLAYER.data[face.loop_indices[index]].uv
    
            # Is this PASMVert unique?
            if tempVertex not in aVertexBuffer:
                aVertexBuffer.append(tempVertex)
                #print("ADD NEW PASMVERTEX AT INDEX:", indexIndex)
                aIndexBuffer.append(indexIndex)
                indexIndex = indexIndex + 1
            else:
                #print("PASMVERTEX ALREADY EXISTS AT INDEX:", aVertexBuffer.index(tempVertex))
                aIndexBuffer.append(aVertexBuffer.index(tempVertex))
    
    # Another index buffer lol
    bIndexBuffer = []
    for entry in aIndexBuffer:
        indexBuf = pasm_file_def.PASMVertIndex()
        indexBuf.nVertIndex = entry
        bIndexBuffer.append(indexBuf)
    
    outSegment.aMaterials.append(mat)
    outSegment.nNumMaterials = 1
    outSegment.aVertices = aVertexBuffer
    outSegment.aIndicies = bIndexBuffer
    
    outSegment.nNumVerts = len(aVertexBuffer)
    outSegment.nNumIndices = len(bIndexBuffer)
    # This is assuming the entire mesh is the same material
    mat.nNumIndices = len(bIndexBuffer)
    
    # Folks, never forget to remove data blocks you are no longer using, otherwise Blender might crash,
    # and that's no good
    #test.to_mesh_clear()
    
    # Finally, write data to the file, and our header
    g_class.file.write(outSegment.packBytes())
    g_class.gWldHeader.fileSize += len(outSegment.packBytes())
    g_class.gWldHeader.nNumSegments += 1
    
    
    
    
    