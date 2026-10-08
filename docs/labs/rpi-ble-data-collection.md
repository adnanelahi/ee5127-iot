---
title: "Lab 4: BLE Data Collection on a Gateway"
nav_order: 5
permalink: /labs/rpi-ble-data-collection/
---

## Aim

Collect the Feather's sensor readings on a Linux gateway over BLE, save them as JSON lines, and use the message counters to examine what the gateway received.

## Learning outcomes

You can identify a BLE peripheral during a scan, connect to its UART service from a Linux gateway, assemble a JSON record from notifications, compare node and gateway records, and calculate the achieved sampling rate.

## Equipment and starting point

Use the Feather running the **full JSON UART program from Lab 3** and one gateway board: a Raspberry Pi running Raspberry Pi OS Desktop 64-bit or a ROCK 4C+ running its Debian Linux image. The gateway needs working Bluetooth and a terminal. Keep the Feather's USB serial console available so you can compare its counter with the gateway output. Disconnect Bluefruit LE Connect from the Feather before connecting the gateway.

The gateway is the **central** that scans and collects. The Feather is the **peripheral** that advertises your group's name, such as `EE5127-G001-UART`, and sends readings. Its JSON `nodeId` remains `feather-01`.

Set up your gateway before starting the BLE activity: follow [Raspberry Pi headless setup]({{ '/support/raspberry-pi/' | relative_url }}) or [ROCK 4C+ gateway setup]({{ '/support/rock-4c-plus/' | relative_url }}) for your board. The Pi page covers imaging, hostname and SSH setup, WayVNC and TigerVNC for a remote desktop, and VS Code installation on the Pi. Return here when your gateway is running and connected to the network.

Download [scan_ble_devices.py]({{ '/assets/downloads/rpi-ble-data-collection/scan_ble_devices.py' | relative_url }}) and [ble_uart_collect.py]({{ '/assets/downloads/rpi-ble-data-collection/ble_uart_collect.py' | relative_url }}) to a folder named `ee5127-ble` on the gateway. Open a terminal in that folder and run:

```bash
hostname
python3 --version
bluetoothctl --version
bluetoothctl show
python3 -m venv .venv
source .venv/bin/activate
python -m pip install bleak
```

In `bluetoothctl show`, a `Controller` line means the gateway detects a Bluetooth adapter; `Powered: yes` means it is switched on. If you see `Powered: no`, run `bluetoothctl power on` and check again. If the command reports `No default controller available`, follow your board's setup page or ask the demonstrator to check the adapter.

Bleak requires BlueZ 5.55 or later on Linux. The activated Python environment holds Bleak, the library used by both gateway programs. In a new terminal, return to the folder and run `source .venv/bin/activate` before using the programs. If `python3 -m venv .venv` reports that `venv` is unavailable, install the image's `python3-venv` package with `sudo apt install python3-venv` and repeat that command.

## Practical investigation

### 1. Find your Feather

Check the Feather serial console for `Advertising BLE UART telemetry: True`. Then scan on the gateway:

```bash
python scan_ble_devices.py
```

Find your group's `EE5127-G001-UART` name in the output; substitute your own group ID. A scan also reports a device address and received signal strength (RSSI). Nearby groups may appear in the same list. The name identifies the Feather you intend to connect to for this exercise.

The scan stops automatically after 10 seconds and prints `Scan complete` before returning to the terminal prompt. To stop it early, press **Ctrl+C**. Run the same command again if your Feather was not visible during the first scan.

### 2. Collect a short sensor-data run

For this comparison, make the Feather show each complete record in its USB serial console. In the Lab 3 UART program on `CIRCUITPY/code.py`, add the second print line immediately after the existing byte-count print:

```python
print("JSON bytes including newline:", len(json_line))
print("Sent:", json_line.decode("utf-8").strip())
```

Save `code.py` and keep the Feather serial console open. Each `Sent:` line shows the record passed to `uart.write`. The Feather sends approximately one record every two seconds while connected.

Open `ble_uart_collect.py` and set its first two values for your group and this run:

```python
DEVICE_NAME = "EE5127-G001-UART"  # Replace G001 with your group ID.
OUTPUT_FILE = "near.jsonl"
```

Save the file, then run:

```bash
python ble_uart_collect.py
```

The gateway connects to the Feather's Nordic UART TX characteristic and receives notification chunks. The program holds the chunks until a newline completes a JSON record. It adds a whole-second UTC `receivedAt` timestamp (for example, `2026-10-08T12:08:32+00:00`), prints the record and writes it to `near.jsonl`. One line in that file is one sensor record. Keep the Feather and gateway close together for this 30-second run. About 15 records should fit on the Feather console; scroll back to the first `Sent:` line if needed.

Read the collector as three small jobs: `main()` finds and connects to the Feather, `receive_bytes()` joins the incoming chunks into complete lines, and `save_line()` checks and saves each JSON record. Bleak calls the short `receive()` function whenever a notification arrives; that function passes the new bytes to `receive_bytes()`.

