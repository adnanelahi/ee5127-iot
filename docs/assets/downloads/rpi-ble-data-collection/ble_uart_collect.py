"""Save one Feather's BLE UART JSON records on a Linux gateway."""

import asyncio
import json
import time
from datetime import datetime, timezone

from bleak import BleakClient, BleakScanner


DEVICE_NAME = "EE5127-G001-UART"  # Replace G001 with your group ID.
OUTPUT_FILE = "near.jsonl"       # Use obstructed.jsonl for the second run.
SECONDS = 30
UART_TX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"


def save_line(raw, log, counts):
    """Check one complete line and write its JSON record."""
    try:
        record = json.loads(raw.decode("utf-8"))
        if not isinstance(record, dict) or "counter" not in record:
            raise ValueError("Expected a JSON record with a counter")
    except (UnicodeError, ValueError):
        counts["unreadable"] += 1
        print("Skipped an unreadable record")
        return

    record["receivedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    line = json.dumps(record)
    log.write(line + "\n")
    log.flush()
    counts["saved"] += 1
    print(line)


def receive_bytes(data, buffer, log, counts):
    """Join notification chunks and pass complete lines to save_line."""
    buffer.extend(data)
    while b"\n" in buffer:
        raw, _, rest = buffer.partition(b"\n")
        buffer[:] = rest
        save_line(raw, log, counts)


async def main():
    print(f"Scanning for {DEVICE_NAME}...")
    device = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=20.0)
    if device is None:
        raise RuntimeError(f"Could not find {DEVICE_NAME}. Check its BLE name and disconnect the phone.")

    buffer = bytearray()
    counts = {"saved": 0, "unreadable": 0}

    with open(OUTPUT_FILE, "w", encoding="utf-8") as log:

        def receive(sender, data):
            receive_bytes(data, buffer, log, counts)

        async with BleakClient(device) as client:
            print(f"Connected to {DEVICE_NAME}")
            await client.start_notify(UART_TX_UUID, receive)
            started = time.monotonic()
            while client.is_connected and time.monotonic() - started < SECONDS:
                await asyncio.sleep(0.2)
            duration = time.monotonic() - started
            if client.is_connected:
                await client.stop_notify(UART_TX_UUID)

    print(f"Connected observation: {duration:.1f} s")
    print(f"Saved records: {counts['saved']}; unreadable records: {counts['unreadable']}")
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
