# Third rewrite after hiatus. Module that processes a geo object and returns byte data

# FANG TOOLKIT
from . import file_def_ape  # Get our PASM file classes
from . import g_class       # Get our global variables for the header data
from . import pasm_math     # PASM helper defs
from .process_star_command import CMaterialStringParser # Import just the Material Star Command Parser
# BLENDER
import copy # We need to do a deep copy rather than shallow copy because exported data gets finicky
import bpy  # Pass this into the func or something so we aren't constantly grabbing, releasing this

# Process and create a FANG Material
def ParseMaterial(matName, fangMatGroup, matStrParser):
    # Construct a layer containing all information to create a surface
    # This Layer is based on Floor & Wall Mesh from testwld scene... Are these good default values?
    layer = file_def_ape.PASMLayer()
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
        layer.szTexName[file_def_ape.PASMLayerIndex_e.APE_LAYER_TEXTURE_DIFFUSE] = fangMatGroup.inputs["Diffuse Color"].links[0].from_node.image.name.split(".",1)[0]
    except:
        g_class.printWARNING("Error extracing Diffuse Color Texture for material" + matName + " defaulting to 'grid_64_pur'")
        layer.szTexName[file_def_ape.PASMLayerIndex_e.APE_LAYER_TEXTURE_DIFFUSE] = "grid_64_pur" 
    
    try:    layer.szTexName[file_def_ape.PASMLayerIndex_e.APE_LAYER_TEXTURE_ALPHA_MASK] = fangMatGroup.inputs["Alpha Mask"].links[0].from_node.image.name.split(".",1)[0]
    except: pass
        
    try:    layer.szTexName[file_def_ape.PASMLayerIndex_e.APE_LAYER_TEXTURE_SPECULAR_MASK] = fangMatGroup.inputs["Specular Mask"].links[0].from_node.image.name.split(".",1)[0]
    except: pass
        
    try:    layer.szTexName[file_def_ape.PASMLayerIndex_e.APE_LAYER_TEXTURE_EMISSIVE_MASK] = fangMatGroup.inputs["Emissive Mask"].links[0].from_node.image.name.split(".",1)[0]
    except: pass
        
    try:    layer.szTexName[file_def_ape.PASMLayerIndex_e.APE_LAYER_TEXTURE_ENVIRONMENT] = fangMatGroup.inputs["Environment Map"].links[0].from_node.image.name.split(".",1)[0]
    except: pass
        
    try:    layer.szTexName[file_def_ape.PASMLayerIndex_e.APE_LAYER_TEXTURE_BUMP] = fangMatGroup.inputs["Bump Map"].links[0].from_node.image.name.split(".",1)[0]
    except: pass
        
    try:    layer.szTexName[file_def_ape.PASMLayerIndex_e.APE_LAYER_TEXTURE_DETAIL] = fangMatGroup.inputs["Detail Map"].links[0].from_node.image.name.split(".",1)[0]
    except: pass
    
    if(fangMatGroup.inputs["Illumination"].default_value != 0):
        layer.StarCommands.bUseEmissiveColor = 1
        layer.IllumRGB[0] = fangMatGroup.inputs["Illumination"].default_value
        layer.IllumRGB[1] = fangMatGroup.inputs["Illumination"].default_value
        layer.IllumRGB[2] = fangMatGroup.inputs["Illumination"].default_value
    
    if(layer.StarCommands.nFlags & 0x02 == 0x02):
        matStrParser.m_TintRGB[0] = pasm_math.color_scene_linear_to_srgb(fangMatGroup.inputs["Tint Color"].default_value[0])
        matStrParser.m_TintRGB[1] = pasm_math.color_scene_linear_to_srgb(fangMatGroup.inputs["Tint Color"].default_value[1])
        matStrParser.m_TintRGB[2] = pasm_math.color_scene_linear_to_srgb(fangMatGroup.inputs["Tint Color"].default_value[2])
        
    layer.bTwoSided = int(fangMatGroup.inputs["Two Sided"].default_value)
    if layer.bTwoSided > 1: layer.bTwoSided = 1
    if layer.bTwoSided < 0: layer.bTwoSided = 0
        
    return layer
  
