from pymodbus.server import StartTcpServer, ServerStop
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder
from time import sleep
import signal
import logging

FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)


def handler(signum, frame):
    ServerStop()
    sleep(1)


def run_server():
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
    block = ModbusSequentialDataBlock(1, builder.to_registers())
    builder_for_coils = BinaryPayloadBuilder(byteorder=Endian.LITTLE,
                                             wordorder=Endian.LITTLE)
    builder_for_coils.add_bits(
        [False, True, False, True, True, False, True, True, True, True, False, True, False, False, True, False])
    coils_block = ModbusSequentialDataBlock(1, builder_for_coils.to_coils())
    store = ModbusSlaveContext(di=coils_block, co=coils_block, hr=block, ir=block)
    slaves = {
        0x01: store
    }
    context = ModbusServerContext(slaves=slaves, single=False)
    StartTcpServer(context=context, address=("0.0.0.0", 5021))


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    run_server()
