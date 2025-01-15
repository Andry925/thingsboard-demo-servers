import random
import asyncio
import logging

from bacpypes3.ipv4.app import NormalApplication
from bacpypes3.local.device import DeviceObject
from bacpypes3.local.analog import AnalogValueObject
from bacpypes3.local.binary import BinaryInputObject
from bacpypes3.pdu import Address
from bacpypes3.apdu import WhoIsRequest, IAmRequest

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


class TemperatureDevice:
    def __init__(self, device_id, address):
        self.device = DeviceObject(
            objectIdentifier=("device", device_id),
            objectName="TemperatureSensor",
            maxApduLengthAccepted=1024,
            segmentationSupported="segmentedBoth",
            vendorIdentifier=15,
        )
        self.temperature_object = AnalogValueObject(
            objectIdentifier=("analogValue", 1),
            objectName="Temperature",
            presentValue=20.0,
            units="degreesCelsius",
        )
        self.humidity_object = AnalogValueObject(
            objectIdentifier=("analogValue", 2),
            objectName="Humidity",
            presentValue=26.5,
            units="percent",
        )

        self.relay_value_object = BinaryInputObject(
            objectIdentifier=("binaryInput", 1),
            objectName="Relay 1",
            presentValue=False
        )
        self.relay_value_object_2 = BinaryInputObject(
            objectIdentifier=("binaryInput", 2),
            objectName="Relay 2",
            presentValue=True
        )

        self.app = NormalApplication(self.device, address)
        self.app.add_object(self.temperature_object)
        self.app.add_object(self.humidity_object)
        self.app.add_object(self.relay_value_object)
        self.app.add_object(self.relay_value_object_2)
        self.app.add_object(self.date_time_object)

        self.app.who_is = self.handle_who_is

    def handle_who_is(self, apdu: WhoIsRequest, address: Address):
        LOG.info(f"Received Who-Is from {address}")
        if apdu.device_instance_range:
            low_limit, high_limit = apdu.device_instance_range
            if not (low_limit <= self.device.objectIdentifier[1] <= high_limit):
                return

        i_am = IAmRequest(
            deviceIdentifier=self.device.objectIdentifier,
            maxAPDULengthAccepted=self.device.maxApduLengthAccepted,
            segmentationSupported=self.device.segmentationSupported,
            vendorID=self.device.vendorIdentifier,
        )
        self.app.request(i_am)
        LOG.info(f"Responded with I-Am to {address}")

    async def run(self):
        LOG.info("Starting BACnet temperature emulator...")
        while True:
            new_temperature = round(self.temperature_object.presentValue + random.uniform(-0.5, 0.5), 2)
            self.temperature_object.presentValue = new_temperature
            LOG.info(f"Temperature updated: {new_temperature}°C")

            new_humidity = round(self.humidity_object.presentValue + random.uniform(-0.5, 0.5), 2)
            self.humidity_object.presentValue = new_humidity
            LOG.info(f"Humidity updated: {new_humidity}%")

            await asyncio.sleep(5)


async def main():
    device_id = 1234
    address = Address("0.0.0.0:47809")
    temp_device = TemperatureDevice(device_id, address)
    await temp_device.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
