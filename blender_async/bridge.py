import bpy
import asyncio
import heapq
import socket
import subprocess
import time
import os
import sys

def _run_once(self):
    """Run one full iteration of the event loop.

    This calls all currently ready callbacks, polls for I/O,
    schedules the resulting callbacks, and finally schedules
    'call_later' callbacks.

    This is copied verbatim from the standard library code, with
    only one little change, namely the default timeout value.
    """
    # Remove delayed calls that were cancelled from head of queue.
    while self._scheduled and self._scheduled[0]._cancelled:
        heapq.heappop(self._scheduled)

    # Set default timeout for call to "select" API. In the original
    # standard library code this timeout is 0, meaning select with block
    # until anything happens. Can't have that with foreign event loops!
    timeout = 1.0/30
    if self._ready:
        timeout = 0
    elif self._scheduled:
        # Compute the desired timeout.
        when = self._scheduled[0]._when
        deadline = max(0, when - self.time())
        if timeout is None:
            timeout = deadline
        else:
            timeout = min(timeout, deadline)
    event_list = self._selector.select(timeout)
    self._process_events(event_list)

    # Handle 'later' callbacks that are ready.
    end_time = self.time() + self._clock_resolution
    while self._scheduled:
        handle = self._scheduled[0]
        if handle._when >= end_time:
            break
        handle = heapq.heappop(self._scheduled)
        self._ready.append(handle)

    # This is the only place where callbacks are actually *called*.
    # All other places just add them to ready.
    # Note: We run all currently scheduled callbacks, but not any
    # callbacks scheduled by callbacks run this time around --
    # they will be run the next time (after another I/O poll).
    # Use an idiom that is threadsafe without using locks.
    ntodo = len(self._ready)
    for i in range(ntodo):
        handle = self._ready.popleft()
        if not handle._cancelled:
            handle._run()
    handle = None  # Needed to break cycles when an exception


class AsyncioBridgeOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "bpy.start_asyncio_bridge"
    bl_label = "Start Asyncio Modal Operator"


    def __init__(self):
        print("Start.")
        super().__init__()
    def __del__(self):
        print("End.")
    def modal(self, context, event):
        if event.type == 'TIMER':
            _run_once(self.loop)
        else:
            for listener_id, listener in self.listeners.items():
                fire, catch = listener.check_event(event)
                if fire:
                    listener.flag.set()
                    # In the case of firing an event, it is important to
                    # quit the listener processing in this loop iteration.
                    # This assures that only one asyncio.Event flag is
                    # set per iteration.
                    if catch:
                        return {'RUNNING_MODAL'}
                    else:
                        return {'PASS_THROUGH'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        self.types = {}
        self.listeners = {}
        self.listener_id = 0
        self.loop = asyncio.get_event_loop()
        self.loop.operator = self
        wm = context.window_manager
        wm.modal_handler_add(self)
        self._timer = wm.event_timer_add(0.005, context.window)
        return {'RUNNING_MODAL'}
    def invoke(self, context, event):
        self.execute(context)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)




def register():
    try:
        bpy.utils.register_class(AsyncioBridgeOperator)
    except:
        pass

def ensure_running():
    register()
    loop = asyncio.get_event_loop()
    if not hasattr(loop, "operator") or loop.operator is None:
        print("Starting Asyncio")
        bpy.ops.bpy.start_asyncio_bridge("INVOKE_DEFAULT")

def unregister():
    bpy.utils.unregister_class(AsyncioBridgeOperator)
