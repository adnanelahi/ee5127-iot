import time
import json
import board
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from adafruit_bmp280 import Adafruit_BMP280_I2C
from adafruit_sht31d import SHT31D

GROUP_ID = "G001"  # Replace with your four-character group ID
NODE_ID = "feather-01"

i2c = board.I2C()
bmp280 = Adafruit_BMP280_I2C(i2c)
sht30 = SHT31D(i2c)

ble = BLERadio()
ble.name = "EE5127-" + GROUP_ID + "-UART"
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

counter = 0

while True:
    ble.stop_advertising()
    ble.start_advertising(advertisement)
    print("Advertising BLE UART telemetry:", ble.advertising)

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
        json_line = (json.dumps(payload) + "\n").encode("utf-8")

        try:
            uart.write(json_line)
        except (OSError, RuntimeError):
            # A central can disconnect in the middle of a write.
            break
        print("JSON bytes including newline:", len(json_line))
        counter += 1
        time.sleep(2)

    print("Disconnected")
