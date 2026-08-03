# Module for writting errors that occured during export to a .txt file

# BUILT IN
import datetime
import os
# FANG TOOLKIT
from .g_class import g_SrcDir
# BLENDER
import bpy

class ErrorLogger:

    def __init__(self):

        self.file_log_path = g_SrcDir / "blender_ma_error_log.txt"

        self.file_log         = None
        self.show_error_log   = False
        self.invalid_geometry = {}

    def __enter__(self):

        self.file_log = open(self.file_log_path, "a", encoding="utf-8")

        return self

    def __exit__(self, exc_type, exc_value, traceback):

        self.flush_invalid_geometry_logs()

        if self.file_log:
            self.file_log.close()
            self.file_log = None

        # Open the log if errors occurred
        if self.show_error_log:
            os.startfile(self.file_log_path)

        # Return False so exceptions propagate normally
        return False
    
    def add_invalid_geometry(self, reason: str, object_name: str):

        if reason not in self.invalid_geometry:
            self.invalid_geometry[reason] = {}

        if object_name not in self.invalid_geometry[reason]:
            self.invalid_geometry[reason][object_name] = 0

        self.invalid_geometry[reason][object_name] += 1

    def flush_invalid_geometry_logs(self):

        if not self.invalid_geometry:
            return

        lines = []

        lines.append("INVALID GEOMETRY: The following meshes had some invalid polygons that were skipped.")
        lines.append("COMMON FIX: Select the affected mesh > Edit Mode > Select All vertices > Mesh > Clean Up > Merge by Distance.")
        lines.append("")

        for reason, objects in self.invalid_geometry.items():

            lines.append(f"Reason: {reason}")
            lines.append("")

            for object_name, count in sorted(objects.items()):

                face_word = "face" if count == 1 else "faces"

                lines.append(f"    Object '{object_name}' had {count} {face_word} skipped.")

            lines.append("")

        self.log_error("\n".join(lines))

        self.invalid_geometry = {}

    def log_error(self, message: str):

        self.show_error_log = True

        self.file_log.write("\n")
        self.file_log.write("BLENDER FANG FILE EXPORTER " + bpy.data.filepath + "\n")
        self.file_log.write("Occurred - " + datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y") + "\n")
        self.file_log.write(message + "\n")
        self.file_log.flush()