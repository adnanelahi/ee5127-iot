---
title: "Lab 1: Sensor Node Foundations"
nav_order: 2
permalink: /labs/sensor-node-foundations/
---
## Engineering question

How can a Feather nRF52840 Sense be prepared and checked as a reliable starting point for later IoT experiments?

## Learning outcomes

By the end you can identify the board features relevant to IoT design, install and verify CircuitPython and its libraries, use the serial console, and recover common setup faults.

## Equipment and starting point

Use a Feather nRF52840 Sense, USB data cable, computer with VS Code and a serial terminal, and the supplied CircuitPython firmware/library bundle. Keep your Lab 1 firmware and board setup ready for the later telemetry lab. Use the tested board/library versions supplied for the session.

## Practical investigation

### 1. Inspect the board

![Adafruit Feather nRF52840 Sense board]({{ '/assets/images/sensor-node-foundations/feather-nrf52840-sense-board-front.png' | relative_url }})

Before programming the board, identify the major hardware features that affect IoT system design.

![Feather nRF52840 Sense pinout overview]({{ '/assets/images/sensor-node-foundations/feather-nrf52840-sense-pinout-overview.png' | relative_url }})

Important features include:

- nRF52840 BLE microcontroller with 1 MB flash, 256 KB RAM, and an Arm Cortex-M4 core.
- Onboard QSPI flash for CircuitPython files or local data logging.
- USB connector for power, programming, and serial console access.
- LiPo battery connector for untethered sensing.
- I2C-connected onboard sensors.
- Analog, digital, PWM, I2C, SPI, and UART-capable pins.

![Feather nRF52840 microcontroller and QSPI flash]({{ '/assets/images/sensor-node-foundations/feather-nrf52840-microcontroller-and-qspi.png' | relative_url }})



Use only 3.3 V-compatible I/O. The [board reference]({{ '/support/circuitpython/' | relative_url }}) gives additional pin and REPL details.

### 2. Verify CircuitPython

Back up existing board files before reinstalling firmware. If `CIRCUITPY` already appears, verify it and continue without reflashing.

Your board may already have CircuitPython installed. If it does, it should appear as a removable drive named `CIRCUITPY` when connected to your laptop. If it does not, check the cable and boot mode, then install the supplied firmware if needed.

1. Use the supplied, tested CircuitPython UF2 for the Adafruit Feather nRF52840 Sense from the CircuitPython website.
2. Connect the Feather using a known-good USB data cable.
3. Double-press the reset button to enter bootloader mode.

![Feather reset button used for bootloader mode]({{ '/assets/images/sensor-node-foundations/circuitpython-reset-button.jpg' | relative_url }})

When bootloader mode is active, a drive such as `FEATHERBOOT` should appear.

![FEATHERBOOT drive visible on Windows]({{ '/assets/images/sensor-node-foundations/circuitpython-featherboot-drive.png' | relative_url }})

4. Drag the downloaded `.uf2` file onto the bootloader drive.

![Dragging the CircuitPython UF2 file to the bootloader drive]({{ '/assets/images/sensor-node-foundations/circuitpython-drag-uf2-to-boot-drive.png' | relative_url }})

5. Wait for the board to restart. The bootloader drive should disappear and the `CIRCUITPY` drive should appear.

![CIRCUITPY drive visible after CircuitPython installation]({{ '/assets/images/sensor-node-foundations/circuitpython-circuitpy-drive.png' | relative_url }})

{: .note }
`FEATHERBOOT` is used only for installing firmware. Your Python code and libraries go on `CIRCUITPY`.

### 3. Check editing and board operation

Open the supplied editor environment. If needed, install the module's Python/CircuitPython extensions; the screenshots illustrate the controls used for editing board files.

![Installing the CircuitPython extension in VS Code]({{ '/assets/images/sensor-node-foundations/vscode-install-circuitpython-extension.png' | relative_url }})

Open the `CIRCUITPY` drive as a folder in VS Code.

![Opening the CIRCUITPY folder in VS Code]({{ '/assets/images/sensor-node-foundations/vscode-open-circuitpy-folder.png' | relative_url }})

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

![Saving code.py for the blink program in VS Code]({{ '/assets/images/sensor-node-foundations/vscode-save-codepy-blink-program.png' | relative_url }})

{: .observation }
Self-check: the onboard LED blinks on and off every half second.

### What the Blink Program Demonstrates

The `board` module gives CircuitPython access to board-specific pins and devices. The `digitalio` module configures the LED pin as a digital output. The `while True:` loop keeps the embedded program running continuously. Without a loop, the program would finish and the board would reset the pin state.

### 4. Open the serial console

The serial console is essential for embedded debugging. It shows `print()` output and error messages from the board over USB.

Open the CircuitPython serial terminal in VS Code and select the COM port for the Feather.

![CircuitPython serial terminal in VS Code]({{ '/assets/images/sensor-node-foundations/vscode-circuitpython-serial-terminal.png' | relative_url }})

![Selecting the Feather COM port in VS Code]({{ '/assets/images/sensor-node-foundations/vscode-select-feather-com-port.png' | relative_url }})

Once connected, the serial console should show output from the board.

![Serial console connected to the Feather]({{ '/assets/images/sensor-node-foundations/vscode-serial-console-connected.png' | relative_url }})

{: .observation }
Self-check: when a board program runs, this console shows its output and any Python errors.



## Handoff to the next lab

Keep the board and tested CircuitPython installation available for the next lab, where you will install the sensor libraries and turn readings into measured telemetry.
