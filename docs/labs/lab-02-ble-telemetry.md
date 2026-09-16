---
title: "Lab 2: BLE Telemetry"
parent: Labs
nav_order: 2
permalink: /labs/lab-02-ble-telemetry/
---

## Aim

What evidence shows that a BLE UART stream is usable by a gateway, and what overhead does the chosen representation impose? Verify discovery and notifications, quantify application traffic, and compare a compact representation on paper.

## Learning outcomes

You can distinguish advertising, GATT services and notifications, calculate framing and payload costs, and evaluate reconnection behaviour while identifying limits of phone-based measurements.

## Equipment and starting point

Prepared Feather from Lab 1, matching `adafruit_ble` library and dependencies, smartphone with nRF Connect for Mobile, USB serial console. Use the UART starter in [code assets]({{ '/assets/downloads/feather-circuitpython/ble-uart-telemetry/code.py' | relative_url }}). Copy the matching `adafruit_ble` library and its supplied dependencies into `CIRCUITPY/lib`. Keep the sensor libraries from Lab 1. Follow the labels in your installed nRF Connect app.

Predict how many notifications might carry a 130-byte line if each carries at most 20 application bytes. Explain why this is an assumption to test, not a fixed property of every BLE connection.

## Practical investigation

### 1. Prepare the BLE peripheral

In this module:

| BLE Concept | EE5127 Role |
|---|---|
| Peripheral | Feather nRF52840 Sense sensor node |
| Central/client | nRF Connect app |
| Advertisement | Short discovery message sent by the Feather |
| Service | Group of related BLE capabilities |
| Characteristic | A readable, writable, or notifiable value inside a service |

Advertising is useful for discovery and small identifiers. Connected services are used when the central needs richer data, repeated updates, or explicit interaction.

The starter below advertises the UART service, waits for a connection and sends newline-delimited JSON. It returns to advertising after disconnection. Save it as `CIRCUITPY/code.py`, keeping a copy of your Lab 1 program.

```python
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
```

### 2. Discover the node and verify services

Open the serial console to check startup errors. Ensure the name is `EE5127-feather-01` and the payload identity is `feather-01`. Scan in nRF Connect, connect and discover services. Find Nordic UART service UUID `6e400001-b5a3-f393-e0a9-e50e24dcca9e`. Enable notifications on TX characteristic `6e400003-b5a3-f393-e0a9-e50e24dcca9e` (peripheral-to-central); RX ending `0002` is the opposite direction.

![nRF Connect showing a Feather BLE advertisement]({{ '/assets/images/lab-02-ble-telemetry/nrf-connect-feather-uart-advertisement.png' | relative_url }})

The screenshot illustrates discovery; your readings may differ. RSSI indicates received signal strength and is not a reliable distance measurement by itself.

The characteristic view/log may display hex or UTF-8. Select UTF-8 if available. If a line is split across notifications, concatenate bytes through newline before interpreting JSON. Do not assume a dedicated UART screen exists.

### 3. Bound the traffic

Change the final `time.sleep(2)` in the telemetry loop to select the interval. Observe two 60-second runs at nominal 1 s and 2 s intervals. Record complete unique counters, observed duration, one full JSON line, its UTF-8 length including newline, and any available negotiated MTU. If the app does not expose MTU, report it as unknown.

Compare observed complete lines per second with the nominal rate. Under the common ATT notification assumption of MTU minus 3 bytes available, calculate the **minimum** notifications per line as ceiling(line bytes / (MTU − 3)); if MTU is unknown use 23 and 247 as hypothetical cases. Actual library chunking can use more notifications. Report application B/s separately from radio throughput.

### 4. Test recovery

Disconnect and reconnect three times without resetting firmware. Record elapsed time from starting the scan to the first complete telemetry line, failures and whether the counter continued. Then reset once and record the counter behaviour. Use the phone's log time or a stopwatch and state its resolution. Do not call this measurement one-way network latency.

### 5. Design a compact alternative

Specify a hypothetical binary record: node code (1 byte), session code (4), counter (4), temperature in hundredths of a degree (signed 2), humidity in hundredths of percent (unsigned 2), pressure in Pa (unsigned 4). Total **17 bytes** before any framing/authentication. Specify byte order, integer ranges and how a receiver knows the schema version. Compare with your measured JSON size; add the cost of your proposed version/framing bytes. Implementation of custom GATT is an extension.

## Observations and reflection

Can you identify the service and the notification characteristic carrying a complete JSON line? Compare the byte cost of JSON and your proposed binary format across the two MTU assumptions. What would make the binary format harder to debug or extend?

Compare the mean and range of recovery times. Explain why an advertised name does not authenticate a node and why a counter reset needs a session model. Keep the working UART firmware for Lab 3 and disconnect the phone before using the Pi.

## Troubleshooting and extension

No notifications: verify TX subscription and inspect serial errors. Cannot connect: disconnect any other central. Service missing: confirm the UART starter replaced the advertising-only example. If hardware is unavailable, use a prepared spare or labelled capture and distinguish its observations from your own live test.

Disconnect the phone before Lab 3. Optional: implement and validate the binary format, compare advertising and telemetry intervals, or inspect the [advertising-only example]({{ '/code/feather-circuitpython-ble-advertising/' | relative_url }}). Advertising-only data, UART streaming and custom GATT characteristics have different payload and interaction trade-offs.

## References

[Adafruit BLE UART API](https://docs.circuitpython.org/projects/ble/en/latest/api.html), [Nordic nRF Connect for Mobile](https://www.nordicsemi.com/Products/Development-tools/nRF-Connect-for-mobile).
