import time
from adafruit_ble import BLERadio
from adafruit_ble.advertising import Advertisement

ble = BLERadio()
ble.name = "EE5127-feather-01"

advertisement = Advertisement()
advertisement.complete_name = "EE5127-feather-01"
advertisement.data_dict[0xFF] = bytearray([0x00, 0x08, 0x03, 0x04])

if not ble.advertising:
    ble.start_advertising(advertisement, interval=0.1)
    print("Advertising as EE5127-feather-01")

while True:
    time.sleep(1)