# 1 unit of work for a given mesh
# Return True when successfully added geometry data to PASMSegment
# Return False when an error has occured
def ProcessSegment(obj, outSegment, bExportHierarchy, nLODIdx):
    # If we got this far we can assume that LOD0 has successfully exported and
    # we can therefore skip None entries
    if obj == None: return True
    if(len(obj.data.materials) == 0):
        g_class.printWARNING("The object " + obj.name + " has no materials, skipping")
        return False # Don't work with meshes that have no material
        
    if(len(obj.data.loop_triangles) == 0):
        g_class.printWARNING("The object " + obj.name + " has no triangles, skipping")
        return False # Don't work with meshes that have no material
        
    if(len(obj.data.vertices) == 0):
        g_class.printWARNING("The object " + obj.name + " has no vertices, skipping")
        return False # Don't work with meshes that have no material
        
    #print(obj.name, "is a geo object")
    
    # Check to see if this geo is attached to an armature
    hSkeleton = None
    bSkinned = False
    if(bExportHierarchy):
        # Is this weight painted...
        if obj.vertex_groups: 
            for modifier in obj.modifiers:
                if modifier.type == "ARMATURE":
                    #print("WEIGHT PAINTED: Found our skeleton!")
                    hSkeleton = modifier.object
                    bSkinned = True
                    continue
        # Or is it parented?
        elif (obj.parent_bone):
            #print("PARENTED: Found our skeleton!")
            hSkeleton = obj.parent
            bSkinned = False
                
        # If there is weight painting and theres an armature modifier attached, we got a skinned mesh
        if hSkeleton != None:
            outSegment.bSkinned = True # NOTE: Weight painted and parented geo are both considered skinned by the file
            # Make sure we are in REST pose so we can grab all the data in the rest position
            hSkeleton.data.pose_position = "REST"
            bpy.context.view_layer.update()
            # Rest Pose Change https://blenderartists.org/t/cannot-change-pose-when-rest-position-is-enabled/637989
    
    # This returns a new instance of geometry data with modifiers applied that wont affect scene
    dg = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(dg)
    geo = eval_obj.to_mesh()
    
    # If negative scaling normals will flip when world matrix is applied
    if obj.matrix_world.determinant() < 0.0:
        geo.flip_normals()
    
    # Transform the verts from local space to world space
    from mathutils import Matrix
    # Objects are in local space when part of hierarchy, they are driven by bone location
    geo.transform(Matrix() @ obj.matrix_world)
    
    # Prep
    geo.calc_loop_triangles()
    geo.calc_normals_split()
    
    # Reflect all UVs early to prepare them for the pipeline
    reflectionPoint = 0.500
    for uvlayer in geo.uv_layers:
        for layer in uvlayer.data:
            layer.uv[1] =  layer.uv[1] - reflectionPoint
            layer.uv[1] = -layer.uv[1]
            layer.uv[1] =  layer.uv[1] + reflectionPoint
    
    # Get our color layers
    ColorChannel = None
    AlphaChannel = None
    for vc in geo.color_attributes:
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
        try:
            material = obj.material_slots[face.material_index].material
        except:
            g_class.logError("MATERIAL ERROR: The object " + obj.name + " has faces not assigned to any of it's materials, skipping mesh.")
            return False
        if material is None:
            g_class.printWARNING("There are some faces on the mesh " + obj.name + " that are assigned to an empty material slot.")
            continue
        faceDict[face.material_index].append(face)
    
    # STAR COMMANDS PT 1
    # Star Commands start by grabbing the star commands in the object
    objStrParser = CMaterialStringParser()
    objStrParser.ResetToDefaults()
    objStrParser.Parse( obj.name.lower() )
        
    # We itterate over each material to append new polygons into the segment   
    for matIndex in range(len(obj.data.materials)):
        if not faceDict[matIndex]: continue # If material is unused, bail early
            
        mat = file_def_ape.PASMMaterial()  # Construct our material
        mat.StarCommands.nShaderNum = -1    # Set shader # to -1 to signal we need to set a default
        mat.nLODIndex = nLODIdx
            
        # STAR COMMANDS PT 2
        # We then use the object star commands as a base for all the materials
        matStrParser = CMaterialStringParser()
        matStrParser.ResetToDefaults()
        matStrParser.m_ApeCommands = copy.deepcopy ( objStrParser.m_ApeCommands )
        matStrParser.Parse( obj.data.materials[matIndex].name.lower() ) # Then we parse the material name for star commands & material flags
        
        mat.StarCommands = matStrParser.m_ApeCommands
        mat.nFlags       = matStrParser.m_nMatFlags
        mat.nAffectAngle = matStrParser.m_nAffectAngle
            
        mat.nFirstIndex = len(aIndexBuffer) + outSegment.nNumIndices
        
        layer  = file_def_ape.PASMLayer()
        layer1 = file_def_ape.PASMLayer()
        
        # Get the material output
        for node in obj.data.materials[matIndex].node_tree.nodes:
            if node.type == "OUTPUT_MATERIAL" and node.is_active_output:
                matOut = node
                continue
                
        try:
            fangMatGroup = matOut.inputs["Surface"].links[0].from_node # Get the Node connected to it
        except:
            g_class.logError("MATERIAL ERROR: The Material Output Node for material " + obj.data.materials[matIndex].name.lower() + " in object " + obj.name + " is not connected to a FANG Material / FANG Composite Node Tree. Please fix and retry exporting.")
            return
        
        if fangMatGroup.type != "GROUP":
            g_class.logError("MATERIAL ERROR: The Material Output Node for material " + obj.data.materials[matIndex].name.lower() + " in object " + obj.name + " is not connected to a FANG Material / FANG Composite Node Tree. Please fix and retry exporting.")
            return False
        
        if (fangMatGroup.node_tree.name.split(".",1)[0] == "FANG Material"):
            #print("We got a FANG Material!")
            
            try:
                matStrParser.ResetToDefaults()
                matStrParser.m_ApeCommands = copy.deepcopy ( objStrParser.m_ApeCommands )
                layer = ParseMaterial(obj.data.materials[matIndex].name.lower(), fangMatGroup, matStrParser)
            except:
                g_class.logError("MATERIAL ERROR: Trouble parsing Fang Material " + obj.data.materials[matIndex].name.lower() + " in object " + obj.name + ". Validate your node setup.")
                return False
            mat.aMatLayers[0] = copy.deepcopy( layer ) # Link base layer with our material
            mat.StarCommands.TintRGB = copy.deepcopy ( matStrParser.m_TintRGB ) # Tint applied at the material level, NOT the layer level
            mat.nLayerCount += 1
            
        elif (fangMatGroup.node_tree.name.split(".",1)[0] == "FANG Composite"):
            #print("We got a FANG Composite!")
            
            try:
                matStrParser.ResetToDefaults()
                matStrParser.m_ApeCommands = copy.deepcopy ( objStrParser.m_ApeCommands )
                layer = ParseMaterial(fangMatGroup.inputs["Base"].links[0].from_node.name.lower(), fangMatGroup.inputs["Base"].links[0].from_node, matStrParser)
            except:
                g_class.logError("MATERIAL ERROR: Trouble parsing Fang Material " + obj.data.materials[matIndex].name.lower() + " in object " + obj.name + ". Validate your node setup.")
                return False
            mat.aMatLayers[0] = copy.deepcopy( layer ) # Link base layer with our material
            mat.StarCommands.TintRGB = copy.deepcopy ( matStrParser.m_TintRGB ) # Tint applied at the material level, NOT the layer level
            mat.nLayerCount += 1
            
            try:
                matStrParser.ResetToDefaults()
                matStrParser.m_ApeCommands = copy.deepcopy ( objStrParser.m_ApeCommands )
                layer1 = ParseMaterial(fangMatGroup.inputs["Layer 1"].links[0].from_node.name.lower(), fangMatGroup.inputs["Layer 1"].links[0].from_node, matStrParser)
            except:
                g_class.logError("MATERIAL ERROR: Trouble parsing Fang Material " + obj.data.materials[matIndex].name.lower() + " in object " + obj.name + ". Validate your node setup.")
                return False
            mat.aMatLayers[1] = copy.deepcopy( layer1 ) # Link layer 1 with our material
            mat.nLayerCount += 1
        else:
            raise ValueError("NOT A FANG MATERIAL!!!")
            g_class.logError("MATERIAL ERROR: Unable to parse FANG Material / FANG Composite Node Tree. This is a programmer error.")
            return False
            
        # Setup a default shader if not supplied
        if mat.StarCommands.nShaderNum < 0:
            if mat.nLayerCount == 1: mat.StarCommands.nShaderNum = 0
            else:                    mat.StarCommands.nShaderNum = 11
            
        # This can get annoying showing up everytime so commenting it out until a better solution
        if mat.StarCommands.nShaderNum == 11:
            if mat.aMatLayers[0].szTexName[file_def_ape.PASMLayerIndex_e.APE_LAYER_TEXTURE_DETAIL] != "":
                g_class.printWARNING("MATERIAL WARNING: If you are exporting for Xbox ignore this. Shader 11 is broken on GameCube. Layer 1 will incorrectly " +
                                     "render only the detail map found in the base layer.\n" +
                                     "FIX: Disconnect the detail map from your base layer FANG Material in the FANG Composite material " + obj.data.materials[matIndex].name)
        
        # Buffer of UVs
        # The hacky hack that smells... hacky
        try:
            if (fangMatGroup.node_tree.name.split(".",1)[0] == "FANG Material"):   
                try:    UV0 = geo.uv_layers[ fangMatGroup.inputs["Diffuse Color"].links[0].from_node.inputs["Vector"].links[0].from_node.uv_map ]
                except: UV0 = geo.uv_layers[0]
                
            elif (fangMatGroup.node_tree.name.split(".",1)[0] == "FANG Composite"):
                try:    UV0 = geo.uv_layers[ fangMatGroup.inputs["Base"].links[0].from_node.inputs["Diffuse Color"].links[0].from_node.inputs["Vector"].links[0].from_node.uv_map ]
                except: UV0 = geo.uv_layers[0]
                
                try:    UV1 = geo.uv_layers[ fangMatGroup.inputs["Layer 1"].links[0].from_node.inputs["Diffuse Color"].links[0].from_node.inputs["Vector"].links[0].from_node.uv_map ]
                except: UV1 = geo.uv_layers[0]
                
        except Exception as e: 
            g_class.printWARNING("Error extracing UV Group for mesh " + obj.name)
            print(e)
    
        # Mesh geometry take 2
        for triangle in faceDict[matIndex]:
            
            # We need to check if there is an infinitely thin face, said face will cause PASM to crash
            samePos = 0
            if geo.vertices[triangle.vertices[0]].co[0] == geo.vertices[triangle.vertices[1]].co[0] == geo.vertices[triangle.vertices[2]].co[0]:  samePos += 1
            if geo.vertices[triangle.vertices[0]].co[1] == geo.vertices[triangle.vertices[1]].co[1] == geo.vertices[triangle.vertices[2]].co[1]:  samePos += 1
            if geo.vertices[triangle.vertices[0]].co[2] == geo.vertices[triangle.vertices[1]].co[2] == geo.vertices[triangle.vertices[2]].co[2]:  samePos += 1
            
            if(samePos > 1):
                g_class.printWARNING("ATTENTION ARTIST: YOU HAVE AN INFINITELY THIN FACE!!!")
                continue
    
            for loop, vertex, normal in zip(triangle.loops, triangle.vertices, triangle.split_normals):
                entryVertex = file_def_ape.PASMVert() # Assemble a PASMVert for this vertex
                
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
                    entryVertex.Color[0] = copy.copy ( pasm_math.color_scene_linear_to_srgb(float(ColorChannel.data[vertex].color[0]) ) )
                    entryVertex.Color[1] = copy.copy ( pasm_math.color_scene_linear_to_srgb(float(ColorChannel.data[vertex].color[1]) ) )
                    entryVertex.Color[2] = copy.copy ( pasm_math.color_scene_linear_to_srgb(float(ColorChannel.data[vertex].color[2]) ) )
                
                # Vertex Alpha
                if AlphaChannel != None: entryVertex.Color[3] = copy.copy ( pasm_math.color_scene_linear_to_srgb(float(AlphaChannel.data[vertex].color[0]) ) )
                else:                    entryVertex.Color[3] = 1.0 # What the... if the default is 1.0 set it on init
                
                # Vertex Weights
                # In FANG, the 3 vertices that form a triangle can only have a max of 4 vertex weights total.
                # SAS's Max Exporter contextually understands how to assign 1 vertex of a triangle 2 vertex weights instead of 1.
                # This Blender implimentation could support that, but for brevity's sake we use only the largest weight group per vertex and assign it max influence (1.0f)
                # https://blender.stackexchange.com/questions/14250/how-to-restrict-vertex-weights-to-no-more-than-n-number-of-bones
                if hSkeleton != None:
                    pWeight = file_def_ape.PASMWeight()
                    if(bSkinned): # This is a weight painted mesh
                        for vgroup in geo.vertices[vertex].groups:
                            # Survival of the fittest, largest weight wins
                            if vgroup.weight > pWeight.fWeight:
                                pWeight.fWeight = vgroup.weight
                                pWeight.fBoneIndex = hSkeleton.pose.bones.find(obj.vertex_groups[vgroup.group].name)
                        pWeight.fWeight = 1 # If this is the only weight, might as well have it be max influence
                        entryVertex.aWeights[0] = pWeight
                        entryVertex.fNumWeights = 1 # We could support 2 max
                    else: # This is a unskinned / parented mesh
                        pWeight.fBoneIndex = hSkeleton.pose.bones.find(obj.parent_bone)
                        pWeight.fWeight = 1 # If this is the only weight, might as well have it be max influence
                        entryVertex.aWeights[0] = pWeight
                        entryVertex.fNumWeights = 1 # We could support 2 max
                    
                # We need to check if we've seen this PASMVert yet, use a hashmap / dict for super fast lookups ( hashmap is O(n), list is O(n^2) )
                indexBuf = file_def_ape.PASMVertIndex()
                if entryVertex in vertexMap: # We've seem this PASMVert already
                    indexBuf.nVertIndex = vertexMap[entryVertex] # Find the PASMVert in the hashmap
                else: # We have not seen this PASMVert yet
                    vertexMap[entryVertex] = len(aVertexBuffer)                         # Add the hash of the PASMVert to the hashmap / dict
                    indexBuf.nVertIndex    = len(aVertexBuffer) + outSegment.nNumVerts  # This is now the newest triangle index, therefore it is the largest
                    aVertexBuffer.append(entryVertex)                                   # Add the PASMVert to the vertex buffer
                aIndexBuffer.append(indexBuf) # Finally, add the PASMVertIndex to the index buffer list
    
        mat.nNumIndices = len(aIndexBuffer) - (mat.nFirstIndex - outSegment.nNumIndices)
    
        outSegment.aMaterials.append(copy.deepcopy(mat))
        outSegment.nNumMaterials += 1
    
    # Clean up? IDK what this does honestly
    eval_obj.to_mesh_clear()
    
    # OK, every polygon accounted for, now update outSegment data
    # We do this multiple times per LOD
    outSegment.aVertices   += aVertexBuffer
    outSegment.aIndicies   += aIndexBuffer
    outSegment.nNumVerts   += len(aVertexBuffer)
    outSegment.nNumIndices += len(aIndexBuffer)

    # NICE! Return True to let code know we successfully added data to this Segment!
    return True

