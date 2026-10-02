---
title: "Lab 3: BLE Advertising and Services"
nav_order: 4
permalink: /labs/ble-telemetry/
---

## Aim

How does a phone discover a BLE sensor node, and when does it need to connect? Broadcast a simple advertisement and an Eddystone beacon, then inspect a standard Temperature service and send Lab 2 sensor readings over BLE UART.

## Learning outcomes

You can distinguish connectionless advertising from connected GATT services; identify Eddystone UID and URL frames; decode a standard two-byte temperature value; and inspect JSON sent through BLE UART. You can also explain what changes when the phone disconnects and reconnects.

## Equipment and starting point

Use the Feather prepared in Lab 2, a USB serial console and a BLE-capable phone. Copy `adafruit_ble`, `adafruit_ble_eddystone` and their matching dependencies from the CircuitPython library bundle into `CIRCUITPY/lib`. Keep the sensor libraries from Lab 2. The four programs below are also available as [Advertising code]({{ '/assets/downloads/ble-telemetry/ble-advertising.py' | relative_url }}), [Eddystone code]({{ '/assets/downloads/ble-telemetry/ble-eddystone.py' | relative_url }}), [Environmental Sensing code]({{ '/assets/downloads/ble-telemetry/ble-environmental-sensing.py' | relative_url }}) and [BLE UART code]({{ '/assets/downloads/ble-telemetry/ble-uart-telemetry.py' | relative_url }}).

Choose the four-character code assigned to your group, such as `G001`, and replace `G001` in each program. The advertised names will then include your group code. The Eddystone UID uses the same code in its namespace.