Open `near.jsonl` in a text editor or inspect the first few lines with:

```bash
head -n 3 near.jsonl
```

Locate `nodeId`, `counter`, the three sensor readings and `receivedAt`. Check that the readings change plausibly when you warm the Feather gently with your hand. Compare the Feather's `JSON bytes including newline:` value with what you saw in Bluefruit in Lab 3. The collector combines the notification chunks before it parses each line.

### 3. Verify the node-to-gateway link

Place the Feather's `Sent:` lines beside `near.jsonl`, using two windows or copying the console lines into a text editor. Scan the `counter` values **from the first counter in the gateway file to the last**. Make a short list of counters shown by the Feather that have no matching gateway line. Leave out counters before the first gateway line and after the last, because the gateway's observation did not cover those edges. If the Feather restarted during this short run, repeat it with one uninterrupted counter sequence.

Choose the first, a middle and the last matching counter. Compare their `temperatureC`, `humidityPct` and `pressureHpa` values in the Feather console and gateway file. The gateway adds `receivedAt`, so that field appears only in its file. Record any value that differs. The short run keeps this visual check to about 15 counter values and three full records.

At the end of the run, the collector prints its connected observation time, saved-record count and unreadable-record count. Calculate the **achieved gateway sampling rate**:

```text
achieved rate (samples/s) = saved records / connected observation time (s)
```

Compare your answer with the Feather's intended rate of about 0.5 samples/s. Report the missing counters, any mismatched values among the three checked records, and the collector's unreadable-record count. The collector counts a line as unreadable when its text cannot be decoded as a JSON record with a `counter` field. The three-record check detects value mismatches in those records; a checksum or authentication tag would support a stronger integrity check.

A jump from counter 12 to counter 15 means that counters 13 and 14 were **absent from the gateway log during that observed sequence**. Resetting the Feather starts its counter again. The first and last unseen parts of a run cannot be counted from this log. Report counter gaps as missing application records at the gateway; measuring radio packet loss would require link-layer information.

### 4. Repeat in a second position

Keep the same two-second Feather program running. Put an obstruction between the Feather and gateway. Change `OUTPUT_FILE` in `ble_uart_collect.py` to `"obstructed.jsonl"` and save the script. Then make a second 30-second collection:

```bash
python ble_uart_collect.py
```

Record the approximate distance, obstruction and both results in a small table:

| Position | Saved records | Achieved rate (samples/s) | Missing counters | Unreadable records |
| --- | ---: | ---: | ---: | ---: |
| Near | | | | |
| Obstructed | | | | |

For the obstructed run, compare the Feather and gateway counters within the gateway file's first and last counters. Record its distance and obstruction beside the table. If the Feather resets between runs, its counter starts a new sequence. Compare each run on its own. A short run with no observed gaps is one observation under those conditions.

## Observations and reflection

- Which BLE name did you select, and how did you distinguish it from nearby devices?
- What happened to the Feather's advertising message when the gateway connected and disconnected?
- Why does the gateway wait for a newline before parsing JSON?
- Which node counters were absent from the gateway log? Did any of the three checked sensor records differ?
- How did the achieved rate and missing/unreadable record counts compare between the two positions?
- What would you need to measure sensor-to-gateway delay? Consider where a timestamp would be created and whether the two clocks agree.

## Troubleshooting

- **No group name in the scan:** Check the Feather serial console, confirm the group's BLE name in `code.py`, disconnect the phone and scan again.
- **Connection fails:** Move the Feather closer, check that Bluefruit is disconnected and rerun the collector. Only one central can use this UART connection at a time.
- **No JSON records:** Confirm that the full Lab 3 UART program is running and that its serial console prints `JSON bytes including newline:`. Check the gateway terminal for a connection or notification error.
- **Counter goes backwards:** Check whether the Feather restarted during collection. Record the restart before interpreting gaps.
- **Gateway Bluetooth controller missing:** Follow the checks for your [Raspberry Pi]({{ '/support/raspberry-pi/' | relative_url }}) or [ROCK 4C+]({{ '/support/rock-4c-plus/' | relative_url }}). Ask the demonstrator to help check the adapter if it still does not appear.

## Further exploration

Read the [Bleak scanner](https://bleak.readthedocs.io/en/latest/api/scanner.html) and [client](https://bleak.readthedocs.io/en/latest/api/client.html) documentation. Find where `start_notify` is called in the collector. Trace how bytes are held until a newline and then written to the JSONL file. If time permits, compare the `receivedAt` intervals between successive lines in one run.

## References

[Bleak documentation](https://bleak.readthedocs.io/en/latest/), [Raspberry Pi documentation](https://www.raspberrypi.com/documentation/), [Radxa ROCK 4C+ documentation](https://docs.radxa.com/en/rock4/rock4c+/getting-started/overview).
