---
title: ROCK 4C+ Gateway Setup
parent: Support
nav_order: 3
permalink: /support/rock-4c-plus/
---

Use this page to assemble and set up a ROCK 4C+ for [Lab 4]({{ '/labs/rpi-ble-data-collection/' | relative_url }}).

## Assemble the starter kit

Before powering the board, follow the illustrated [ROCK 4C+ starter-kit assembly guide](https://www.rs-online.com/designspark/get-started-with-the-radxa-rock-4c-4gb-starter-kit). **Fit the supplied heat sinks to the components shown, place the board in the case, and mount the fan in the case with its two screws.** The fan supplied with this kit connects to the GPIO header: red lead to **pin 4 (5 V)** and black lead to **pin 6 (GND)**. Check the guide's connection photograph before applying power. The board's separate fan connector remains unused with this kit fan. Fit the ROCK 4C+'s external wireless antenna, and keep the fan and antenna cables clear of the fan blades when closing the case.

## Prepare the operating system

Use the supplied USB-C power supply, a microSD card or eMMC module, and a monitor, keyboard and mouse for first setup. Radxa specifies a 5 V, 3 A power input and recommends a microSD card of at least 16 GB for installation.

Obtain the **ROCK 4C+ Debian 12 Bookworm KDE** image from [Radxa's ROCK 4C+ download page](https://docs.radxa.com/en/rock4/rock4c+/download). Follow [Radxa's installation guide](https://docs.radxa.com/en/rock4/rock4c+/getting-started/install-os) to write the image to a microSD card or eMMC module. For a microSD card, Radxa's guide uses balenaEtcher: decompress the downloaded image if required, select the image, select the intended card and flash it. Writing an image replaces the card's existing contents, so check the selected target first.

Insert the imaged storage, connect the display and input devices, then power on the ROCK 4C+. Follow any on-screen account setup. Radxa lists `radxa` as both the initial username and password for its downloadable official image; after logging in, run `passwd` in a terminal to set your own password. Connect to the laboratory network using Ethernet or Wi-Fi. Keep the wireless antenna connected when using Bluetooth.

## Check Linux and Bluetooth

Open a terminal on the ROCK 4C+ and run:

```bash
hostname
cat /etc/os-release
python3 --version
bluetoothctl --version
systemctl is-active bluetooth
bluetoothctl show
```

The operating-system output should identify the installed Linux image. `systemctl is-active bluetooth` should print `active`, and `bluetoothctl show` should list a controller. Bleak's Linux backend requires BlueZ 5.55 or later. If the service is inactive, start it and check again:

```bash
sudo systemctl start bluetooth
bluetoothctl show
```

If the controller is listed but powered off, run `bluetoothctl power on` and check `bluetoothctl show` again. If `bluetoothctl` is missing, or no controller appears, check the ROCK 4C+ image, wireless antenna and Bluetooth software with the demonstrator. Radxa's [Bluetooth guidance](https://docs.radxa.com/en/rock4/rock4ab-se/getting-started/interface-usage/witibt) gives further service and firmware checks for the ROCK 4 series.

Return to [Lab 4]({{ '/labs/rpi-ble-data-collection/' | relative_url }}) to create the Python environment, scan for the Feather and collect its data.

## References

[ROCK 4C+ starter-kit assembly guide](https://www.rs-online.com/designspark/get-started-with-the-radxa-rock-4c-4gb-starter-kit), [Radxa ROCK 4C+ overview](https://docs.radxa.com/en/rock4/rock4c+/getting-started/overview), [Radxa ROCK 4C+ downloads](https://docs.radxa.com/en/rock4/rock4c+/download), [Radxa installation guide](https://docs.radxa.com/en/rock4/rock4c+/getting-started/install-os), [Bleak Linux support](https://bleak.readthedocs.io/en/latest/).
