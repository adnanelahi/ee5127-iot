"""Send a few Lab 4 gateway records to Azure IoT Hub."""

import json
import os
import time

from azure.iot.device import IoTHubDeviceClient, Message


DATA_FILE = "near.jsonl"
MAX_RECORDS = 5


def read_records(filename):
    """Read up to five complete JSON records from the gateway file."""
    records = []
    with open(filename, encoding="utf-8") as source:
        for line in source:
            if not line.strip():
                continue
            record = json.loads(line)
            if not isinstance(record, dict) or "counter" not in record:
                raise ValueError("Expected a JSON object with a counter")
            records.append(record)
            if len(records) == MAX_RECORDS:
                break
    return records


def send_records(client, records):
    """Send each record and show the counter to look for in the monitor."""
    for record in records:
        message = Message(json.dumps(record))
        message.content_type = "application/json"
        message.content_encoding = "utf-8"
        client.send_message(message)
        print("Sent counter:", record["counter"])
        time.sleep(2)


def main():
    connection_string = os.environ.get("IOTHUB_DEVICE_CONNECTION_STRING")
    if not connection_string:
        raise SystemExit("Set IOTHUB_DEVICE_CONNECTION_STRING in this terminal first.")

    records = read_records(DATA_FILE)
    if not records:
        raise SystemExit(f"No records found in {DATA_FILE}.")

    client = IoTHubDeviceClient.create_from_connection_string(connection_string)
    try:
        client.connect()
        send_records(client, records)
    finally:
        client.shutdown()

    print("Sent", len(records), "records to IoT Hub.")


if __name__ == "__main__":
    main()
