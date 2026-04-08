"""
Collection Visibility Workaround Module
--------------------------------------

Background:
    In Blender 4.2, collections that are excluded or hidden in the
    active view layer do not have the world matrices of the objects
    contained winth initialized when a .blend file is first opened.

    A reproducible scenario occurs when a user opens a .blend file 
    containing hidden collections and immediately runs an export. 
    Objects within the hidden collections will have invalid
    world matrices, resulting in incorrect export data.

    When a collection is made visible and the dependency graph
    is updated the world matrices are correctly evaluated.

Solution:
    This module provides a context manager that will
    1. Un-excludes all collections in the active view layer
    2. Force a dependency graph update
    3. Restores the original visibility state when the context exits.

Usage:
    Wrap export code in the context manager:

        with CollectionVisibilityManager():
            export_data()

"""

# BUILT IN
from typing import Optional, Type, Any
# BLENDER
import bpy

def get_layer_collection(collection: bpy.types.Collection, view_layer: Optional[bpy.types.ViewLayer] = None) -> Optional[bpy.types.LayerCollection]:
    """Return the LayerCollection for a given Collection in a view layer, or None if not found."""
    view_layer = view_layer or bpy.context.view_layer

    def scan(lc: bpy.types.LayerCollection) -> Optional[bpy.types.LayerCollection]:
        if lc.collection == collection:
            return lc
        for child in lc.children:
            found = scan(child)
            if found:
                return found
        return None

    return scan(view_layer.layer_collection)

class CollectionVisibilityManager:
    """Context manager: temporarily unhide all hidden/excluded collections in a view layer."""

    def __init__(self, view_layer: Optional[bpy.types.ViewLayer] = None) -> None:
        self.view_layer          = view_layer or bpy.context.view_layer
        self._hidden_collections = []

    def __enter__(self):
        """Unhide hidden/excluded collections and store previous state."""
        self._hidden_collections.clear()

        for coll in bpy.data.collections:
            lc = get_layer_collection(coll, self.view_layer)
            if lc and (lc.exclude or lc.hide_viewport):

                # Save previous state
                self._hidden_collections.append((lc, lc.exclude, lc.hide_viewport))

                # Unhide temporarily
                lc.exclude       = False
                lc.hide_viewport = False

        # Force Blender to update evaluated data for hidden objects
        bpy.context.evaluated_depsgraph_get().update()

        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[Any]) -> None:
        """Restore original visibility/exclude states."""
        for lc, exclude, hide_viewport in self._hidden_collections:
            lc.exclude       = exclude
            lc.hide_viewport = hide_viewport