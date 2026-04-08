# Module for adding context on the add-on to the export panel.

# BLENDER
import bpy
# FANG TOOLKIT
from ..process.g_class import g_AddonInfo

# Footer info we write in the description of every exporter dialog
def writeFooterInfo(layout: bpy.types.UILayout) -> None:
    fileRevision = layout.row()
    fileRevision.label(text = "PASM File Version # 1.5.0")
              
    toolRevision = layout.row()
    strToolRevision = f"MA Toolkit Version # {g_AddonInfo['version']}"
    toolRevision.label(text = strToolRevision)