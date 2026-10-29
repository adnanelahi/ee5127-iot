---
title: "Streaming and Storing Sensor Data in the IoT Cloud"
nav_order: 7
permalink: /labs/sensor-data-streaming-storage/
---

## Aim

Stream the Feather sensor records from the gateway through Azure IoT Hub to an Azure Stream Analytics job, and store them in a private Blob Storage container. Then use the timestamps added along the path to measure how long each stage takes.

## Learning outcomes

You can create a storage account and a private container, configure a Stream Analytics job with an IoT Hub input, a Blob Storage output and a query, replay gateway records with a send time, and calculate the delay from the gateway to IoT Hub and from IoT Hub to Stream Analytics from the stored records.

## Equipment and starting point

You need the IoT Hub, the registered device identity and the gateway prepared in [Gateway Telemetry to Azure IoT Hub]({{ '/labs/gateway-iot-hub-telemetry/' | relative_url }}). On the gateway, keep `near.jsonl` and the Python environment `.venv` in `~/Documents/ee5127-ble`. The `azure-iot-device` library installed in that environment is used again here.

If you are working in a group, use the Azure for Students subscription that hosts your group's IoT Hub, and work together on the account holder's computer for the portal steps. Create every resource in this lab in the same resource group and region as the Hub. Keep connection strings private.

The data path in this lab is:

```text
near.jsonl → gateway replay program → IoT Hub → Stream Analytics query → private Blob container
```

Each stored record carries three times that describe its journey. The gateway adds `sentAt` just before sending the record. IoT Hub adds `EventEnqueuedUtcTime` when the message arrives at the Hub. Stream Analytics adds `EventProcessedUtcTime` when the job reads the message. The `receivedAt` time in `near.jsonl` was recorded when the gateway collected the record from the Feather, which was during an earlier session, so this lab measures delay with `sentAt`.

Stream Analytics charges your subscription credit for every hour the job runs. Start the job only when the steps below ask you to, and stop it when you finish.

## 1. Check the gateway clock

The delay from the gateway to IoT Hub compares the gateway's clock with the Hub's clock. Azure services keep their clocks synchronised, and the gateway synchronises its clock over the network with the Network Time Protocol (NTP). Check that synchronisation is active in a gateway terminal:

```bash
timedatectl
```

The output should include `System clock synchronized: yes`. If it shows `no`, check the gateway's network connection, then make the time service contact its server again:

```bash
sudo systemctl restart systemd-timesyncd
timedatectl
```

Within a few seconds, `timedatectl` should report `System clock synchronized: yes`. A gateway clock that is a few tens of milliseconds out adds the same error to every gateway-to-Hub delay you measure.

## 2. Create a storage account and a private container

A storage account holds Azure data services; a container inside it holds files, which Azure calls blobs. Stream Analytics will write the sensor records as blobs in your container.

