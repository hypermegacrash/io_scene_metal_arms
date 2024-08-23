# Fourth rewrite after hiatus. Module that processes a geo object and returns byte data

# FANG TOOLKIT
from . import file_def_ape  # Get our PASM file classes
from . import g_class       # Get our global variables for the header data
from . import pasm_math     # PASM helper defs
from .process_star_command import CMaterialStringParser # Import just the Material Star Command Parser
# BLENDER
import bpy        # For interacting with Blender Data
import copy       # We need to do a deep copy rather than shallow copy because exported data gets finicky

# This texture only appears in GameCube, could set this up differently
DEFAULT_ERROR_TEXTURE = "grid_64_pur"

# Temporary flag, GameCube has a rendering bug
GC_DEBUG = 0

# This is important because the origin influences how the matrix_local works
def setOrigin(target, inObj):
    bpy.ops.object.select_all(action="DESELECT")
    inObj.select_set(True)
    bpy.context.view_layer.objects.active = inObj
    bpy.ops.object.transform_apply()
    bpy.context.scene.cursor.location = target.location
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    bpy.ops.object.select_all(action="DESELECT")

def attemptModifierApply(modifier):
    try:
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    except Exception as e:
        print("Skipping modifier " + str(modifier.name))

def apply_objects_modifiers_and_transformations(inObj):
    # first apply modifiers so that any objects that affect each other are taken into consideration
    bpy.ops.object.select_all(action="DESELECT")
    inObj.select_set(True)
    bpy.context.view_layer.objects.active = inObj

    for modifier in inObj.modifiers:
        attemptModifierApply(modifier)

    # apply transformations now that world space changes are applied
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True, properties=False)

