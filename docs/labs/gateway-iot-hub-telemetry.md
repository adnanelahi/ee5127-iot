---
title: "Lab 5: Gateway Telemetry to Azure IoT Hub"
nav_order: 6
permalink: /labs/gateway-iot-hub-telemetry/
---

## Aim

Create an Azure IoT Hub, check it with a web simulator, and then send Feather sensor records from the Lab 4 gateway to the same Hub, first with the Azure Python device library and then with the Paho MQTT library. Monitor the messages in Azure Cloud Shell to trace what each sender delivered.

## Learning outcomes

You can create an IoT Hub and register a device identity, monitor its messages with Azure CLI, send gateway JSON records with the Azure Python device library, send the same records over MQTT with Paho by supplying the topic, credentials and TLS settings yourself, and match a cloud message to its gateway record.

## Equipment and starting point

You need an Azure for Students subscription, a browser, and the Raspberry Pi or ROCK 4C+ gateway prepared in Lab 4. Keep `near.jsonl` from the Lab 4 collection in `~/Documents/ee5127-ble` on the gateway. It contains the Feather's `nodeId`, `counter`, sensor readings and the gateway's `receivedAt` time.

If you are working in a group, decide whose Azure for Students subscription will host the group's IoT Hub. Work together on the account holder's computer for the portal and Cloud Shell steps. Keep connection strings private. Keep the Hub available for later cloud labs.

The three transmissions in this lab use the same registered device identity, one at a time:

```text
Web simulator → IoT Hub → Cloud Shell monitor
Feather → BLE gateway → near.jsonl → Azure device library → IoT Hub → Cloud Shell monitor
Feather → BLE gateway → near.jsonl → Paho MQTT → IoT Hub → Cloud Shell monitor
```

## 1. Create an IoT Hub

### Sign up and check your available regions

