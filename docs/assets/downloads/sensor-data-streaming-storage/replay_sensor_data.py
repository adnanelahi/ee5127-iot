"""Replay the gateway's sensor records to Azure IoT Hub with a send time."""

import json
import os
import time
from datetime import datetime, timezone

from azure.iot.device import IoTHubDeviceClient, Message


DATA_FILE = "near.jsonl"
DEFAULT_INTERVAL_S = 2.0


def read_records(filename):
    """Read every complete JSON record from the gateway file."""
    records = []
    with open(filename, encoding="utf-8") as source:
        for line in source:
            if not line.strip():
                continue
            record = json.loads(line)
            if not isinstance(record, dict) or "counter" not in record:
                raise ValueError("Expected a JSON object with a counter")
            records.append(record)
    return records


def sampling_interval(records):
    """Estimate the original interval between records from receivedAt."""
    if len(records) < 2:
        return DEFAULT_INTERVAL_S
    try:
        first = datetime.fromisoformat(records[0]["receivedAt"])
        last = datetime.fromisoformat(records[-1]["receivedAt"])
    except (KeyError, ValueError):
        return DEFAULT_INTERVAL_S
    interval = (last - first).total_seconds() / (len(records) - 1)
    return interval if interval > 0 else DEFAULT_INTERVAL_S


def send_records(client, records, interval):
    """Send one record per interval, adding sentAt just before each send."""
    start = time.monotonic()
    for index, record in enumerate(records):
        wait = start + index * interval - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        outgoing = dict(record)
        outgoing["sentAt"] = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        message = Message(json.dumps(outgoing))
        message.content_type = "application/json"
        message.content_encoding = "utf-8"
        client.send_message(message)
        print("Sent counter:", record["counter"], "at", outgoing["sentAt"])


def main():
    connection_string = os.environ.get("IOTHUB_DEVICE_CONNECTION_STRING")
    if not connection_string:
        raise SystemExit("Set IOTHUB_DEVICE_CONNECTION_STRING in this terminal first.")

    records = read_records(DATA_FILE)
    if not records:
        raise SystemExit(f"No records found in {DATA_FILE}.")
    interval = sampling_interval(records)
    print(f"Replaying {len(records)} records, one every {interval:.1f} s")

    client = IoTHubDeviceClient.create_from_connection_string(connection_string)
    try:
        client.connect()
        send_records(client, records, interval)
    finally:
        client.shutdown()

    print("Sent", len(records), "records to IoT Hub.")


if __name__ == "__main__":
    main()
