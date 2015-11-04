import bpy
import bpy_types
import asyncio
import time
import os

from asyncio import Future

#def destroy_operator(cls):
#    bpy.utils.unregister_class(cls)

class BlenderFuture(Future):
    futures = {}
    future_counter = 0
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = self.__class__.future_counter
        self.__class__.future_counter += 1
        self.__class__.futures[self.id] = self
    def __del__(self):
        del self__class__.futures[self.id]
        super().__del__()

class TemporaryDialogOperatorClass(bpy.types.Operator):
    """ An operator to turn a file dialog into an asyncio task. """
    bl_label = ""
    bl_idname = 'asyncio.temp_file_dialog'
    filepath = bpy.props.StringProperty(subtype="FILE_NAME")
    future_id = bpy.props.IntProperty()

    def execute(self, context):
        self.future.set_result(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def __del__(self):
        if not self.future.cancelled() and not self.future.done():
            self.future.set_result(None)

bpy.utils.register_class(TemporaryDialogOperatorClass)
@asyncio.coroutine
def open_file_dialog():
    bl_idname = "asyncio.file_dialog"
    future = BlenderFuture()

    TemporaryDialogOperatorClass.future = future
    bpy.ops.asyncio.temp_file_dialog("INVOKE_DEFAULT")
    yield from future
    return future.result()



properties = []
class AsyncDialog(object, metaclass=bpy_types.OrderedMeta):
    """ Base Class for Dialog specifications. It's necessary
        to make sure the user's dialog class has ordered
        properties, without actually being an operator. """
    pass


class TestDialog(AsyncDialog):
    my_float = bpy.props.FloatProperty(name="Some Floating Point")
    my_bool = bpy.props.BoolProperty(name="Toggle Option")
    my_string = bpy.props.StringProperty(name="String Value")


@asyncio.coroutine
def open_dialog(dialog_class):
    class DialogOperator(bpy.types.Operator, TestDialog):
        bl_idname = "object.dialog_operator"
        bl_label = "Simple Dialog Operator"

        def execute(self, context):
            result = {}
            for key, value in self.rna_type.properties.items():
                result[key] = getattr(self, key)
            self.future.set_result(result)
            return {'FINISHED'}

        def invoke(self, context, event):
            wm = context.window_manager
            return wm.invoke_props_dialog(self)

        def __del__(self):
            if not self.future.cancelled() and not self.future.done():
                self.future.set_result(None)


    future = asyncio.Future()
    DialogOperator.future = future
    bpy.utils.register_class(DialogOperator)
    bpy.ops.object.dialog_operator('INVOKE_DEFAULT')
    result = yield from future
    return result
