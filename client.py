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


async def sub_handler():
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:5556")
    socket.setsockopt(zmq.SUBSCRIBE, b'\x0a')
    print("Subscriber handler running...")
    while (True):
        channel, data = await socket.recv_multipart()
        print("topic received")


async def read_write_handler():
    #  Socket to talk to server
    print("Connecting to hello world server…")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    #  Do 10 requests, waiting each time for a response
    req = REQ()
    for _ in range(10):
        await socket.send(b"\x01")

        #  Get the reply.
        message = await socket.recv()
        struct_contents_set(req, message[1:])
        print(f"Received {message[0]} [%s]\n" % (struct_contents(req)))
    socket.close()


async def main():
    await asyncio.gather(sub_handler(), read_write_handler())


asyncio.run(main())
