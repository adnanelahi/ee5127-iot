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

## Set up a remote KDE desktop with VNC

These steps use the **Debian 12 KDE image** named above. TigerVNC creates a separate KDE X11 desktop on display `:2` (TCP port `5902`). Work at the ROCK 4C+ terminal as your usual account; the VNC password and startup file belong in that account's home directory.

Install the server and the D-Bus launcher, then create a VNC password. Choose `n` if asked for a view-only password:

```bash
sudo apt update
sudo apt install tigervnc-standalone-server tigervnc-tools dbus-x11
mkdir -p ~/.vnc
tigervncpasswd
```

Open the startup file with `nano ~/.vnc/xstartup` and enter:

```sh
#!/bin/sh
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
exec dbus-launch startplasma-x11
```

Save with **Ctrl+O**, **Enter**, then **Ctrl+X**. Make the file executable and start a test session:

```bash
chmod +x ~/.vnc/xstartup
vncserver -localhost no :2
vncserver -list
```

The list should show display `:2` on port `5902`. On your laptop, install [TigerVNC Viewer](https://github.com/TigerVNC/tigervnc/releases) and connect to `<ROCK-IP-address>:2`. You can find the ROCK 4C+'s local IP address with `hostname -I`. Enter the **VNC password** you set above. The `-localhost no` option lets the laptop reach the VNC server over the laboratory network.

After the test, stop the manually started session:

```bash
vncserver -kill :2
```

To start the VNC desktop automatically when the ROCK 4C+ boots, first check that `command -v vncserver` prints `/usr/bin/vncserver`. If it prints another path, use that path on the three `Exec` lines below. Run the following from your usual account. The shell places that account's name in the service file:

```bash
VNC_ACCOUNT="$(id -un)"
echo "[Unit]
Description=VNC Server
After=network.target

[Service]
Type=forking
User=$VNC_ACCOUNT
ExecStartPre=-/usr/bin/vncserver -kill :2
ExecStart=/usr/bin/vncserver -localhost no :2
ExecStop=/usr/bin/vncserver -kill :2

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/vnc.service

sudo systemctl daemon-reload
sudo systemctl enable vnc.service
sudo systemctl start vnc.service
sudo systemctl status vnc.service --no-pager
```

The status should show that the service is active. Reboot the board and reconnect to `<ROCK-IP-address>:2` to check that the service starts again. If it does not, inspect `sudo journalctl -u vnc.service -b --no-pager` for the startup error.

Return to [Lab 4]({{ '/labs/rpi-ble-data-collection/' | relative_url }}) to create the Python environment, scan for the Feather and collect its data.

## References

[ROCK 4C+ starter-kit assembly guide](https://www.rs-online.com/designspark/get-started-with-the-radxa-rock-4c-4gb-starter-kit), [Radxa ROCK 4C+ overview](https://docs.radxa.com/en/rock4/rock4c+/getting-started/overview), [Radxa installation guide](https://docs.radxa.com/en/rock4/rock4c+/getting-started/install-os), [Radxa VNC setup](https://docs.radxa.com/en/rock4/rock4ab-se/getting-started/basic-software-conf#vnc), [TigerVNC server manual](https://manpages.debian.org/bookworm/tigervnc-standalone-server/tigervncserver.1.en.html), [Bleak Linux support](https://bleak.readthedocs.io/en/latest/).
