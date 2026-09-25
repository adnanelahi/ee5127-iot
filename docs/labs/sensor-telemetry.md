---
title: "Lab 2: Sensor Data Acquisition and Sampling"
nav_order: 3
permalink: /labs/sensor-telemetry/
---

## Aim

Use the onboard sensors of the Feather nRF52840 Sense, then build a structured telemetry stream whose timing, variability and application payload can be measured and explained.

## Learning objectives

By the end of this lab, you should be able to:

- identify the onboard sensing, power, input and status hardware;
- install and use CircuitPython sensor libraries;
- distinguish a sensor reading from a calibrated physical measurement;
- encode environmental readings as JSON telemetry;
- measure sampling interval, variability and payload size;
- explain how sensor processing affects a sleep-after-work sampling interval; and
- estimate whether a multi-node telemetry stream meets a stated application budget.

## Equipment and starting point

Use the Feather nRF52840 Sense prepared in Lab 1, with CircuitPython running and a working serial console. You also need a USB data cable and the CircuitPython library bundle that matches the **major version** of CircuitPython installed on the board.

Keep your working firmware and useful sample logs. Lab 3 will transmit a related telemetry structure over BLE.

Before you begin, consider two questions:

1. Does sleeping for 0.5 s after each sensor reading produce an exact 0.5 s sampling interval?
2. If two onboard temperature sensors agree, does that establish their absolute accuracy?

## Practical investigation

### 1. Inspect the onboard hardware

The Feather Sense combines environmental, optical, motion, magnetic and acoustic sensing on one board. Board revisions may contain either an LSM6DS33 or an LSM6DS3TR-C motion sensor.

![Feather Sense board revisions and motion-sensor variants]({{ '/assets/images/sensor-telemetry/feather-sense-motion-sensor-variants.png' | relative_url }})

#### Magnetic field: LIS3MDL

The LIS3MDL is a three-axis magnetometer. It measures magnetic field strength along three axes and can support compass-like orientation when combined with suitable calibration and, where needed, tilt compensation. It uses the standard I²C bus at address <code>0x1C</code>.

![LIS3MDL magnetometer on the Feather Sense]({{ '/assets/images/sensor-telemetry/feather-sense-lis3mdl-magnetometer.png' | relative_url }})

#### Acceleration and angular rate: LSM6DS33 or LSM6DS3TR-C

The motion sensor combines a three-axis accelerometer and three-axis gyroscope. Acceleration includes the effect of gravity; the gyroscope measures angular rate. Both board variants use I²C address <code>0x6A</code> and have an interrupt connection on digital pin 3.

![LSM6DS motion sensor on the Feather Sense]({{ '/assets/images/sensor-telemetry/feather-sense-lsm6ds-motion-sensor.png' | relative_url }})

#### Proximity, colour and gestures: APDS9960

The APDS9960 uses an infrared emitter and directional photodiodes to estimate proximity and recognise simple gestures. It also reports red, green, blue and clear light channels. It uses I²C address <code>0x39</code> and has an interrupt connection on digital pin 36.

![APDS9960 proximity, colour and gesture sensor on the Feather Sense]({{ '/assets/images/sensor-telemetry/feather-sense-apds9960-proximity-colour.png' | relative_url }})

#### Temperature and relative humidity: SHT30

The SHT30 measures temperature and relative humidity. It uses I²C address <code>0x44</code>.

![SHT30 temperature and humidity sensor on the Feather Sense]({{ '/assets/images/sensor-telemetry/feather-sense-sht30-temperature-humidity.png' | relative_url }})

#### Pressure and temperature: BMP280

The BMP280 measures barometric pressure and temperature. It can estimate altitude from pressure, but that result depends on the configured sea-level pressure and local weather. It uses I²C address <code>0x77</code>.

![BMP280 pressure and temperature sensor on the Feather Sense]({{ '/assets/images/sensor-telemetry/feather-sense-bmp280-pressure-temperature.png' | relative_url }})

#### Sound activity: MP34DT01-M PDM microphone

