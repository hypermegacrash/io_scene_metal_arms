# Module that processes a geo object and returns byte data

# BUILT IN
import copy
import re
from typing import Dict, List, Optional, Tuple, Union
# BLENDER
import bpy
import mathutils
# FANG TOOLKIT
from ..defs import file_def_ape
from ..defs.file_def_ape_mesh import PASMMaterialFlag_e
from ..star_commands.star_command_material import CMaterialStringParser
from . import g_class

FANG_MAT_VERSION  = 1
FANG_COMP_VERSION = 1

# Class for handling the conversion of a Blender Mesh to a PASM Segment
# Acts like a container for all the input with functions for processing
class CSegmentConverter:
    def __init__(self, inObj: bpy.types.Object = None, bExportBinarySkinning: bool = True, bExportHierarchy: bool = False) -> None:
        self.inObj      = inObj # Starting mesh we are operating for reference
        self.inArmature = None # If our input is rigged this is the armature we are dealing with

        self.eval_obj  = None
        self.eval_mesh = None
        
        self.workLimbPolygons = None 
        self.workName         = None

        self.bExportHierarchy      = bExportHierarchy
        self.bExportBinarySkinning = bExportBinarySkinning

        self.objStrParser   = None
        self.ColorAttribute = None
        self.AlphaAttribute = None
        self.matNodeGroup   = None
        
        self.nLodIdx = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Automatic cleanup
        if self.eval_obj:
            self.eval_obj.to_mesh_clear()
        self.eval_obj  = None
        self.eval_mesh = None

    def getWorkNameAndLODIndex(self) -> None:
        """Check for LOD*_ Prefix to determine potential segment name and LOD Index"""
        self.workName = self.inObj.name
        if self.workName[:3] == "LOD" and self.workName[4:5] == "_":
            self.workName = self.workName[5:]
            self.nLodIdx = int(self.inObj.name[3:4])

    def getArmatureObject(self) -> None:
        """Check to see if this geo is attached to an armature."""
        for modifier in self.inObj.modifiers:
            if modifier.type == "ARMATURE":
                self.inArmature = modifier.object
                return

    def getColorAttributes(self) -> None:
        """Retrieve color and alpha attributes for the mesh."""
        self.ColorAttribute = None
        self.AlphaAttribute = None

        for attr in self.eval_mesh.color_attributes:
            name_prefix = attr.name.lower().split('.', 1)[0]

            if name_prefix not in ("color", "alpha"):
                g_class.logError(f"COLOR ATTRIBUTE ERROR: Attribute '{attr.name}' must be prefixed with color. or alpha. in object {self.inObj.name}")
                continue

            if name_prefix == "color":
                if self.ColorAttribute:
                    g_class.logError(f"Only 1 Color Attribute can be exported. Found {self.ColorAttribute.name} and {attr.name}")
                else:
                    self.ColorAttribute = attr

            elif name_prefix == "alpha":
                if self.AlphaAttribute:
                    g_class.logError(f"Only 1 Alpha Attribute can be exported. Found {self.AlphaAttribute.name} and {attr.name}")
                else:
                    self.AlphaAttribute = attr

    def validateColorAttributes(self) -> bool:
        """Ensure the color attributes are in the correct format for us to process"""
        isValid = True
        if self.ColorAttribute:
            if self.ColorAttribute.data_type != 'FLOAT_COLOR':
                g_class.logError(f"COLOR ATTRIBUTE ERROR: The Color Attribute {self.ColorAttribute.name} for object {self.inObj.name} is not set to Data Type Color. Please fix and retry exporting.")
            
        if self.AlphaAttribute:
            if self.AlphaAttribute.data_type != 'FLOAT_COLOR':
                g_class.logError(f"COLOR ATTRIBUTE ERROR: The Color Attribute {self.AlphaAttribute.name} for object {self.inObj.name} is not set to Data Type Color. Please fix and retry exporting.")

        return isValid

    def getObjectStarCommands(self) -> None:
        """Get our input object star commands flags"""
        self.objStrParser = CMaterialStringParser()
        self.objStrParser.ResetToDefaults()
        self.objStrParser.Parse( self.inObj.name.lower() )

    def _get_dominant_bone(self, tri: bpy.types.MeshLoopTriangle, vertex_groups: bpy.types.VertexGroups, bone_names: set[str]):
        best_bone   = None
        best_weight = 0.0

        for vert_idx in tri.vertices:
            vertex = self.eval_mesh.vertices[vert_idx]

            for vg in vertex.groups:
                if vg.weight <= 0:
                    continue

                vg_name = vertex_groups[vg.group].name

                if vg_name.lower().startswith("off_"):
                    continue

                if vg_name not in bone_names:
                    continue

                if vg.weight > best_weight:
                    best_weight = vg.weight
                    best_bone   = vg_name

        return best_bone

    # Split mesh triangles into "segments" based on rigging and skinning:
    # - No armature -> single segment containing all triangles
    # - Armature + Binary skinning enabled -> one segment per bone
    # - Armature + Binary skinning disabled -> one segment per bone,
    #   triangles grouped by dominant bone
    # The resulting dictionary (`self.workLimbPolygons`) has:
    #   key   = segment name (bone name or mesh name)
    #   value = list of triangles belonging to that segment
    # Segment naming convention:
    # - Armature    -> Bone Names
    # - No Armature -> Mesh Name
    def getTrianglesByBone(self) -> None:
        self.workLimbPolygons = {}

        # Single segment for unrigged mesh
        if not (self.bExportHierarchy and self.bExportBinarySkinning and self.inArmature):
            self.workLimbPolygons[self.workName] = list(self.eval_mesh.loop_triangles)
            return
        
        # Precompute for performance
        bone_names    = {b.name for b in self.inArmature.data.bones}
        vertex_groups = self.eval_obj.vertex_groups

        # Maintain hierarchy order
        bone_order = [b.name for b in self.inArmature.data.bones]

        # Main loop
        for tri in self.eval_mesh.loop_triangles:
            assigned_bone = self._get_dominant_bone(tri, vertex_groups, bone_names)

            if not assigned_bone: # If no bone found, warn
                g_class.printWARNING( f"Face {tri.index} has no valid bone assignment, using fallback" )
                assigned_bone = self.workName  # fallback bucket

            self.workLimbPolygons.setdefault(assigned_bone, []).append(tri)

        # Sort by bone hierarchy
        self.workLimbPolygons = { bone: self.workLimbPolygons[bone] for bone in bone_order if bone in self.workLimbPolygons }
    
    def isZeroAreaFace(self, triangle: bpy.types.MeshLoopTriangle) -> bool:
        """Return True if triangle has zero or nearly zero area."""
        v0 = self.eval_mesh.vertices[triangle.vertices[0]].co
        v1 = self.eval_mesh.vertices[triangle.vertices[1]].co
        v2 = self.eval_mesh.vertices[triangle.vertices[2]].co

        # Compute the cross product of edges
        edge1 = v1 - v0
        edge2 = v2 - v0
        area = edge1.cross(edge2).length / 2

        if area < 1e-8:  # Small epsilon to catch thin triangles
            g_class.printWARNING(f"ATTENTION ARTIST: Triangle {triangle.index} has near-zero area!")
            return True
        return False
    
    def _get_uv_layers(self) -> Tuple[Optional[bpy.types.MeshUVLoopLayer], Optional[bpy.types.MeshUVLoopLayer]]:
        UV0 = UV1 = None

        if self.matNodeGroup.node_tree.name.startswith("FANG Material"):
            try:
                UV0 = self.eval_mesh.uv_layers[self.matNodeGroup.inputs["Diffuse Color"].links[0].from_node.inputs["Vector"].links[0].from_node.uv_map]
            except:
                if self.eval_mesh.uv_layers:
                    UV0 = self.eval_mesh.uv_layers[0]
    
        elif self.matNodeGroup.node_tree.name.startswith("FANG Composite"):
            try:
                UV0 = self.eval_mesh.uv_layers[self.matNodeGroup.inputs["Base"].links[0].from_node.inputs["Diffuse Color"].links[0].from_node.inputs["Vector"].links[0].from_node.uv_map]
            except:
                if self.eval_mesh.uv_layers:
                    UV0 = self.eval_mesh.uv_layers[0]
            try:
                UV1 = self.eval_mesh.uv_layers[self.matNodeGroup.inputs["Layer 1"].links[0].from_node.inputs["Diffuse Color"].links[0].from_node.inputs["Vector"].links[0].from_node.uv_map]
            except:
                if self.eval_mesh.uv_layers:
                    UV1 = self.eval_mesh.uv_layers[0]

        return UV0, UV1

    def _get_color(self, loop_idx: int, vert_idx: int) -> Tuple[float, float, float]:
        if not self.ColorAttribute:
            return (0.0, 0.0, 0.0)

        src = self.ColorAttribute.data

        if self.ColorAttribute.domain == 'POINT':
            color_linear = mathutils.Color(src[vert_idx].color[:3])
        else:
            color_linear = mathutils.Color(src[loop_idx].color[:3])

        return tuple(color_linear.from_scene_linear_to_srgb())

    def _get_alpha(self, loop_idx: int, vert_idx: int) -> float:
        if not self.AlphaAttribute:
            return 1.0

        src = self.AlphaAttribute.data
        idx = vert_idx if self.AlphaAttribute.domain == 'POINT' else loop_idx

        color_linear = mathutils.Color((src[idx].color[0],) * 3)
        return color_linear.from_scene_linear_to_srgb()[0]

    def _apply_weights(self, vtx: file_def_ape.PASMVert, vert_idx: int) -> None:
        if not (self.inArmature and self.bExportHierarchy):
            return

        pWeight = file_def_ape.PASMWeight()

        if self.bExportBinarySkinning:
            for vg in self.eval_mesh.vertices[vert_idx].groups:
                if vg.weight > 0:
                    bone_name = self.eval_obj.vertex_groups[vg.group].name
                    pWeight.fBoneIndex = self.inArmature.pose.bones.find(bone_name) + 1
                    pWeight.fWeight = 1
                    vtx.aWeights[0] = pWeight
                    vtx.fNumWeights = 1
                    return
        else:
            max_weight = 0
            best_group = None

            for vg in self.eval_mesh.vertices[vert_idx].groups:
                if vg.weight > max_weight:
                    max_weight = vg.weight
                    best_group = vg

            # For the time being we are hardcoding this to only 1 bone
            if best_group:
                bone_name = self.eval_obj.vertex_groups[best_group.group].name
                pWeight.fBoneIndex = self.inArmature.pose.bones.find(bone_name) + 1

                # Hardcoded to 1 bone only
                pWeight.fWeight = 1
                vtx.aWeights[0] = pWeight
                vtx.fNumWeights = 1

    def _build_vertex(self, loop_idx: int, vert_idx: int, UV0: Optional[bpy.types.MeshUVLoopLayer], UV1: Optional[bpy.types.MeshUVLoopLayer] ) -> file_def_ape.PASMVert:
        vtx = file_def_ape.PASMVert()

        # Position (Y-Up)
        co = self.eval_mesh.vertices[vert_idx].co
        vtx.Pos = (co[0], co[2], co[1])

        # Normal (Y-Up)
        normal = self.eval_mesh.loops[loop_idx].normal
        vtx.Norm = (normal[0], normal[2], normal[1])

        # UVs
        uv0 = tuple(UV0.data[loop_idx].uv) if UV0 else (0.0, 0.0)
        uv1 = tuple(UV1.data[loop_idx].uv) if UV1 else (0.0, 0.0)
        vtx.aUVs = (uv0, uv1, (0.0, 0.0), (0.0, 0.0))

        # Color + Alpha
        color = self._get_color(loop_idx, vert_idx)
        alpha = self._get_alpha(loop_idx, vert_idx)
        vtx.Color = (color[0], color[1], color[2], alpha)

        # Weights
        self._apply_weights(vtx, vert_idx)

        return vtx

    def ParseMesh(self, inTriangleList: List[bpy.types.MeshLoopTriangle], outSegment: file_def_ape.PASMSegment, vertexMap: Dict[file_def_ape.PASMVert, int] ) -> None:
        """Parse through the polygons for the material of a given segment"""
        UV0, UV1 = self._get_uv_layers()
    
        for triangle in inTriangleList:
            # We need to check if there is a zero area triangle face
            # ( A Face where two vertices share the same point in 3D space )
            # Zero Area Faces will cause PASM to crash
            if self.isZeroAreaFace(triangle):
                continue
            
            for loop_idx, vert_idx in zip(triangle.loops, triangle.vertices):
                vtx = self._build_vertex(loop_idx, vert_idx, UV0, UV1)
    
                # Vertex deduplication
                idx_buf = file_def_ape.PASMVertIndex()
    
                if vtx in vertexMap:
                    idx_buf.nVertIndex = vertexMap[vtx]
                else:
                    new_index = len(outSegment.aVertices)
                    vertexMap[vtx] = new_index
                    idx_buf.nVertIndex = new_index
                    outSegment.aVertices.append(vtx)
    
                outSegment.aIndicies.append(idx_buf)

    def ParseLayer(self, matName: str, fangMatGroup: bpy.types.NodeGroupInput) -> file_def_ape.PASMLayer:
        """Construct a layer of a FANG Material"""
        layer                      = file_def_ape.PASMLayer()
        layer.bTextured            = 1
        layer.fUnitAlphaMultiplier = 1.0

        # Parse layer / child material name for star commands
        layerStrParser = CMaterialStringParser()
        layerStrParser.ResetToDefaults()
        # Use Star Commands from the Parent Material as a starting base for the layer material
        layerStrParser.m_ApeCommands = copy.deepcopy( self.objStrParser.m_ApeCommands )
        layerStrParser.Parse( matName.lower() )
        layer.StarCommands = layerStrParser.m_ApeCommands

        texture_map = {
            file_def_ape.PASMLayerIndex_e.APE_LAYER_TEXTURE_DIFFUSE:       "Diffuse Color",
            file_def_ape.PASMLayerIndex_e.APE_LAYER_TEXTURE_ALPHA_MASK:    "Alpha Mask",
            file_def_ape.PASMLayerIndex_e.APE_LAYER_TEXTURE_EMISSIVE_MASK: "Emissive Mask",
            file_def_ape.PASMLayerIndex_e.APE_LAYER_TEXTURE_ENVIRONMENT:   "Environment Map",
            file_def_ape.PASMLayerIndex_e.APE_LAYER_TEXTURE_BUMP:          "Bump Map",
            file_def_ape.PASMLayerIndex_e.APE_LAYER_TEXTURE_DETAIL:        "Detail Map",
        }

        for slot, input_name in texture_map.items():
            try:
                linked_node = fangMatGroup.inputs[input_name].links[0].from_node
                if hasattr(linked_node, "image") and linked_node.image:
                    layer.szTexName[slot] = linked_node.image.name.split(".", 1)[0]
            except (KeyError, IndexError, AttributeError): # Input not connected or missing, skip
                pass

        # Called Illumination in 3ds max
        if(fangMatGroup.inputs["Emissive"].default_value != 0):
            layer.StarCommands.bUseEmissiveColor = 1
            layer.IllumRGB = ( fangMatGroup.inputs["Emissive"].default_value, fangMatGroup.inputs["Emissive"].default_value, fangMatGroup.inputs["Emissive"].default_value )

        layer.bTwoSided = int(fangMatGroup.inputs["Two-Sided"].default_value)

        return layer

    def _create_base_material(self, mat_name: str) -> file_def_ape.PASMMaterial:
        mat = file_def_ape.PASMMaterial()

        mat.StarCommands.nShaderNum = -1 # Set shader # to -1 to signal we need to set a default
        mat.nLODIndex = self.nLodIdx

        parser = CMaterialStringParser()
        parser.ResetToDefaults()
        parser.m_ApeCommands = copy.deepcopy(self.objStrParser.m_ApeCommands)
        parser.Parse(mat_name)

        mat.StarCommands = parser.m_ApeCommands
        mat.nFlags = parser.m_nMatFlags
        mat.nAffectAngle = parser.m_nAffectAngle
        mat.StarCommands.TintRGB = copy.deepcopy(parser.m_TintRGB)

        return mat

    def _get_material_output(self, material: bpy.types.Material) -> Optional[bpy.types.Node]:
        for node in material.node_tree.nodes:
            if node.type == "OUTPUT_MATERIAL" and node.is_active_output:
                return node
        return None
    
    def _get_fang_node(self, matOut: bpy.types.Node, mat_name: str) -> Optional[bpy.types.NodeGroupInput]:
        try:
            node = matOut.inputs["Surface"].links[0].from_node
        except (AttributeError, KeyError, IndexError):
            g_class.logError(
                f"MATERIAL ERROR: Material {mat_name} in object {self.inObj.name} "
                "is not connected to a FANG Material / FANG Composite."
            )
            return None

        if node.type != "GROUP":
            g_class.logError(
                f"MATERIAL ERROR: Material {mat_name} in object {self.inObj.name} "
                f"is connected to invalid node type {node.type}."
            )
            return None

        return node
    
    def _safe_node(self, node: bpy.types.NodeGroupInput, input_name: str) -> bpy.types.Node:
        try:
            return node.inputs[input_name].links[0].from_node
        except (KeyError, IndexError):
            raise ValueError(f"Missing node input: {input_name}")

    def _get_fang_version(self, fang_group):
        for node in fang_group.node_tree.nodes:
            if node.type == 'FRAME' and node.label:
                match = re.search(r"Version\s*(\d+)", node.label)
                if match:
                    return int(match.group(1))
        return 0

    def _validate_fang_version(self, fang_group: bpy.types.NodeGroupInput, matType: str, mat_name: str) -> bool:
        version = self._get_fang_version(fang_group)

        expected = None
        if matType == "FANG Material":
            expected = FANG_MAT_VERSION
        elif matType == "FANG Composite":
            expected = FANG_COMP_VERSION

        if expected is None:
            return True

        if version != expected:
            g_class.logError(
                f"MATERIAL ERROR: {matType} {mat_name} in object {self.inObj.name} "
                f"is out of date (found {version}, expected {expected})."
            )
            return False

        return True

    def _parse_fang_material(self, mat: file_def_ape.PASMMaterial, fang_group: bpy.types.NodeGroupInput, mat_name: str) -> None:
        layer = self.ParseLayer(mat_name, fang_group)

        mat.aMatLayers[0] = copy.deepcopy(layer)
        mat.nLayerCount = 1

    def _parse_fang_composite(self, mat: file_def_ape.PASMMaterial, fang_group: bpy.types.NodeGroupInput) -> None:
        base_node = self._safe_node(fang_group, "Base")
        layer0 = self.ParseLayer(base_node.name.lower(), base_node)

        layer1_node = self._safe_node(fang_group, "Layer 1")
        layer1 = self.ParseLayer(layer1_node.name.lower(), layer1_node)

        mat.aMatLayers[0] = copy.deepcopy(layer0)
        mat.aMatLayers[1] = copy.deepcopy(layer1)
        mat.nLayerCount = 2

    def _apply_tint(self, mat: file_def_ape.PASMMaterial, fang_group: bpy.types.NodeGroupInput, matType: str) -> None:
        if not (mat.aMatLayers[0].StarCommands.nFlags & PASMMaterialFlag_e.APE_MAT_FLAGS_APPLY_TINT):
            return

        if matType == "FANG Material":
            color = fang_group.inputs["Tint Color"].default_value

        elif matType == "FANG Composite":
            base_node = self._safe_node(fang_group, "Base")
            color = base_node.inputs["Tint Color"].default_value

        else:
            raise ValueError("Invalid material type for tint")

        linear = mathutils.Color(color[:3])
        mat.StarCommands.TintRGB[0:3] = linear.from_scene_linear_to_srgb()

    def _apply_default_shader(self, mat: file_def_ape.PASMMaterial) -> None:
        if mat.StarCommands.nShaderNum < 0:
            mat.StarCommands.nShaderNum = 0 if mat.nLayerCount == 1 else 11

    def ParseMaterial(self, matIndex: int) -> Optional[file_def_ape.PASMMaterial]:
        """Process a material for a given segment"""
        material = self.inObj.data.materials[matIndex]
        mat_name = material.name.lower()

        mat = self._create_base_material(mat_name)

        matOut = self._get_material_output(material)
        fang_group = self._get_fang_node(matOut, mat_name)

        if not fang_group:
            return False
        
        self.matNodeGroup = fang_group

        matType = fang_group.node_tree.name.split(".", 1)[0]

        #if not self._validate_fang_version(fang_group, matType, mat_name):
        #    return False

        if matType == "FANG Material":
            self._parse_fang_material(mat, fang_group, mat_name)
        elif matType == "FANG Composite":
            self._parse_fang_composite(mat, fang_group)
        else:
            raise ValueError("NOT A FANG MATERIAL")
        
        self._apply_tint(mat, fang_group, matType)
        self._apply_default_shader(mat)
    
        return mat

    def _getSegment(self, inBufferName: str) -> file_def_ape.PASMSegment:
        """Returns a segment to work on, either one that has already been started or a brand new one"""

        # Test to see if this segment already exists
        for segment in g_class.g_ApeSegments:
            if inBufferName == segment.header.szMeshName:
                return segment
            
        # Otherwise this is a new segment we are adding
        outSegment = file_def_ape.PASMSegment()

        # If this segment is binary skinned the name will be the bone / vertex group
        # otherwise it will default to the name of the mesh
        outSegment.header.szMeshName = inBufferName

        if self.bExportHierarchy:
            outSegment.header.bSkinned = True

        return outSegment

    def ProcessSegment(self, inBufferName: str, inTriBuffer: list[bpy.types.MeshLoopTriangle] ) -> Union[bool, file_def_ape.PASMSegment]:
        """Return True/False on failure or a PASMSegment when successfully added geometry data"""
        outSegment = self._getSegment(inBufferName)

        # Cache polygons by material index
        mat_count = len(self.eval_mesh.materials)
        faceDict = [[] for _ in range(mat_count)]

        for tri in inTriBuffer:
            faceDict[tri.material_index].append(tri)

        # Vertex mapping for deduplication
        vertexMap = {}  # key = (co, normal, uv, color), value = vertex index

        for matIndex in range(mat_count):
            tris = faceDict[matIndex]
            if not tris:
                continue  # Skip unused materials

            mat = self.ParseMaterial(matIndex)

            if not isinstance(mat, file_def_ape.PASMMaterial):
                g_class.logError(f"[MATERIAL ERROR] Failed to parse material {matIndex} on object {self.inObj.name}")
                return False

            mat.nFirstIndex = len(outSegment.aIndicies)

            # Process triangles for this material
            self.ParseMesh(tris, outSegment, vertexMap)

            if len(outSegment.aIndicies) - mat.nFirstIndex == 0:
                g_class.logError(f"[MATERIAL ERROR] Failed to construct valid polygons for material {matIndex} on object {self.inObj.name}")
                continue

            mat.nNumIndices = len(outSegment.aIndicies) - mat.nFirstIndex

            # OK, every polygon accounted for, now update outSegment data
            outSegment.aMaterials.append(mat)
            outSegment.header.nNumMaterials += 1
            outSegment.header.nNumVerts   = len(outSegment.aVertices)
            outSegment.header.nNumIndices = len(outSegment.aIndicies)

        if outSegment.header.nNumVerts == 0:
            g_class.logError(
                f"[GEO ERROR] Object '{self.inObj.name}' produced no vertices! "
                "Check for empty material slots."
            )
            return False

        return outSegment # We will write out this segment later

    def Process(self) -> None:
        """Main processing pipeline: evaluate mesh, handle transforms, split by bones, build segments"""
        
        # 1. Get segment name and LOD index
        self.getWorkNameAndLODIndex()
        self.getArmatureObject()
        self.getObjectStarCommands()

        # 2. Get evaluated mesh (modifiers applied, armature deformation applied)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        self.eval_obj = self.inObj.evaluated_get(depsgraph)
        self.eval_mesh = self.eval_obj.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)

        # 3. Apply world transform numerically (replaces transform_apply)
        self.eval_mesh.transform(self.eval_obj.matrix_world)
        
        # 4. Handle negative scaling: flip normals if determinant < 0
        if self.eval_obj.matrix_world.determinant() < 0.0:
            self.eval_mesh.flip_normals()

        # 5. FANG UV V-axis reflection
        reflectionPoint = 0.5
        for uv_layer in self.eval_mesh.uv_layers:
            for loop in uv_layer.data:
                loop.uv[1] = -(loop.uv[1] - reflectionPoint) + reflectionPoint

        # 6. Triangulate mesh
        self.eval_mesh.calc_loop_triangles()

        # 7. Get color/alpha attributes
        self.getColorAttributes()
        if not self.validateColorAttributes():
            self.eval_obj.to_mesh_clear()
            self.eval_mesh = None
            self.eval_obj  = None
            return

        # 8. Split triangles into segments
        self.getTrianglesByBone()

        # 9. Create a segment for each bowl of polygon soup
        for name, tri_list in self.workLimbPolygons.items():
            outSegment = self.ProcessSegment(name, tri_list)

            if outSegment:
                # We need to check if this is a LOD segment first
                for idx, segment in enumerate(g_class.g_ApeSegments):
                    if segment.header.szMeshName == outSegment.header.szMeshName:
                        g_class.g_ApeSegments[idx] = outSegment
                        break
                # Otherwise it's a new segment we are adding
                else:
                    g_class.g_ApeSegments.append(outSegment)
            else:
                g_class.printWARNING(f"[GEO ERROR]: Could not process {name}")

