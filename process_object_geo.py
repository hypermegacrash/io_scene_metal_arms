# Module that processes a geo object and returns byte data

import bmesh # Need this to triangulate the mesh

from . import pasm_file_def # Get our PASM file classes

from . import g_class # Get our global variables for the header data

from .process_star_command import CMatStringParser # Import just the Material Star Command Parser

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
    # Special request from Vissova, add support for start_ meshes
    if(obj.name.find("start_", 0, 6) != -1):
        return
    # Don't work with meshes that have no material... yet
    # Maybe in the future apply a S2 styled missing material
    if(len(obj.data.materials) == 0):
        print("The object", obj.name, "has no materials, skipping")
        return
        
    print(obj.name, "is a geo object")

    outSegment = pasm_file_def.PASMSegment()
    outSegment.szMeshName = obj.name
    #outSegment.szMeshName = "segment" + str(g_class.gWldHeader.nNumSegments)
    
    # This returns a new instance of the vertex data with modifiers applied
    # Whatever modifed here won't affect the scene
    import bpy
    dg = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(dg)
    geo = eval_obj.to_mesh()
    #geo = obj.to_mesh()
        
    # We're gonna triangulate the mesh first before we work with it further
    bm = bmesh.new()
    bm.from_mesh(geo)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(geo)
    bm.free()
    
    UVLAYER = geo.uv_layers[0] # Hardcoded reference to UV MAP
    # Flip UVs vertically across (0.5, 0.5) point
    reflectionPoint = 0.500
    for uv in UVLAYER.data:
        VBuffer = uv.uv[1]
        VBuffer = VBuffer - reflectionPoint
        VBuffer = -VBuffer
        VBuffer = VBuffer + reflectionPoint
        uv.uv[1] = VBuffer
        
    aVertexBuffer = [] # Buffer to hold all unique PASMVerts
    aIndexBuffer  = [] # New PASMVertIndex buffer for remapped indices
    indexIndex    = 0  # my brain is melting 
    bIndexBuffer  = [] # Another index buffer lol
    
    #strParser = CMatStringParser()
    
    # We itterate over each material to append new polygons into the segment   
    for matIndex in range(len(obj.data.materials)):
        # Check if this material is unused
        bIsUsed = False
        for face in geo.polygons:
            if face.material_index == matIndex:
                bIsUsed = True             
        if bIsUsed == False:
            # Unused material slot
            continue            
        #print("MATERIAL INDEX:", matIndex, "bIsUsed:", bIsUsed)
        
        # Construct our material
        mat = pasm_file_def.PASMMaterial()
        mat.StarCommands.bUseDiffuseColor = 1
        mat.StarCommands.bUseSpecularColor = 1
        mat.StarCommands.TintRGB = [1.0, 1.0, 1.0]
        mat.StarCommands.nShaderNum = 0
        mat.StarCommands.fBumpMapTileFactor = 1
        mat.StarCommands.fDetailMapTileFactor = 4
        mat.StarCommands.nCollMask = 255 # Can also be represented as -1
        mat.StarCommands.nReactType = 0
        mat.StarCommands.nSurfaceType = -1
        
        nStartingIndex = len(bIndexBuffer)
        mat.nFirstIndex  = nStartingIndex

        # Construct a layer that will act as our diffuse texture, nothing fancy YET
        # This Layer is based on Floor & Wall Mesh from testwld scene... Are these good default values?
        layer = pasm_file_def.PASMLayer()
        layer.bTextured = 1
        layer.fUnitAlphaMultiplier = 1.0
        layer.SpecularRGB = [0.8, 0.8, 0.8]
        layer.fShininess = 58.5
        layer.fShinStr = 0.25
        # Layer uses a special nShaderNum compared to Material
        # Are Star Commands from the Material used as a starting base to then be overwritten by the layer?
        layer.StarCommands.bUseDiffuseColor = 1
        layer.StarCommands.bUseSpecularColor = 1
        layer.StarCommands.TintRGB = [1.0, 1.0, 1.0]
        layer.StarCommands.nShaderNum = -1  # Difference between Layer & Material
        layer.StarCommands.fBumpMapTileFactor = 1
        layer.StarCommands.fDetailMapTileFactor = 4
        layer.StarCommands.nCollMask = 255
        layer.StarCommands.nReactType = 0
        layer.StarCommands.nSurfaceType = -1
        
        mat.aMatLayers[0] = layer # Link our base layer with our material
        mat.nLayerCount += 1
        
        # Messily get our diffuse texture for this material   
        try:
            # Get the nodes in the material node tree
            nodes = obj.data.materials[matIndex].node_tree.nodes
            # Get a principled node (If there is 2 of these we should probably freak out and assert)
            bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
            # Get the NodeLink from the base color node
            base_color = bsdf.inputs['Base Color'].links[0]
            # Print the image connecting to this node
            outTex = base_color.from_node.image.name
            outTexB = outTex.split(".",1)[0]
            layer.szTexName[0] = outTexB
        except:
            #print("Unable to extract texture from", obj.name)
            layer.szTexName[0] = "grid_64_pur"
     
        # Get the faces of the mesh
        for face in geo.polygons:
            if face.material_index != matIndex:
                #print("Polygon not of material index:", matIndex)
                continue
            for index in (range(len(face.vertices))):
                
                #Sanity Print
                #print("VERTEX INDEX:", face.vertices[index], "POS:", geo.vertices[face.vertices[index]].co, "  \tNORMAL:", geo.vertices[face.vertices[index]].normal, "  \tLOOP INDEX:", face.loop_indices[index], "  \tUV:", UVLAYER.data[face.loop_indices[index]].uv)
        
                # Assemble a PASMVert with this vertex info
                tempVertex = pasm_file_def.PASMVert()
                
                # Multiply our world position matrix by the vertex position X Y Z to get world space position of verts
                vertPosAfterWTM = obj.matrix_world @ geo.vertices[face.vertices[index]].co
                tempVertex.Pos[0] = vertPosAfterWTM[0]
                tempVertex.Pos[1] = vertPosAfterWTM[2]
                tempVertex.Pos[2] = vertPosAfterWTM[1]
                
                # This deserves a bit of history...
                # For the longest time I tried making tempVertex.Norm = "geo.vertices[face.vertices[index]].normal" work
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
      
        for entry in aIndexBuffer:
            indexBuf = pasm_file_def.PASMVertIndex()
            indexBuf.nVertIndex = entry
            bIndexBuffer.append(indexBuf)
        
        mat.nNumIndices = len(bIndexBuffer) - nStartingIndex
    
        outSegment.aMaterials.append(mat)
        outSegment.nNumMaterials += 1
    
    # OK, every polygon accounted for, now update outSegment data
    outSegment.aVertices   = aVertexBuffer
    outSegment.aIndicies   = bIndexBuffer   
    outSegment.nNumVerts   = len(aVertexBuffer)
    outSegment.nNumIndices = len(bIndexBuffer)
    
    # Finally, write data to the file, and our header
    g_class.file.write(outSegment.packBytes())
    g_class.gWldHeader.fileSize += len(outSegment.packBytes())
    g_class.gWldHeader.nNumSegments += 1