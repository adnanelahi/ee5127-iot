import asyncio

from bleak import BleakScanner


SCAN_SECONDS = 10


async def main():
    print(f"Scanning for BLE devices for {SCAN_SECONDS} seconds...")
    devices = await BleakScanner.discover(timeout=SCAN_SECONDS, return_adv=True)

    for device, advertisement in devices.values():
        name = device.name or advertisement.local_name or "(unnamed)"
        rssi = getattr(advertisement, "rssi", None)
        rssi_text = f"{rssi} dBm" if rssi is not None else "RSSI unavailable"
        print(f"{name:24} {device.address:20} {rssi_text}")

    print(f"Scan complete. Found {len(devices)} devices.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScan stopped.")
