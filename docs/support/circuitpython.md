---
title: CircuitPython Board Reference and REPL
parent: Support
nav_order: 1
permalink: /support/circuitpython/
---
Essential board setup is in [Lab 1]({{ '/labs/sensor-node-foundations/' | relative_url }}), and sensor telemetry is developed in [Lab 2]({{ '/labs/sensor-telemetry/' | relative_url }}). Use this supplementary reference for additional pin details or interactive debugging.

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

## References

[Adafruit Feather Sense guide](https://learn.adafruit.com/adafruit-feather-sense), [CircuitPython documentation](https://docs.circuitpython.org/en/latest/).
