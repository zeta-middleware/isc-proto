#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import asyncio
from zmq.asyncio import Context
import zmq
import ctypes
from ctypes import c_uint8, sizeof, cast, POINTER, c_char

context = Context.instance()


class FLAG_(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("read", c_uint8, 1),
        ("write", c_uint8, 1),
        ("erase", c_uint8, 1),
        ("update", c_uint8, 1),
    ]


class REQ(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [("id", c_uint8), ("flag", FLAG_), ("data", c_uint8 * 32)]


def struct_contents(struct):
    return cast(ctypes.byref(struct),
                POINTER(c_char * sizeof(struct))).contents.raw


def struct_contents_set(struct, raw_data):
    cast(ctypes.byref(struct),
         POINTER(c_char * sizeof(struct))).contents.raw = raw_data


async def main():
    socket = context.socket(zmq.REP)
    req = REQ(1, FLAG_(0, 1, 1, 0), (c_uint8 * 32)(*range(32)))
    print(f"{ctypes.sizeof(req)} bytes: {struct_contents(req)}")
    socket.bind("tcp://*:5555")

    while True:
        #  Wait for next request from client
        message = await socket.recv()
        print("Received request: %s" % message)

        #  Do some 'work'
        await asyncio.sleep(1)

        #  Send reply back to client
        await socket.send(struct_contents(req))
        req.id = req.id + 1


asyncio.run(main())