# Class for handling the conversion of a Blender Mesh to a PASM Segment
# Acts like a container for all the input with functions for processing
class CSegmentConverter:
    def __init__(self):
        self.inObj      = None # Starting mesh we are operating for reference
        self.inArmature = None # If our input is rigged this is the armature we are dealing with
        
        self.workObj    = None # Duplicate Object we edit to our heart's content
        self.workLimbPolygons = None 
        self.workName = None

        self.bExportHierarchy = False
        self.bExportBinarySkinning = False

        self.objStrParser = None
        self.ColorChannel = None
        self.AlphaChannel = None
        self.matNodeGroup = None
        self.nLodIdx = 0

    # Check for LOD*_ Prefix to determine potential segment name and LOD Index
    def getWorkNameAndLODIndex(self):
        self.workName = self.inObj.name
        if self.workName[:3] == "LOD" and self.workName[4:5] == "_":
            self.workName = self.workName[5:]
            self.nLodIdx = int(self.inObj.name[3:4])

    # To not destroy the existing scene, we will duplicate the input object
    # we want to modify then delete after we finish exporting segments
    def createWorkObject(self):
        # Ensure we don't already have a work object
        # In practice this should never happen, more a sanity check
        if self.workObj:
            bpy.ops.object.select_all(action="DESELECT")
            self.workObj.select_set(True)
            bpy.ops.object.delete()
    
        # Duplicate object to apply scale / modifiers / linked data
        bpy.ops.object.select_all(action="DESELECT")
        self.inObj.select_set(True)
        bpy.context.view_layer.objects.active = self.inObj
        bpy.ops.object.duplicate()

        # Assign a handle to our new work object
        self.workObj = bpy.context.view_layer.objects.active

    def deleteWorkObject(self):
        if self.workObj:
            bpy.ops.object.select_all(action="DESELECT")
            self.workObj.select_set(True)
            bpy.ops.object.delete()

    # Check to see if this geo is attached to an armature
    def getArmatureObject(self):
        for modifier in self.inObj.modifiers:
            if modifier.type == "ARMATURE":
                self.inArmature = modifier.object
                return

    # Get our color layers    
    def getColorAttributes(self):
        for attribute in self.workObj.data.color_attributes:
            outName = attribute.name.lower()[:]
            outName = outName.split(".",1)[0]
            if(outName == "alpha"):   self.AlphaChannel = attribute
            elif(outName == "color"): self.ColorChannel = attribute

    # Get our input object star commands flags
    def getObjectStarCommands(self):
        self.objStrParser = CMaterialStringParser()
        self.objStrParser.ResetToDefaults()
        self.objStrParser.Parse( self.inObj.name.lower() )

    # If this is a binary skinned rig we need to update the geometry to follow
    # how the armature is set up
    def prepareWorkRiggedGeo(self):
        # Make object and armature space the same.
        setOrigin(self.inArmature, self.workObj)
    
        # Apply armature scale.
        bpy.ops.object.select_all(action="DESELECT")
        self.inArmature.select_set(True)
        bpy.context.view_layer.objects.active = self.inArmature
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True, properties=False)

    # OBSOLETE: THIS DOESN"T APPLY PASM HANDLES THIS FOR US! =)
    # If we export a binary skinned mesh we need to transform the vertices to our new 
    # origin by applying the inverse model matrix of the bone they are skinned to
    def prepareWorkBinaryRiggedGeo(self):
        for vertex in self.workObj.data.vertices:
            for vgroup in vertex.groups:
                if vgroup.weight > 0.0:
                    tempMtxInv2 = self.inArmature.data.bones[self.workObj.vertex_groups[vgroup.group].name].matrix_local.inverted()
                    vertex.co = tempMtxInv2 @ vertex.co

    # Ingest a Blender Object and preform conversions needed to get the mesh data ready for export
    def prepareWorkObject(self):
        #bpy.ops.object.make_single_user(self.workObj)
    
        apply_objects_modifiers_and_transformations(self.workObj)

        # Rigged geometry must be placed at the origin of the skeleton
        if self.bExportHierarchy and self.inArmature:
            self.prepareWorkRiggedGeo()

        # If negative scaling normals will flip when world matrix is applied
        if self.workObj.matrix_world.determinant() < 0.0:
            self.workObj.data.flip_normals()

        # FANG UV is reflected on the V axis
        reflectionPoint = 0.500
        for uvlayer in self.workObj.data.uv_layers:
            for layer in uvlayer.data:
                layer.uv[1] =  layer.uv[1] - reflectionPoint
                layer.uv[1] = -layer.uv[1]
                layer.uv[1] =  layer.uv[1] + reflectionPoint

        # Convert the mesh to triangles
        self.workObj.data.calc_loop_triangles()

    def areVertexGroupWeightsBinary(self):
        for face in self.workObj.data.loop_triangles:
            for vgroup in self.workObj.data.vertices[face.vertices[0]].groups:
                if vgroup.weight == 0.0:
                    continue
                elif vgroup.weight == 1.0:
                    continue
                else:
                    return False
                
        return True

    # Sort all the triangle polygons by bone they are rigged to if an armature exists
    # Otherwise all polygons are assumed to be in the same segment
    # Key   = Bone Name
    # Value = Polygons rigged to that bone
    def getTrianglesByBone(self):

        self.workLimbPolygons: dict[int, []] = {}

        if self.bExportHierarchy and self.bExportBinarySkinning:
            for face in self.workObj.data.loop_triangles:
                for vgroup in self.workObj.data.vertices[face.vertices[0]].groups:
                    if vgroup.weight > 0.0:
                        if self.workObj.vertex_groups[vgroup.group].name not in self.workLimbPolygons:
                            self.workLimbPolygons[self.workObj.vertex_groups[vgroup.group].name] = []
                        self.workLimbPolygons[self.workObj.vertex_groups[vgroup.group].name].append(face)
                        continue
        else:
            # This is a single segment, therefore it uses the name of the mesh
            self.workLimbPolygons[self.workName] = []
            for face in self.workObj.data.loop_triangles:
                self.workLimbPolygons[self.workName].append(face)
    
    # Return if a triangle has zero area or not
    def isZeroAreaFace(self, triangle):
        samePos = 0
        if self.workObj.data.vertices[triangle.vertices[0]].co[0] == self.workObj.data.vertices[triangle.vertices[1]].co[0] == self.workObj.data.vertices[triangle.vertices[2]].co[0]:  samePos += 1
        if self.workObj.data.vertices[triangle.vertices[0]].co[1] == self.workObj.data.vertices[triangle.vertices[1]].co[1] == self.workObj.data.vertices[triangle.vertices[2]].co[1]:  samePos += 1
        if self.workObj.data.vertices[triangle.vertices[0]].co[2] == self.workObj.data.vertices[triangle.vertices[1]].co[2] == self.workObj.data.vertices[triangle.vertices[2]].co[2]:  samePos += 1

        if(samePos > 1):
            # Skip this face and move onto the next
            g_class.printWARNING("ATTENTION ARTIST: YOU HAVE AN INFINITELY THIN FACE!!!")
            return True
        else:
            return False

    # Parse through the polygons for the material of a given segment
    def ParseMesh(self, inTriangleList, outSegment, vertexMap):
        # First we grab the UVs for this polygon's materials
        UV0 = None
        UV1 = None
        if (self.matNodeGroup.node_tree.name.split(".",1)[0] == "FANG Material"):   
            try:    UV0 = self.workObj.data.uv_layers[ self.matNodeGroup.inputs["Diffuse Color"].links[0].from_node.inputs["Vector"].links[0].from_node.uv_map ]
            except: UV0 = self.workObj.data.uv_layers[0]

        elif (self.matNodeGroup.node_tree.name.split(".",1)[0] == "FANG Composite"):
            try:    UV0 = self.workObj.data.uv_layers[ self.matNodeGroup.inputs["Base"].links[0].from_node.inputs["Diffuse Color"].links[0].from_node.inputs["Vector"].links[0].from_node.uv_map ]
            except: UV0 = self.workObj.data.uv_layers[0]

            try:    UV1 = self.workObj.data.uv_layers[ self.matNodeGroup.inputs["Layer 1"].links[0].from_node.inputs["Diffuse Color"].links[0].from_node.inputs["Vector"].links[0].from_node.uv_map ]
            except: UV1 = self.workObj.data.uv_layers[0]

        for triangle in inTriangleList:
            # We need to check if there is a zero area triangle face
            # ( A Face where two vertices share the same point in 3D space )
            # Zero Aera Fces will cause PASM to crash
            if self.isZeroAreaFace(triangle):
                continue
            
            for loopIndex, vertexIndex in zip(triangle.loops, triangle.vertices):
                entryVertex = file_def_ape.PASMVert() # Assemble a PASMVert for this vertex

                # Y-Up for PASM where Blender is Z-Up
                entryVertex.Pos[0] = copy.copy ( self.workObj.data.vertices[vertexIndex].co[0] )
                entryVertex.Pos[1] = copy.copy ( self.workObj.data.vertices[vertexIndex].co[2] )
                entryVertex.Pos[2] = copy.copy ( self.workObj.data.vertices[vertexIndex].co[1] )

                entryVertex.Norm[0] =  copy.copy ( self.workObj.data.loops[loopIndex].normal[0] )
                entryVertex.Norm[1] =  copy.copy ( self.workObj.data.loops[loopIndex].normal[2] )
                entryVertex.Norm[2] =  copy.copy ( self.workObj.data.loops[loopIndex].normal[1] )

                # Assign UV data if we were able to grab it
                if UV0 != None: entryVertex.aUVs[0] = copy.copy ( UV0.data[loopIndex].uv )
                if UV1 != None: entryVertex.aUVs[1] = copy.copy ( UV1.data[loopIndex].uv )

                # Vertex Color
                if self.ColorChannel:
                    entryVertex.Color[0] = copy.copy ( pasm_math.color_scene_linear_to_srgb(float(self.ColorChannel.data[vertexIndex].color[0]) ) )
                    entryVertex.Color[1] = copy.copy ( pasm_math.color_scene_linear_to_srgb(float(self.ColorChannel.data[vertexIndex].color[1]) ) )
                    entryVertex.Color[2] = copy.copy ( pasm_math.color_scene_linear_to_srgb(float(self.ColorChannel.data[vertexIndex].color[2]) ) )

                # Vertex Alpha
                if self.AlphaChannel:
                    entryVertex.Color[3] = copy.copy ( pasm_math.color_scene_linear_to_srgb(float(self.AlphaChannel.data[vertexIndex].color[0]) ) )

                # Vertex Weights
                # In FANG, the 3 vertices that form a triangle can only have a max of 4 vertex weights total
                # meaning 1 of the 3 vertices will have 2 vertex weights instead of 1.
                # SAS's Max Exporter contextually understands how to assign 1 vertex of a triangle 2 vertex weights instead of 1.
                # This Blender implimentation could support that, but for brevity's sake we use only the largest weight group per vertex and assign it max influence (1.0f)
                # https://blender.stackexchange.com/questions/14250/how-to-restrict-vertex-weights-to-no-more-than-n-number-of-bones
                if self.inArmature and self.bExportHierarchy:

                    pWeight = file_def_ape.PASMWeight()

                    if(self.bExportBinarySkinning): # Skinned mesh where a weight is either 1 or 0
                        for vgroup in self.workObj.data.vertices[vertexIndex].groups:
                            if vgroup.weight > 0.0:
                                pWeight.fBoneIndex = self.inArmature.pose.bones.find(self.workObj.vertex_groups[vgroup.group].name) + 1
                                pWeight.fWeight = 1
                                entryVertex.aWeights[0] = pWeight
                                entryVertex.fNumWeights = 1
                                continue

                    # Skinned mesh where a weight can have more than 1 weight
                    else: 
                        # TODO: Add support for triangle with 4 weights
                        # Currently we only use 1 weight per vertex assigning the largest
                        # weight the maximum influence when one vertex from the group can use 2
                        for vgroup in self.workObj.data.vertices[vertexIndex].groups:
                            if vgroup.weight > pWeight.fWeight:
                                pWeight.fWeight = vgroup.weight
                                pWeight.fBoneIndex = self.inArmature.pose.bones.find(self.workObj.vertex_groups[vgroup.group].name) + 1
                        
                        pWeight.fWeight = 1
                        entryVertex.aWeights[0] = pWeight
                        entryVertex.fNumWeights = 1

                # We need to check if we've seen this PASMVert yet
                # use a hashmap / dict for super fast lookups ( hashmap is O(n), list is O(n^2) )
                indexBuf = file_def_ape.PASMVertIndex()
                if entryVertex in vertexMap: # We've seem this PASMVert already
                    indexBuf.nVertIndex = vertexMap[entryVertex] # Find the PASMVert in the hashmap
                else: # We have not seen this PASMVert yet
                    vertexMap[entryVertex] = len(outSegment.aVertices)  # Add the hash of the PASMVert to the hashmap / dict
                    indexBuf.nVertIndex    = len(outSegment.aVertices)  # This is now the newest triangle index, therefore it is the largest
                    outSegment.aVertices.append(entryVertex)            # Add the PASMVert to the vertex buffer
                outSegment.aIndicies.append(indexBuf) # Finally, add the PASMVertIndex to the index buffer list

    # Process and create a layer of a FANG Material
    def ParseLayer(self, matName, fangMatGroup):
        # Construct a layer containing all information to create a surface
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
        layerStrParser.m_ApeCommands = copy.copy ( self.objStrParser.m_ApeCommands )
        layerStrParser.Parse(matName.lower())
        layer.StarCommands = layerStrParser.m_ApeCommands

        try:
            layer.szTexName[file_def_ape.PASMLayerIndex_e.APE_LAYER_TEXTURE_DIFFUSE] = fangMatGroup.inputs["Diffuse Color"].links[0].from_node.image.name.split(".",1)[0]
        except:
            g_class.printWARNING(f"Error extracing Diffuse Color Texture for material {matName} defaulting to '{DEFAULT_ERROR_TEXTURE}'")
            layer.szTexName[file_def_ape.PASMLayerIndex_e.APE_LAYER_TEXTURE_DIFFUSE] = DEFAULT_ERROR_TEXTURE

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

        layer.bTwoSided = int(fangMatGroup.inputs["Two Sided"].default_value)
        if layer.bTwoSided > 1: layer.bTwoSided = 1
        if layer.bTwoSided < 0: layer.bTwoSided = 0

        return layer

    # Process a material for a given segment
    def ParseMaterial(self, matIndex):
        mat = file_def_ape.PASMMaterial()  # Construct our material
        mat.StarCommands.nShaderNum = -1    # Set shader # to -1 to signal we need to set a default
        mat.nLODIndex = self.nLodIdx
        

        # STAR COMMANDS PT 2
        # We then use the object star commands as a base for all the materials
        matStrParser = CMaterialStringParser()
        matStrParser.ResetToDefaults()
        matStrParser.m_ApeCommands = copy.deepcopy ( self.objStrParser.m_ApeCommands )
        matStrParser.Parse( self.inObj.data.materials[matIndex].name.lower() ) # Then we parse the material name for star commands & material flags

        mat.StarCommands = matStrParser.m_ApeCommands
        mat.nFlags       = matStrParser.m_nMatFlags
        mat.nAffectAngle = matStrParser.m_nAffectAngle
        mat.StarCommands.TintRGB = copy.deepcopy ( matStrParser.m_TintRGB ) # Tint applied at the material level, NOT the layer level

        layer  = file_def_ape.PASMLayer()
        layer1 = file_def_ape.PASMLayer()

        # Get the material output
        for node in self.inObj.data.materials[matIndex].node_tree.nodes:
            if node.type == "OUTPUT_MATERIAL" and node.is_active_output:
                matOut = node
                continue

        try:
            fangMatGroup = matOut.inputs["Surface"].links[0].from_node # Get the Node connected to it
        except:
            g_class.logError(f"MATERIAL ERROR: The Material Output Node for material {self.inObj.data.materials[matIndex].name.lower()} in object {self.inObj.name} is not connected to a FANG Material / FANG Composite Node Tree. Please fix and retry exporting.")
            return False

        if fangMatGroup.type != "GROUP":
            g_class.logError(f"MATERIAL ERROR: The Material Output Node for material {self.inObj.data.materials[matIndex].name.lower()} in object {self.inObj.name} is not connected to a FANG Material / FANG Composite Node Tree. Please fix and retry exporting.")
            return False

        self.matNodeGroup = fangMatGroup

        if (fangMatGroup.node_tree.name.split(".",1)[0] == "FANG Material"):
            #print("We got a FANG Material!")

            layer = self.ParseLayer(self.inObj.data.materials[matIndex].name.lower(), fangMatGroup)
            mat.aMatLayers[0] = copy.deepcopy( layer ) # Link base layer with our material
            mat.nLayerCount += 1

        elif (fangMatGroup.node_tree.name.split(".",1)[0] == "FANG Composite"):
            #print("We got a FANG Composite!")

            layer = self.ParseLayer(fangMatGroup.inputs["Base"].links[0].from_node.name.lower(), fangMatGroup.inputs["Base"].links[0].from_node)
            mat.aMatLayers[0] = copy.deepcopy( layer ) # Link base layer with our material
            mat.nLayerCount += 1

            layer1 = self.ParseLayer(fangMatGroup.inputs["Layer 1"].links[0].from_node.name.lower(), fangMatGroup.inputs["Layer 1"].links[0].from_node)
            mat.aMatLayers[1] = copy.deepcopy( layer1 ) # Link layer 1 with our material
            mat.nLayerCount += 1
        else:
            raise ValueError("NOT A FANG MATERIAL!!!")
            g_class.logError("MATERIAL ERROR: Unable to parse FANG Material / FANG Composite Node Tree. This is a programmer error.")
            return False
        
        # Tint color is based on the first layer and applied at the material level
        if(mat.aMatLayers[0].StarCommands.nFlags & 0x02 == 0x02):
            mat.StarCommands.TintRGB[0] = pasm_math.color_scene_linear_to_srgb(fangMatGroup.inputs["Tint Color"].default_value[0])
            mat.StarCommands.TintRGB[1] = pasm_math.color_scene_linear_to_srgb(fangMatGroup.inputs["Tint Color"].default_value[1])
            mat.StarCommands.TintRGB[2] = pasm_math.color_scene_linear_to_srgb(fangMatGroup.inputs["Tint Color"].default_value[2])

        # Setup a default shader if not supplied
        if mat.StarCommands.nShaderNum < 0:
            if mat.nLayerCount == 1: mat.StarCommands.nShaderNum = 0
            else:                    mat.StarCommands.nShaderNum = 11

        if GC_DEBUG:
            if mat.StarCommands.nShaderNum == 11:
                if mat.aMatLayers[0].szTexName[file_def_ape.PASMLayerIndex_e.APE_LAYER_TEXTURE_DETAIL] != "":
                    g_class.printWARNING("GAMECUBE MATERIAL WARNING: Shader 11 is broken. Layer 1 will incorrectly " +
                                        "render only the detail map found in the base layer.\n" +
                                        "FIX: Disconnect the detail map from your base layer FANG Material in the FANG Composite material " + self.workObj.data.materials[matIndex].name)
    
        return mat

    def createSegment(self, inBufferName):
        # Test to see if this segment already exists
        for segment in g_class.gApeSegments:
            if inBufferName == segment.szMeshName:
                return segment
            
        # Otherwise this is a new segment we are adding
        outSegment = file_def_ape.PASMSegment()

        # If this segment is binary skinned the name will be the bone / vertex group
        # otherwise it will default to the name of the mesh
        outSegment.szMeshName = inBufferName

        if self.bExportHierarchy:
            outSegment.bSkinned = True

        return outSegment

    # Return True when successfully added geometry data to a new PASMSegment
    def ProcessSegment(self, inBufferName, inTriBuffer):
        outSegment = self.createSegment(inBufferName)

        # Itterate through the materials once to cache polygons into per material lists for access
        # rather than full itteration through polygons, everytime for each material
        # https://stackoverflow.com/a/8713681
        faceDict = [[] for _ in self.workObj.material_slots]

        vertexMap  = {} # Sorting map / dictonary for faster duplicate lookups

        # Create a new dictionary of polygons seperated by material
        for face in inTriBuffer:
            faceDict[face.material_index].append(face)

        # Itterate through our material polygons
        for matIndex in range(len(self.workObj.data.materials)):
            if not faceDict[matIndex]: continue # If material is unused, bail early

            mat = self.ParseMaterial(matIndex)

            if not isinstance(mat, file_def_ape.PASMMaterial):
                print("Encountered an error")
                return False

            mat.nFirstIndex = len(outSegment.aIndicies)

            self.ParseMesh(faceDict[matIndex], outSegment, vertexMap)

            mat.nNumIndices = len(outSegment.aIndicies) - mat.nFirstIndex

            outSegment.aMaterials.append(copy.deepcopy(mat))
            outSegment.nNumMaterials += 1

        # OK, every polygon accounted for, now update outSegment data
        outSegment.nNumVerts   = len(outSegment.aVertices)
        outSegment.nNumIndices = len(outSegment.aIndicies)

        if outSegment.nNumVerts == 0:
            g_class.logError(f"[GEO ERROR]: The object {self.inObj.name} was processed with no vertices! Are there empty material slots? Skipping object")
            return False

        return outSegment # We will write out this segment later

    def Process(self):
        # We start by creating a duplicate of the existing input geometry
        self.createWorkObject()

        self.getWorkNameAndLODIndex()
        self.getArmatureObject()
        self.getObjectStarCommands()
        
        # Then we transform the data based on our set flags
        self.prepareWorkObject()

        self.getColorAttributes()

        if self.bExportBinarySkinning:
            if not self.areVertexGroupWeightsBinary():
                g_class.printWARNING(f"[GEO ERROR]: Vertex Groups are not binary for {self.inObj.name}!")
                return False

        # After we seperate our polygons out by bones and export flags.
        # Each bowl represents a segment, segments created based on the following...
        # Unskinned mesh                   = 1 segment
        # Skinned mesh w/o Binary Skinning = 1 segment
        # Skinned mesh w/ Binary Skinning  = N segments
        self.getTrianglesByBone()

        # Finally we create a segment for each bowl of polygon soup
        for name in self.workLimbPolygons.keys():
            outSegment = self.ProcessSegment(name, self.workLimbPolygons[name])

            # Check to see if this exported without error
            if outSegment != False:

                # We need to check if this is a LOD segment first
                for idx, segment in enumerate(g_class.gApeSegments):
                    if segment.szMeshName == outSegment.szMeshName:
                        g_class.gApeSegments[idx] = outSegment
                        #print(f"Updated segment at idx {idx}")
                        break

                # Otherwise it's a new segment we are adding
                else:
                    g_class.gApeSegments.append(outSegment)

            else:
                g_class.printWARNING(f"[GEO ERROR]: Could not process {name}")

