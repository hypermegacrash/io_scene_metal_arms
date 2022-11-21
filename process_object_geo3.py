# Third rewrite after hiatus. Module that processes a geo object and returns byte data
# Reference: https://github.com/sobotka/blender-addons/blob/master/io_scene_obj/export_obj.py

from . import pasm_file_def # Get our PASM file classes
from . import g_class       # Get our global variables for the header data
from . import pasm_math     # PASM helper defs
from .process_star_command import CMaterialStringParser # Import just the Material Star Command Parser

import copy # We need to do a deep copy rather than shallow copy because exported data gets finicky
#import time # For debugging performance bottlenecks

def ParseMaterial(matName, fangMatGroup, matStrParser):
    # Construct a layer containing all information to create a surface
    # This Layer is based on Floor & Wall Mesh from testwld scene... Are these good default values?
    layer = pasm_file_def.PASMLayer()
    layer.bTextured = 1
    layer.fUnitAlphaMultiplier = 1.0
    
    layer.SpecularRGB[0] = fangMatGroup.inputs["Specular Color"].default_value[0]
    layer.SpecularRGB[1] = fangMatGroup.inputs["Specular Color"].default_value[1]
    layer.SpecularRGB[2] = fangMatGroup.inputs["Specular Color"].default_value[2]
    
    if(fangMatGroup.inputs["Shine Strength"].default_value < 0.05):
        layer.fShinStr   = 0.0
        layer.fShininess = 0.0
    else:
        layer.fShinStr   =  fangMatGroup.inputs["Shine Strength"].default_value / 100.0
        layer.fShininess = (fangMatGroup.inputs["Shininesss"].default_value / 100) * 127.0
        
    # Parse layer / child material name for star commands
    layerStrParser = CMaterialStringParser()
    layerStrParser.ResetToDefaults()
    # Use Star Commands from the Parent Material as a starting base for the layer material
    layerStrParser.m_ApeCommands = copy.copy ( matStrParser.m_ApeCommands )
    layerStrParser.Parse(matName.lower())
    layer.StarCommands = layerStrParser.m_ApeCommands
    
    try:
        # Get the NodeLink from the Base Color node
        base_color = fangMatGroup.inputs["Diffuse Color"].links[0].from_node.image.name
        # Print the image connecting to this node
        outTexB = base_color.split(".",1)[0]
        layer.szTexName[pasm_file_def.PASMLayerIndex_e.APE_LAYER_TEXTURE_DIFFUSE] = outTexB
    except:
        print("Error extracing Diffuse Color Texture, defaulting to 'grid_64_pur'")
        layer.szTexName[pasm_file_def.PASMLayerIndex_e.APE_LAYER_TEXTURE_DIFFUSE] = "grid_64_pur" 
    
    try:
        # Get the NodeLink from the Alpha Mask node
        base_color = fangMatGroup.inputs["Alpha Mask"].links[0].from_node.image.name
        # Print the image connecting to this node
        outTexB = base_color.split(".",1)[0]
        layer.szTexName[pasm_file_def.PASMLayerIndex_e.APE_LAYER_TEXTURE_ALPHA_MASK] = outTexB
    except: pass
        
    try:
        # Get the NodeLink from the Specular Mask node
        base_color = fangMatGroup.inputs["Specular Mask"].links[0].from_node.image.name
        # Print the image connecting to this node
        outTexB = base_color.split(".",1)[0]
        layer.szTexName[pasm_file_def.PASMLayerIndex_e.APE_LAYER_TEXTURE_SPECULAR_MASK] = outTexB
    except: pass
        
    try:
        # Get the NodeLink from the Emissive Mask node
        base_color = fangMatGroup.inputs["Emissive Mask"].links[0].from_node.image.name
        # Print the image connecting to this node
        outTexB = base_color.split(".",1)[0]
        layer.szTexName[pasm_file_def.PASMLayerIndex_e.APE_LAYER_TEXTURE_EMISSIVE_MASK] = outTexB
    except: pass
        
    try:
        # Get the NodeLink from the Environment Map node
        base_color = fangMatGroup.inputs["Environment Map"].links[0].from_node.image.name
        # Print the image connecting to this node
        outTexB = base_color.split(".",1)[0]
        layer.szTexName[pasm_file_def.PASMLayerIndex_e.APE_LAYER_TEXTURE_ENVIRONMENT] = outTexB
    except: pass
        
    try:
        # Get the NodeLink from the Bump Map node
        base_color = fangMatGroup.inputs["Bump Map"].links[0].from_node.image.name
        # Print the image connecting to this node
        outTexB = base_color.split(".",1)[0]
        layer.szTexName[pasm_file_def.PASMLayerIndex_e.APE_LAYER_TEXTURE_BUMP] = outTexB
    except: pass
        
    try:
        # Get the NodeLink from the Detail Map node
        base_color = fangMatGroup.inputs["Detail Map"].links[0].from_node.image.name
        # Print the image connecting to this node
        outTexB = base_color.split(".",1)[0]
        layer.szTexName[pasm_file_def.PASMLayerIndex_e.APE_LAYER_TEXTURE_DETAIL] = outTexB
    except: pass
    
    if(fangMatGroup.inputs["Illumination"].default_value != 0):
        layer.StarCommands.bUseEmissiveColor = 1
        layer.IllumRGB[0] = fangMatGroup.inputs["Illumination"].default_value
        layer.IllumRGB[1] = fangMatGroup.inputs["Illumination"].default_value
        layer.IllumRGB[2] = fangMatGroup.inputs["Illumination"].default_value
    
    if(layer.StarCommands.nFlags & 0x02 == 0x02):
        layer.StarCommands.TintRGB[0] = pasm_math.color_scene_linear_to_srgb(fangMatGroup.inputs["Tint Color"].default_value[0])
        layer.StarCommands.TintRGB[1] = pasm_math.color_scene_linear_to_srgb(fangMatGroup.inputs["Tint Color"].default_value[1])
        layer.StarCommands.TintRGB[2] = pasm_math.color_scene_linear_to_srgb(fangMatGroup.inputs["Tint Color"].default_value[2])
        
    return layer

