---
title: Lab 1: Sensor Node Foundations
parent: Labs
nav_order: 1
permalink: /labs/lab-01-sensor-node-foundations/
---
## Aim

What sampling policy produces useful environmental telemetry within a constrained node's timing and payload budget? Configure the Feather baseline, then compare two sampling intervals using measured timing and sensor variability.

## Learning outcomes

By the end you can quantify sampling jitter and application payload size, distinguish repeatability, resolution and accuracy, and justify a sampling policy from measured evidence and a stated bandwidth budget.

## Equipment and starting point

Use a Feather nRF52840 Sense, USB data cable, computer with VS Code and a serial terminal, and the supplied CircuitPython firmware/library bundle. Keep your Lab 1 firmware and sample logs for later BLE work. Use the tested board/library versions supplied for the session.

Before running the program, predict whether a fixed sleep after sensing produces an exact sampling period. Would two sensors agreeing establish absolute accuracy?

## Practical investigation

### 1. Inspect the board

![Adafruit Feather nRF52840 Sense board]({{ '/assets/images/lab-01-sensor-node-foundations/feather-nrf52840-sense-board-front.png' | relative_url }})

Before programming the board, identify the major hardware features that affect IoT system design.

![Feather nRF52840 Sense pinout overview]({{ '/assets/images/lab-01-sensor-node-foundations/feather-nrf52840-sense-pinout-overview.png' | relative_url }})

Important features include:

- nRF52840 BLE microcontroller with 1 MB flash, 256 KB RAM, and an Arm Cortex-M4 core.
- Onboard QSPI flash for CircuitPython files or local data logging.
- USB connector for power, programming, and serial console access.
- LiPo battery connector for untethered sensing.
- I2C-connected onboard sensors.
- Analog, digital, PWM, I2C, SPI, and UART-capable pins.

![Feather nRF52840 microcontroller and QSPI flash]({{ '/assets/images/lab-01-sensor-node-foundations/feather-nrf52840-microcontroller-and-qspi.png' | relative_url }})



Use only 3.3 V-compatible I/O. The [board reference]({{ '/support/circuitpython/' | relative_url }}) gives additional pin and REPL details.

### 2. Verify CircuitPython

Back up existing board files before reinstalling firmware. If `CIRCUITPY` already appears, verify it and continue without reflashing.

Your board may already have CircuitPython installed. If it does, it should appear as a removable drive named `CIRCUITPY` when connected to your laptop. If it does not, check the cable and boot mode, then install the supplied firmware if needed.

1. Use the supplied, tested CircuitPython UF2 for the Adafruit Feather nRF52840 Sense from the CircuitPython website.
2. Connect the Feather using a known-good USB data cable.
3. Double-press the reset button to enter bootloader mode.

![Feather reset button used for bootloader mode]({{ '/assets/images/lab-01-sensor-node-foundations/circuitpython-reset-button.jpg' | relative_url }})

When bootloader mode is active, a drive such as `FEATHERBOOT` should appear.

![FEATHERBOOT drive visible on Windows]({{ '/assets/images/lab-01-sensor-node-foundations/circuitpython-featherboot-drive.png' | relative_url }})

4. Drag the downloaded `.uf2` file onto the bootloader drive.

![Dragging the CircuitPython UF2 file to the bootloader drive]({{ '/assets/images/lab-01-sensor-node-foundations/circuitpython-drag-uf2-to-boot-drive.png' | relative_url }})

5. Wait for the board to restart. The bootloader drive should disappear and the `CIRCUITPY` drive should appear.

![CIRCUITPY drive visible after CircuitPython installation]({{ '/assets/images/lab-01-sensor-node-foundations/circuitpython-circuitpy-drive.png' | relative_url }})

{: .note }
`FEATHERBOOT` is used only for installing firmware. Your Python code and libraries go on `CIRCUITPY`.

### 3. Check editing and board operation

Open the supplied editor environment. If needed, install the module's Python/CircuitPython extensions; the screenshots illustrate the controls used for editing board files.

![Installing the CircuitPython extension in VS Code]({{ '/assets/images/lab-01-sensor-node-foundations/vscode-install-circuitpython-extension.png' | relative_url }})

Open the `CIRCUITPY` drive as a folder in VS Code.

![Opening the CIRCUITPY folder in VS Code]({{ '/assets/images/lab-01-sensor-node-foundations/vscode-open-circuitpy-folder.png' | relative_url }})

Create or replace `code.py` with the following board test:

```python
import time
import board
import digitalio

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

while True:
    led.value = True
    time.sleep(0.5)
    led.value = False
    time.sleep(0.5)
```

Save the file to the `CIRCUITPY` drive. CircuitPython automatically restarts the program when `code.py` changes.

![Saving code.py for the blink program in VS Code]({{ '/assets/images/lab-01-sensor-node-foundations/vscode-save-codepy-blink-program.png' | relative_url }})

{: .observation }
Self-check: the onboard LED blinks on and off every half second.

### What the Blink Program Demonstrates

The `board` module gives CircuitPython access to board-specific pins and devices. The `digitalio` module configures the LED pin as a digital output. The `while True:` loop keeps the embedded program running continuously. Without a loop, the program would finish and the board would reset the pin state.

