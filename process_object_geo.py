# Module that processes a geo object and returns byte data

import bmesh # Need this to triangulate the mesh

from . import pasm_file_def # Get our PASM file classes

from . import g_class # Get our global variables for the header data

from . import pasm_math # PASM helper defs

from .process_star_command import CMaterialStringParser # Import just the Material Star Command Parser

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
    # Don't work with meshes that have no material
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
        
    aVertexBuffer  = [] # Array buffer for holding every all unique PASMVerts(), used for file export
    aIndexBuffer   = [] # Array buffer for holding every remapped index as a PASMVertIndex(), used for file export
    nLargestIndex  = 0  # When adding a new unique vertex index to aIndexBuffer we use this value then increment
       
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
              
        # Parse parent material name for star commands & material flags
        matStrParser = CMaterialStringParser()       
        matStrParser.ResetToDefaults()
        matStrParser.Parse(obj.data.materials[matIndex].name.lower())
        mat.StarCommands = matStrParser.m_ApeCommands     
        mat.nFlags = matStrParser.m_nMatFlags
        mat.nAffectAngle = matStrParser.m_nAffectAngle

        #Parent material uses a special nShaderNum compared to layer / child materials
        mat.StarCommands.nShaderNum = 0 # In the future don't hard code this
               
        mat.nFirstIndex = len(aIndexBuffer)
        
        layer = pasm_file_def.PASMLayer()
        
        # Messily get our diffuse texture for this material   
        try:
            # Get the material output
            matOut = obj.data.materials[matIndex].node_tree.nodes["Material Output"]
            # Get the Fang Material Node group connected to it
            fangMatGroup = matOut.inputs["Surface"].links[0].from_node
            
            if (fangMatGroup.node_tree.name == "FANG Material"):
                print("We got a FANG Material!")
                
                # Construct a layer that will act as our diffuse texture, nothing fancy YET
                # This Layer is based on Floor & Wall Mesh from testwld scene... Are these good default values?
                layer = pasm_file_def.PASMLayer()
                layer.bTextured = 1
                layer.fUnitAlphaMultiplier = 1.0
                layer.SpecularRGB = [0.8, 0.8, 0.8]
                layer.fShininess = 58.5
                layer.fShinStr = 0.25
                
                # Parse layer / child material name for star commands
                layerStrParser = CMaterialStringParser()
                layerStrParser.ResetToDefaults()
                # Use Star Commands from the Parent Material as a starting base for the layer material
                layerStrParser.m_ApeCommands = matStrParser.m_ApeCommands
                layerStrParser.Parse(obj.data.materials[matIndex].name.lower())
                layer.StarCommands = layerStrParser.m_ApeCommands
            
                # Get the NodeLink from the base color node
                base_color = fangMatGroup.inputs["Diffuse Color"].links[0].from_node.image.name
                # Print the image connecting to this node
                outTexB = base_color.split(".",1)[0]
                layer.szTexName[pasm_file_def.PASMLayerIndex_e.APE_LAYER_TEXTURE_DIFFUSE] = outTexB
                
                try:
                    # Get the NodeLink from the Environment Map node
                    base_color = fangMatGroup.inputs["Environment Map"].links[0].from_node.image.name
                    # Print the image connecting to this node
                    outTexB = base_color.split(".",1)[0]
                    layer.szTexName[pasm_file_def.PASMLayerIndex_e.APE_LAYER_TEXTURE_ENVIRONMENT] = outTexB
                except:
                    pass
                    
                try:
                    # Get the NodeLink from the Detail Map node
                    base_color = fangMatGroup.inputs["Detail Map"].links[0].from_node.image.name
                    # Print the image connecting to this node
                    outTexB = base_color.split(".",1)[0]
                    layer.szTexName[pasm_file_def.PASMLayerIndex_e.APE_LAYER_TEXTURE_DETAIL] = outTexB
                except:
                    pass
                
                if(fangMatGroup.inputs["Illumination"].default_value != 0):
                    layer.StarCommands.bUseEmissiveColor = 1
                    layer.IllumRGB[0] = fangMatGroup.inputs["Illumination"].default_value
                    layer.IllumRGB[1] = fangMatGroup.inputs["Illumination"].default_value
                    layer.IllumRGB[2] = fangMatGroup.inputs["Illumination"].default_value
                
                if(layer.StarCommands.nFlags & 0x02 == 0x02):
                    layer.StarCommands.TintRGB[0] = pasm_math.color_scene_linear_to_srgb(fangMatGroup.inputs["Tint Color"].default_value[0])
                    layer.StarCommands.TintRGB[1] = pasm_math.color_scene_linear_to_srgb(fangMatGroup.inputs["Tint Color"].default_value[1])
                    layer.StarCommands.TintRGB[2] = pasm_math.color_scene_linear_to_srgb(fangMatGroup.inputs["Tint Color"].default_value[2])
                    
                mat.aMatLayers[0] = layer # Link our base layer with our material
                mat.nLayerCount += 1
            elif (fangMatGroup.node_tree.name == "FANG Composite"):
                print("We got a FANG Composite!")
                
                # Construct a layer that will act as our diffuse texture, nothing fancy YET
                # This Layer is based on Floor & Wall Mesh from testwld scene... Are these good default values?
                layer = pasm_file_def.PASMLayer()
                layer.bTextured = 1
                layer.fUnitAlphaMultiplier = 1.0
                layer.SpecularRGB = [0.8, 0.8, 0.8]
                layer.fShininess = 58.5
                layer.fShinStr = 0.25
                
                # Parse layer / child material name for star commands
                layerStrParser = CMaterialStringParser()
                layerStrParser.ResetToDefaults()
                # Use Star Commands from the Parent Material as a starting base for the layer material
                layerStrParser.m_ApeCommands = matStrParser.m_ApeCommands
                layerStrParser.Parse(obj.data.materials[matIndex].name.lower())
                layer.StarCommands = layerStrParser.m_ApeCommands
            
                # Get the NodeLink from the base color node
                base_color = fangMatGroup.inputs["Base"].links[0].from_node.inputs["Diffuse Color"].links[0].from_node.image.name
                # Print the image connecting to this node
                outTexB = base_color.split(".",1)[0]
                layer.szTexName[pasm_file_def.PASMLayerIndex_e.APE_LAYER_TEXTURE_DIFFUSE] = outTexB
                
                try:
                    # Get the NodeLink from the Environment Map node
                    base_color = fangMatGroup.inputs["Base"].links[0].from_node.inputs["Environment Map"].links[0].from_node.image.name
                    # Print the image connecting to this node
                    outTexB = base_color.split(".",1)[0]
                    layer.szTexName[pasm_file_def.PASMLayerIndex_e.APE_LAYER_TEXTURE_ENVIRONMENT] = outTexB
                except:
                    pass
                    
                try:
                    # Get the NodeLink from the Detail Map node
                    base_color = fangMatGroup.inputs["Base"].links[0].from_node.inputs["Detail Map"].links[0].from_node.image.name
                    # Print the image connecting to this node
                    outTexB = base_color.split(".",1)[0]
                    layer.szTexName[pasm_file_def.PASMLayerIndex_e.APE_LAYER_TEXTURE_DETAIL] = outTexB
                except:
                    pass
                
                if(fangMatGroup.inputs["Base"].links[0].from_node.inputs["Illumination"].default_value != 0):
                    layer.StarCommands.bUseEmissiveColor = 1
                    layer.IllumRGB[0] = fangMatGroup.inputs["Base"].links[0].from_node.inputs["Illumination"].default_value
                    layer.IllumRGB[1] = fangMatGroup.inputs["Base"].links[0].from_node.inputs["Illumination"].default_value
                    layer.IllumRGB[2] = fangMatGroup.inputs["Base"].links[0].from_node.inputs["Illumination"].default_value
                
                if(layer.StarCommands.nFlags & 0x02 == 0x02):
                    layer.StarCommands.TintRGB[0] = pasm_math.color_scene_linear_to_srgb(fangMatGroup.inputs["Base"].links[0].from_node.inputs["Tint Color"].default_value[0])
                    layer.StarCommands.TintRGB[1] = pasm_math.color_scene_linear_to_srgb(fangMatGroup.inputs["Base"].links[0].from_node.inputs["Tint Color"].default_value[1])
                    layer.StarCommands.TintRGB[2] = pasm_math.color_scene_linear_to_srgb(fangMatGroup.inputs["Base"].links[0].from_node.inputs["Tint Color"].default_value[2])
                
                mat.aMatLayers[0] = layer # Link our base layer with our material
                mat.nLayerCount += 1
                
                # Construct a layer that will act as our diffuse texture, nothing fancy YET
                # This Layer is based on Floor & Wall Mesh from testwld scene... Are these good default values?
                layer = pasm_file_def.PASMLayer()
                layer.bTextured = 1
                layer.fUnitAlphaMultiplier = 1.0
                layer.SpecularRGB = [0.8, 0.8, 0.8]
                layer.fShininess = 58.5
                layer.fShinStr = 0.25
                
                # Parse layer / child material name for star commands
                layerStrParser = CMaterialStringParser()
                layerStrParser.ResetToDefaults()
                # Use Star Commands from the Parent Material as a starting base for the layer material
                layerStrParser.m_ApeCommands = matStrParser.m_ApeCommands
                layerStrParser.Parse(obj.data.materials[matIndex].name.lower())
                layer.StarCommands = layerStrParser.m_ApeCommands
            
                # Get the NodeLink from the base color node
                base_color = fangMatGroup.inputs["Layer 1"].links[0].from_node.inputs["Diffuse Color"].links[0].from_node.image.name
                # Print the image connecting to this node
                outTexB = base_color.split(".",1)[0]
                layer.szTexName[pasm_file_def.PASMLayerIndex_e.APE_LAYER_TEXTURE_DIFFUSE] = outTexB
                
                try:
                    # Get the NodeLink from the Environment Map node
                    base_color = fangMatGroup.inputs["Layer 1"].links[0].from_node.inputs["Environment Map"].links[0].from_node.image.name
                    # Print the image connecting to this node
                    outTexB = base_color.split(".",1)[0]
                    layer.szTexName[pasm_file_def.PASMLayerIndex_e.APE_LAYER_TEXTURE_ENVIRONMENT] = outTexB
                except:
                    pass
                    
                try:
                    # Get the NodeLink from the Detail Map node
                    base_color = fangMatGroup.inputs["Layer 1"].links[0].from_node.inputs["Detail Map"].links[0].from_node.image.name
                    # Print the image connecting to this node
                    outTexB = base_color.split(".",1)[0]
                    layer.szTexName[pasm_file_def.PASMLayerIndex_e.APE_LAYER_TEXTURE_DETAIL] = outTexB
                except:
                    pass
                
                if(fangMatGroup.inputs["Layer 1"].links[0].from_node.inputs["Illumination"].default_value != 0):
                    layer.StarCommands.bUseEmissiveColor = 1
                    layer.IllumRGB[0] = fangMatGroup.inputs["Layer 1"].links[0].from_node.inputs["Illumination"].default_value
                    layer.IllumRGB[1] = fangMatGroup.inputs["Layer 1"].links[0].from_node.inputs["Illumination"].default_value
                    layer.IllumRGB[2] = fangMatGroup.inputs["Layer 1"].links[0].from_node.inputs["Illumination"].default_value
                
                if(layer.StarCommands.nFlags & 0x02 == 0x02):
                    layer.StarCommands.TintRGB[0] = pasm_math.color_scene_linear_to_srgb(fangMatGroup.inputs["Layer 1"].links[0].from_node.inputs["Tint Color"].default_value[0])
                    layer.StarCommands.TintRGB[1] = pasm_math.color_scene_linear_to_srgb(fangMatGroup.inputs["Layer 1"].links[0].from_node.inputs["Tint Color"].default_value[1])
                    layer.StarCommands.TintRGB[2] = pasm_math.color_scene_linear_to_srgb(fangMatGroup.inputs["Layer 1"].links[0].from_node.inputs["Tint Color"].default_value[2])
                
                mat.aMatLayers[1] = layer # Link layer 1 with our material
                mat.nLayerCount += 1
            else:
                raise ValueError("NOT A FANG MATERIAL!!!")
            
        except Exception as e: 
            print("Error extracing texture")
            print(e)
            
            layer.szTexName[0] = "grid_64_pur"         
            mat.aMatLayers[0] = layer # Link our base layer with our material
            mat.nLayerCount += 1
     
        # Get the faces of the mesh
        for face in geo.polygons:
            if face.material_index != matIndex:
                #print("Polygon not of material index:", matIndex)
                continue
            for index in (range(len(face.vertices))):
                
                #Sanity Print
                #print("VERTEX INDEX:", face.vertices[index], "POS:", geo.vertices[face.vertices[index]].co, "  \tNORMAL:", geo.vertices[face.vertices[index]].normal, "  \tLOOP INDEX:", face.loop_indices[index], "  \tUV:", UVLAYER.data[face.loop_indices[index]].uv)
        
                # Assemble a PASMVert with this vertex info
                entryVertex = pasm_file_def.PASMVert()
                
                # Multiply our world position matrix by the vertex position X Y Z to get world space position of verts
                vertPosAfterWTM = obj.matrix_world @ geo.vertices[face.vertices[index]].co
                entryVertex.Pos[0] = vertPosAfterWTM[0]
                entryVertex.Pos[1] = vertPosAfterWTM[2]
                entryVertex.Pos[2] = vertPosAfterWTM[1]
                
                # This deserves a bit of history...
                # For the longest time I tried making entryVertex.Norm = "geo.vertices[face.vertices[index]].normal" work
                # But this doesn't work since a single vert can be shared across multiple polygons
                # However on a whim I decided each of the verts of a single polygon share the same normal...
                # And it worked!
                entryVertex.Norm[0] = face.normal[0]
                entryVertex.Norm[1] = face.normal[2]
                entryVertex.Norm[2] = face.normal[1]
                
                entryVertex.aUVs[0] = UVLAYER.data[face.loop_indices[index]].uv
        
                # Is this PASMVert unique?
                if entryVertex not in aVertexBuffer:
                    aVertexBuffer.append(entryVertex)
                    #print("ADD NEW PASMVERTEX AT INDEX:", nLargestIndex)
                    indexBuf = pasm_file_def.PASMVertIndex()
                    indexBuf.nVertIndex = nLargestIndex
                    aIndexBuffer.append(indexBuf)
                    nLargestIndex = nLargestIndex + 1
                else:
                    #print("PASMVERTEX ALREADY EXISTS AT INDEX:", aVertexBuffer.index(entryVertex))
                    indexBuf = pasm_file_def.PASMVertIndex()
                    indexBuf.nVertIndex = aVertexBuffer.index(entryVertex)
                    aIndexBuffer.append(indexBuf)
        
        mat.nNumIndices = len(aIndexBuffer) - mat.nFirstIndex
    
        outSegment.aMaterials.append(mat)
        outSegment.nNumMaterials += 1
    
    # OK, every polygon accounted for, now update outSegment data
    outSegment.aVertices   = aVertexBuffer
    outSegment.aIndicies   = aIndexBuffer   
    outSegment.nNumVerts   = len(aVertexBuffer)
    outSegment.nNumIndices = len(aIndexBuffer)
    
    # Finally, write data to the file, and our header
    g_class.file.write(outSegment.packBytes())
    g_class.gWldHeader.fileSize += len(outSegment.packBytes())
    g_class.gWldHeader.nNumSegments += 1