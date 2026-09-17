---
title: "Lab 2: Sensor Telemetry and Sampling"
nav_order: 3
permalink: /labs/sensor-telemetry/
---

## Engineering question

How can a constrained sensor node produce telemetry whose timing, payload size and variability can be measured and defended?

## Learning outcomes

By the end you can produce structured sensor telemetry, instrument boot-relative sampling time, quantify interval and payload variability, compare scheduling policies, and explain the limits of the measurements.

## Equipment and starting point

Start with the Feather nRF52840 Sense prepared in Lab 1, including the tested CircuitPython version and a working serial console. Keep the firmware and sample logs from this lab for later BLE work.

Before running the program, predict whether a fixed sleep after sensing produces an exact sampling period. Would two sensors agreeing establish absolute accuracy?

## Practical investigation

### 1. Install the sensor libraries

To use the onboard sensors, install the CircuitPython libraries that match your CircuitPython major version.

1. Download the matching Adafruit CircuitPython library bundle.
2. Extract the bundle on your laptop.

![Extracted CircuitPython library bundle]({{ '/assets/images/sensor-telemetry/circuitpython-library-bundle-extracted.png' | relative_url }})

3. Open the bundle's `lib` folder.

![CircuitPython library bundle lib folder]({{ '/assets/images/sensor-telemetry/circuitpython-library-bundle-lib-folder.png' | relative_url }})

4. Copy the required libraries into the `lib` folder on `CIRCUITPY`.

![Copying a CircuitPython library to the CIRCUITPY lib folder]({{ '/assets/images/sensor-telemetry/circuitpython-copy-library-to-circuitpy-lib.png' | relative_url }})

For the environmental program below, copy `adafruit_bmp280.mpy`, `adafruit_sht31d.mpy` and the matching `adafruit_bus_device` and `adafruit_register` dependencies. The supplied bundle may also contain motion, light and LED libraries for optional exploration; they are not all used by this program.

![Completed CIRCUITPY lib folder for Feather Sense sensors]({{ '/assets/images/sensor-telemetry/circuitpython-feather-lib-folder-complete.png' | relative_url }})

### 2. Read structured sensor telemetry

The Feather nRF52840 Sense includes several sensors that can be used to create different IoT telemetry streams.

| Sensor                  | Measurement                         | Typical IoT Use                         |
| ----------------------- | ----------------------------------- | --------------------------------------- |
| SHT30                   | Temperature and relative humidity   | Environmental monitoring                |
| BMP280                  | Temperature and barometric pressure | Weather, altitude, enclosure conditions |
| APDS9960                | Proximity, colour, simple gestures  | Interaction, occupancy, ambient light   |
| LIS3MDL                 | Magnetic field                      | Orientation and compass-like behaviour  |
| LSM6DS33 or LSM6DS3TR-C | Acceleration and gyroscope          | Motion, vibration, tilt, activity       |
| PDM microphone          | Sound level                         | Event detection, sound activity         |

Raw print output is useful for debugging, but structured data is easier to inspect, save, and process. Rewrite the output as a Python dictionary and print it as JSON.

```python
import time
import json
import board
from adafruit_bmp280 import Adafruit_BMP280_I2C
from adafruit_sht31d import SHT31D

NODE_ID = "feather-01"

i2c = board.I2C()
bmp280 = Adafruit_BMP280_I2C(i2c)
sht30 = SHT31D(i2c)

counter = 0

while True:
    payload = {
        "nodeId": NODE_ID,
        "counter": counter,
        "temperatureC": round(sht30.temperature, 2),
        "humidityPct": round(sht30.relative_humidity, 2),
        "pressureHpa": round(bmp280.pressure, 2)
    }

    print(json.dumps(payload))
    counter += 1
    time.sleep(2)
```

Expected output:

```json
{"nodeId": "feather-01", "counter": 17, "temperatureC": 22.6, "humidityPct": 48.2, "pressureHpa": 1008.4}
```

This structure makes the sensor output easier to inspect and reuse:

- `nodeId` identifies which physical node produced the data.
- `counter` gives ordering between successive readings.
- Field names include units where practical.
- JSON is easier for another program to parse than free-form printed text.

### 3. Instrument the sampling time

Verify that the telemetry program above produces `nodeId`, an increasing `counter`, and temperature, humidity and pressure values. Add `start = time.monotonic()` before its loop. Then add `sampleElapsedS = time.monotonic() - start` immediately before reading the sensors, and include that value in the payload. This is boot-relative software timing, not UTC or an exact sensor-conversion timestamp. Save the serial output from each run.

Use monotonic time for durations on one machine. Comparing timestamps from different devices requires synchronised clocks and an error bound.

### 4. Measure timing and variability

Collect 30 samples at a nominal 0.5 s interval and 30 at 2 s using the sleep-after-work baseline. Keep placement, sensing fields, USB power and environment fixed. For each run calculate adjacent timestamp differences, their mean, standard deviation and maximum, mean temperature and its standard deviation, and the encoded UTF-8 JSON bytes per sample including newline.

Application load estimate = mean bytes / mean measured interval. For a hypothetical 10-node gateway with a **5,000 B/s application budget**, estimate utilisation = 10 × load / 5,000. This is a specified design constraint, not a measured BLE capacity.

### 5. Compare a scheduling alternative

Replace sleep-after-work with an absolute monotonic deadline: initialise the next deadline; acquire and emit a sample; advance the deadline by the target period; sleep only the positive remaining time. Count deadline overruns and explicitly choose to skip missed periods or resynchronise. Avoid a burst of catch-up samples.

Repeat the 0.5 s run for 30 samples. Inject 0.7 s of processing delay once. Demonstrate that your policy records the overrun and recovers. Compare timing error and maximum interval against the baseline. Explain why this software change does not guarantee a real-time deadline.

## Observations and reflection

Compare your three runs using interval statistics, temperature variability, payload bytes and estimated utilisation. Which scheduling policy best meets the stated budget? Does your injected overrun recover as intended? Explain the difference between repeatability, resolution and accuracy.

Keep the firmware and useful sample logs for your own comparison and the later BLE lab. Traffic measurements alone cannot determine battery lifetime, and agreement between sensors does not establish calibration without a traceable reference. Sample standard deviation describes variability under the conditions you tested.

## Troubleshooting and extension

No serial output: verify data cable, correct serial port and that only one terminal owns it. Missing sensor module: use the prepared spare and report the version mismatch. If the board remains unavailable, ask for a prepared spare; a supplied example log can support analysis but is not a physical measurement you made.

Optional after core: measure current with suitable instrumentation, or analyse a motion-sampling/aliasing problem. Zephyr installation and RTOS implementation are optional exploration.

## References

[Adafruit Feather Sense guide](https://learn.adafruit.com/adafruit-feather-sense), [CircuitPython documentation](https://docs.circuitpython.org/en/latest/). CircuitPython setup material draws on Adafruit Learn guides by Kattni Rembor and related Adafruit documentation.