### 4. Open the serial console

The serial console is essential for embedded debugging. It shows `print()` output and error messages from the board over USB.

Open the CircuitPython serial terminal in VS Code and select the COM port for the Feather.

![CircuitPython serial terminal in VS Code]({{ '/assets/images/lab-01-sensor-node-foundations/vscode-circuitpython-serial-terminal.png' | relative_url }})

![Selecting the Feather COM port in VS Code]({{ '/assets/images/lab-01-sensor-node-foundations/vscode-select-feather-com-port.png' | relative_url }})

Once connected, the serial console should show output from the board.

![Serial console connected to the Feather]({{ '/assets/images/lab-01-sensor-node-foundations/vscode-serial-console-connected.png' | relative_url }})

{: .observation }
Self-check: when the telemetry program below runs, this console shows its output and any Python errors.



### 5. Check sensor libraries

To use the onboard sensors, install the CircuitPython libraries that match your CircuitPython major version.

1. Download the matching Adafruit CircuitPython library bundle.
2. Extract the bundle on your laptop.

![Extracted CircuitPython library bundle]({{ '/assets/images/lab-01-sensor-node-foundations/circuitpython-library-bundle-extracted.png' | relative_url }})

3. Open the bundle's `lib` folder.

![CircuitPython library bundle lib folder]({{ '/assets/images/lab-01-sensor-node-foundations/circuitpython-library-bundle-lib-folder.png' | relative_url }})

4. Copy the required libraries into the `lib` folder on `CIRCUITPY`.

![Copying a CircuitPython library to the CIRCUITPY lib folder]({{ '/assets/images/lab-01-sensor-node-foundations/circuitpython-copy-library-to-circuitpy-lib.png' | relative_url }})

For the environmental program below, copy `adafruit_bmp280.mpy`, `adafruit_sht31d.mpy` and the matching `adafruit_bus_device` and `adafruit_register` dependencies. The supplied bundle may also contain motion, light and LED libraries for optional exploration; they are not all used by this program.

![Completed CIRCUITPY lib folder for Feather Sense sensors]({{ '/assets/images/lab-01-sensor-node-foundations/circuitpython-feather-lib-folder-complete.png' | relative_url }})

### 6. Read structured sensor telemetry

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

-
odeId` identifies which physical node produced the data.
- `counter` gives ordering between successive readings.
- Field names include units where practical.
- JSON is easier for another program to parse than free-form printed text.

### 7. Instrument the sampling time

Verify that the telemetry program above produces
odeId`, increasing `counter`, temperature, humidity and pressure. Add `start = time.monotonic()` before its loop, then add `sampleElapsedS = time.monotonic() - start` immediately before reading the sensors and include that value in the payload. This is boot-relative software timing, not UTC or an exact sensor-conversion timestamp. Save serial output for each run.

Use monotonic time for durations on one machine. Comparing timestamps from different devices requires synchronised clocks and an error bound.

### 8. Measure timing and variability

Collect 30 samples at a nominal 0.5 s interval and 30 at 2 s using the sleep-after-work baseline. Keep placement, sensing fields, USB power and environment fixed. For each run calculate adjacent timestamp differences, their mean, standard deviation and maximum, mean temperature and its standard deviation, and the encoded UTF-8 JSON bytes per sample including newline.

Application load estimate = mean bytes / mean measured interval. For a hypothetical 10-node gateway with a **5,000 B/s application budget**, estimate utilisation = 10 × load / 5,000. This is a specified design constraint, not a measured BLE capacity.

### 9. Compare a scheduling alternative

Replace sleep-after-work with an absolute monotonic deadline: initialise the next deadline; acquire and emit a sample; advance the deadline by the target period; sleep only the positive remaining time. Count deadline overruns and explicitly choose to skip missed periods or resynchronise. Avoid a burst of catch-up samples.

Repeat the 0.5 s run for 30 samples. Inject 0.7 s of processing delay once. Demonstrate that your policy records the overrun and recovers. Compare timing error and maximum interval against the baseline. Explain why this software change does not guarantee a real-time deadline.

## Observations and reflection

Compare your three runs using interval statistics, temperature variability, payload bytes and estimated utilisation. Which scheduling policy best meets the stated budget? Does your injected overrun recover as intended? Explain the difference between repeatability, resolution and accuracy.

Keep the firmware and useful sample logs for your own comparison and Lab 2. Traffic measurements alone cannot determine battery lifetime, and agreement between sensors does not establish calibration without a traceable reference. Sample standard deviation describes variability under the conditions you tested.

## Troubleshooting and extension

No serial output: verify data cable, correct serial port and that only one terminal owns it. Missing sensor module: use the prepared spare and report the version mismatch. If the board remains unavailable, ask for a prepared spare; a supplied example log can support analysis but is not a physical measurement you made.

Optional after core: measure current with suitable instrumentation, or analyse a motion-sampling/aliasing problem. Zephyr installation and RTOS implementation are optional exploration.

## References

[Adafruit Feather Sense guide](https://learn.adafruit.com/adafruit-feather-sense), [CircuitPython documentation](https://docs.circuitpython.org/en/latest/). CircuitPython setup material draws on Adafruit Learn guides by Kattni Rembor and related Adafruit documentation.
