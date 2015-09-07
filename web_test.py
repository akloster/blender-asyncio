import bpy
import asyncio
from asyncio import Task
import sys
import os
sys.path.append(os.path.dirname(__file__))
external_path = os.path.join(os.path.dirname(__file__), "external")

libs = ["aiohttp", "jinja2", "markupsafe", "chardet"]
for name in libs:
    sys.path.append(os.path.join(external_path, name))

import aiohttp
import asyncio_bridge
from asyncio_bridge import BlenderListener
from blendsite import BlendSite, BasicWebOn, RESTWebOn, TextResource


asyncio_bridge.ensure_running()
app = BlendSite()
basic_web_on = BasicWebOn(app)
rest_web_on = RESTWebOn(app)
rest_web_on.rest_handler.register_resources([TextResource])

asyncio.get_event_loop().create_task(app.start())
