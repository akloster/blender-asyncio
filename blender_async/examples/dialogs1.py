import bpy
import asyncio
from asyncio import Task, coroutine, sleep
import sys
import os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "..","..") )
external_path = os.path.join(os.path.dirname(__file__), "external")

libs = ["aiohttp", "jinja2", "markupsafe", "chardet"]
for name in libs:
        sys.path.append(os.path.join(external_path, name))

import blender_async
#from asyncio_bridge import BlenderListener

class TestDialog(blender_async.dialogs.AsyncDialog):
    my_float = bpy.props.FloatProperty(name="Some Floating Point")
    my_bool = bpy.props.BoolProperty(name="Toggle Option")
    my_string = bpy.props.StringProperty(name="String Value")

@coroutine
def example():
    yield from sleep(1)

    file_name = yield from blender_async.open_file_dialog()
    print(file_name)
    yield from sleep(1)

    results = yield from blender_async.open_dialog(TestDialog)
    print(results)
    yield from sleep(1)

blender_async.ensure_running()

Task(example())
#asyncio.get_event_loop().create_task(app.start())
