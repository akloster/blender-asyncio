import bpy

import asyncio
from asyncio import Task, coroutine, sleep
import blender_async


class TestDialog(blender_async.dialogs.AsyncDialog):
    my_float = bpy.props.FloatProperty(name="Some Floating Point")
    my_bool = bpy.props.BoolProperty(name="Toggle Option")
    my_string = bpy.props.StringProperty(name="String Value")


async def example():
    await sleep(1)

    file_name = await blender_async.open_file_dialog()
    print(file_name)
    await sleep(1)

    results = await blender_async.open_dialog(TestDialog)
    print(results)
    await sleep(1)


loop = blender_async.get_event_loop()
loop.create_task(example())
