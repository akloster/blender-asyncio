import bpy
from dependency_utils import add_external_libs
add_external_libs("external", ["aiohttp", "jinja2", "markupsafe", "chardet"])

import asyncio
from asyncio import Task
import aiohttp
from blender_async import get_event_loop
from blendsite import BlendSite, BasicWebOn, RESTWebOn, TextResource


loop = get_event_loop()
app = BlendSite()
basic_web_on = BasicWebOn(app)
rest_web_on = RESTWebOn(app)
rest_web_on.rest_handler.register_resources([TextResource])

loop.create_task(app.start())

