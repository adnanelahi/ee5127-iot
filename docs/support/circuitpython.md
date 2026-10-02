---
title: CircuitPython Board Reference and REPL
parent: Support
nav_order: 1
permalink: /support/circuitpython/
---

Board setup, pin details, programming basics and interactive debugging are covered in [Lab 1]({{ '/labs/sensor-node-foundations/' | relative_url }}), and sensor data acquisition and sampling are developed in [Lab 2]({{ '/labs/sensor-telemetry/' | relative_url }}). Use this supplementary reference as a quick reminder during later labs.

## Power and I/O



The board can be powered by USB or battery. The 3.3 V regulator supplies the microcontroller and onboard sensors. Later, when designing deployed sensor nodes, battery behaviour and sampling rate become important because every sensing, BLE, and processing decision affects power consumption.

![Feather nRF52840 power pins]({{ '/assets/images/sensor-node-foundations/feather-nrf52840-power-pins.png' | relative_url }})

The available analog inputs can be used for external sensors, but several pins have board-specific roles. Use the board pinout and CircuitPython `board` module rather than assuming that every label behaves identically across boards.

![Feather nRF52840 analog pins]({{ '/assets/images/sensor-node-foundations/feather-nrf52840-analog-pins.png' | relative_url }})

![Feather nRF52840 I2C pins]({{ '/assets/images/sensor-node-foundations/feather-nrf52840-i2c-pins.png' | relative_url }})

## Interactive debugging with the REPL



The REPL is the interactive CircuitPython prompt. It is useful for quick inspection and testing.

Press `CTRL+C` in the serial console to interrupt the running program, then press any key if prompted.

![CircuitPython keyboard interrupt before entering the REPL]({{ '/assets/images/sensor-node-foundations/circuitpython-repl-keyboard-interrupt.png' | relative_url }})

The prompt should show:

```text
>>>
```

![CircuitPython REPL prompt]({{ '/assets/images/sensor-node-foundations/circuitpython-repl-prompt.png' | relative_url }})

Try:

```python
help()
```

![Running help in the CircuitPython REPL]({{ '/assets/images/sensor-node-foundations/circuitpython-repl-help-command.png' | relative_url }})

![CircuitPython REPL help output]({{ '/assets/images/sensor-node-foundations/circuitpython-repl-help-output.png' | relative_url }})

Press Ctrl+D to reload the program after interactive inspection. Keep private credentials out of console captures.

## Erase and reformat CIRCUITPY

Use this procedure when you need a clean CIRCUITPY filesystem. First copy any files you want to keep, including `code.py`, the `lib` folder and any settings files, to your computer. **The erase command removes all files on CIRCUITPY.**

Open the CircuitPython serial console. Press Ctrl+C to stop a running program and wait for the `>>>` REPL prompt. Enter these commands one line at a time:

```python
import storage
storage.erase_filesystem()
```

The board erases and reformats CIRCUITPY, then restarts. CircuitPython may recreate default files such as `boot_out.txt`, so the drive may contain files again after the restart. The board's CircuitPython firmware remains installed. Copy your program and required libraries back to CIRCUITPY before running a lab that needs them.

This command applies to **CIRCUITPY**, not the separate bootloader drive that appears when you enter UF2 mode. See Adafruit's [CIRCUITPY erase and reformat guidance](https://learn.adafruit.com/welcome-to-circuitpython/troubleshooting).

## References

[Adafruit Feather Sense guide](https://learn.adafruit.com/adafruit-feather-sense), [CircuitPython documentation](https://docs.circuitpython.org/en/latest/).