def ExportObjGeo(obj): 
    if obj.type != "MESH":               return # Validate we're working with mesh data and not other stuff
    if obj.name[:5].lower() == "cell_":  return # We don't do cells
    if obj.name[:4].lower() == "obj_":   return # objs could be ANY DATATYPE, so check for that
    if obj.name[:6].lower() == "start_": return # Special request from Vissova, add support for start_ meshes
    if(len(obj.data.materials) == 0):
        print("The object", obj.name, "has no materials, skipping")
        return # Don't work with meshes that have no material
        
    print(obj.name, "is a geo object")
    
    #tickA = None
    #tickB = None

    outSegment = pasm_file_def.PASMSegment()
    outSegment.szMeshName = obj.name
    
    # This returns a new instance of geometry data with modifiers applied that wont affect scene
    import bpy # Pass this into the func or something so we aren't constantly grabbing, releasing this
    dg = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(dg)
    geo = eval_obj.to_mesh()
    
    # If negative scaling normals will flip when world matrix is applied
    if obj.matrix_world.determinant() < 0.0:
        geo.flip_normals()
    
    # Transform the verts from local space to world space
    from mathutils import Matrix
    geo.transform(Matrix() @ obj.matrix_world)
    
    # Prep
    geo.calc_loop_triangles()
    geo.calc_normals_split()
    
    # UV Requirement
    reflectionPoint = 0.500
    # Reflect all UVs early to prepare them for the pipeline
    for uvlayer in geo.uv_layers:
       for layer in uvlayer.data:
           layer.uv[1] =  layer.uv[1] - reflectionPoint
           layer.uv[1] = -layer.uv[1]
           layer.uv[1] =  layer.uv[1] + reflectionPoint
      
    # Get our color layers
    ColorChannel = None
    AlphaChannel = None
    for vc in geo.vertex_colors:
        outName = vc.name.lower()[:]
        outName = outName.split(".",1)[0]
        if(outName == "alpha"):   AlphaChannel = vc
        elif(outName == "color"): ColorChannel = vc

    aVertexBuffer  = [] # Array buffer for holding every all unique PASMVerts(), used for file export
    aIndexBuffer   = [] # Array buffer for holding every remapped index as a PASMVertIndex(), used for file export
    vertexMap      = {} # Sorting map / dictonary for faster duplicate lookups
    
    # Itterate through the materials once to cache polygons into per material lists for access
    # rather than full itteration through polygons, everytime for each material
    # https://stackoverflow.com/a/8713681
    faceDict = [[] for _ in obj.material_slots]
    
    # Itterate through every loop to seperate faces by material
    for face in geo.loop_triangles:
        material = obj.material_slots[face.material_index].material
        if material is None:
            print("There are some faces on your mesh that are assigned to an empty material slot.")
        faceDict[face.material_index].append(face)
       
    # We itterate over each material to append new polygons into the segment   
    for matIndex in range(len(obj.data.materials)):
        if not faceDict[matIndex]: continue # If material is unused, bail early
            
        mat = pasm_file_def.PASMMaterial()  # Construct our material
        mat.StarCommands.nShaderNum = -1    # Set shader # to -1 to know we need to set a default
              
        # STAR COMMANDS
        # Geometry Name -> Composite Material Name > Material Name
        matStrParser = CMaterialStringParser()
        matStrParser.ResetToDefaults()
        
        matStrParser.Parse( obj.name.lower() )                          # First we parse geo name for star commands & material flags
        matStrParser.Parse( obj.data.materials[matIndex].name.lower() ) # Then we parse the material name for star commands & material flags
        
        mat.StarCommands = matStrParser.m_ApeCommands
        mat.nFlags       = matStrParser.m_nMatFlags
        mat.nAffectAngle = matStrParser.m_nAffectAngle
               
        mat.nFirstIndex = len(aIndexBuffer)
        
        layer  = pasm_file_def.PASMLayer()
        layer1 = pasm_file_def.PASMLayer()
        
        matOut = obj.data.materials[matIndex].node_tree.nodes["Material Output"] # Get the material output
        fangMatGroup = matOut.inputs["Surface"].links[0].from_node               # Get the Fang Material Node group connected to it
        
        if (fangMatGroup.node_tree.name == "FANG Material"):
            print("We got a FANG Material!")
            
            layer = ParseMaterial(obj.data.materials[matIndex].name.lower(), fangMatGroup, matStrParser)
            mat.aMatLayers[0] = copy.copy( layer ) # Link base layer with our material
            mat.nLayerCount += 1
            
        elif (fangMatGroup.node_tree.name == "FANG Composite"):
            print("We got a FANG Composite!")
            
            layer = ParseMaterial(fangMatGroup.inputs["Base"].links[0].from_node.name.lower(), fangMatGroup.inputs["Base"].links[0].from_node, matStrParser)
            mat.aMatLayers[0] = copy.copy( layer ) # Link base layer with our material
            mat.nLayerCount += 1
            
            layer1 = ParseMaterial(fangMatGroup.inputs["Layer 1"].links[0].from_node.name.lower(), fangMatGroup.inputs["Layer 1"].links[0].from_node, matStrParser)
            mat.aMatLayers[1] = copy.copy( layer1 ) # Link layer 1 with our material
            mat.nLayerCount += 1
        else:
            raise ValueError("NOT A FANG MATERIAL!!!")
            
        # Setup a default shader if not supplied
        if mat.StarCommands.nShaderNum < 0:
            if mat.nLayerCount == 1: mat.StarCommands.nShaderNum = 0
            else:                    mat.StarCommands.nShaderNum = 11
        
        # Buffer of UVs
        # The hacky hack that smells... hacky
        try:
            if (fangMatGroup.node_tree.name == "FANG Material"):   
                try:    UV0 = geo.uv_layers[ fangMatGroup.inputs["Diffuse Color"].links[0].from_node.inputs["Vector"].links[0].from_node.uv_map ]
                except: UV0 = geo.uv_layers[0]
                
            elif (fangMatGroup.node_tree.name == "FANG Composite"):
                try:    UV0 = geo.uv_layers[ fangMatGroup.inputs["Base"].links[0].from_node.inputs["Diffuse Color"].links[0].from_node.inputs["Vector"].links[0].from_node.uv_map ]
                except: UV0 = geo.uv_layers[0]
                
                try:    UV1 = geo.uv_layers[ fangMatGroup.inputs["Layer 1"].links[0].from_node.inputs["Diffuse Color"].links[0].from_node.inputs["Vector"].links[0].from_node.uv_map ]
                except: UV1 = geo.uv_layers[0]
                
        except Exception as e: 
            print("Error extracing UV Group")
            print(e)
     
        # Mesh geometry take 2
        for triangle in faceDict[matIndex]:
            
            # We need to check if there is an infinitely thin face, it will cause PASM to crash
            samePos = 0
            if geo.vertices[triangle.vertices[0]].co[0] == geo.vertices[triangle.vertices[1]].co[0] == geo.vertices[triangle.vertices[2]].co[0]:  samePos += 1
            if geo.vertices[triangle.vertices[0]].co[1] == geo.vertices[triangle.vertices[1]].co[1] == geo.vertices[triangle.vertices[2]].co[1]:  samePos += 1
            if geo.vertices[triangle.vertices[0]].co[2] == geo.vertices[triangle.vertices[1]].co[2] == geo.vertices[triangle.vertices[2]].co[2]:  samePos += 1
            
            if(samePos > 1):
                print("ATTENTION ARTIST: YOU HAVE AN INFINITELY THIN FACE!!!")
                continue

            for loop, vertex, normal in zip(triangle.loops, triangle.vertices, triangle.split_normals):
                #geoLogicTic1 = time.perf_counter()
                entryVertex = pasm_file_def.PASMVert() # Assemble a PASMVert for this vertex
                
                entryVertex.Pos[0] = copy.copy ( geo.vertices[vertex].co[0] )
                entryVertex.Pos[1] = copy.copy ( geo.vertices[vertex].co[2] )
                entryVertex.Pos[2] = copy.copy ( geo.vertices[vertex].co[1] )
                
                entryVertex.Norm[0] =  copy.copy ( geo.loops[loop].normal[0] )
                entryVertex.Norm[1] =  copy.copy ( geo.loops[loop].normal[2] )
                entryVertex.Norm[2] =  copy.copy ( geo.loops[loop].normal[1] )
                
                # Blindly try and get the UV data if it exists, if not whatever move on
                try: entryVertex.aUVs[0] = copy.copy ( UV0.data[loop].uv )
                except: pass
                try: entryVertex.aUVs[1] = copy.copy ( UV1.data[loop].uv )
                except: pass
                                       
                 # Vertex Color
                if ColorChannel != None:
                    entryVertex.Color[0] = copy.copy ( float("%.2f" % ColorChannel.data[loop].color[0]) )
                    entryVertex.Color[1] = copy.copy ( float("%.2f" % ColorChannel.data[loop].color[1]) )
                    entryVertex.Color[2] = copy.copy ( float("%.2f" % ColorChannel.data[loop].color[2]) )
                
                # Vertex Alpha
                if AlphaChannel != None: entryVertex.Color[3] = copy.copy ( float("%.2f" % AlphaChannel.data[loop].color[0]) )
                else:                    entryVertex.Color[3] = 1.0 # What the... if the default is 1.0 set it on init
        
                #geoLogicTic2 = time.perf_counter()
                #geoLogicUniqueTic1 = time.perf_counter()
                    
                # We need to check if we've seen this PASMVert yet, use a hashmap / dict for super fast lookups ( hashmap is O(n), list is O(n^2) )
                indexBuf = pasm_file_def.PASMVertIndex()
                if entryVertex in vertexMap: # We've seem this vertex already...
                    indexBuf.nVertIndex = vertexMap[entryVertex] # ...therefore find the vertex in question in the hashmap
                else: # We have not seen this vertex yet
                    vertexMap[entryVertex] = len(aVertexBuffer)  # Add the hash of the PASMVert to the hashmap / dict
                    indexBuf.nVertIndex    = len(aVertexBuffer)  # This is now the newest triangle index, therefore it is the largest
                    aVertexBuffer.append(entryVertex)            # Add the vertex to the vertex buffer
                aIndexBuffer.append(indexBuf) # Finally, add the PASMVertIndex to the index buffer list
                    
                #geoLogicUniqueTic2 = time.perf_counter()
                
            #if tickA == None: tickA = geoLogicTic2 - geoLogicTic1
            #else: tickA += geoLogicTic2 - geoLogicTic1
            #if tickB == None: tickB = geoLogicUniqueTic2 - geoLogicUniqueTic1
            #else: tickB += geoLogicUniqueTic2 - geoLogicUniqueTic1

        mat.nNumIndices = len(aIndexBuffer) - mat.nFirstIndex
    
        outSegment.aMaterials.append(mat)
        outSegment.nNumMaterials += 1
    
    # Clean up? IDK what this does honestly
    eval_obj.to_mesh_clear()
    
    # OK, every polygon accounted for, now update outSegment data
    outSegment.aVertices   = aVertexBuffer
    outSegment.aIndicies   = aIndexBuffer   
    outSegment.nNumVerts   = len(aVertexBuffer)
    outSegment.nNumIndices = len(aIndexBuffer)
    
    # Finally, write data to the file, and our header
    g_class.file.write(outSegment.packBytes())
    g_class.gWldHeader.fileSize += len(outSegment.packBytes())
    g_class.gWldHeader.nNumSegments += 1
    
    # DEBUG
    #print("PROFILING FOR GEO: " + obj.name)
    #print("PASM VERTEX CONSTRUCTION: " + str( float("%.3f" % tickA) ) )
    #print("PASM VERTEX NOT IN LOOP: " + str( float("%.3f" % tickB) ) )