"""Expose Feather Sense temperature as a standard BLE characteristic."""

import time

import board
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.characteristics import Characteristic
from adafruit_ble.characteristics.int import Int16Characteristic
from adafruit_ble.services import Service
from adafruit_ble.uuid import StandardUUID
from adafruit_sht31d import SHT31D


class EnvironmentalSensingService(Service):
    uuid = StandardUUID(0x181A)
    temperature = Int16Characteristic(
        uuid=StandardUUID(0x2A6E),
        properties=Characteristic.READ | Characteristic.NOTIFY,
    )


GROUP_ID = "G001"  # Replace with your four-character group ID
sensor = SHT31D(board.I2C())
environment = EnvironmentalSensingService()
environment.temperature = int(round(sensor.temperature * 100))

ble = BLERadio()
ble.name = "EE5127-" + GROUP_ID + "-TEMP"
advertisement = ProvideServicesAdvertisement(environment)
advertisement.complete_name = ble.name

while True:
    ble.stop_advertising()
    ble.start_advertising(advertisement)
    print("Advertising temperature service:", ble.advertising)

    while not ble.connected:
        time.sleep(0.1)

    print("Connected")
    while ble.connected:
        temperature_c = sensor.temperature
        environment.temperature = int(round(temperature_c * 100))
        print("Temperature: {:.2f} C".format(temperature_c))
        time.sleep(2)

    print("Disconnected")
