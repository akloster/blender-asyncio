import bpy
import asyncio
import heapq
import socket
import subprocess
import time
import os
import sys

from bpy.app.handlers import persistent
from asyncio import Future
from functools import partial

handler_names = ["frame_change_post", 
            "frame_change_pre",
            "game_post",
            "game_pre",
            "load_post",
            "render_cancel",
            "render_complete",
            "render_init",
            "render_post",
            "render_pre",
            "render_stats",
            "render_write",
            "save_post",
            "save_pre",
            "scene_update_post",
            "scene_update_pre",
            "version_update",
           ]

class AppHandler(object):
    def __init__(self, name):
        self.name = name
        self.futures = []
    def fire(self, *args):
        for fut in self.futures:
            fut.set_result(args)
        self.futures = []

    def wait(self):
        fut = Future()
        self.futures.append(fut)
        return fut

handlers = dict()


@persistent
def fire_handler(name, *args, **kwargs):
    handlers[name].fire(*args)


def install_handlers():
    global handlers
    for name in handler_names:
        handlers[name] = AppHandler(name)
        _handler = getattr(bpy.app.handlers, name)
        _handler.append(partial(fire_handler, name))


def app_handler(name):
    if not name in handler_names:
        raise Exception("'%s' is not a valid handler in bpy.app.handlers." % name)
    return handlers[name].wait()

    


