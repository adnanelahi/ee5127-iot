---
title: "Lab 1: Sensor Node Foundations"
nav_order: 2
permalink: /labs/sensor-node-foundations/
---

## Aim and engineering question

Prepare the Adafruit Feather nRF52840 Sense for IoT device programming and understand how its hardware is accessed from CircuitPython. How can you distinguish a working installation, a running program and a working connection to the serial console?

## Learning outcomes

By the end you can:

- Identify the microcontroller, memory, power connections and main pin functions on the Feather Sense.
- Install or verify CircuitPython and distinguish the bootloader drive from the program filesystem.
- Edit and run a blink program, explain its imports, pin configuration and loop, and predict the effect of changing it.
- Use the serial console and REPL to inspect output, interrupt a program and explore the board.
- Discover board-specific pin names and available modules, and explain how default I2C, SPI and UART bus objects are used.

## Equipment and starting point

Use a Feather nRF52840 Sense, a known-good USB **data** cable, a computer with Visual Studio Code and a serial terminal, and the tested CircuitPython UF2 supplied for the session. Back up existing board files before replacing programs or reinstalling firmware. The programs in this lab use built-in modules; sensor-library installation follows in Lab 2.

## Practical investigation

### 1. Adafruit Feather nRF52840 Sense

Inspect the board and identify the hardware features used for IoT device programming.

![Adafruit Feather nRF52840 Sense board]({{ '/assets/images/sensor-node-foundations/feather-nrf52840-sense-board-front.png' | relative_url }})

Use the pinout to locate the power connections, reset button, LED and peripheral pins.

![Feather nRF52840 Sense pinout overview]({{ '/assets/images/sensor-node-foundations/feather-nrf52840-sense-pinout-overview.png' | relative_url }})

#### Microcontroller and QSPI flash

![Feather nRF52840 microcontroller and QSPI flash]({{ '/assets/images/sensor-node-foundations/feather-nrf52840-microcontroller-and-qspi.png' | relative_url }})

- **Nordic nRF52840:** a Bluetooth Low Energy microcontroller with 1 MB of on-chip flash, 256 KB RAM and a 64 MHz Arm Cortex-M4 processor.
- **QSPI flash:** a separate 2 MB flash device on the board provides storage for CircuitPython files or local data. Its six connections are not brought out to the pin headers, avoiding conflicts with external connections. Quad SPI can transfer data over four data lines, compared with a single data line in each direction for ordinary SPI. Application throughput also depends on clock speed, transfer mode and software overhead; the number of data lines alone does not establish a fixed speed improvement.

Distinguish persistent storage from RAM: saved Python files remain after power is removed, while live variables do not.

#### Power pins

![Feather nRF52840 power pins]({{ '/assets/images/sensor-node-foundations/feather-nrf52840-power-pins.png' | relative_url }})

| Pin | Role |
|---|---|
| **3V** | Output of the onboard 3.3 V regulator; can supply compatible external hardware within the regulator's available current budget. |
| **BAT / LiPo input** | Connected to the optional battery supply through the JST PH connector; battery voltage changes with charge state and can reach about 4.2 V when fully charged. |
| **EN** | Regulator enable input, pulled high by default. Connecting it to ground disables the 3.3 V regulator output. |
| **USB** | USB power supply, nominally about 5 V; distinct from the regulated 3.3 V rail. |

Use USB power for this lab. Power-input voltage and I/O voltage are different constraints: use only **3.3 V-compatible I/O**, even when the board is powered from USB.

#### Analog pins

![Feather nRF52840 analog pins]({{ '/assets/images/sensor-node-foundations/feather-nrf52840-analog-pins.png' | relative_url }})

The six exposed analog inputs, **A0–A5**, connect to the microcontroller's analog-to-digital converter (ADC). The hardware supports 8-, 10- and 12-bit conversion, with 14-bit results using oversampling, and rates up to 200 ksample/s under suitable settings. These are hardware capabilities, not a guaranteed acquisition rate for a Python program. ADC functions are tied to particular pins; they cannot be assigned to every digital pin.

