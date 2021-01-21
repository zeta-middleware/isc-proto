import asyncio
import serial_asyncio as serial
from bitstruct import unpack_from
from libscrc import crc8


class ZetaISCCommand:
    def __init__(self, *args):
        if len(args) != 5:
            raise ValueError("Arg must have 4 items given {}".format(
                len(args)))
        self.__type = args[1]
        self.__cmd = args[0]
        self.__channel = args[2]
        self.__crc = args[3]
        self.__size = args[4]
        self.__data = None

    def __repr__(self):
        representation = "ZetaISCCommand(\n" + \
             f"    type: {self.__type}\n" + \
             f"    cmd: {self.__cmd}\n" + \
             f"    channel {self.__channel}\n" + \
             f"    crc: {self.__crc}\n" + \
             f"    size: {self.__size}\n" + \
             f"    data: {self.__data}\n)"
        return representation

    def size(self):
        return self.__size

    def crc8(self):
        return self.__crc

    def set_data(self, data):
        self.__data = data

    def data(self):
        return self.__data


class ZetaDataHandle:
    STATE_DIGEST_HEADER = 0
    STATE_DIGEST_BODY = 1

    def __init__(self):
        self.__buffer = bytearray()
        self.__state = self.STATE_DIGEST_HEADER
        self.__current_pkt = None

    def append(self, data):
        self.__buffer.extend(data)
        self.digest()

    def digest(self):
        if self.__state == self.STATE_DIGEST_HEADER:
            if len(self.__buffer) >= 4:
                self.__current_pkt = ZetaISCCommand(
                    *unpack_from("u6u2u8u8u8", self.__buffer[:4], 0))
                self.__buffer = self.__buffer[4:]
                self.__state = self.STATE_DIGEST_BODY
        if self.__state == self.STATE_DIGEST_BODY:
            if len(self.__buffer) == self.__current_pkt.size():
                if crc8(self.__buffer) == self.__current_pkt.crc8():
                    self.__current_pkt.set_data(self.__buffer)
                    print("Pkt assembled: {}".format(self.__current_pkt))
                    self.__current_pkt = None
                    self.__state = self.STATE_DIGEST_HEADER
                else:
                    print("CRC error, pkt discarded")
                self.__buffer = self.__buffer[self.__current_pkt.size():]


zt_data_handler = ZetaDataHandle()


class SerialMonitor(asyncio.Protocol):
    def __init__(self):
        pass

    def connection_made(self, transport):
        self.transport = transport
        print('Port opened:', transport)

    def data_received(self, data):
        # print(str(data), end="")
        zt_data_handler.append(data)

    def connection_lost(self, exc):
        print('Port closed')
        asyncio.get_event_loop().stop()


loop = asyncio.get_event_loop()
coro = serial.create_serial_connection(loop,
                                       SerialMonitor,
                                       '/dev/ttyACM0',
                                       baudrate=115200)
loop.run_until_complete(coro)
loop.run_forever()
loop.close()
