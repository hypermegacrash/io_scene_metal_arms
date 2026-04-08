# Module that processes an object object and returns byte data

# FANG TOOLKIT
from ..defs import file_def_ape_volume
from . import g_class
from ..star_commands.star_command_portal import CPortalStringParser

def ExportObjPortal(obj):
    if obj.name[:4].lower() == "off_":  return # Doesn't matter it's off bail early
    # Check if this is a portal object
    if obj.name[:5].lower() != "port_": return
    if obj.type             != "CURVE": return
    
    # Spline speciifc checks
    if len(obj.data.splines) == 1:
        spline = obj.data.splines[0]
    else:
        g_class.logError(f"PORTAL ERROR: The spline object {obj.name} should only have 1 spline, found {len(obj.data.splines)}")
        return
    
    if not spline.use_cyclic_u:
        g_class.logError(f"PORTAL ERROR: The spline object {obj.name} is not set to closed")
        return
    
    if spline.type != "POLY":
        g_class.logError(f"PORTAL ERROR: The spline object {obj.name} is using an unsuported spline type {spline.type}")
        return
    
    if len(spline.points) != 4:
        g_class.logError(f"PORTAL ERROR: The spline object {obj.name} does not have 4 points, found {len(spline.points)}")
        return
    
    outPortal = file_def_ape_volume.PASMVisPortal()
    outPortal.szName = obj.name
    
    # Parse layer / child material name for star commands
    portalStrParser = CPortalStringParser()
    portalStrParser.ResetToDefaults()
    portalStrParser.Parse(obj.name.lower())
    outPortal.nFlags = portalStrParser.m_ApePortalFlag

    worldVerts = [(obj.matrix_world @ p.co).to_3d() for p in spline.points]
     
    VisVerts = []
    for v in worldVerts:
        tempVisVert = file_def_ape_volume.PASMVisPoint()
        tempVisVert.Pos[0] = v.x
        tempVisVert.Pos[1] = v.z
        tempVisVert.Pos[2] = v.y
        VisVerts.append(tempVisVert)
        
    for x in range(len(VisVerts)):
        outPortal.ACorners[x] = VisVerts[x]
        
    V0t, V1t, V2t, V3t = worldVerts

    # Normal calculation
    edge1 = V1t - V0t
    edge2 = V2t - V0t

    Normal = edge2.cross(edge1)

    if Normal.length != 0:
        Normal.normalize()
    else:
        g_class.logError(f"PORTAL ERROR: Degenerate portal (zero area): {obj.name}")
        return

    # Axis conversion (Z-up -> Y-up)
    outPortal.Normal[0] = Normal.x
    outPortal.Normal[1] = Normal.z
    outPortal.Normal[2] = Normal.y
    
    # Coplanarity check
    # cross2 = (V2t - V0t).cross(V3t - V0t)

    # if cross2.length != 0:
    #     cross2.normalize()
    #     if cross2.dot(Normal) < 0.99:
    #         g_class.logError(f"PORTAL ERROR: Not coplanar: {obj.name}")

    # Centroid  
    centroid = (V0t + V1t + V2t + V3t) * 0.25
    
    outPortal.Centroid[0] = centroid.x
    outPortal.Centroid[1] = centroid.z
    outPortal.Centroid[2] = centroid.y
                        
    # Finally, write data to the file
    g_class.g_FileOut.write(outPortal.pack())
    g_class.g_ApeHeader.fileSize += file_def_ape_volume.PASMVisPortal.EXPECTED_SIZE
    g_class.g_ApeHeader.nNumVisPortals += 1