#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#
import asyncio
import zmq
from zmq.asyncio import Context
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
    #  Socket to talk to server
    print("Connecting to hello world server…")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    #  Do 10 requests, waiting each time for a response
    req = REQ()
    for request in range(10):
        print("Sending request %s …" % request)
        await socket.send(b"read")

        #  Get the reply.
        message = await socket.recv()
        struct_contents_set(req, message)
        print("Received %s [ %s ]" % (request, struct_contents(req)))
    socket.close()


asyncio.run(main())
