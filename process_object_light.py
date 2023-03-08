# Module that processes a light object and returns byte data

# FANG TOOLKIT
from . import pasm_file_def # Get our PASM file classes
from . import g_class       # Get our global variables for the header data
from . import pasm_math     # PASM helper defs
from .process_star_command import CLightStringParser # Import just the Light Star Command Parser
# BLENDER
import math # Needed for computing sqrt and pi for light
import colorsys # Light intensity

def ExportObjLight(obj):
    bExitEarly = False
    
    if obj.name[:4].lower() == "off_": return # Doesn't matter it's off bail early
    if obj.type             != "LIGHT":                           bExitEarly = True  # Not a light then we don't export
    if obj.name[:7].lower() == "ambient" and obj.type == "EMPTY": bExitEarly = False # Ambient lights are empty cube objects
    
    if(bExitEarly): return
        
    print(obj.name, "is a light object")

    outLight = pasm_file_def.PASMLight()
    
    if obj.type == "LIGHT":
        if   obj.data.type == "SUN":   outLight.nApeLightType = pasm_file_def.PASMLightType_e.APE_LIGHT_TYPE_DIR
        elif obj.data.type == "POINT": outLight.nApeLightType = pasm_file_def.PASMLightType_e.APE_LIGHT_TYPE_OMNI
        elif obj.data.type == "SPOT":  outLight.nApeLightType = pasm_file_def.PASMLightType_e.APE_LIGHT_TYPE_SPOT
        
    if obj.name[:7].lower() == "ambient" and obj.type == "EMPTY": outLight.nApeLightType = pasm_file_def.PASMLightType_e.APE_LIGHT_TYPE_AMBIENT
        
    if outLight.nApeLightType == -1:
        print("Unable to assign nApeLightType, skipping " + obj.name)
        return
        
    outLight.szLightName = obj.name
    
    if obj.type == "LIGHT":
        outLight.Color[0] = pasm_math.color_scene_linear_to_srgb(obj.data.color[0])
        outLight.Color[1] = pasm_math.color_scene_linear_to_srgb(obj.data.color[1])
        outLight.Color[2] = pasm_math.color_scene_linear_to_srgb(obj.data.color[2])
    elif obj.name[:7].lower() == "ambient" and obj.type == "EMPTY":
        try:
            # Grab the custom properties (we only need red green and blue but just grab them all)
            dictProperties = {}
            cmds = obj["ma"].split('\n')
            for index in cmds:   
                if index == "" or index.isspace(): continue # Check if string is empty
                if index[0] == "#":                continue # Check if comment line
                a = index.find("=")
                i = a - 1
                j = a + 1
                while index[i] == " ":
                    i = i - 1
                while index[j] == " ":
                    j = j + 1
                dictProperties[index[:i + 1]] = int(index[j:])
            nRed   = dictProperties["red"]
            nGreen = dictProperties["green"]
            nBlue  = dictProperties["blue"]
            # Floor it
            nRed   = max(0, min(nRed,   255))
            nGreen = max(0, min(nGreen, 255))
            nBlue  = max(0, min(nBlue,  255))
            # Convert to float
            nRed   = nRed   * float((1/255))
            nGreen = nGreen * float((1/255))
            nBlue  = nBlue  * float((1/255))
        except:
            print("Unable to find integer custom property values for red green blue, skipping " + obj.name)
            return       
        # Assign it
        outLight.Color[0] = nRed
        outLight.Color[1] = nGreen
        outLight.Color[2] = nBlue
    else:
        print("Unable to assign Light color, skipping " + obj.name)
        return
         
    if obj.type == "LIGHT":
         if outLight.nApeLightType == pasm_file_def.PASMLightType_e.APE_LIGHT_TYPE_DIR:
            outLight.Intensity = obj.data.energy
         else:
            # Pretty kludgely hack
            # If the light is small, you need to calculate intensity in a specific way,
            # This methodology only works for small lights, large lights don't work with this
            # For the time being compromise, this is better than before but still not ideal
            if(obj.data.energy < 1000):
                #light_threshold = bpy.context.scene.eevee.light_threshold
                # I guess we're doing this mathematically as well
                # https://www.youtube.com/watch?v=b9HgDScFoTo
                radius = math.sqrt(((( obj.data.energy / 0.01) *  obj.data.diffuse_factor) / ( 4 * math.pi )))     
                outLight.Intensity = (( obj.data.energy ) / ( radius * radius ))
            else:
                if outLight.nApeLightType == pasm_file_def.PASMLightType_e.APE_LIGHT_TYPE_SPOT:
                    radius = math.sqrt(((( obj.data.energy / 0.02) *  obj.data.diffuse_factor) / ( 4 * math.pi )))     
                    outLight.Intensity = (( obj.data.energy ) / ( radius * radius ))
                else:
                    tempHSV = colorsys.rgb_to_hsv(obj.data.color[0], obj.data.color[1], obj.data.color[2])
                    outLight.Intensity = tempHSV[2]
    elif obj.name[:7].lower() == "ambient" and obj.type == "EMPTY":
        outLight.Intensity = 1.0
    else:
        print("Unable to assign Light intensity, skipping " + obj.name)
        return
    
    # Parse light name for star commands
    lightStrParser = CLightStringParser()
    lightStrParser.Parse(obj.name.lower())
    outLight.nFlags = lightStrParser.m_ApeLightFlag
    outLight.fCoronaScale = lightStrParser.m_fCoronaScale
    outLight.szCoronaTexture = lightStrParser.m_szCoronaTexture
    outLight.szPerPixelTexture = lightStrParser.m_szPerPixelTexture
    outLight.nLightID = lightStrParser.m_nLightID
      
    # Lights calculate their rotation matrix in a different way to everything else
    outLight.mtxOrientation = pasm_math.BObj2F43MtxLIGHT(obj)
    
    if outLight.nApeLightType == pasm_file_def.PASMLightType_e.APE_LIGHT_TYPE_DIR or outLight.nApeLightType == pasm_file_def.PASMLightType_e.APE_LIGHT_TYPE_SPOT:
        # This is the 3rd row of the rotation matrix
        outLight.Direction[0] =  outLight.mtxOrientation[6]
        outLight.Direction[1] =  outLight.mtxOrientation[7]
        outLight.Direction[2] =  outLight.mtxOrientation[8]
    
    if outLight.nApeLightType == pasm_file_def.PASMLightType_e.APE_LIGHT_TYPE_OMNI or outLight.nApeLightType == pasm_file_def.PASMLightType_e.APE_LIGHT_TYPE_SPOT:
        # light_threshold = bpy.context.scene.eevee.light_threshold
        # Blender doesn't give a radius of light that we want
        # So we're gonna calculate inverse square law with a distance of 0.02 to try and approximate one
        # Thx The Science Asylum! https://www.youtube.com/watch?v=2FMx2GDqMo4
        radius2 = math.sqrt(((( obj.data.energy / 0.02) *  obj.data.diffuse_factor) / ( 4 * math.pi )))    
        outLight.Sphere[0] = radius2
        outLight.Sphere[1] = outLight.mtxOrientation[9]
        outLight.Sphere[2] = outLight.mtxOrientation[10]
        outLight.Sphere[3] = outLight.mtxOrientation[11]
        
    if outLight.nApeLightType == pasm_file_def.PASMLightType_e.APE_LIGHT_TYPE_SPOT:
        if obj.data.spot_blend == 1.0: # This is a super soft light
            outLight.fSpotInnerAngle = 0.0
        else: # Regular light
            outLight.fSpotInnerAngle = (1 - obj.data.spot_blend) * obj.data.spot_size

        # If fSpotInnerAngle > fSpotOuterAngle the light will become inverted
        if outLight.fSpotInnerAngle >= obj.data.spot_size:
            outLight.fSpotInnerAngle = obj.data.spot_size - 2
        if outLight.fSpotInnerAngle <= 0.5:
            outLight.fSpotInnerAngle = 0.5

        if obj.data.spot_size <= 1.0:
            outLight.fSpotOuterAngle = 1.0
        else:
            outLight.fSpotOuterAngle = obj.data.spot_size
        
    # Check to see if this light is attached to an armature
    if (obj.parent_bone): outLight.szParentBoneName = obj.parent_bone
    
    # Finally, write data to the file, and our header
    g_class.file.write(outLight.packBytes())
    g_class.gWldHeader.fileSize += len(outLight.packBytes())
    g_class.gWldHeader.nNumLights += 1
    



