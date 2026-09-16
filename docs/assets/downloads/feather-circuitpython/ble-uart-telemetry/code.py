import time
import json
import board
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from adafruit_bmp280 import Adafruit_BMP280_I2C
from adafruit_sht31d import SHT31D

NODE_ID = "feather-01"

i2c = board.I2C()
bmp280 = Adafruit_BMP280_I2C(i2c)
sht30 = SHT31D(i2c)

ble = BLERadio()
ble.name = "EE5127-feather-01"
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

counter = 0

while True:
    if not ble.advertising:
        ble.start_advertising(advertisement)
    print("Advertising BLE UART telemetry...")

    while not ble.connected:
        time.sleep(0.1)

    print("Connected")

    while ble.connected:
        payload = {
            "nodeId": NODE_ID,
            "counter": counter,
            "temperatureC": round(sht30.temperature, 2),
            "humidityPct": round(sht30.relative_humidity, 2),
            "pressureHpa": round(bmp280.pressure, 2)
        }

        try:
            uart.write((json.dumps(payload) + "\n").encode("utf-8"))
        except (OSError, RuntimeError):
            # A central can disconnect in the middle of a write.
            break
        print(payload)
        counter += 1
        time.sleep(2)

    print("Disconnected")
