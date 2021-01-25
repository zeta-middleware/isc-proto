import asyncio
import serial_asyncio as serial
from bitstruct import unpack_from, pack
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

    def args(self):
        return (self.__cmd, self.__type, self.__channel, self.__crc,
                self.__size)


class ZetaDataHandle:
    STATE_DIGEST_HEADER = 0
    STATE_DIGEST_BODY = 1

    def __init__(self):
        self.iqueue = asyncio.Queue()
        self.oqueue = asyncio.Queue()
        self.__buffer = bytearray()
        self.__state = self.STATE_DIGEST_HEADER
        self.__current_pkt = None

    async def append(self, data):
        self.__buffer.extend(data)
        await self.digest()

    async def encode_command(self, cmd: ZetaISCCommand):
        await self.oqueue.put(pack("u6u2u8u8u8", *cmd.args()))
        await self.oqueue.put(cmd.data())

    async def digest(self):
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
                    await self.encode_command(self.__current_pkt)

                    self.__current_pkt = None
                    self.__state = self.STATE_DIGEST_HEADER
                else:
                    print("CRC error, pkt discarded")
                self.__buffer = bytearray()
                # self.__buffer[self.__current_pkt.size():]

    async def run(self):
        while (True):
            data = await self.iqueue.get()
            await self.append(data)


async def main(loop):
    print("Running main task")
    zt_data_handler = ZetaDataHandle()
    reader, writer = await serial.open_serial_connection(url='/dev/ttyACM0',
                                                         baudrate=115200,
                                                         loop=loop)
    await asyncio.gather(send(writer, zt_data_handler.oqueue),
                         recv(reader, zt_data_handler.iqueue),
                         zt_data_handler.run())


async def send(w: asyncio.StreamWriter, oqueue: asyncio.Queue):
    print("Running send task")
    while True:
        data = await oqueue.get()
        print(f"Data: {data}")
        w.write(data)


async def recv(r, iqueue: asyncio.Queue):
    print("Running recv task")
    while True:
        data = await r.read(1)
        await iqueue.put(data)


loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))
