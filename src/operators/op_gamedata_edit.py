# Module to open an external text editor for writing Gamedata Parameters

# BUILT IN
import subprocess
from pathlib import Path
import sys
# BLENDER
import bpy
      
def get_default_editor():
    if sys.platform.startswith("win"):
        return ["notepad.exe"]

class MA_Gamedata_Edit(bpy.types.Operator):
    bl_idname      = "object.ma_ui_gamedata_external"
    bl_label       = "MA Gamedata"
    bl_description = "Editor for Metal Arms Entity Parameters"

    _process   = None
    _timer     = None
    _temp_file = None
    _obj       = None

    def invoke(self, context, event):
        self._obj = context.active_object
        if not self._obj:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}

        # Ensure the property exists
        if "ma" not in self._obj:
            self._obj["ma"] = ""

        # Create temporary file
        self._temp_file = Path(__file__).parent / "GD.txt"
        self._temp_file.write_text(self._obj["ma"], encoding="utf-8")

        # Launch editor
        editor_cmd = get_default_editor() + [str(self._temp_file)]
        self._process = subprocess.Popen(editor_cmd)

        # Start timer
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.5, window=context.window)
        wm.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'TIMER':
            # Check if editor closed
            if self._process.poll() is not None:
                self._obj["ma"] = self._temp_file.read_text(encoding="utf-8") # Read changes back into object
                self._temp_file.unlink(missing_ok=True)                       # Delete temp file
                context.window_manager.event_timer_remove(self._timer)        # Remove timer
                return {'FINISHED'}

        return {'PASS_THROUGH'}
    
def MA_Gamedata_Edit_MenuFunc(self, context):
    self.layout.separator()
    col = self.layout.column()
    self.layout.operator_context = 'INVOKE_DEFAULT'
    col.operator(MA_Gamedata_Edit.bl_idname, icon="TEXT")