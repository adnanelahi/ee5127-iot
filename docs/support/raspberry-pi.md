---
title: Raspberry Pi Headless Setup and Recovery
parent: Support
nav_order: 2
permalink: /support/raspberry-pi/
---

Use this page when preparing or recovering a Raspberry Pi gateway for [Lab 4]({{ '/labs/rpi-ble-data-collection/' | relative_url }}). The Pi runs Raspberry Pi OS **Desktop 64-bit** without a connected monitor, keyboard or mouse. You first connect from a laptop using SSH, then enable the Pi's WayVNC server and view its desktop with TigerVNC Viewer.

Writing an image replaces the contents of the selected microSD card. Check the target device and preserve needed files first. Use the laboratory network details provided for the session.

## 1. Prepare the microSD card

Follow Raspberry Pi's [Imager setup guide](https://www.raspberrypi.com/documentation/computers/getting-started.html#install-an-os-onto-boot-media). In Raspberry Pi Imager, select your Pi model, **Raspberry Pi OS Desktop (64-bit)** and the correct microSD card. Choose **Customisation** before writing the image:

1. Set a unique **hostname**, for example `ee5127-g001-pi` for group G001. Replace `g001` with your group ID.
2. Create a **username and password**. The commands below use `ee5127` as an example username; substitute the one you created.
3. Set the correct **localisation** and, for Wi-Fi, the laboratory **SSID and password**. An Ethernet connection can also be used.
4. In **Remote Access**, enable **SSH** and choose **password authentication** with the account you created.
5. Apply the customisation, write and verify the card, then insert it into the Pi. Connect the network cable if using Ethernet and power the Pi.

![Raspberry Pi Imager main screen]({{ '/assets/images/raspberry-pi/raspberry-pi-imager-main-screen.png' | relative_url }})

The Pi and your laptop must be on a network that allows them to reach each other. The first boot may take several minutes.

## 2. Connect by SSH using the hostname

On your **laptop**, open PowerShell, Terminal or another SSH-capable terminal. Replace the example username and hostname with the values you set in Imager:

```bash
ssh ee5127@ee5127-g001-pi.local
```

The `.local` name uses local network discovery. Accept the first-connection host-key prompt after checking that the name is your Pi, then enter the account password. The password does not appear as you type. At the Pi prompt, check:

```bash
hostname
python3 --version
bluetoothctl show
```

If the `.local` name does not resolve, confirm the Pi and laptop are on the intended network and ask the demonstrator for the Pi's IP address. Use `ssh ee5127@<Pi-IP-address>` with your own username and the supplied address. Some managed networks restrict device-to-device connections.

## 3. Enable WayVNC from SSH

Raspberry Pi OS Desktop includes the **WayVNC server**. At the **Pi's SSH prompt**, run:

```bash
sudo raspi-config
```

Select **Interface Options → VNC → Yes**, then finish and reboot if prompted. This enables the VNC server for the Pi's graphical desktop. See Raspberry Pi's [VNC setup instructions](https://www.raspberrypi.com/documentation/computers/remote-access.html#screen-share-with-vnc) if the menu wording differs on your image.

## 4. Open the desktop with TigerVNC Viewer

On your **laptop**, get **TigerVNC Viewer** from the [TigerVNC releases page](https://github.com/TigerVNC/tigervnc/releases). Open the viewer and enter `ee5127-g001-pi.local` as the VNC server, replacing the example hostname. Use the same Pi username and password when prompted. If the viewer cannot resolve the hostname, enter the Pi's IP address instead. Raspberry Pi's [TigerVNC connection guide](https://www.raspberrypi.com/documentation/computers/remote-access.html#connect-to-a-vnc-server) shows the viewer screens and connection steps.

WayVNC runs on the Pi; TigerVNC Viewer runs on your laptop. Once the desktop appears, open a Pi terminal there or continue using SSH.

## 5. Install Visual Studio Code on the Pi

At the **Pi terminal** (in the remote desktop or over SSH), install VS Code from the Raspberry Pi OS package repository:

```bash
sudo apt update
sudo apt install code
```

Open VS Code from the Pi desktop's **Programming** menu, or run `code` in a terminal **on the Pi desktop**. In VS Code, use **File → Open Folder** to open your `ee5127-ble` folder for Lab 4. Use **Terminal → New Terminal** to run the gateway commands in that folder. These installation and launch commands follow the [VS Code Raspberry Pi guide](https://code.visualstudio.com/docs/setup/raspberry-pi).

Return to [Lab 4]({{ '/labs/rpi-ble-data-collection/' | relative_url }}) to prepare Bleak and collect sensor data.

## Recovery checks

- **SSH cannot find the Pi:** Check the hostname, power and network connection. Try the Pi's IP address if `.local` discovery is unavailable.
- **SSH works but VNC does not connect:** Confirm that VNC was enabled in `raspi-config` and that the Pi and laptop can reach each other on the network. Reboot the Pi and try again.
- **Bluetooth controller missing:** Run `bluetoothctl show` at the Pi prompt and check the image or adapter with the demonstrator.

## References

[Raspberry Pi headless and Imager setup](https://www.raspberrypi.com/documentation/computers/getting-started.html#headless-remote-setup), [Raspberry Pi remote access](https://www.raspberrypi.com/documentation/computers/remote-access.html), [TigerVNC](https://tigervnc.org/), [VS Code on Raspberry Pi](https://code.visualstudio.com/docs/setup/raspberry-pi).
