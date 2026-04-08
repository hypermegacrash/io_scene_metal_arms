# Entry point for the Blender add-on.
# Blender calls register() on enable and unregister() on disable.

# FANG TOOLKIT
from .src import export
from .src import properties
from .src import operators
from .src import process

# Ordered list of modules that manage their own registration
modules = (
    export,
    properties,
    operators,
    process,
)

def register():
    for module in modules:
        module.register()

def unregister():
    # Reverse order ensures dependent systems are torn down safely
    for module in reversed(modules):
        module.unregister()