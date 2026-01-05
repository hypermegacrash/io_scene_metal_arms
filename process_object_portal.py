# Module that processes an object object and returns byte data

# FANG TOOLKIT
from . import file_def_ape  # Get our PASM file classes
from . import g_class       # Get our global variables for the header data
from . import pasm_math     # PASM helper defs
from .process_star_command import CPortalStringParser # Import just thePortal Star Command Parser
# BLENDER
from math import sqrt       # Compute some quick maths

def ExportObjPortal(obj):
    if obj.name[:4].lower() == "off_":  return # Doesn't matter it's off bail early
    # First check if this is a portal object
    if obj.name[:5].lower() != "port_": return
    if obj.type             != "CURVE": return
        
    # print(obj.name, "is a portal object") # Looks good so far
    
    # Round 2
    if len(obj.data.splines) == 1:
        spline = obj.data.splines[0]
    else:
        g_class.logError("PORTAL ERROR: The spline object " + obj.name + " should only have 1 spline, found " + len(obj.data.splines))
        return
    
    if not spline.use_cyclic_u:
        g_class.logError("PORTAL ERROR: The spline object " + obj.name + " is not set to closed")
        return
    
    if spline.type != "POLY":
        g_class.logError("PORTAL ERROR: The spline object " + obj.name + " is using an unsuported spline type " + spline.type)
        return
    
    if len(spline.points) != 4:
        g_class.logError("PORTAL ERROR: The spline object " + obj.name + " does not have 4 points, found " + len(spline.points) )
        return
    
    outPortal = file_def_ape.PASMVisPortal()
    outPortal.szName = obj.name
    
    # Parse layer / child material name for star commands
    portalStrParser = CPortalStringParser()
    portalStrParser.ResetToDefaults()
    portalStrParser.Parse(obj.name.lower())
    outPortal.nFlags = portalStrParser.m_ApePortalFlag
     
    VisVerts = []
    for point in spline.points:
        tempVisVert = file_def_ape.PASMVisPoint()
           
        vertPosAfterWTM = obj.matrix_world @ point.co
        tempVisVert.Pos[0] = vertPosAfterWTM[0]
        tempVisVert.Pos[1] = vertPosAfterWTM[2]
        tempVisVert.Pos[2] = vertPosAfterWTM[1]
        
        VisVerts.append(tempVisVert)
        
    for x in range(len(VisVerts)):
        outPortal.ACorners[x] = VisVerts[x]
        
    # Kinda messy as heck but roll with it for now
    V0t = obj.matrix_world @ spline.points[0].co
    V0t.resize(3)
    V1t = obj.matrix_world @ spline.points[1].co
    V1t.resize(3)
    V2t = obj.matrix_world @ spline.points[2].co
    V2t.resize(3)
    V3t = obj.matrix_world @ spline.points[3].co
    V3t.resize(3)
     
    V1 = V2t - V1t
    V2 = V0t - V1t
    Normal = V1.cross( V2 )
    Normal *= (1.0 / sqrt( Normal[0] * Normal[0] + Normal[1] * Normal[1] + Normal[2] * Normal[2] ) )
    
    # Only checked this on the x-axis... does this owrk on y and z axis?
    outPortal.Normal[0] = Normal[0] * -1 # This is inverted because otherwise portal normal is inverted???
    outPortal.Normal[1] = Normal[2]
    outPortal.Normal[2] = Normal[1]
    
    # Surprise! Another check
    V1 = V0t - V3t
    V2 = V2t - V3t
    Cross = V1.cross( V2 )
    Cross = Cross.normalized()
    fDot = Cross.dot(Normal)
    if(fDot < 0.99):
        print("Not coplanar")
        
    centroid = V0t + V1t + V2t + V3t
    centroid *= (1.0 / 4.0)
    
    outPortal.Centroid[0] = centroid[0]
    outPortal.Centroid[1] = centroid[2]
    outPortal.Centroid[2] = centroid[1]
                        
    # Finally, write data to the file, and our header
    g_class.file.write(outPortal.packBytes())
    g_class.gApeHeader.fileSize += len(outPortal.packBytes())
    g_class.gApeHeader.nNumVisPortals += 1