The [Adafruit nRF52 ADC guide](https://learn.adafruit.com/adafruit-feather-sense/nrf52-adc) describes an Arduino configuration using a 0.6 V internal reference with 1/6 gain, giving a nominal 0–3.6 V conversion range. At 12 bits there are 4,096 codes, **0–4095**, and an ideal step of 3.6 V / 4,096 = **0.87890625 mV**. This conversion range is not permission to exceed the board's I/O voltage limits. CircuitPython uses a different configuration: 1/4 gain with a VDD/4 reference. Do not transfer Arduino scaling assumptions directly into CircuitPython code.

Two additional labelled connections have special roles:

- **AREF / A7 / P0.31:** an optional external reference for the comparator, not an external ADC reference on this board. Its voltage must not exceed VDD, normally 3.3 V. Check the available CircuitPython alias using `dir(board)` before referring to it in code.
- **VOLTAGE_MONITOR / A6 / P0.29:** connected to a voltage divider on the battery input. Reserve it for its board function rather than treating it as an unconnected general-purpose input or output.

#### PWM outputs and I2C pins

![Feather nRF52840 pins used for PWM output]({{ '/assets/images/sensor-node-foundations/feather-nrf52840-pwm-pins.png' | relative_url }})

Pulse-width modulation (PWM) switches an output repeatedly while controlling the fraction of each cycle spent high. GPIO pins can be assigned to hardware PWM outputs, subject to pin availability and peripheral resources. Channels using the same PWM peripheral share timing constraints; do not assume every output can have an independent frequency. CircuitPython provides the `pwmio` module for PWM use.

![Feather nRF52840 I2C pins]({{ '/assets/images/sensor-node-foundations/feather-nrf52840-i2c-pins.png' | relative_url }})

The I2C pins are **SCL** (clock) and **SDA** (data). The board has 4.7 kΩ pull-up resistors and connects its onboard sensors, except the microphone, to this bus. Additional compatible devices can share the bus if their addresses do not conflict and the electrical loading remains suitable. These pins already serve onboard hardware, so changing their function can disrupt those devices.

### 2. Install or verify CircuitPython

CircuitPython may already be installed. Connect the board and look for a drive named **CIRCUITPY**. If it is present, inspect `boot_out.txt` to check the board and firmware version against the version supplied for the session. Continue without reflashing when they match. Installing or updating firmware is a separate operation from saving each new Python program.

#### Obtain the firmware

Back up your code and other board files before installation or an update. Use the supplied, tested UF2 for the **Feather nRF52840 Sense**; the [board download page](https://circuitpython.org/board/feather_bluefruit_sense/) provides the board-specific releases. The `.uf2` extension identifies the USB Flashing Format used by the bootloader. Match the session's specified version instead of choosing a version solely because it is newest.

Connect the board using a known-good USB data cable. A charge-only cable can power the board without providing access to its drives or serial console.

#### Enter the UF2 bootloader

Locate the board's reset button, labelled **RESET** or **RST**, near the USB connector. The photograph below illustrates the reset-button action; the board pinout above identifies the button on the Feather Sense.

![Reset button used to enter the CircuitPython bootloader]({{ '/assets/images/sensor-node-foundations/circuitpython-reset-button.jpg' | relative_url }})

Press reset twice in quick succession. If the bootloader does not appear, try the double press again; the spacing between presses matters. Status-LED behaviour depends on the board and bootloader, so use the appearance of the bootloader drive as the main check.

#### Recognise bootloader mode

A drive such as **FEATHERBOOT** should appear. The general naming pattern is **boardnameBOOT**, where the first part identifies the board.

![FEATHERBOOT drive visible on Windows]({{ '/assets/images/sensor-node-foundations/circuitpython-featherboot-drive.png' | relative_url }})

The board is now ready to accept the UF2 firmware file.

#### Install CircuitPython

Drag the downloaded `.uf2` file onto **FEATHERBOOT**. The following illustration shows the same drag-and-drop process on another CircuitPython board; use the Feather Sense UF2 and the drive belonging to your board.

![Dragging a UF2 file onto a bootloader drive]({{ '/assets/images/sensor-node-foundations/circuitpython-drag-uf2-to-boot-drive.png' | relative_url }})

Allow the transfer and restart to finish. The bootloader drive should disappear and a new drive named **CIRCUITPY** should appear.

![CIRCUITPY drive visible after CircuitPython installation]({{ '/assets/images/sensor-node-foundations/circuitpython-circuitpy-drive.png' | relative_url }})

Inspect `boot_out.txt` again to verify the installed board and firmware version.

#### CIRCUITPY and the bootloader drive

The two drives serve different purposes:

- **FEATHERBOOT** accepts firmware installation files. The UF2 is processed by the bootloader and the drive disconnects; it is normal for the copied file not to remain visible as an ordinary saved file.
- **CIRCUITPY** exposes the filesystem used by CircuitPython. Save your Python program as `code.py` here, and place additional libraries in its `lib` folder when required.

Copying a Python file to the bootloader drive does not make it available to CircuitPython. Once installation is complete, edit and save files on **CIRCUITPY**.

### 3. Run the CircuitPython blink program

#### Set up Visual Studio Code

Use the supplied editor environment, or install [Visual Studio Code](https://code.visualstudio.com/) and the module's tested Python and [CircuitPython V2](https://marketplace.visualstudio.com/items?itemName=wmerkens.vscode-circuitpython-v2) extensions. Python editing support and completion tools such as IntelliCode assist editing; the board's CircuitPython firmware executes the program. Reload VS Code when prompted after installing extensions.

![Installing the CircuitPython extension in VS Code]({{ '/assets/images/sensor-node-foundations/vscode-install-circuitpython-extension.png' | relative_url }})

Open **CIRCUITPY** as a folder in VS Code.

![Opening the CIRCUITPY folder in VS Code]({{ '/assets/images/sensor-node-foundations/vscode-open-circuitpy-folder.png' | relative_url }})

#### Create code.py

Save a copy of any existing program, then create or replace `code.py` on **CIRCUITPY** with:

```python
import board
import digitalio
import time

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

while True:
    led.value = True
    time.sleep(0.5)
    led.value = False
    time.sleep(0.5)
```

![Saving code.py for the blink program in VS Code]({{ '/assets/images/sensor-node-foundations/vscode-save-codepy-blink-program.png' | relative_url }})

All four lines inside `while True:` have the same four-space indentation. The setup lines above the loop are not indented. Indentation defines which statements belong to the loop.

Save the file. CircuitPython normally detects a filesystem write and reruns `code.py` from the beginning. Wait for the computer to finish writing before unplugging or resetting the board; interrupting a write can corrupt the filesystem. Use the operating system's safe-removal procedure before disconnecting.

The onboard LED should remain on for approximately 0.5 s and off for approximately 0.5 s: one complete cycle takes about one second. The extension may identify the board as **Adafruit Industries LLC: Feather Bluefruit Sense** in its status bar. The visible LED behaviour checks execution on the board; the editor's board label alone does not.

You can save the editor workspace using **File > Save Workspace As**, for example as `feather-sense.code-workspace`. Prefer storing editor workspace files on your computer and keeping a separate backup of the board program there. Reopen the **CIRCUITPY** folder when working on the connected board.

### 4. Understand the CircuitPython program

#### Imports, modules and libraries

A module groups related functionality. A library can contain one or more modules; modules may be built into the firmware or provided as separate `.py` or compiled `.mpy` files. Additional CircuitPython libraries are normally stored in **CIRCUITPY/lib**.

The blink program imports three built-in modules, so it needs no downloaded libraries:

```python
import board
import digitalio
import time
```

- `board` provides board-specific objects, including named pins.
- `digitalio` configures digital inputs and outputs and reads or writes their states.
- `time` provides timing functions, including pauses with `sleep()`.

The `import` statements make these modules available by name in the program.

#### Set up the LED

```python
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
```

`board.LED` identifies the pin connected to the onboard LED. `DigitalInOut` creates an object for using the pin as digital I/O, and the second line sets its direction to output. The variable `led` holds that object so later statements can change its state.

#### Follow the loop

```python
while True:
    led.value = True
    time.sleep(0.5)
    led.value = False
    time.sleep(0.5)
```

A `while` loop repeats while its condition is true. Here the condition is the constant `True`, so the loop continues until execution is interrupted, an error occurs or the board loses power. Its indented statements execute in order:

1. Set the LED output high, turning the LED on.
2. Pause for 0.5 s with the LED on.
3. Set the output low, turning the LED off.
4. Pause for another 0.5 s, then return to the first statement.

Change **only the first** `time.sleep(0.5)` to `time.sleep(0.1)`. Predict the effect before saving. The on-time becomes about 0.1 s while the off-time stays about 0.5 s, producing a shorter flash. Calculate the nominal period and on-time fraction for both versions. The original is approximately 1 s and 50%; the changed version is approximately 0.6 s and 16.7%. These are predictions from the delays, not precise timing measurements.

Restore both delays to 0.5 s after the comparison.

#### What happens when a program finishes?

CircuitPython resets hardware state when a program finishes, preparing it for subsequent execution. Setting a pin once does not necessarily leave it driven after the program exits.

Keep the imports and LED setup, but temporarily replace the entire loop with the single unindented statement:

```python
led.value = True
```

Save and observe. The LED may flash too briefly to see before its pin state is reset as the program ends. This differs from keeping the program alive inside a loop. Restore the working blink program afterwards.

### 5. Use the serial console and REPL

#### Print text to the serial console

A print statement sends text to an output stream. For example:

```python
print("Hello, world!")
```

produces:

```text
Hello, world!
```

The USB serial console displays output from the board, including print statements and Python error messages. It requires either an editor with serial-terminal support or a separate serial-terminal application. The blink program above does not print anything, so a lack of application text while it blinks is expected.

#### Connect through VS Code

Open **View > Terminal** and select the CircuitPython serial monitor. If it has not opened automatically, use the Command Palette's **Circuit Python: Open Serial Console** command provided by the extension. The precise controls can vary with the installed extension version.

![CircuitPython serial terminal in VS Code]({{ '/assets/images/sensor-node-foundations/vscode-circuitpython-serial-terminal.png' | relative_url }})

Use the serial-port control to choose the port belonging to the Feather. On Windows this is a **COM** port. The selected port should appear in the status bar. Only one terminal application should own the port at a time.

![Selecting the Feather COM port in VS Code]({{ '/assets/images/sensor-node-foundations/vscode-select-feather-com-port.png' | relative_url }})

Save a copy of your blink program on the computer. Temporarily replace the contents of `code.py` with the `print("Hello, world!")` example and save it while the console is open. Expect the greeting followed by a message that the program has finished. The screenshot illustrates the same one-line print test.

![Serial console displaying a greeting from the Feather]({{ '/assets/images/sensor-node-foundations/vscode-serial-console-connected.png' | relative_url }})

If you connected after the program finished, reload it from the console to see the greeting. Restore the blink program before trying the interrupt below.

#### Enter the REPL

The **Read–Evaluate–Print Loop (REPL)** lets you enter Python statements interactively and see their results immediately. It is useful for checking an individual expression, inspecting hardware names or investigating a failure without repeatedly editing a whole program.

While connected to the serial console, press **Ctrl+C** to interrupt the running blink program. If prompted with `Press any key to enter the REPL. Use CTRL-D to reload.`, press a key.

A traceback describes where execution stopped. A `KeyboardInterrupt` after pressing Ctrl+C is expected; it records your interruption rather than a fault in the blink program. The screenshot illustrates an interruption in another program; your filename and line number can differ.

![KeyboardInterrupt after interrupting a CircuitPython program]({{ '/assets/images/sensor-node-foundations/circuitpython-repl-keyboard-interrupt.png' | relative_url }})

The interactive prompt is:

```text
>>>
```

![CircuitPython REPL prompt]({{ '/assets/images/sensor-node-foundations/circuitpython-repl-prompt.png' | relative_url }})

#### Interact with the REPL

At the prompt, type the following and press Enter:

```python
help()
```

![Entering help() in the CircuitPython REPL]({{ '/assets/images/sensor-node-foundations/circuitpython-repl-help-command.png' | relative_url }})

Read the help message to find the available interaction and reload commands. Its wording can vary between firmware versions.

![Help output in the CircuitPython REPL]({{ '/assets/images/sensor-node-foundations/circuitpython-repl-help-output.png' | relative_url }})

Statements entered at the REPL are not automatically saved into `code.py`. Copy anything you want to retain into a program file. **Ctrl+D** reloads the saved program after interactive inspection. Keep the REPL open for the next two sections.

### 6. Explore board pins and bus objects

#### Inspect the board module

Microcontrollers connect to external hardware through their input/output pins. CircuitPython uses modules such as `board` and `digitalio` to identify and control these connections. The `board` module supplies names specific to the board, and a physical pin can have more than one alias.

At the REPL, run:

```python
import board
dir(board)
```

![Using dir(board) to list Feather Sense pin names and bus helpers]({{ '/assets/images/sensor-node-foundations/circuitpython-repl-board-pins.png' | relative_url }})

Compare the returned names with the physical labels and the pinout. Firmware versions and different board models can expose different names, so your list may differ from the screenshot. Some boards use names such as `IO1`; the Feather also uses names such as `D13`, `A0`, `SCL` and `SDA`. Use the names your board actually provides.

A protocol label does not necessarily fix a pin permanently to that protocol: an otherwise available SDA pin may also support digital I/O. Check the board wiring first. On the Feather Sense, SDA and SCL are already connected to onboard devices. A pin alias also does not imply that the pin supports every peripheral function.

If a program raises an `AttributeError` for a missing `board` name, use `dir(board)` to check the spelling and the names available on the actual board.

#### I2C, SPI and UART

The board module may provide `I2C()`, `SPI()` and `UART()` helpers for its default buses. These are available on many boards, but not every board or firmware configuration. Look for them in the output of `dir(board)`.

| Bus | Typical default pin names | Purpose |
|---|---|---|
| I2C | `SCL`, `SDA` | Clock and shared bidirectional data |
| SPI | `SCK`, `MOSI`, `MISO` | Clock and separate data directions; devices normally also need a chip-select connection |
| UART | `TX`, `RX` | Asynchronous serial transmit and receive |

Creating an object is called **instantiation**. For example, constructing an I2C bus explicitly specifies its clock and data pins:

```python
import board
import busio

i2c = busio.I2C(board.SCL, board.SDA)
```

The resulting object can be passed to a device driver. The following TSL2591 example illustrates the interface only: that external light sensor and its library are not required for this lab, and it is not the Feather's onboard light sensor.

```python
# Illustrative continuation: requires a connected TSL2591 and its library.
import adafruit_tsl2591

tsl2591 = adafruit_tsl2591.TSL2591(i2c)
```

Using the default board helper expresses the same bus choice more simply:

```python
# Illustrative alternative: requires a connected TSL2591 and its library.
import board
import adafruit_tsl2591

tsl2591 = adafruit_tsl2591.TSL2591(board.I2C())
```

Here `board.I2C()` supplies a **singleton**: it creates the default bus object when first needed and returns the same object on subsequent calls. This lets drivers share one bus object and removes the need to construct it explicitly with `busio` in the application. The `SPI()` and `UART()` helpers follow the same default-bus idea where available.

These are alternative ways of obtaining a bus, not instructions to initialise the same pins twice. If you try the explicit `busio.I2C(...)` example at the REPL, release it with `i2c.deinit()` before switching approaches, or press Ctrl+D to reload. Sensor drivers and acquisition are developed in Lab 2.

### 7. Discover built-in modules

Modules such as `board` and `digitalio` are part of the CircuitPython firmware, so they are not files you need to find in the Adafruit library bundle. The documentation lists [hardware modules](https://docs.circuitpython.org/en/latest/shared-bindings/index.html) and [Python-compatible modules](https://docs.circuitpython.org/en/latest/docs/library/index.html).

Not every module is available on every board: firmware size and hardware capabilities constrain the selection. To check support, consult the [CircuitPython support matrix](https://docs.circuitpython.org/en/latest/shared-bindings/support_matrix.html) for the relevant board and firmware version, or inspect the running board.

With the board connected and the REPL open, enter:

```python
help("modules")
```

![Listing modules available on the Feather in the CircuitPython REPL]({{ '/assets/images/sensor-node-foundations/circuitpython-repl-built-in-modules.png' | relative_url }})

Find `board`, `digitalio` and `time` in the output. The result can include modules available from the filesystem as well as firmware modules, so it is an inventory of available imports rather than proof that every listed module is built in. Compare the list with the documentation for your installed version; do not expect an exact match to a screenshot from another installation.

## Observations and reflection

- What does a visible **CIRCUITPY** drive establish, and what additional evidence does the blinking LED provide?
- Explain the different roles of on-chip flash, the QSPI filesystem and RAM.
- Why did changing only the first sleep affect both the blink period and its on-time fraction?
- Why did the LED stop remaining on when the program reached its end? How does this differ from the intentional Ctrl+C interruption?
- Why was the serial console quiet during the original blink program, and what made the greeting visible?
- What do `dir(board)` and `help("modules")` tell you when adapting code written for another board?
- Why should two drivers sharing the default I2C bus use one bus object?

## Troubleshooting

| Symptom | Check and recovery |
|---|---|
| No drive or serial port appears | Check the USB data cable, connector and another USB port. A power light alone does not prove a data connection. |
| FEATHERBOOT appears instead of CIRCUITPY | The board is in bootloader mode. Follow the firmware-installation steps if needed; save application programs on CIRCUITPY after it restarts. |
| LED does not blink | Confirm the file is named `code.py` on CIRCUITPY, the save has finished, and the serial console shows no error. Inspect indentation and the pin name. |
| Console is empty | Confirm the selected board port and serial-monitor terminal. The blink program prints nothing; run the greeting example with the console already open. |
| Serial port is busy | Close other serial monitors before reconnecting. |
| KeyboardInterrupt appears | This is expected after Ctrl+C. Enter the REPL, or use Ctrl+D to reload the saved program. |
| A board pin name is missing | Inspect `dir(board)` and compare the result with the board pinout. |
| A module cannot be imported | Check its spelling and availability for the installed board/firmware. Additional sensor libraries are installed in Lab 2. |
| Pin already in use | Avoid creating a second owner for the same pin or bus. Release an explicitly created object with `deinit()` when appropriate, or reload before trying an alternative. |

The [CircuitPython Board Reference and REPL]({{ '/support/circuitpython/' | relative_url }}) provides a short reminder for later labs.

## References and acknowledgements

Board descriptions and pinout material draw on the [Adafruit Feather nRF52840 Sense guide](https://learn.adafruit.com/adafruit-feather-sense), including its [pinouts](https://learn.adafruit.com/adafruit-feather-sense/pinouts) and [nRF52 ADC](https://learn.adafruit.com/adafruit-feather-sense/nrf52-adc) pages.

CircuitPython installation, editing, program explanations and REPL material are adapted from Kattni Rembor's and the other contributors' [Welcome to CircuitPython](https://learn.adafruit.com/welcome-to-circuitpython/overview) guide, including [Installing CircuitPython](https://learn.adafruit.com/welcome-to-circuitpython/installing-circuitpython), [Creating and Editing Code](https://learn.adafruit.com/welcome-to-circuitpython/creating-and-editing-code) and [Exploring Your First CircuitPython Program](https://learn.adafruit.com/welcome-to-circuitpython/exploring-your-first-circuitpython-program).

See also the [CircuitPython board-module reference](https://docs.circuitpython.org/en/latest/shared-bindings/board/index.html), [PWM reference](https://docs.circuitpython.org/en/latest/shared-bindings/pwmio/index.html) and [CircuitPython V2 extension documentation](https://marketplace.visualstudio.com/items?itemName=wmerkens.vscode-circuitpython-v2).