# Run checks to ensure this input should be processed into a segment
def validateInput(inObj):
    if inObj == None:                      return False # HOW could this even happen? Sanity check it anyway
    if inObj.type != "MESH":               return False # Validate we're working with mesh data and not other stuff
    
    if inObj.name[:4].lower() == "off_":   return False # Anything off_ isn't exported
    if inObj.name[:5].lower() == "cell_":  return False # Cells are special meshes not exported as segments
    if inObj.name[:4].lower() == "obj_":   return False # objs could be ANY DATATYPE but we only export them as objects
    if inObj.name[:6].lower() == "start_": return False # Ignore start_ meshes (i.e. objects using a Glitch mesh instead of an empty)
    
    if(len(inObj.data.materials) == 0):
        g_class.printWARNING(f"[GEO ERROR]: The object {inObj.name} has no materials, skipping")
        return False # Don't work with meshes that have no material

    # TODO: Update to check for loops and not explicitly loop triangles  
    if(len(inObj.data.loop_triangles) == 0):
        g_class.printWARNING(f"[GEO ERROR]: The object {inObj.name} has no triangles, skipping")
        return False # Don't work with meshes that have no triangles
        
    if(len(inObj.data.vertices) == 0):
        g_class.printWARNING(f"[GEO ERROR]: The object {inObj.name} has no vertices, skipping")
        return False # Don't work with meshes that have no vertices
        
    return True

# This is the main function that converts a blender mesh to the .ape tool mesh format
def ExportObjGeo(inObj, bExportHierarchy, bExportBinarySkinning):
    if not validateInput(inObj): return
    
    print(inObj.name, "is a geo object")
    
    segConvInst = CSegmentConverter()

    segConvInst.inObj = inObj
    segConvInst.bExportBinarySkinning = bExportBinarySkinning
    segConvInst.bExportHierarchy = bExportHierarchy

    segConvInst.Process()

    segConvInst.deleteWorkObject()

    return True
