"""Send a few Lab 4 gateway records to Azure IoT Hub with Paho MQTT."""

import base64
import hashlib
import hmac
import json
import os
import ssl
import time
import urllib.parse

import certifi
import paho.mqtt.client as mqtt


DATA_FILE = "near.jsonl"
MAX_RECORDS = 5
API_VERSION = "2021-04-12"
TOKEN_LIFETIME_S = 3600


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


def parse_connection_string(text):
    """Split HostName=...;DeviceId=...;SharedAccessKey=... into its parts."""
    parts = dict(item.split("=", 1) for item in text.strip().split(";") if item)
    return parts["HostName"], parts["DeviceId"], parts["SharedAccessKey"]


def make_sas_token(host, device_id, key, lifetime_s):
    """Sign the resource URI and expiry time with the device key (HMAC-SHA256)."""
    uri = f"{host}/devices/{device_id}"
    expiry = str(int(time.time()) + lifetime_s)
    to_sign = f"{urllib.parse.quote_plus(uri)}\n{expiry}".encode("utf-8")
    digest = hmac.new(base64.b64decode(key), to_sign, hashlib.sha256).digest()
    signature = base64.b64encode(digest).decode("utf-8")
    fields = {"sr": uri, "sig": signature, "se": expiry}
    return "SharedAccessSignature " + urllib.parse.urlencode(fields)


def main():
    connection_string = os.environ.get("IOTHUB_DEVICE_CONNECTION_STRING")
    if not connection_string:
        raise SystemExit("Set IOTHUB_DEVICE_CONNECTION_STRING in this terminal first.")

    records = read_records(DATA_FILE)
    if not records:
        raise SystemExit(f"No records found in {DATA_FILE}.")

    host, device_id, key = parse_connection_string(connection_string)
    topic = f"devices/{device_id}/messages/events/$.ct=application%2Fjson&$.ce=utf-8"

    client = mqtt.Client(client_id=device_id, protocol=mqtt.MQTTv311)
    client.username_pw_set(
        username=f"{host}/{device_id}/?api-version={API_VERSION}",
        password=make_sas_token(host, device_id, key, TOKEN_LIFETIME_S),
    )
    client.tls_set(ca_certs=certifi.where(), tls_version=ssl.PROTOCOL_TLSv1_2)

    client.connect(host, port=8883)
    client.loop_start()
    try:
        for _ in range(100):
            if client.is_connected():
                break
            time.sleep(0.1)
        else:
            raise SystemExit("IoT Hub did not accept the connection. Check the connection string.")

        print("Connected as", device_id)
        print("Topic:", topic)
        for record in records:
            info = client.publish(topic, json.dumps(record), qos=1)
            info.wait_for_publish(timeout=10)
            if not info.is_published():
                raise SystemExit(f"No acknowledgement for counter {record['counter']}.")
            print("Sent counter:", record["counter"])
            time.sleep(2)
    finally:
        client.disconnect()
        client.loop_stop()

    print("Sent", len(records), "records to IoT Hub over MQTT.")


if __name__ == "__main__":
    main()
