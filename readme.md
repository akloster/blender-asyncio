Asyncio for Blender Python API
=================================

This is an experimental project to explore the use of Asyncio in Blender. With asyncio it is possible to run clients and servers from inside a Blender instance.

- "BlendSite" is a fledgling framework to build aiohttp-based web-interfaces and REST API endpoints to interact with a running Blender instance
- A couple of examples explore how to use dialogs, events and handlers asynchronously

Nothing of this is currently meant to for inclusion into mainstream Blender.

Installation / Running
======================

To run the examples use this command:

    > PYTHONPATH=./ blender -P blender_async/examples/dialogs1.py


This project uses quite a few dependencies, so there is a dependency_utils module which makes them available to the PYTHONPATH. Something of an improvised package manager, if you will.
