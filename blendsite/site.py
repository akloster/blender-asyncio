""" BlendSite framework.

    This is a minimalistic web framework designed to be run inside Blender
    using the AsyncIO library.

    It is not meant to be run over the internet, as there are no security
    features implemented. There are two main usecases for this framework:

    1. As additional User Interface, accessed with a browser from a local computer.
    2. To interact with blender and the data inside a .blend file from a process
       which is not a blender application instance (like a real web application).


    Planned Features:

    * Serve static assets from python packages (implemented)
    * Serve dynamic pages, with templating (implemented)
    * Basic REST API
    * Websocket communication

    A lot of the design and implementation details would be very unwise in a
    framework meant for publicly accessed websites. For example, there is no
    security built-in, the REST framework isn't as extensible and flexible as
    django-rest, and the URL routing is quite hard-coded. But all these
    compromises are meant to better integrate with Blender and its addon
    ecosystem.

    Quite a few limitations are also due to not enough time spent on the code.
    Especially the REST Framework could use some more polishing and error
    handling.

    Blender is usually distributed with its own Python distribution, lacking
    support for package management and compilation of C extensions, so
    care has to be taken with dependencies.

"""
import asyncio
import aiohttp
from asyncio import coroutine, Task, sleep
from aiohttp import web
import sys
import os
from jinja2 import Environment, FileSystemLoader
from aiohttp import web
import bpy
import json

extension_to_mime = {'css': 'text/css', 'js': 'text/javascript'}

API_VERSION = "v1"

@coroutine
def blendsite_basic_middleware(app, handler):
    @coroutine
    def middleware(request):
        request.blend_filepath = bpy.data.filepath
        request.blender_version_string = bpy.app.version_string
        return (yield from handler(request))
    return middleware


class BlendSite(web.Application):
    """ A BlendSite represents an http server listening on a particular
        host/port. Ideally, only one such server should run inside a particular
        blender application instance, but multiple servers are supported.

        A BlendSite can have multiple WebOns, which provide extra functionality
        much like blender's Addon System. The "BasicWebOn" contains an index
        page, bootstrap static files, and a basic REST API.

        Other Webons could offer a Scripting IDE, REPLs, Text managers, etc.

        The BasicWebon is where most Webons should register themselves. It is
        meant for both API and web browser clients. But you may create your
        own BlendSite class, if, for example, you just want the REST API and
        some custom handlers to interact with external programs.
    """
    port = 9090
    def __init__(self):
        loop = asyncio.get_event_loop()
        super().__init__(loop=loop, middlewares=[blendsite_basic_middleware])

    @coroutine
    def start(self):
        loop = asyncio.get_event_loop()
        srv = yield from loop.create_server(self.make_handler(), "127.0.0.1",
                                            self.port)
        print("Serving BlendSite at http://127.0.0.1:%s" % self.port)

class WebOn(object):
    """ A WebOn adds url handlers to a BlendSite. These will usually be
        dynamic html pages and static assets.

        The notion of a WebOn is similar to an Add On or plugin. The idea is
        to mix several plugins into a common server, so you can access them
        from the same site. This way it is also possible to only start the
        WebOns you actually need for a particular situation, for example the
        REST API without all the web interface stuff, to interact with other
        processes.

        WebOns can interfere with each other. Therefore it is important to make
        your urls unique. Also currently there is no url routing "reversal"
        implemented, so references in html, js or css files should be designed
        carefully.

    """
    root_redirect = "/basic/"
    def __init__(self, app):
        self.app = app
        self.app.router.add_route('GET', '/', self.root_redirect_handler)
        template_path = os.path.join(os.path.dirname(__file__), "templates")

        self.template_paths = [template_path]


    def serve_static(self, name, path):
        handler = StaticHandler(path)
        self.app.router.add_route('GET', '/static/' + name + "/{path:.*}", handler)

    def root_redirect_handler(self, request):
        return aiohttp.web.HTTPFound(self.root_redirect)

    def render_to_string(self, template_name, context={}):
        env = Environment(loader=FileSystemLoader(self.template_paths))
        template = env.get_template(template_name)
        return template.render(**context)

    def render_to_response(self, template_name, context={}, request=None):
        context['request'] = request
        data = self.render_to_string(template_name, context)
        response = web.Response(body=data.encode("utf-8"),
                                content_type="text/html")
        return response


class BasicWebOn(WebOn):
    def __init__(self, app):
        super().__init__(app)
        path = os.path.dirname(__file__)+ "/static"
        self.serve_static("basic", path)
        self.app.router.add_route("GET", "/basic/", self.index)

    @coroutine
    def index(self, request):
        context = dict()
        return self.render_to_response("basic/index.html", context=context,
                                       request=request)

class StaticHandler(object):
    def __init__(self, root):
        self.root = root

    def __call__(self, request):
        path = request.match_info["path"]
        file_path = os.path.join(self.root, path)
        file_name, extension = os.path.splitext(file_path)
        mime_type = extension_to_mime.get(extension[1:], "text/plain")
        data = open(file_path).read()
        return web.Response(text=data, content_type=mime_type)