def ExportObjGeo(aLODs, bExportHierarchy):
    outSegment = file_def_ape.PASMSegment()
    
    if type(aLODs) == list: inObj = aLODs[0]
    else:                   inObj = aLODs
    
    if inObj == None:                      return # HOW could this even happen? Sanity check it anyway
    if inObj.name[:4].lower() == "off_":   return # Doesn't matter it's off bail early
    if inObj.type != "MESH":               return # Validate we're working with mesh data and not other stuff
    if inObj.name[:5].lower() == "cell_":  return # We don't do cells
    if inObj.name[:4].lower() == "obj_":   return # objs could be ANY DATATYPE, so check for that
    if inObj.name[:6].lower() == "start_": return # Special request from Vissova, add support for start_ meshes
    
    outSegment.szMeshName = inObj.name
    
    if type(aLODs) == list:
        print(inObj.name, "is a LOD geo object")
        for nLODIdx, geo in enumerate(aLODs):
            if not (ProcessSegment(geo, outSegment, bExportHierarchy, nLODIdx)):
                # If we fail to process ANY LOD of this geo... skip this mesh
                g_class.printWARNING("ERROR PROCESSING LOD " + str(nLODIdx) + " FOR GEO " + inObj.name)
                return
    else:
        print(inObj.name, "is a geo object")
        if not (ProcessSegment(aLODs, outSegment, bExportHierarchy, 0)):
                g_class.printWARNING("ERROR PROCESSING GEO " + inObj.name)
                return
                
    if outSegment.nNumVerts == 0:
        g_class.logError("GEO ERROR: The object " + inObj.name + " was processed with no vertices! Are there empty material slots? Skipping object")
        return
    
    # Finally, write data to the file, and our header
    g_class.file.write(outSegment.packBytes())
    g_class.gApeHeader.fileSize += len(outSegment.packBytes())
    g_class.gApeHeader.nNumSegments += 1