The onboard digital microphone uses <code>board.MICROPHONE_DATA</code> and <code>board.MICROPHONE_CLOCK</code> in CircuitPython. An RMS value calculated from its samples is a relative sound-activity measure. It is not a calibrated sound-pressure level in decibels.

#### USB and battery connections

The Micro-USB connector provides programming and power. The two-pin JST-PH connector accepts a compatible LiPo battery and supports charging from USB.

![USB and battery connections on the Feather Sense]({{ '/assets/images/sensor-telemetry/feather-sense-usb-battery-connectors.png' | relative_url }})

Use only a battery whose connector polarity matches the Adafruit board. Reversed polarity can damage the charging circuit.

#### Buttons

The button beside USB resets the board; pressing it twice quickly enters the bootloader. The user button is available as <code>board.SWITCH</code> in CircuitPython.

![Reset and user buttons on the Feather Sense]({{ '/assets/images/sensor-telemetry/feather-sense-buttons.png' | relative_url }})

#### NeoPixel and status LEDs

The addressable RGB LED is available as <code>board.NEOPIXEL</code>. The red and blue LEDs are available as <code>board.RED_LED</code> and <code>board.BLUE_LED</code>. The amber <code>CHG</code> LED shows charging status and may flash when no battery is connected.

![NeoPixel and status LEDs on the Feather Sense]({{ '/assets/images/sensor-telemetry/feather-sense-status-leds.png' | relative_url }})

### 2. Install the sensor libraries