Use [nRF Connect for Mobile](https://www.nordicsemi.com/Products/Development-tools/nrf-connect-for-mobile) to inspect advertisements and discover services and characteristics. In the first two activities, inspect the scan entries without connecting. Connect in the Temperature activity to read and subscribe to its characteristic. In the UART activity, use the UART terminal in [Bluefruit LE Connect](https://learn.adafruit.com/bluefruit-le-connect) to view the JSON text. App labels and icons may vary between phone versions.

Each program stops any previous advertisement before starting its own. This helps the Feather send the current program's packet after a soft reload.

Before starting, predict which of the four programs will let the phone discover the board without a connection, and which will provide readings after connecting.

## Practical investigation

### 1. Broadcast a simple advertisement

Install [nRF Connect for Mobile](https://www.nordicsemi.com/Products/Development-tools/nrf-connect-for-mobile) from the app store linked on Nordic's page. Turn on Bluetooth, allow the app's requested Bluetooth permissions and start a scan.

In this module:

| BLE Concept | EE5127 Role |
|---|---|
| Peripheral | Feather nRF52840 Sense sensor node |
| Central/client | nRF Connect app |
| Advertisement | Short discovery message sent by the Feather |
| Service | Group of related BLE capabilities |
| Characteristic | A readable, writable, or notifiable value inside a service |

Advertising is useful for discovery and small identifiers. Connected services hold values that a phone can read or subscribe to. Save a copy of your Lab 2 program before replacing `CIRCUITPY/code.py`.

The following program advertises a name such as `EE5127-G001-ADV` and includes four manufacturer-data bytes. Copy the [advertising program]({{ '/assets/downloads/ble-telemetry/ble-advertising.py' | relative_url }}) to `CIRCUITPY/code.py`:

```python
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
```

Scan in nRF Connect and open your group's advertising entry. Record the device name and manufacturer-data bytes. Does the app offer a connection to this advertisement? Change one byte in `manufacturer_data`, save `code.py` and scan again. Record what changed on the phone. These four example bytes can be broadcast by several boards.

### 2. Broadcast an Eddystone beacon

Eddystone is a format for sending small, structured messages in BLE advertisements. A nearby phone can receive these messages during a scan. A **UID** frame carries an identifier made from a namespace and an instance ID; a **URL** frame carries a web address. Both frame types use the Eddystone service UUID `0xFEAA`, which helps the app recognise them. See the [Eddystone protocol specification](https://github.com/google/eddystone/blob/master/protocol-specification.md) for the frame definitions.

The next program alternates an Eddystone UID frame and a URL frame. It broadcasts each frame for five seconds, giving the phone time to capture both. Copy the [Eddystone program]({{ '/assets/downloads/ble-telemetry/ble-eddystone.py' | relative_url }}) to `CIRCUITPY/code.py`:

```python
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
```

The program sets the BLE device name to a group-specific value such as `EE5127-G001-EDD`. The UID contains a ten-byte namespace such as `EE5127G001` and a six-byte instance ID taken from the Feather's BLE address. The URL frame carries a short web address. Watch the serial console while scanning in nRF Connect. Find your group's device name, open its advertising details and look for the UID and URL frames; repeat the scan if the app shows only one frame at first. Record which fields the app exposes. Find your group's code in the UID namespace. Inspect these frames in scan view.

### 3. Read a standard BLE temperature characteristic

The lecture follows a Feather Sense temperature reading through the BLE stack. The Bluetooth SIG Environmental Sensing Service has UUID `0x181A`. Its Temperature characteristic has UUID `0x2A6E` and stores a signed integer in units of 0.01 °C. For example, 23.45 °C becomes the integer 2345, which is hexadecimal `0x0929`. BLE sends the lower byte first, so the characteristic value is `29 09`. Your live value will vary.

In the lecture example, the Feather reads 23.45 °C. Predict what the phone should receive if the Temperature characteristic stores hundredths of a degree in a signed 16-bit integer. Replace `CIRCUITPY/code.py` with the following program:

```python
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
```

In nRF Connect, scan for your group's temperature entry, such as `EE5127-G001-TEMP`, connect, and find service `0x181A` and characteristic `0x2A6E`. Read the characteristic once, then enable notifications and watch for updates. The app may display raw hexadecimal bytes. For a positive reading, convert the two bytes back to degrees Celsius:

```text
temperature (°C) = (first byte + 256 × second byte) / 100
example: 29 09 → (0x29 + 256 × 0x09) / 100 = 23.45 °C
```

If the value is below 0 °C, the signed 16-bit representation also needs sign conversion. The lecture's attribute handles, such as `0x0012`, illustrate one possible GATT layout; use the service and characteristic UUIDs to locate values on your board. Gently warm the board with your hand and check that the serial reading and phone value change together.

Disconnect the phone before replacing the program. Keep this example as a reference for the difference between a standard GATT value and a text stream.

### 4. Prepare the BLE UART peripheral

The next program advertises the Nordic UART service, waits for a connection and sends newline-delimited JSON. It returns to advertising after disconnection. Replace `CIRCUITPY/code.py` with:

```python
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
```

### 5. View the JSON stream in Bluefruit LE Connect

Open the serial console to check startup errors. Install [Adafruit Bluefruit LE Connect](https://learn.adafruit.com/bluefruit-le-connect) from the Apple App Store or Google Play link in Adafruit's installation guide and allow its requested Bluetooth permissions. Its UART terminal displays the received JSON as text.

Open Bluefruit LE Connect and find your group's UART name, such as `EE5127-G001-UART`, under **Available Devices**. Tap **Connect**. After the app shows the device options, tap **UART** to see the messages. If the terminal offers an ASCII/Hex setting, select **ASCII**. Each received JSON record ends with a newline. The `nodeId` in the record is `feather-01`.

The program uses Nordic UART service UUID `6e400001-b5a3-f393-e0a9-e50e24dcca9e`. Its TX characteristic, ending `0003`, carries data from the Feather to the phone. The UART terminal shows that data as text. Disconnect Bluefruit when you finish the activity.

<p align="center"><img src="{{ '/assets/images/ble-telemetry/bluefruit-modules.png' | relative_url }}" alt="Bluefruit LE Connect device options showing UART"></p>

<p align="center"><img src="{{ '/assets/images/ble-telemetry/bluefruit-uart-text.png' | relative_url }}" alt="Bluefruit LE Connect UART terminal showing received sensor text"></p>

These screenshots show the UART option and received text. Their appearance and example values may differ from your app. Your device uses your group's UART name and sends JSON.

### 6. Test reconnection

Disconnect the phone while the UART program is running. Check that the Feather advertises again, reconnect, and observe the next JSON message. Does its counter continue? Reset the Feather, reconnect, and check what happens to the counter. Record what you observed in each case.

### 7. Optional: investigate the split JSON message

The JSON message appears in several pieces in Bluefruit's UART terminal. Why might one message be displayed this way? Find a `JSON bytes including newline:` count in the Feather's serial console. This is the number of bytes in one message, including its final newline. The [CircuitPython UART library](https://github.com/adafruit/Adafruit_CircuitPython_BLE/blob/main/adafruit_ble/characteristics/stream.py) sends at most **20 bytes per notification**. Divide your byte count by 20 and round up: how many notifications are needed for that message?

Now send a shorter message. In the Section 4 program, temporarily replace the `json_line = ...` line with:

```python
json_line = (json.dumps({"id": GROUP_ID}) + "\n").encode("utf-8")
```

Save `code.py` and reconnect in Bluefruit. With a four-character group ID, the new message is 15 bytes including the newline. Check that count in the serial console. Does the complete message now appear on one line in the UART terminal? Restore the original `json_line = ...` line afterward so the Feather sends the full sensor record for Lab 4.

## Observations and reflection

- Which information could you see during a scan? Which values became available after connecting to the Feather?
- What information did the simple advertisement carry? What did the Eddystone UID and URL frames carry?
- Which service and characteristic did you open to read the temperature?
- How did you identify your Feather among the nearby BLE devices?
- What happened to the UART counter after reconnecting and after resetting the Feather? What extra field could the Feather send to help a receiver identify a new run?

## Troubleshooting and extension

- **No scan result:** Check the serial console, verify that the expected `code.py` is on CIRCUITPY, clear any active name or service filters in nRF Connect, and restart the scan.
- **Temperature entry missing:** Look for your group's `-TEMP` name or Environmental Sensing service `0x181A` in the advertising details.
- **Eddystone name or frame missing:** Check the `ble.name` line if the entry appears as `CIRCUITPY`. The UID namespace also identifies your group. Scan through both five-second frame intervals to see UID and URL.
- **No temperature updates:** Subscribe to the Temperature characteristic in nRF Connect and inspect the serial console for errors.
- **No JSON text:** Check that you selected **UART** in Bluefruit LE Connect and inspect the serial console for errors.
- **Cannot connect:** Disconnect any other phone app connected to the Feather.

### Optional extension: investigate Eddystone proximity

Eddystone-UID includes a [reference-power field](https://github.com/google/eddystone/blob/master/eddystone-uid/README.md) that can be used with a scanner's RSSI reading to estimate proximity. If you have time, run the Section 2 beacon and observe its RSSI in nRF Connect at positions you label **near** and **far**. Take several readings at each position, then choose an RSSI threshold that separates their typical values. Test your threshold after turning the phone or placing an obstacle between the devices. A BLE receiver could use that threshold to report **near** or **far**. Investigate calibration of the UID reference-power field if you want to estimate distance in metres.

Further Feather experiments cover [button presses](https://learn.adafruit.com/circuitpython-nrf52840/button-press), [NeoPixel colour](https://learn.adafruit.com/circuitpython-nrf52840/neopixel-color), [phone movement](https://learn.adafruit.com/circuitpython-nrf52840/mobile-movement-data) and [location](https://learn.adafruit.com/circuitpython-nrf52840/location).

## References

[Bluetooth SIG assigned numbers](https://www.bluetooth.com/specifications/assigned-numbers/), [Bluetooth SIG on RSSI and proximity](https://www.bluetooth.com/core-specification-6-feature-overview/), [Eddystone UID specification](https://github.com/google/eddystone/blob/master/eddystone-uid/README.md), [Adafruit BLE services](https://docs.circuitpython.org/projects/ble/en/latest/services.html), [Adafruit BLE characteristics](https://docs.circuitpython.org/projects/ble/en/latest/characteristics.html), [Adafruit Eddystone example](https://docs.circuitpython.org/projects/ble_eddystone/en/latest/examples.html), [Nordic nRF Connect for Mobile](https://www.nordicsemi.com/Products/Development-tools/nrf-connect-for-mobile), [Adafruit Bluefruit LE Connect](https://learn.adafruit.com/bluefruit-le-connect).
