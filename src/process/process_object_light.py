# Module that processes a light object and returns byte data

# BLENDER
import mathutils
# FANG TOOLKIT
from ..defs import file_def_ape_light
from . import g_class
from . import pasm_math
from ..star_commands.star_command_light import CLightStringParser
from .process_gamedata import parse_gamedata_string

def ExportObjLight(obj):
    bExitEarly = False
    
    if obj.name[:4].lower() == "off_": return # Doesn't matter it's off bail early
    if obj.type             != "LIGHT":                           bExitEarly = True  # Not a light then we don't export
    if obj.name[:7].lower() == "ambient" and obj.type == "EMPTY": bExitEarly = False # Ambient lights are empty cube objects
    
    if(bExitEarly): return

    outLight = file_def_ape_light.PASMLight()
    
    if obj.type == "LIGHT":
        if   obj.data.type == "SUN":   outLight.nApeLightType = file_def_ape_light.PASMLightType_e.APE_LIGHT_TYPE_DIR
        elif obj.data.type == "POINT": outLight.nApeLightType = file_def_ape_light.PASMLightType_e.APE_LIGHT_TYPE_OMNI
        elif obj.data.type == "SPOT":  outLight.nApeLightType = file_def_ape_light.PASMLightType_e.APE_LIGHT_TYPE_SPOT
        
    if obj.name[:7].lower() == "ambient" and obj.type == "EMPTY": outLight.nApeLightType = file_def_ape_light.PASMLightType_e.APE_LIGHT_TYPE_AMBIENT
        
    if outLight.nApeLightType == -1:
        g_class.logError(f"LIGHT ERROR: Unable to assign nApeLightType for {obj.name}, skipping.")
        return
        
    outLight.szLightName = obj.name
    
    if obj.type == "LIGHT":
        light_color_linear = mathutils.Color(obj.data.color[:3])
        outLight.Color[0:3] = light_color_linear.from_scene_linear_to_srgb()
    elif obj.name[:7].lower() == "ambient" and obj.type == "EMPTY":
        # Pull the 'red' 'green' 'blue' gamedata fields for the ambient color

        if "ma" not in obj:
            g_class.logError(f"LIGHT ERROR: No gamedata for ambient entity {obj.name}, skipping.")
            return

        try:
            parsed = parse_gamedata_string(obj["ma"])
            parsed = {k.lower(): v for k, v in parsed.items()}
        except Exception as e:
            g_class.logError(f"LIGHT ERROR: Failed to parse gamedata on ambient entity {obj.name}, skipping. {e}")
            return
        
        if "red" not in parsed or "green" not in parsed or "blue" not in parsed:
            g_class.logError(f"LIGHT ERROR: Unable to find integer gamedata values red green blue for {obj.name}, skipping.")
            return
        
        try:
            nRed, nGreen, nBlue = (
                int(parsed["red"]),
                int(parsed["green"]),
                int(parsed["blue"]),
            )
        except (ValueError, TypeError):
            g_class.logError(f"LIGHT ERROR: Non-integer RGB gamedata on {obj.name}, skipping.")
            return
        
        # Floor it
        nRed   = max(0, min(nRed,   255))
        nGreen = max(0, min(nGreen, 255))
        nBlue  = max(0, min(nBlue,  255))
        # Convert to float
        nRed   = nRed   * float((1/255))
        nGreen = nGreen * float((1/255))
        nBlue  = nBlue  * float((1/255))    
        # Assign it
        outLight.Color[0] = nRed
        outLight.Color[1] = nGreen
        outLight.Color[2] = nBlue
    else:
        g_class.logError(f"LIGHT ERROR: Unable to assign Light color for {obj.name}, skipping.")
        return
        
    # Parse light name for star commands
    lightStrParser = CLightStringParser()

    lightStrParser.Parse(obj.name.lower())

    outLight.nFlags            = lightStrParser.m_ApeLightFlag
    outLight.fCoronaScale      = lightStrParser.m_fCoronaScale
    outLight.szCoronaTexture   = lightStrParser.m_szCoronaTexture
    outLight.szPerPixelTexture = lightStrParser.m_szPerPixelTexture
    outLight.nLightID          = lightStrParser.m_nLightID
  
    if obj.type == "LIGHT":
        outLight.Intensity = obj.data.ma_light_props.fIntensity
    elif obj.name[:7].lower() == "ambient" and obj.type == "EMPTY":
        outLight.Intensity = 1.0
    else:
        g_class.logError(f"LIGHT ERROR: Unable to assign Light intensity for {obj.name}, skipping.")
        return
      
    # Lights calculate their rotation matrix in a different way to everything else
    outLight.mtxOrientation = pasm_math.BObj2F43MtxLIGHT(obj)
    
    if outLight.nApeLightType == file_def_ape_light.PASMLightType_e.APE_LIGHT_TYPE_DIR or outLight.nApeLightType == file_def_ape_light.PASMLightType_e.APE_LIGHT_TYPE_SPOT:
        # This is the 3rd row of the rotation matrix
        outLight.Direction[0] = outLight.mtxOrientation[6]
        outLight.Direction[1] = outLight.mtxOrientation[7]
        outLight.Direction[2] = outLight.mtxOrientation[8]
    
    if outLight.nApeLightType == file_def_ape_light.PASMLightType_e.APE_LIGHT_TYPE_OMNI or outLight.nApeLightType == file_def_ape_light.PASMLightType_e.APE_LIGHT_TYPE_SPOT:
        outLight.Sphere[0] = obj.data.ma_light_props.fRadius
        outLight.Sphere[1] = outLight.mtxOrientation[9]
        outLight.Sphere[2] = outLight.mtxOrientation[10]
        outLight.Sphere[3] = outLight.mtxOrientation[11]
        
    if outLight.nApeLightType == file_def_ape_light.PASMLightType_e.APE_LIGHT_TYPE_SPOT:
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
    if (obj.parent_bone):
        hArmature = obj.parent.data
        outLight.szParentBoneName = hArmature.bones[obj.parent_bone].parent.name
    
    # Finally, write data to the file
    data = outLight.pack()
    g_class.g_FileOut.write(data)
    g_class.g_ApeHeader.fileSize += len(data)
    g_class.g_ApeHeader.nNumLights += 1