1. Download the [CircuitPython library bundle](https://circuitpython.org/libraries) that matches the major version installed on the Feather.
2. Extract the downloaded ZIP file on your computer.

![Extracted CircuitPython library bundle]({{ '/assets/images/sensor-telemetry/circuitpython-library-bundle-extracted.png' | relative_url }})

3. Open the extracted bundle's <code>lib</code> folder.

![CircuitPython library bundle lib folder]({{ '/assets/images/sensor-telemetry/circuitpython-library-bundle-lib-folder.png' | relative_url }})

4. Open or create the <code>lib</code> folder on <code>CIRCUITPY</code>.
5. Copy these files and folders from the bundle's <code>lib</code> folder to <code>CIRCUITPY/lib</code>:

```text
adafruit_apds9960
adafruit_bmp280.mpy
adafruit_bus_device
adafruit_lis3mdl.mpy
adafruit_lsm6ds
adafruit_register
adafruit_sht31d.mpy
neopixel.mpy
```

![Copying a CircuitPython library to CIRCUITPY]({{ '/assets/images/sensor-telemetry/circuitpython-copy-library-to-circuitpy-lib.png' | relative_url }})

Your folder should contain the selected libraries and their dependencies.

![Completed CIRCUITPY library folder]({{ '/assets/images/sensor-telemetry/circuitpython-feather-lib-folder-complete.png' | relative_url }})

### 3. Run the full sensor demonstration

Replace <code>code.py</code> with the program below. It initialises every onboard sensor, handles either motion-sensor variant and prints one readable block of observations at a time.

```python
# SPDX-FileCopyrightText: 2020 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT
#
"""Read all onboard sensors on an Adafruit Feather nRF52840 Sense."""

import array
import math
import time

import audiobusio
import board
from adafruit_apds9960.apds9960 import APDS9960
from adafruit_bmp280 import Adafruit_BMP280_I2C
from adafruit_lis3mdl import LIS3MDL
from adafruit_sht31d import SHT31D

i2c = board.I2C()

try:
    from adafruit_lsm6ds.lsm6ds33 import LSM6DS33 as LSM6DS
    motion = LSM6DS(i2c)
except RuntimeError:
    from adafruit_lsm6ds.lsm6ds3trc import LSM6DS3TRC as LSM6DS
    motion = LSM6DS(i2c)

optical = APDS9960(i2c)
pressure = Adafruit_BMP280_I2C(i2c)
magnetometer = LIS3MDL(i2c)
humidity = SHT31D(i2c)
microphone = audiobusio.PDMIn(
    board.MICROPHONE_CLOCK,
    board.MICROPHONE_DATA,
    sample_rate=16000,
    bit_depth=16,
)


def normalized_rms(values):
    mean = sum(values) / len(values)
    mean_square = sum((sample - mean) ** 2 for sample in values) / len(values)
    return int(math.sqrt(mean_square))


optical.enable_proximity = True
optical.enable_color = True

# Replace this with current sea-level pressure for a meaningful altitude estimate.
pressure.sea_level_pressure = 1013.25

while True:
    microphone_samples = array.array("H", [0] * 160)
    microphone.record(microphone_samples, len(microphone_samples))

    red, green, blue, clear = optical.color_data
    magnetic_x, magnetic_y, magnetic_z = magnetometer.magnetic
    accel_x, accel_y, accel_z = motion.acceleration
    gyro_x, gyro_y, gyro_z = motion.gyro

    print("\nFeather Sense sensor demo")
    print("---------------------------------------------")
    print(f"Proximity: {optical.proximity}")
    print(f"Colour R/G/B/C: {red}, {green}, {blue}, {clear}")
    print(f"Temperature (SHT30): {humidity.temperature:.1f} deg C")
    print(f"Relative humidity: {humidity.relative_humidity:.1f} %")
    print(f"Temperature (BMP280): {pressure.temperature:.1f} deg C")
    print(f"Barometric pressure: {pressure.pressure:.1f} hPa")
    print(f"Estimated altitude: {pressure.altitude:.1f} m")
    print(f"Magnetic field: {magnetic_x:.3f}, {magnetic_y:.3f}, {magnetic_z:.3f} uT")
    print(f"Acceleration: {accel_x:.2f}, {accel_y:.2f}, {accel_z:.2f} m/s^2")
    print(f"Angular rate: {gyro_x:.2f}, {gyro_y:.2f}, {gyro_z:.2f} rad/s")
    print(f"Microphone RMS activity: {normalized_rms(microphone_samples)}")
    time.sleep(0.3)
```

Observe the output while you:

- cover and uncover the optical sensor;
- move and rotate the board carefully;
- bring a magnetic object near the board without touching it;
- speak or clap near the microphone; and
- warm the board gently with your hand.

Stop the program with **Ctrl+C** when you have finished.

The displayed values need interpretation:

- BMP280 altitude is an estimate derived from pressure. Set <code>sea_level_pressure</code> to a suitable current local value before interpreting altitude.
- APDS9960 proximity and colour depend on distance, surface reflectance, geometry, gain and integration settings.
- Magnetometer heading requires calibration for sensor offsets and nearby magnetic material. A level-board heading also needs correct axis conventions; a tilted board needs tilt compensation.
- Microphone RMS is useful for detecting changes or events, but it is not calibrated in dB SPL.
- Agreement between the SHT30 and BMP280 temperature readings shows consistency under this test; it does not prove either sensor's accuracy.

### 4. Produce structured environmental telemetry

Free-form output is useful for inspection. A consistent record is easier for another program to parse, save and transmit. The next program will produce one JSON record for every sensor sample.

Example record:

```json
{"nodeId": "feather-01", "counter": 17, "sampleElapsedS": 34.084221, "temperatureC": 22.6, "humidityPct": 48.2, "pressureHpa": 1008.4}
```

The fields have distinct purposes:

- <code>nodeId</code> identifies the physical node.
- <code>counter</code> establishes record order and later helps reveal missing records.
- <code>sampleElapsedS</code> is elapsed software time since this program started. It is neither UTC nor an exact sensor-conversion timestamp.
- measurement field names include units where practical.

The program reads each sensor into a named variable before constructing the payload. This makes the sampling point and the values placed in one record explicit. The core identity and environmental fields continue into Lab 3; <code>sampleElapsedS</code> supports this local timing investigation.

### 5. Measure timing, variability and payload size

Replace <code>code.py</code> with the program below. It collects 20 sensor records and then reports the observed timing and size of its own telemetry.

```python
import json
import time

import board
from adafruit_bmp280 import Adafruit_BMP280_I2C
from adafruit_sht31d import SHT31D

# These are the settings you will change.
NODE_ID = "feather-01"
SAMPLE_COUNT = 20
PERIOD_S = 0.5

i2c = board.I2C()
pressure = Adafruit_BMP280_I2C(i2c)
humidity = SHT31D(i2c)

# A list stores several values so that they can be summarised later.
intervals = []
payload_sizes = []

start = time.monotonic()
previous_sample_time = None

for counter in range(SAMPLE_COUNT):
    sample_time = time.monotonic()

    # There is no interval before the first sample.
    if previous_sample_time is not None:
        interval = sample_time - previous_sample_time
        intervals.append(interval)

    temperature_c = humidity.temperature
    humidity_pct = humidity.relative_humidity
    pressure_hpa = pressure.pressure

    payload = {
        "nodeId": NODE_ID,
        "counter": counter,
        "sampleElapsedS": round(sample_time - start, 6),
        "temperatureC": round(temperature_c, 2),
        "humidityPct": round(humidity_pct, 2),
        "pressureHpa": round(pressure_hpa, 2),
    }

    json_line = json.dumps(payload)
    print(json_line)

    # UTF-8 bytes in the JSON text, plus one newline byte.
    payload_size = len(json_line.encode("utf-8")) + 1
    payload_sizes.append(payload_size)

    previous_sample_time = sample_time
    time.sleep(PERIOD_S)

# Calculate simple summary values after all samples have been collected.
mean_interval = sum(intervals) / len(intervals)
shortest_interval = min(intervals)
longest_interval = max(intervals)
mean_payload_size = sum(payload_sizes) / len(payload_sizes)

maximum_timing_error = 0
for interval in intervals:
    timing_error = abs(interval - PERIOD_S)
    if timing_error > maximum_timing_error:
        maximum_timing_error = timing_error

node_output_bps = mean_payload_size / mean_interval

print("\nSummary")
print("---------------------------------------------")
print(f"Requested period: {PERIOD_S:.3f} s")
print(f"Mean measured interval: {mean_interval:.3f} s")
print(f"Shortest interval: {shortest_interval:.3f} s")
print(f"Longest interval: {longest_interval:.3f} s")
print(f"Maximum timing error: {maximum_timing_error:.3f} s")
print(f"Mean JSON record size: {mean_payload_size:.1f} bytes")
print(f"Node telemetry output: {node_output_bps:.1f} B/s")
```

The program uses a **sleep-after-work** schedule. It reads the sensors, creates and prints the JSON, and then sleeps for <code>PERIOD_S</code>. The measured interval therefore includes both the requested sleep and the time spent doing the work.

Twenty records produce nineteen intervals because an interval is the time **between** two records. The program uses familiar operations to summarise them:

- <code>sum(values) / len(values)</code> calculates an average;
- <code>min(values)</code> and <code>max(values)</code> find the shortest and longest intervals; and
- <code>abs(interval - PERIOD_S)</code> finds how far an interval is from the requested period.

Run two controlled trials:

1. Leave <code>PERIOD_S = 0.5</code>, save the program and wait for the summary.
2. Write down the summary values in the first row of the table below.
3. Change only that line to <code>PERIOD_S = 2.0</code>.
4. Save the program again, wait for the new summary and complete the second row.

| Schedule | Requested period | Mean interval | Shortest interval | Longest interval | Maximum error | Mean JSON bytes | Node output |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sleep after work | 0.5 s |  |  |  |  |  |  |
| Sleep after work | 2.0 s |  |  |  |  |  |  |

Keep the board position, USB power and surrounding conditions as consistent as practical.

#### Estimate the load arriving at a gateway

The value printed by the Feather describes one sensor node. If a gateway receives equivalent telemetry from 10 nodes, estimate the combined incoming application payload using:

```text
estimated gateway input = 10 × measured node output
```

For example, a measured node output of <code>280 B/s</code> gives an estimated gateway input of <code>2800 B/s</code>. This estimate scales the JSON payload only.

### 6. Sensor applications

After completing the telemetry investigation, adapt the full sensor demonstration for one of these applications.

#### Tilt-based interaction

Use the accelerometer values to detect left, right, forward and backward tilt. Choose thresholds, map each direction to a message or NeoPixel colour, and add hysteresis or a short debounce so noise near a boundary does not repeatedly change the result.

#### Gesture-based control

Enable APDS9960 gesture detection and map left, right, up and down gestures to actions. Test how distance, hand speed, ambient light and orientation affect detection.

#### Digital compass

For a level-board first experiment, calculate:

```python
heading_deg = math.degrees(math.atan2(magnetic_y, magnetic_x)) % 360
```

Map angular sectors to cardinal directions and add hysteresis at sector boundaries. Treat the result as a basic experiment: axis orientation, hard-iron and soft-iron calibration, local declination and tilt compensation all affect a useful compass.

#### Clap or sound-event detector

Detect a sharp increase in microphone RMS relative to a measured background level. Add a refractory interval to prevent one event from being counted several times. A two-event detector can test whether two threshold crossings occur within one second.

#### Vibration or knock detector

Use changes in acceleration magnitude to detect a tap or knock. Determine a threshold experimentally, count events in a defined window, and add debounce to reject repeated crossings from one physical event.

## Observations and reflection

Compare the 0.5 s and 2.0 s runs.

- How much longer than the requested period was each mean interval, and what work contributed to the difference?
- What do the shortest interval, longest interval and maximum timing error reveal about variability in each run?
- How did sampling period affect the output rate of one sensor node?
- What combined application payload did you estimate for a gateway receiving 10 equivalent node streams?
- Did the environmental readings remain plausible during the trials? Does this timing experiment establish their accuracy?
- Explain the difference between resolution, repeatability and accuracy for one sensor used in the lab.
- Which full-demo values depended strongly on geometry, configuration, calibration or environmental context?

Keep the firmware and completed comparison table for your own reference. The shortest, longest and maximum-error values describe only the intervals observed in these short trials.

## Troubleshooting

**A module cannot be imported:** confirm that the bundle major version matches CircuitPython and that each listed file or folder is directly inside <code>CIRCUITPY/lib</code>.

**The motion sensor raises an error:** keep the two-variant <code>try</code>/<code>except</code> import exactly as shown. It supports both Feather Sense motion-sensor revisions.

**No serial output appears:** confirm that the cable carries data, select the correct serial port, close other terminals that may own the port, and press reset once.

**The summary does not appear:** the program prints the summary only after all 20 records. Wait for the final record. If the program stops earlier, read the final error message in the serial console and check that the code was copied completely.

**A reading seems implausible:** first check units, sensor placement and configuration. Pressure-derived altitude, optical sensing, magnetic heading and microphone activity all need contextual interpretation.

If a board remains unavailable, use a prepared spare. Supplied example output can support interpretation of the calculations, but identify it as supplied data rather than a physical measurement you made.

## References

- [Adafruit Feather Sense guide](https://learn.adafruit.com/adafruit-feather-sense)
- [CircuitPython library bundles](https://circuitpython.org/libraries)
- [APDS9960 CircuitPython documentation](https://docs.circuitpython.org/projects/apds9960/en/latest/)
- [BMP280 CircuitPython documentation](https://docs.circuitpython.org/projects/bmp280/en/latest/)
- [LIS3MDL CircuitPython documentation](https://docs.circuitpython.org/projects/lis3mdl/en/latest/)
- [LSM6DS CircuitPython documentation](https://docs.circuitpython.org/projects/lsm6ds/en/latest/)
- [NeoPixel CircuitPython documentation](https://docs.circuitpython.org/projects/neopixel/en/latest/)
- [SHT31D CircuitPython documentation](https://docs.circuitpython.org/projects/sht31d/en/latest/)

The full-board demonstration is adapted from the MIT-licensed Adafruit Feather Sense sensor example by Kattni Rembor for Adafruit Industries.
