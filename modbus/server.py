from os import execv
from os.path import pathsep
import random
from sys import argv, executable
from pymodbus.server import StartTcpServer, ServerStop
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder
from time import sleep
import signal
import logging
from threading import Thread

FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)


def handler(signum, frame):
    ServerStop()
    sleep(1)


class CallbackDataBlock(ModbusSequentialDataBlock):
    def __init__(self, address, values):
        super().__init__(address=address, values=values)

    def setValues(self, address, value):
        if address == 29:
            execv(executable, [executable.split(pathsep)[-1]] + argv)
        else:
            super().setValues(address, value)


def create_store_for_tests():
    builder = BinaryPayloadBuilder(byteorder=Endian.LITTLE,
                                   wordorder=Endian.LITTLE)
    builder.add_string('abcd')
    builder.add_bits(
        [False, True, False, True, True, False, True, True, True, True, False, True, False, False, True, False])
    builder.add_8bit_int(-0x12)
    builder.add_8bit_uint(0x12)
    builder.add_16bit_int(-0x5678)
    builder.add_16bit_uint(0x1234)
    builder.add_32bit_int(-0x1234)
    builder.add_32bit_uint(0x12345678)
    builder.add_16bit_float(12.34375)
    builder.add_32bit_float(223546.34375)
    builder.add_32bit_float(-22.34)
    builder.add_64bit_int(-0xDEADBEEF)
    builder.add_64bit_uint(0x12345678DEADBEEF)
    builder.add_64bit_uint(0xDEADBEEFDEADBEED)
    builder.add_64bit_float(123.45)
    builder.add_64bit_float(-123.45)
    block = CallbackDataBlock(1, builder.to_registers())
    builder_for_coils = BinaryPayloadBuilder(byteorder=Endian.LITTLE,
                                             wordorder=Endian.LITTLE)
    builder_for_coils.add_bits(
        [False, True, False, True, True, False, True, True, True, True, False, True, False, False, True, False])
    coils_block = CallbackDataBlock(1, builder_for_coils.to_coils())
    store = ModbusSlaveContext(di=coils_block, co=coils_block, hr=block, ir=block)
    return store


def create_initial_values(initial_values):
    return (list(initial_values) or []) + [0] * (16 - len(initial_values or []))


def create_store_for_emulator():
    block = ModbusSequentialDataBlock(1, create_initial_values([265, 300, 1123, 90]))
    return ModbusSlaveContext(hr=block)


def as_int(value):
    return int(round(value, 1) * 10)


def emulate_values(store):
    while True:
        temperature = random.uniform(25.0, 35.0)
        humidity = 100 - (temperature - 5) * 2.5
        power = random.uniform(9.00, 12.00)
        pressure = 1100 - (temperature - 25) * 10

        store.setValues(6, 0, [as_int(temperature)])
        store.setValues(6, 1, [as_int(humidity)])
        store.setValues(6, 2, [as_int(power)])
        store.setValues(6, 3, [as_int(pressure)])

        sleep(1)


def run_server():
    store_for_tests = create_store_for_tests()
    store_for_emulator = create_store_for_emulator()
    slaves = {
        0x01: store_for_emulator,
        0x02: store_for_tests
    }
    context = ModbusServerContext(slaves=slaves, single=False)

    emulation_thread = Thread(target=emulate_values, args=(store_for_emulator,), daemon=True, name='emulation_thread')
    emulation_thread.start()

    StartTcpServer(context=context, address=("0.0.0.0", 5021))


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    run_server()
