import bpy
import asyncio
from asyncio import Task, coroutine, sleep
import blender_async
from blender_async import app_handler


async def main():
    await sleep(1)
    for i in range(3):
        print("Please change Frame")
        await app_handler("frame_change_post")



loop = blender_async.get_event_loop()
loop.create_task(main())
