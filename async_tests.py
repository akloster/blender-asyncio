import bpy
import asyncio
from asyncio import coroutine, sleep, Task, wait_for
import sys
import os
sys.path.append(os.path.dirname(__file__))
external_path = os.path.join(os.path.dirname(__file__), "external")

libs = ["aiohttp", "jinja2", "markupsafe", "pyzmq"]
for name in libs:
    sys.path.append(os.path.join(external_path, name))

import aiohttp
import asyncio_bridge
import feedparser
from asyncio_bridge import BlenderListener


def prompt(text):
    bpy.data.objects['prompt'].data.body = text

def title(text):
    bpy.data.objects['title'].data.body = text


@coroutine
def test_1():
    feed_title_text = bpy.data.objects['feed_title']
    feed_text = bpy.data.objects['feed_text']
    feed_title_text.hide = True
    feed_text.hide = True

    listener =  BlenderListener(event_type="SPACE", catch=True)
    title("AsyncIO Demonstration")
    prompt("Note: Blender stays responsive all the time!\nPress 'Space' to continue...")
    yield from listener.wait()
    bpy.ops.screen.animation_play()

    title("Basic Timeouts")
    prompt("Press 'Space' to continue...")
    for i in reversed(range(10)):
        prompt("Count down {0}...".format(i))
        yield from sleep(1)

    listener.remove()

    yield from http_request_demo()
    #yield from http_server_demo()


@coroutine
def http_request_demo():
    listener =  BlenderListener(event_type="SPACE", catch=True)
    title("HTTP Requests")
    prompt("Retrieving blendernation's newsfeed ...")
    request_coro = aiohttp.request('get', 'http://feeds.feedburner.com/Blendernation')
    try:
        request = yield from wait_for(request_coro,  3)
    except asyncio.TimeoutError:
        prompt("Sorry, server couldn't be reached.")
        yield from sleep(3)
        return

    feed_title_text = bpy.data.objects['feed_title']
    feed_text = bpy.data.objects['feed_text']
    feed_title_text.hide = False
    feed_text.hide = False

    prompt("Reading Feed...")
    text = yield from wait_for(request.text(), 10)
    feed = feedparser.parse(text)
    feed_title_text.data.body = feed['feed']['title']
    feed_content = ""
    for entry in feed['entries'][:10]:
        feed_content += entry['title'] + "\n"
    feed_text.data.body = feed_content
    prompt("Press Space to continue...")
    yield from listener.wait()
    listener.remove()

    feed_title_text.hide = True
    feed_text.hide = True


@coroutine
def http_server_demo():
    print("Server Demo")
    import aiohttp
    from aiohttp import web

    prompt_text = "Server started at http://127.0.0.1:9090\nUser input:"
    user_input = "Put some text here!"

    @coroutine
    def handle(request):
        user_input = request.GET.get("user_input","")
        prompt(prompt_text+"\n"+user_input)
        html = """<html><title>Blender Async Demo</title><body>
        <h2>User input:</h2>
        <form method="GET">
        <textarea name="user_input">{0}</textarea>
        <br>
        <button type="submit">Submit</button>
        </form>
        </body></html>""".format(user_input)
        return web.Response(body=html.encode('utf-8'))


    @coroutine
    def start(loop):
        app = web.Application(loop=loop)
        app.router.add_route('GET', '/', handle)

        srv = yield from loop.create_server(app.make_handler(),
                                            '127.0.0.1', 9090)
        prompt(prompt_text +  "\n" + user_input)
        return srv
    yield from init(asyncio.get_event_loop())

if __name__ == "__main__":
    asyncio_bridge.register()
    bpy.ops.bpy.start_asyncio_bridge()
    #Task(test_1())