1. Open [Azure for Students](https://azure.microsoft.com/en-us/free/students/) and select **Start free**. Sign in with a Microsoft account, verify your student status with your university email address, and complete the sign-up steps. If you already have an Azure for Students subscription, sign in with that account. [Microsoft's eligibility guidance](https://learn.microsoft.com/en-us/azure/education-hub/about-azure-for-students) explains who can use this offer.
2. In the [Azure portal](https://portal.azure.com/), search for **Subscriptions** and confirm that **Azure for Students** is active.
3. Search for **Policy**. Under **Authoring**, open **Assignments** and select your Azure for Students subscription as the scope. Look for **Allowed resource deployment regions** or **Allowed locations**. Open the assignment and read **Parameters → Allowed locations**. These are the regions permitted by your subscription's policy; the list can differ between students.

Use Microsoft's [Product Availability by Region](https://azure.microsoft.com/en-us/explore/global-infrastructure/products-by-region/) page to check which of your allowed regions list **IoT Hub**. Then check the region, **Free** tier and validation on the Hub creation screen for your subscription. If you cannot find an allowed region that offers IoT Hub, follow the Azure free account entry under [Troubleshooting and finishing](#troubleshooting-and-finishing), and talk to the Teaching Support Staff (TSS) before choosing a paid tier.

### Create the Hub

1. Sign in to the [Azure portal](https://portal.azure.com/). Select **+ Create a resource**, choose **Internet of Things**, then **IoT Hub**. You can also search the Marketplace for **IoT Hub**.
2. On **Basics**, use the entries below. Replace `g001` with your group ID. Choose a region allowed by your subscription where IoT Hub is available.

| Field | Entry |
| --- | --- |
| Subscription | **Azure for Students** |
| Resource group | Create new: `ee5127-g001-rg` |
| Resource group region, if requested | One of your subscription's allowed regions |
| IoT hub name | `ee5127-g001-iot-1234` (change the final digits to make the name globally unique) |
| Region | An allowed region that offers IoT Hub |
| Tier | **Free**, if available |
| Daily message limit | Check the limit displayed for the Free tier |

Keep personal information out of the Hub name. The **Tier** list may default to **Standard**; select **Free**. If **Free** is unavailable, ask the TSS before selecting a tier that uses student credit.

3. On **Networking**, select **Public access** so the web simulator and gateway can reach the Hub over the Internet.
4. On **Management**, select **Allow shared access policies** for the connection-string activities below.
5. Review **Add-ons** and **Tags**. Select **Review + create** and check that validation succeeds for your subscription, region and tier. Check the configuration once more, then select **Create**. When deployment finishes, select **Go to resource**.

The Hub is the cloud service that accepts messages. A registered device identity specifies which sender may connect to it.

## 2. Register a device identity

1. In your Hub, open **Device management → Devices** and select **Add Device**.
2. Enter a device ID using your group ID, such as `ee5127-g001-gateway`. Select **Symmetric key**, enable **Auto-generate keys**, and select **Save**.

3. Open that device's details and copy its **Primary connection string** into a private place for this session. It contains `HostName`, `DeviceId` and `SharedAccessKey`. The simulator and the gateway program will each use this **device connection string** to send, one after the other.

The IoT Hub device ID identifies the application connecting from the simulator or gateway. The Feather's `nodeId` is a field inside the gateway's JSON record. Find both identities when you inspect the gateway messages later.

## 3. Monitor IoT Hub in Cloud Shell

Cloud Shell runs Azure CLI in the Azure portal. It uses your Azure sign-in to access the Hub. The **device connection string** from Section 2 is for the simulator and gateway when they send messages.

1. In the [Azure portal](https://portal.azure.com/), search for **Subscriptions** and open the subscription that hosts your Hub. Under **Settings**, open **Resource providers**, search for `Microsoft.CloudShell`, select it and choose **Register**. Wait until its status is **Registered**.
2. Select the **Cloud Shell** (`>_`) icon in the portal's top bar. Choose **Bash**. If asked about storage, select **No storage account required** for a temporary session, choose the subscription that hosts your Hub and select **Apply**. Files and installed extensions in this session disappear when it ends.
3. Check the selected subscription and install the Azure IoT extension:

   ```bash
   az account show --output table
   az extension add --name azure-iot
   ```

   If the selected subscription is different, run `az account set --subscription "YOUR_SUBSCRIPTION_ID"` using the ID shown on your subscription page, then check again.

4. Start monitoring. Replace `YOUR_HUB_NAME` with your IoT Hub name and `YOUR_DEVICE_ID` with the ID registered in Section 2:

   ```bash
   az iot hub monitor-events --hub-name YOUR_HUB_NAME --device-id YOUR_DEVICE_ID --transport amqp_ws --timeout 0
   ```

Leave the command running while you send messages. It displays **new** messages as they arrive at the Hub's built-in endpoint. Press **Ctrl+C** when you have finished monitoring. [Monitoring Azure IoT Hub]({{ '/support/monitor-iot-hub/' | relative_url }}) also shows how to use Azure IoT Explorer or Azure CLI on your own computer.

## 4. Test with the web simulator

Open the [Raspberry Pi web simulator](https://azure-samples.github.io/raspberry-pi-web-simulator/). Its assembly area shows a simulated BME280 sensor and LED; the code area contains a sample application; the console shows its output.

1. In the simulator's code area, find the placeholder for the **device connection string** near the start of the sample. Replace it with your group's device connection string from Section 2.
2. With the Cloud Shell monitor running, select **Run** in the simulator. Watch its console for sensor readings and messages sent to IoT Hub.

![Device connection string placeholder in the simulator]({{ '/assets/images/azure/simulator-connection-string.png' | relative_url }})

![Simulator console showing messages sent to IoT Hub]({{ '/assets/images/azure/simulator-running.png' | relative_url }})

3. Return to Cloud Shell. Find a simulator message from your group's device ID. Compare one temperature or humidity value with the simulator console.
4. Refresh or close the simulator tab to stop its program before using the gateway. Keep the Cloud Shell monitor available for the next test.

The simulator gives you a working Hub-and-monitor baseline. The next section uses a record that your Feather sent to the gateway in Lab 4.

## 5. Send Lab 4 records from the gateway

On the Raspberry Pi or ROCK 4C+, open a terminal and activate the Python environment used in Lab 4:

```bash
cd ~/Documents/ee5127-ble
source .venv/bin/activate
python --version
python -m pip install wheel
python -m pip install azure-iot-device
head -n 1 near.jsonl
```

The first line of `near.jsonl` should be a complete JSON object with a `counter`. Keep that file in this folder. Download [send_gateway_telemetry.py]({{ '/assets/downloads/gateway-iot-hub/send_gateway_telemetry.py' | relative_url }}) into the same folder. Its complete code is shown below:

```python
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
```

`read_records()` selects the first five gateway records. `send_records()` sends each complete JSON object and prints its `counter`. `main()` connects using the device connection string and closes the connection when the run ends. The five-message limit keeps the test short and makes its output easy to inspect.

Copy and paste the following three commands into the **same gateway terminal**, then press Enter:

```bash
read -r -s -p "Device connection string: " IOTHUB_DEVICE_CONNECTION_STRING
printf '\n'
export IOTHUB_DEVICE_CONNECTION_STRING
```

The terminal prompts with `Device connection string:`. Copy your device's full **Primary connection string** from the Azure portal, then right-click in the gateway terminal to paste it at this prompt. The connection string will not appear on screen. Press Enter after pasting. Use the complete connection string, including `HostName`, `DeviceId` and `SharedAccessKey`.

Once the terminal returns to its usual command prompt, run the sender separately:

```bash
python send_gateway_telemetry.py
```

The gateway prints five `Sent counter:` lines and a final total when the sends finish. If the Cloud Shell monitor has stopped, run the monitoring command from Section 3 again before rerunning the sender. After the run, clear the shell variable:

```bash
unset IOTHUB_DEVICE_CONNECTION_STRING
```

## 6. Trace a gateway record into IoT Hub

Find one of the gateway counters in the Cloud Shell monitor. Compare its `nodeId`, `counter`, `temperatureC`, `humidityPct`, `pressureHpa` and `receivedAt` with the same line in `near.jsonl`. The `receivedAt` time was added by the gateway in Lab 4.

The registered IoT Hub device ID identifies the sending application on the gateway. The `nodeId` field identifies the Feather whose readings are carried in the JSON body. The simulator's messages use the same registered device ID during the first test, while their payload fields come from its simulated sensor.

## 7. Send the same records with Paho MQTT

The Azure device library in Section 5 sends its messages over MQTT. In this section the gateway sends the same five records with the Paho MQTT library directly, so you supply the connection details that the device library handled for you. Paho is already installed in `.venv`, because `azure-iot-device` depends on it.

IoT Hub accepts MQTT 3.1.1 over TLS on port 8883, but it is not a general MQTT broker. A device may publish telemetry only to its own fixed topic, `devices/{device-id}/messages/events/`. Text appended to that topic is read as message properties; here it sets the content type and encoding, which `message.content_type` and `message.content_encoding` set in Section 5. The connection uses these values:

| MQTT field | Value |
| --- | --- |
| Client ID | The device ID |
| Username | `{hub-name}.azure-devices.net/{device-id}/?api-version=2021-04-12` |
| Password | A SAS token signed with the device key |
| Topic | `devices/{device-id}/messages/events/$.ct=application%2Fjson&$.ce=utf-8` |
| QoS | 1 (IoT Hub does not accept QoS 2) |

Download [send_gateway_mqtt.py]({{ '/assets/downloads/gateway-iot-hub/send_gateway_mqtt.py' | relative_url }}) into `~/Documents/ee5127-ble`. Its complete code is shown below:

```python
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
```

`read_records()` is the same as in Section 5. `parse_connection_string()` takes the host name, device ID and key from the device connection string. `make_sas_token()` builds the password: it signs the device's resource URI and an expiry time one hour ahead with the device key, using HMAC-SHA256, so the key itself is never sent. `main()` sets the client ID, username, password and TLS settings, connects on port 8883 and publishes each record at QoS 1. It prints a counter only after IoT Hub has acknowledged that message. The certificate bundle from `certifi`, installed with the device library, contains the DigiCert root certificate that IoT Hub presents.

Do not upgrade `paho-mqtt` in this environment. The Azure device library requires a version below 2.0, and the script uses the Paho 1.x interface.

1. Check that the Section 5 sender has finished. IoT Hub keeps one MQTT connection per device identity, and a new connection closes the previous one.
2. In Cloud Shell, restart the monitor with the message properties shown:

   ```bash
   az iot hub monitor-events --hub-name YOUR_HUB_NAME --device-id YOUR_DEVICE_ID --properties sys --transport amqp_ws --timeout 0
   ```

3. In the gateway terminal, set the device connection string with the three commands from Section 5 if it is no longer set, then run:

   ```bash
   python send_gateway_mqtt.py
   ```

   The gateway prints the device ID, the topic, five `Sent counter:` lines and a final total. Clear the shell variable afterwards with `unset IOTHUB_DEVICE_CONNECTION_STRING`.

4. Find the five counters in the Cloud Shell monitor and compare one of them with the same counter from Section 5. Run `python send_gateway_telemetry.py` again with this monitor running if you want to see both senders' messages with their properties.

The message body is the same JSON record in both runs, and both runs carry the same content type, encoding and registered device ID.

## Observations and reflection

- Which value in the simulator console matched a message in the Cloud Shell monitor?
- Which gateway counter did you trace, and did every compared field match `near.jsonl`?
- Where was `receivedAt` added, and what does it tell you about the gateway's observation?
- Why do the simulator and gateway need a device connection string, while Cloud Shell uses your Azure sign-in?
- What can five successful sends establish about the gateway-to-cloud path? What would you need to observe a continuous live Feather-to-cloud stream?

## Troubleshooting and finishing

- **Hub creation or device registration is unavailable:** Check that your Azure for Students subscription is active, the region is allowed by its policy, and the selected tier is available there. Check the **Review + create** validation message and ask the TSS for help if needed.
- **None of your allowed regions offers IoT Hub:** Sign up for an [Azure free account](https://azure.microsoft.com/en-us/free/) with a different Microsoft account, and create the IoT Hub and the resources of the later labs in that subscription. The free account has no region restriction, so choose a nearby region that offers IoT Hub, and change **Tier** from the default **Standard** to **Free**, which shows a daily message limit of 8,000 at no charge. The account's credit lasts 30 days; after that, continuing to use paid services requires upgrading to pay-as-you-go, which is charged. Read Microsoft's terms on the sign-up page before you start, and plan as follows:
  - Email the module instructor to say that you will use an Azure free account in place of Azure for Students.
  - Plan the cloud work for your remaining project deliverables so that it is complete within the 30 days.
  - Set a cost alert straight after sign-up: create a monthly budget for the free account's subscription with email alerts at 50%, 90% and 100%, as described in [Azure Budget Alerts]({{ '/support/azure-budget-alert/' | relative_url }}). A budget only sends emails; resources keep running and using credit when an alert arrives.
  - Keep resources from using credit between sessions: stop the Stream Analytics job, let compute clusters scale to zero nodes, and delete any resource the lab tells you to remove.
  - Before the 30 days end, download any data you want to keep. Then delete the resource group, unless you have decided to upgrade and accept the charges.
- **The portal shows "You don't have access" for your own resources:** the portal may have opened in a different directory from the one that holds your subscription, which the error details show as "The access token is from the wrong issuer". Select the settings icon (⚙) at the top of the portal, open **Directories + subscriptions**, and select **Switch** beside **Default Directory**, or beside the directory that holds your subscription.
- **Cloud Shell does not open:** Confirm that `Microsoft.CloudShell` shows **Registered** under the subscription's **Resource providers**, then reopen Cloud Shell.
- **The monitor shows no messages:** Check the Hub name and device ID in the command. Leave it running and send new simulator messages. In the Hub's **Monitoring → Metrics**, check **Telemetry messages sent** to see whether messages reached the Hub.
- **`near.jsonl` cannot be found:** Return to `~/Documents/ee5127-ble` and check the filename from Lab 4. The sender reads five lines from that folder.
- **Python import fails:** Activate `.venv` in this terminal and run `python -m pip install azure-iot-device` again.
- **The gateway cannot connect:** Check network access, the enabled device identity and its complete device connection string. Ask the TSS to check whether the network allows the IoT Hub connection.
- **Only some counters appear in the monitor:** Start monitoring before running the sender. Rerun the same five-record file if you missed the start of the short transmission.
- **The Paho script reports that IoT Hub did not accept the connection:** Check that the complete device connection string is set in this terminal and that the network allows port 8883. A key copied incompletely produces a SAS token that IoT Hub rejects.
- **`paho.mqtt` or `certifi` cannot be imported:** Activate `.venv` in this terminal. Both packages are installed with `azure-iot-device`; reinstall it with `python -m pip install azure-iot-device` if they are missing.

Stop the simulator, the Cloud Shell monitor and the gateway programs when finished. Keep `near.jsonl`, the working senders and the IoT Hub for later cloud activities.

## References

[Azure for Students](https://azure.microsoft.com/en-us/free/students/), [Azure for Students eligibility](https://learn.microsoft.com/en-us/azure/education-hub/about-azure-for-students), [create an IoT Hub](https://learn.microsoft.com/en-us/azure/iot-hub/create-hub), [register a device identity](https://learn.microsoft.com/en-us/azure/iot-hub/create-connect-device), [Cloud Shell setup](https://learn.microsoft.com/en-us/azure/cloud-shell/get-started/ephemeral), [Azure IoT CLI monitoring](https://learn.microsoft.com/en-us/cli/azure/iot/hub#az-iot-hub-monitor-events), [Raspberry Pi web simulator](https://learn.microsoft.com/en-us/azure/iot-hub/iot-hub-raspberry-pi-kit-node-get-started), [Azure IoT Device SDK for Python](https://learn.microsoft.com/en-us/python/api/azure-iot-device/azure.iot.device.iothubdeviceclient?view=azure-python), [MQTT with IoT Hub](https://learn.microsoft.com/en-us/azure/iot/iot-mqtt-connect-to-iot-hub), [SAS tokens for devices](https://learn.microsoft.com/en-us/azure/iot-hub/authenticate-authorize-sas), [Eclipse Paho Python client 1.6.1](https://pypi.org/project/paho-mqtt/1.6.1/).
