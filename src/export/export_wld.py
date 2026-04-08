# Module for exporting a .wld file and adding UI to execute

# BUILT IN
import os
# BLENDER
import bpy
from bpy_extras.io_utils import ExportHelper
# FANG TOOLKIT
from ..defs       import file_def_ape
from ..process    import g_class
from .help_vis    import CollectionVisibilityManager
from .help_footer import writeFooterInfo
from ..process.process_object_geo     import ExportObjGeo
from ..process.process_object_light   import ExportObjLight
from ..process.process_object_object  import ExportObjObject
from ..process.process_object_shape   import ExportObjShape
from ..process.process_object_volume  import ExportObjVolume
from ..process.process_object_portal  import ExportObjPortal

class ExportWLD(bpy.types.Operator, ExportHelper):
    """Export scene to a Pasm compatible .wld file"""
    bl_idname    = 'export_scene.wld'
    bl_label     = 'Export WLD'
    filename_ext = '.wld'
    
    # UI Variables
    m_bUseSelection:  bpy.props.BoolProperty( name="Selection Only",       description="Export selected objects only",       default=False )
    m_bExportLights:  bpy.props.BoolProperty( name="Export Light Data",    description="Export all lights from the scene",   default=True  ) 
    m_bExportGeo:     bpy.props.BoolProperty( name="Export Geometry Data", description="Export all geometry from the scene", default=True  )
    m_bExportObjects: bpy.props.BoolProperty( name="Export Object Data",   description="Export all objects from the scene",  default=True  )

    # Draw the export properties which are then stored in self to be accessed later
    def draw(self, context):
        layout = self.layout
        
        boxHeader = layout.box()
        boxHeader.label(text="Wld File Exporter")
    
        layout.prop(self, "m_bUseSelection")
        
        boxSettings = layout.box()
        
        boxSettings.prop(self, "m_bExportLights")
        boxSettings.prop(self, "m_bExportGeo")
        boxSettings.prop(self, "m_bExportObjects")
        
        writeFooterInfo(layout)
                
    # The Blender Python API's equivalent of C/C++ main()
    def execute(self, context):
        # Init and dress a fresh header
        g_class.g_ApeHeader = file_def_ape.PASMHeader() 

        filename = os.path.basename(self.filepath)
        filename = filename[:len(filename)-4]
        g_class.g_ApeHeader.sceneName = filename

        g_class.g_ApeHeader.bWld = 1

        # Init our out file and error log in the global g_class for other modules to access
        with open(self.filepath, 'wb')     as g_class.g_FileOut, \
                open(g_class.g_FileLogPath, 'a') as g_class.g_FileLog, \
                CollectionVisibilityManager():

            g_class.g_FileOut.write(g_class.g_ApeHeader.pack()) # This will be overwritten at the very end with the correct data
            g_class.g_ShowErrorLog = False # Init our error log file

            if self.m_bUseSelection:
                objects = set(context.selected_objects)
            else:
                objects = set(context.scene.objects)

            # Remove off_ objects
            objects = {obj for obj in objects if not obj.name.lower().startswith("off_")}

            # Get our collections
            off_collections  = []
            cell_collections = []

            for coll in bpy.data.collections:
                lname = coll.name.lower()
                if lname.startswith("off_"):
                    off_collections.append(coll)
                elif lname.startswith("cell_"):
                    cell_collections.append(coll)

            # Remove objects in off_ collections    
            for coll in off_collections:
                objects.difference_update(coll.all_objects)

            # Remove non obj_ children OF obj_ objects
            for obj in tuple(objects):
                if obj.name.lower().startswith("obj_"): # obj_ roots are allowed
                    for child in obj.children_recursive:
                        if not child.name.lower().startswith("obj_"): # obj_ children are allowed
                            objects.discard(child)

            # Organize cell_ collections into volumes   
            VolumeColls = []

            for coll in cell_collections:
                volume = list(coll.all_objects)
                VolumeColls.append(volume)
                objects.difference_update(volume)

            # Final list of objects we are working with
            objects = list(objects)

            # Start up a small progress bar that the user can look at to know things are happening.
            # UI still locks up during export if the user clicks on the window which we just have to deal with.
            wm = context.window_manager
            wm.progress_begin(0, len(objects))

            # To mimic the original exporter as closely as possible
            # We itterate over the entire scene for each section of the PASM file
            # One loop for lights, one for geo, one for cells, and so on

            if(self.m_bExportLights):
                for idx, obj in enumerate(objects):
                    ExportObjLight(obj)
                    wm.progress_update(idx)

            if(self.m_bExportObjects):
                for idx, obj in enumerate(objects):
                    ExportObjObject(obj)
                    wm.progress_update(idx)

            for idx, obj in enumerate(objects):
                ExportObjShape(obj)
                wm.progress_update(idx)

            for idx, obj in enumerate(objects):
                ExportObjVolume(obj)
                wm.progress_update(idx)
            for idx, Volume in enumerate(VolumeColls):
                ExportObjVolume(Volume)
                wm.progress_update(idx)

            for idx, obj in enumerate(objects):
                ExportObjPortal(obj)
                wm.progress_update(idx)

            if(self.m_bExportGeo):        

                # Ensure we have no left over segments
                g_class.g_ApeSegments.clear()

                for idx, obj in enumerate(objects):
                    ExportObjGeo(obj, False, False)
                    wm.progress_update(idx)

                for segment in g_class.g_ApeSegments:
                    data = segment.pack()
                    g_class.g_FileOut.write(data)
                    g_class.g_ApeHeader.fileSize += len(data)
                    g_class.g_ApeHeader.nNumSegments += 1

                # Clean up the data once its done
                g_class.g_ApeSegments.clear()

            # Go back to the start and rewrite the header with correct data
            g_class.g_FileOut.seek(0)
            g_class.g_FileOut.write(g_class.g_ApeHeader.pack())

        # Done exporting, kill the progress cursor
        wm.progress_end()

        # Did we encounter any errors?
        if(g_class.g_ShowErrorLog): os.startfile(g_class.g_FileLogPath)

        self.report({'INFO'}, "WLD Export Finished!")

        return {'FINISHED'}
                
def exportWLD_MenuFunc(self, context):
    self.layout.operator(
        ExportWLD.bl_idname, text="Metal Arms Pasm Wld (.wld)")