1. In the [Azure portal](https://portal.azure.com/), select **+ Create a resource**, then **Storage account**. You can also search the Marketplace for **Storage account**.
2. On **Basics**, use the entries below. Replace `g001` with your group ID.

| Field                | Entry                                                                                                               |
| -------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Subscription         | **Azure for Students**                                                                                              |
| Resource group       | `ee5127-g001-rg`, the group that holds your IoT Hub                                                                 |
| Storage account name | `ee5127g001store1234` (3–24 lowercase letters and digits; change the final digits to make the name globally unique) |
| Region               | The region of your IoT Hub                                                                                          |
| Primary service      | **Azure Blob Storage or Azure Data Lake Storage**                                                                   |
| Primary workload     | **General purpose**                                                                                                 |
| Performance          | **Standard**                                                                                                        |
| Redundancy           | **Locally redundant storage (LRS)**                                                                                  |

![Create a storage account, Basics tab: project details]({{ '/assets/images/sensor-data-streaming-storage/storage-account-basics-project.png' | relative_url }})

![Create a storage account, Basics tab: instance details down to redundancy]({{ '/assets/images/sensor-data-streaming-storage/storage-account-basics-instance.png' | relative_url }})

3. Leave the settings on the other tabs at their defaults. Select **Review + create**, check that validation succeeds, then select **Create**. When deployment finishes, select **Go to resource**.

4. In the storage account, open **Data storage → Containers** and select **+ Add Container**.
5. Enter the name `sensor-data`, keep the anonymous access level at **Private (no anonymous access)**, and select **Create**.

A private container accepts requests only from users and services that hold permission for the storage account. Your sensor records therefore stay inaccessible to anyone who finds the account name.

## 3. Add a consumer group to the IoT Hub

IoT Hub keeps incoming messages at its built-in endpoint for a period of time. Each program that reads them does so through a named consumer group, and each consumer group receives every message. The Cloud Shell monitor uses the `$Default` group. Give the Stream Analytics job its own group so that the job and the monitor can read the same messages at the same time.

1. In your IoT Hub, open **Hub settings → Built-in endpoints**.
2. Under **Consumer Groups**, enter `streamanalytics` in the **Create new consumer group** box. The portal saves the group automatically, and it then appears below `$Default`.

![IoT Hub built-in endpoint with the streamanalytics consumer group]({{ '/assets/images/sensor-data-streaming-storage/iot-hub-consumer-groups.png' | relative_url }})

The **Retain for** setting shows how long the Hub keeps messages at the built-in endpoint; on the Free tier it is one day. A reader that starts later can still read messages sent within that period.

## 4. Create a Stream Analytics job

A Stream Analytics job reads messages from one or more inputs, applies a query written in a language similar to SQL, and writes the results to one or more outputs.

1. Select **+ Create a resource** and search the Marketplace for **Stream Analytics job**. On its Marketplace page, check that **Subscription** shows **Azure for Students** and **Plan** shows **Stream Analytics job**, then select **Create**.

   ![Stream Analytics job Marketplace page with the subscription and plan]({{ '/assets/images/sensor-data-streaming-storage/stream-analytics-marketplace.png' | relative_url }})

2. Use the entries below:

| Field | Entry |
| --- | --- |
| Subscription | **Azure for Students** |
| Resource group | `ee5127-g001-rg` |
| Name | `ee5127-g001-asa` |
| Region | The region of your IoT Hub |
| Hosting environment | **Cloud** |
| Streaming units | **1** |

![New Stream Analytics job form, Basics tab]({{ '/assets/images/sensor-data-streaming-storage/stream-analytics-job-basics.png' | relative_url }})

A streaming unit is the amount of computing capacity allocated to the job. One unit is ample for one gateway's records, and the job is charged for its streaming units only while it runs.

3. Leave the other tabs at their defaults. Select **Review + create**, then **Create**. When deployment finishes, select **Go to resource**.

The job is created in the **Stopped** state. Keep it stopped while you configure its input, output and query.

## 5. Configure the IoT Hub input

1. In the job, open **Job topology → Inputs**, select **+ Add input** and choose **IoT Hub**.
2. Use the entries below and select **Save**:

| Field | Entry |
| --- | --- |
| Input alias | `IoTHubInput` |
| IoT Hub | Select your Hub from your subscriptions |
| Consumer group | `streamanalytics` |
| Shared access policy name | **service** |
| Endpoint | **Messaging** |
| Event serialization format | **JSON** |
| Encoding | **UTF-8** |

The portal fills in the shared access policy key for you. The **service** policy lets the job read messages from the Hub. The input alias is the name the query uses for this input.

## 6. Configure the Blob output

1. Open **Job topology → Outputs**, select **+ Add output** and choose **Blob storage/ADLS Gen2**.
2. Use the entries below and select **Save**:

| Field | Entry |
| --- | --- |
| Output alias | `IoTHubBlobOutput` |
| Storage account | Select `ee5127g001store1234` from your subscriptions |
| Container | Use existing: `sensor-data` |
| Authentication mode | **Connection string** |
| Event serialization format | **JSON** |
| Format | **Line separated** |
| Encoding | **UTF-8** |
| Write mode | **Append, as results arrive** |
| Path pattern | `{date}/{time}` |
| Date format | `YYYY/MM/DD` |
| Time format | `HH` |

![Blob storage output form: alias, storage account, container and authentication]({{ '/assets/images/sensor-data-streaming-storage/stream-analytics-blob-output-1.png' | relative_url }})

![Blob storage output form: write mode, path pattern and time formats]({{ '/assets/images/sensor-data-streaming-storage/stream-analytics-blob-output-2.png' | relative_url }})

Leave **Minimum rows** and **Maximum time** empty, so that the job uses its default batching. The portal fills in the storage account key for you, so the key stays inside Azure. The path pattern makes the job start a new blob each hour, in folders named after the date and hour, and **Line separated** writes one JSON record per line. **Append, as results arrive** adds each batch of records to the current blob as soon as the batch is ready, so stored records appear within minutes.

## 7. Prepare the replay program on the gateway

The replay program sends every record in `near.jsonl` to IoT Hub at the interval at which the Feather produced them. Just before each send, it adds a `sentAt` field holding the gateway's UTC time to the millisecond.

On the gateway, open a terminal and activate the environment:

```bash
cd ~/Documents/ee5127-ble
source .venv/bin/activate
wc -l near.jsonl
```

`wc -l` reports the number of records in `near.jsonl`. Download [replay_sensor_data.py]({{ '/assets/downloads/sensor-data-streaming-storage/replay_sensor_data.py' | relative_url }}) into the same folder. Its complete code is shown below:

```python
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
```

`read_records()` reads every record in the file. `sampling_interval()` divides the time between the first and last `receivedAt` values by the number of gaps between records, which gives the average interval at which the gateway received them. `send_records()` schedules record *n* for *n* intervals after the start, using `time.monotonic()`, so records leave at the original interval even though `send_message()` waits for IoT Hub to acknowledge each message. It copies each record and adds `sentAt` immediately before `send_message()`. The message content type and encoding tell IoT Hub and Stream Analytics that the body is UTF-8 JSON, which lets the job read its fields.

Set the device connection string in the **same gateway terminal**, as in the previous lab:

```bash
read -r -s -p "Device connection string: " IOTHUB_DEVICE_CONNECTION_STRING
printf '\n'
export IOTHUB_DEVICE_CONNECTION_STRING
```

Paste the device's full **Primary connection string** at the prompt and press Enter. Then run the program once, so that Stream Analytics has recent messages to show in the next section:

```bash
python replay_sensor_data.py
```

The gateway prints the interval it uses, then one `Sent counter:` line with its `sentAt` time for each record, and a final total. The output has this form; your times and number of records will differ:

```text
Replaying 15 records, one every 2.0 s
Sent counter: 1 at 2026-10-29T21:44:50.512+00:00
Sent counter: 2 at 2026-10-29T21:44:52.512+00:00
Sent counter: 3 at 2026-10-29T21:44:54.513+00:00
...
Sent counter: 15 at 2026-10-29T21:45:18.514+00:00
Sent 15 records to IoT Hub.
```

If you want to see the records arrive, start the Cloud Shell monitor from the previous lab before running the program. Each message now includes `sentAt`.

## 8. Write and test the query

1. In the Stream Analytics job, open **Job topology → Query**.
2. Replace the example query with:

   ```sql
   SELECT *
   INTO IoTHubBlobOutput
   FROM IoTHubInput
   ```

3. Select **Save query**.
4. Select `IoTHubInput` in the list of inputs. The **Input preview** tab shows a sample of recent messages from the Hub. If it is empty, run the replay program again and refresh the preview.
5. Select **Test query** and inspect the **Test results** tab.

   ![Stream Analytics query with test results showing the replayed records]({{ '/assets/images/sensor-data-streaming-storage/stream-analytics-query-test-results.png' | relative_url }})

`SELECT *` passes every field of each message to the output. Compare the columns in the test results with the fields of a record in `near.jsonl`. Widen the `receivedAt` and `sentAt` columns by dragging their header edges and compare the dates: `receivedAt` is the day you collected the records from the Feather, and `sentAt` is today. The extra columns, such as `EventEnqueuedUtcTime`, `EventProcessedUtcTime`, `PartitionId` and `IoTHub`, are added by IoT Hub and Stream Analytics. Open the `IoTHub` value of one row and find `ConnectionDeviceId`: it is the device identity that sent the message, which you registered in the previous lab.

The test runs on the sample only. It writes nothing to the container, and its `EventProcessedUtcTime` values record when you ran the test. Measure delays from the records the running job stores, in section 11.

## 9. Start the job and replay the records

1. On the job's **Overview** page, select **Start job**.
2. For **Job output start time**, select **Now**, then select **Start**.
3. Wait until the job status changes to **Running**. This can take a few minutes.

   The job page may show a message that diagnostic settings have not been configured. Diagnostic settings send the job's logs to a further Azure service; this lab uses the **Activity log** and the job's metrics instead, so leave the message as it is.

4. In the gateway terminal, run the replay program again:

   ```bash
   python replay_sensor_data.py
   ```

5. Note the first and last `sentAt` times that the gateway prints.

With the output start time **Now**, the job processes messages that reach IoT Hub after it starts. The records you sent before starting the job remain outside the stored output.

## 10. Inspect the stored records

Stream Analytics collects output records into batches before writing them to Blob Storage, so the first blob can appear a few minutes after the last record was sent.

1. In the storage account, open **Data storage → Containers → sensor-data**.
2. Open the folders for today's date and the current UTC hour, such as `2026 → 10 → 29 → 22`. Note the blob's **Last modified** time and size. Select **Refresh** after a minute: while the job runs, it appends new batches to the same blob, and both values grow.

   ![Container listing with the date and hour folders and one blob]({{ '/assets/images/sensor-data-streaming-storage/blob-container-listing.png' | relative_url }})

3. Select the blob's name. Its panel opens on the **Overview** tab.
4. Select the **Edit** tab, next to **Snapshots**, to view the blob's contents. Close the panel without saving. **Download** in the panel's toolbar saves a copy, which you can open in a text editor.

   ![Blob Edit tab showing one stored JSON record per line]({{ '/assets/images/sensor-data-streaming-storage/blob-edit-view.png' | relative_url }})

Each line of the blob is one JSON record. The lines are wider than the panel, so scroll right to see `sentAt` and the fields added by IoT Hub and Stream Analytics. Count the lines and compare the number with the records the gateway sent. Find one counter from the replay and compare its `nodeId`, sensor readings and `receivedAt` with the same line in `near.jsonl`. Check that `sentAt` lies within the range of times the gateway printed.

## 11. Measure the delays

Each stored record holds three times, which divide its journey into two stages:

- **gateway to IoT Hub:** `EventEnqueuedUtcTime − sentAt`, the time to send the message over the network and for IoT Hub to accept it; and
- **IoT Hub to Stream Analytics:** `EventProcessedUtcTime − EventEnqueuedUtcTime`, the time the message waited at the Hub before the job read and processed it.

1. In the blob panel, select **Download** and save the file. Open it in a text editor such as VS Code.
2. Choose one record and find its `counter`, `sentAt`, `EventEnqueuedUtcTime` and `EventProcessedUtcTime`. Check that its `sentAt` matches the time the gateway printed for the same counter.
3. Calculate both delays for that record by hand. All three times are in UTC. `sentAt` has three decimal places of seconds, and the Azure times have seven.
4. Repeat the calculation for the first and the last record in the file.

A few records show the size of each delay. To describe the delays of the whole replay, calculate both delays for every record in the file and summarise them, for example with their minimum, median and maximum. Decide how to do this systematically and reliably. Your method has to read each line of the file, interpret timestamps written with different precision and time-zone notation, and handle any line that lacks `sentAt`.

Compare the two delays. The gateway-to-Hub delay depends on the network path and on the agreement between the gateway clock and the Hub clock, so a value close to zero, or slightly negative, indicates a clock offset of that size. The IoT Hub-to-Stream Analytics delay depends on how often the job reads from the Hub. Then compare the blob's **Last modified** time with the latest `EventProcessedUtcTime` in the file. That difference is the time the record waited in the job's output batch before the blob was written.

## 12. Send records while the job is stopped

1. On the job's **Overview** page, select **Stop job** and wait until the status is **Stopped**.
2. Run `python replay_sensor_data.py` on the gateway and note the `sentAt` time of the first record.
3. Start the job with the output start time **Now**. Wait for **Running** and a few minutes more, then list the blobs again and look for records with that `sentAt` time.
4. Stop the job again, then start it with the output start time **When last stopped**. Wait, then list the blobs and look for the same records.

IoT Hub keeps the messages sent while the job was stopped. The output start time selects which of them the job processes: **Now** begins with messages arriving after the start, and **When last stopped** continues from the point where the job stopped. Records sent while the job was stopped show a larger IoT Hub-to-Stream Analytics delay when you analyse them, because that delay includes the time the job was stopped.

When you finish, stop the job and clear the device connection string from the gateway terminal:

```bash
unset IOTHUB_DEVICE_CONNECTION_STRING
```

## Observations and reflection

- How many records did the replay send, and did every counter appear in the stored blob?
- Which fields in the stored records came from the Feather, which from the gateway, which from IoT Hub and which from Stream Analytics?
- What were the median gateway-to-Hub and Hub-to-Stream Analytics delays? Which stage contributes most to the time between the gateway sending a record and that record being stored?
- What does a negative or near-zero gateway-to-Hub delay tell you about the two clocks involved?
- Why does this lab measure delay from `sentAt`, and what would `receivedAt` measure if the gateway forwarded records as soon as it collected them from the Feather?
- Which output start time would you choose for a deployed system that must store every record, and why?

Keep the storage account, the container with its stored records, the Stream Analytics job and `replay_sensor_data.py`. Later labs add a machine-learning function to this job and visualise the stored records.

## Troubleshooting and finishing

- **`timedatectl` reports that the clock is unsynchronised:** check the gateway's network connection and wait a minute. Ask the demonstrator if the university network blocks NTP.
- **The storage account name is rejected:** use only lowercase letters and digits, 3 to 24 characters, and change the final digits until the name is unique.
- **The consumer group cannot be saved:** check that you are on the **Built-in endpoints** page of your Hub and that the name contains only letters, digits, hyphens, periods and underscores.
- **The input preview is empty:** run the replay program and refresh the preview. Check that the input uses your Hub, the `streamanalytics` consumer group and the **service** policy.
- **The job does not start:** open **Activity log** on the job, and check the input and output with **Test** on their pages.
- **No blob appears:** confirm that the job status is **Running** and that you replayed the records after it started. Wait a few minutes for the output batch, and check the output's container name and path pattern.
- **The gateway cannot connect:** check the device connection string in this terminal and the network, as in the previous lab.

Stop the Stream Analytics job before you leave. A stopped job keeps its input, output and query and incurs no streaming charge. Keep the IoT Hub, storage account and job for the later labs.

## References

[Create a storage account](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-create), [manage blob containers in the portal](https://learn.microsoft.com/en-us/azure/storage/blobs/blob-containers-portal), [IoT Hub built-in endpoint and consumer groups](https://learn.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-messages-read-builtin), [create a Stream Analytics job in the portal](https://learn.microsoft.com/en-us/azure/stream-analytics/stream-analytics-quick-create-portal), [stream data as input into Stream Analytics](https://learn.microsoft.com/en-us/azure/stream-analytics/stream-analytics-define-inputs), [Blob storage output from Stream Analytics](https://learn.microsoft.com/en-us/azure/stream-analytics/blob-storage-azure-data-lake-gen2-output), [test a Stream Analytics query with sample data](https://learn.microsoft.com/en-us/azure/stream-analytics/stream-analytics-test-query), [start a Stream Analytics job](https://learn.microsoft.com/en-us/azure/stream-analytics/start-job), [Stream Analytics pricing](https://azure.microsoft.com/en-us/pricing/details/stream-analytics/).
