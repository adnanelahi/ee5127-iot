"""Broadcast alternating Eddystone UID and URL frames."""

import time

from adafruit_ble import BLERadio
from adafruit_ble_eddystone import uid, url


ble = BLERadio()
GROUP_ID = "G001"  # Replace with your four-character group ID
ble.name = "EE5127-" + GROUP_ID + "-EDD"
namespace_id = ("EE5127" + GROUP_ID).encode("ascii")
instance_id = ble.address_bytes
uid_frame = uid.EddystoneUID(instance_id, namespace_id=namespace_id)
url_frame = url.EddystoneURL("https://adafru.it/discord")

print("Eddystone namespace:", namespace_id)
print("Eddystone instance:", ":".join("{:02X}".format(b) for b in instance_id))

while True:
    ble.stop_advertising()
    ble.start_advertising(uid_frame, interval=0.1)
    print("Advertising UID:", ble.advertising)
    time.sleep(5)
    ble.stop_advertising()

    ble.start_advertising(url_frame, interval=0.1)
    print("Advertising URL:", ble.advertising)
    time.sleep(5)
    ble.stop_advertising()

    time.sleep(1)
