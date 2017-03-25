import bpy

import asyncio
from asyncio import Task, coroutine, sleep
import blender_async
from blender_async import BlenderListener


async def example():
    listener =  BlenderListener(event_type="SPACE", catch=True)
    await listener.wait()
    print("Space key was pressed")

loop = blender_async.get_event_loop()
loop.create_task(example())