def validateInput(inObj: Optional[bpy.types.Object]) -> bool:
    """Run checks to ensure this input should be processed into a segment"""

    if inObj == None:                      return False # HOW could this even happen? Sanity check it anyway
    if inObj.type != "MESH":               return False # Validate we're working with mesh data and not other stuff
    
    if inObj.name[:4].lower() == "off_":   return False # Anything off_ isn't exported
    if inObj.name[:5].lower() == "cell_":  return False # Cells are special meshes not exported as segments
    if inObj.name[:4].lower() == "obj_":   return False # objs could be ANY DATATYPE but we only export them as objects
    if inObj.name[:6].lower() == "start_": return False # Ignore start_ meshes (i.e. objects using a Glitch mesh instead of an empty)
    
    if(len(inObj.data.materials) == 0):
        g_class.printWARNING(f"[GEO ERROR]: The object {inObj.name} has no materials, skipping")
        return False
 
    if(len(inObj.data.loop_triangles) == 0):
        g_class.printWARNING(f"[GEO ERROR]: The object {inObj.name} has no triangles, skipping")
        return False
        
    if(len(inObj.data.vertices) == 0):
        g_class.printWARNING(f"[GEO ERROR]: The object {inObj.name} has no vertices, skipping")
        return False
        
    return True

def ExportObjGeo(inObj: bpy.types.Object, bExportHierarchy: bool, bExportBinarySkinning: bool) -> bool:
    """Main function to convert a blender mesh to the .ape tool mesh format"""

    if not validateInput(inObj): return False
    
    with CSegmentConverter(inObj, bExportBinarySkinning, bExportHierarchy) as segConvInst:
        segConvInst.Process()

    return True