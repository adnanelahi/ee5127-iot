
# type: ignore
import time
import board
import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble import BLERadio

# Initialize BLE radio (GAP)
GROUP_ID = "G001"  # Replace with your four-character group ID
ble = BLERadio()
ble.name = "EE5127-" + GROUP_ID + "-ADV"

# --- GAP: Create an Advertisement (Broadcasting Information) ---
advertisement = Advertisement()
advertisement.complete_name = ble.name

# GAP: Add manufacturer-specific data manually
manufacturer_data = bytearray([0x00, 0x08, 0x03, 0x04])  # Example of custom data
advertisement.data_dict[0xFF] = manufacturer_data

# --- GAP: Start BLE Advertising ---
ble.stop_advertising()
ble.start_advertising(advertisement, interval=0.1)
print("Advertising:", ble.advertising)

# Keep broadcasting indefinitely
while True:
    time.sleep(1)
