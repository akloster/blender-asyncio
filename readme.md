Asyncio Bridge for Blender Python API

Up to now, network programming in blender has been a nightmare and virtually
absent. Python threading did not work reliably inside blender, and so any
script running for extended periods of time would block the user interface. Any
code running outside the main process would not have full or reliable access to
the API.

The larger Python community solved this problem using asyncio. In fact, Guido
van Rossum himself designed a standard event loop library for concurrency and
asynchronous input/output. Codenamed Tulip, this library is already included
in the standard library and current distributions of Blender.

This project offers a modal operator to integrate the asyncio event loop inside
blender. It also converts UI operator events into something asyncio "threads"
can deal with more easily.

With asyncio compatibility, blender scripts instantly gain the following
functionality from libraries built on top of asyncio:

- HTTP client and server, including websockets, TLS encryption and REST
  interfaces
- ZMQ for distributed concurrency
- IRC clients
- AMQP messaging
- Non-blocking database IO, most notably Redis and Postgres

It may not be immediately obvious, why non-blocking network programming would
be so useful for blender, but here are a few ideas:

- Easier integration with render farms, for clients, brokers and renderers
- Uploading of pictures or videos directly to sharing sites
- Integration of blender rendering into web applications (product
  customization)
- Controlling a running blender instance through a web interface exposes the
  world of HTML5 on desktop and mobile to blender: Multitouch, Accelerometer,
  camera capture and gamepads. At the very least, a tablet could be used as
  a button panel.
- better integration with foreign processes, like ffmpeg or rendering engines
- communication with the blender cloud or the shop, for example managing and
  downloading small gimmicks like materials or fonts.
- content generation based on public APIs, like open street map or molecular
  structure databases (PDB), without external downloading
- communication with applications written with other UI toolkits
- integration of distributed pipeline and asset managers
- saner/easier multi-step workflow scripting
- An aiozmq based IPython Kernel would mean full compatibility between Blender
  and IPython notebook, supercharging scripting tutorials and developer
  documentation.

In general, asyncio provides concurrent multi-threading without multiple
threads and enables predictable context switching through pythonic syntax sugar.

Eventually, I believe a standard Asyncio loop should be included into the
blender addon library, to ensure that multiple addon scripts can depend on a
common API and not step on each others digital toes. A final implementation
should also provide a central webserver which different addons can provide url
handlers for, and a way to turn this webserver on/off from the UI.

Installation / Running
======================

Currently this code is not meant to be installed into blender's script
directory, but rather to be run as a demo from inside the main directory.

You will need to make the "aiohttp" package available to blender's Python
library. In many cases, "pip install aiohttp" and copying the aiohttp
directory from the corresponding site-packages directory into either the
directory of this project or into your blender installation's Python
site-packages directory will be enough.

To run the demonstration, you need to run a command like the following:

> blender async_tests.blend --python async_tests.py

Where "blender" is a recent blender binary.
