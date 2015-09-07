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
from .site import WebOn


class BlenderResource(object):
    """ Base class for Resources. Resources do not necessarily need to be
        related to blender data objects!
    """
    def make_reference(self,instance):
        url = "/API/%s/%s/%s" % (API_VERSION, self.resource_name, instance.name)
        return dict(name=instance.name, url=url)

    def __init__(self):
        pass

    @coroutine
    def handle(self):
        return "[{}]"

class TextResource(BlenderResource):
    """ Represents a Text data object. """
    resource_name = "text"
    def serialize(self, name):
        obj = bpy.data.texts[name]
        d = dict(name=obj.name,
                 content= obj.as_string()
                 )
        return d

    def put(self, name, data):
        obj = bpy.data.texts[name]
        obj.name = data.get('name', name)
        obj.from_string(data.get('content', ""))
        return {}
    def items(self):
        for name, instance in bpy.data.texts.items():
            yield self.make_reference(instance)

class BlenderEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bpy.types.Text):
            return {'name': obj.name}
        return json.JSONEncoder.default(self, obj)


class RESTWebOn(WebOn):
    def __init__(self, app):
        super().__init__(app)
        self.rest_handler = RESTHandler()
        self.app.router.add_route("GET", "/rest/{api:v\d+}/{resource}", self.rest_handler)
        self.app.router.add_route("GET", "/rest/{api:v\d+}/{resource}/{name:.*}",
                self.rest_handler)
        self.app.router.add_route("PUT", "/rest/{api:v\d+}/{resource}/{name:.*}",
                self.rest_handler.put)


class RESTHandler(object):
    def __init__(self):
        self.resources = dict()

    def __call__(self, request):
        if "name" in request.match_info:
            name = request.match_info
            return self.handle_resource(request, name)
        else:
            return self.handle_list(request)

    def get_resource_class(self, resource):
        return self.resourceſ[resource]

    @coroutine
    def put(self, request):
        resource = request.match_info["resource"]
        name = request.match_info["name"]
        data = yield from request.post()
        rclass = self.get_resource_class(resource)
        res = rclass.put(name, data)
        json_data = json.dumps(res, cls=BlenderEncoder)
        return web.Response(text=json_data)


    def handle_resource(self, request, name):
        resource = request.match_info.get("resource")
        name = request.match_info.get("name")
        data = {}
        if resource in self.resources:
            res = self.resources[resource].serialize(name)
            data = json.dumps(res, cls=BlenderEncoder)
        return web.Response(text=data)


    def handle_list(self, request):
        version = request.match_info.get("api")
        resource = request.match_info.get("resource")
        if resource in self.resources:
            r_list = list(self.resources[resource].items())
            data = json.dumps(r_list, cls=BlenderEncoder)
            return web.Response(text=data)

        return web.Response(text=data)


    def register_resource(self, cls):
        self.resources[cls.resource_name] = cls()


    def register_resources(self, cls_set):
        for cls in cls_set:
            self.register_resource(cls)

