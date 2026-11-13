---
title: "Sensor Data Visualisation and Analytics on a Dashboard"
nav_order: 11
permalink: /labs/sensor-data-visualisation-analytics/
---

## Aim

Send the sensor records from the Stream Analytics job to Power BI, display them on a dashboard that updates as records arrive, and summarise them in a report with simple statistics.

## Learning outcomes

You can add a Power BI output to a Stream Analytics job, select the fields that the dashboard needs in the query, build live dashboard tiles from the streamed records, and use report visuals to calculate and check the average, minimum, maximum and count of a measurement.

## Equipment and starting point

You need:

- the IoT Hub, Stream Analytics job, storage account and container from [Streaming and Storing Sensor Data in the IoT Cloud]({{ '/labs/sensor-data-streaming-storage/' | relative_url }}), with the input `IoTHubInput` and the output `IoTHubBlobOutput`;
- the gateway with `replay_sensor_data.py` and `near.jsonl`, or a Feather streaming live records through the gateway to IoT Hub;
- your university Microsoft account, which you use to sign in to Power BI at [app.powerbi.com](https://app.powerbi.com/).

The data path in this lab, with replayed records, is:

```text
near.jsonl → gateway replay program → IoT Hub → Stream Analytics query → Power BI semantic model → dashboard and report
```

The Blob output from the storage lab stays in place, so the job continues to store every record while it sends the same records to Power BI.

Power BI is Microsoft's service for dashboards and reports. A **dashboard** is a single page of tiles; a tile built from streamed data redraws itself as records arrive. A **report** holds visuals that you build from the stored records and can filter and summarise. Stream Analytics writes the records into a **semantic model**, which is Power BI's name for a dataset with its tables and fields. Stream Analytics creates a push dataset, a kind of streaming dataset that also stores its records. Power BI lists it as a semantic model in the workspace and as a streaming dataset when you add a dashboard tile. Its live tiles update as records arrive, and its stored records can be used to build a report.

The Stream Analytics job is charged while it runs. Start it only when the steps ask you to, and stop it when you finish.

## 1. Sign in to Power BI

Open [app.powerbi.com](https://app.powerbi.com/) and sign in with your university account. Use the same account as in the Azure portal; the Stream Analytics output can then list your Power BI workspaces.

A workspace holds dashboards, reports and semantic models. **My workspace** is your personal workspace and is enough for this lab.

## 2. Add a Power BI output to the job

1. In the Azure portal, open your Stream Analytics job. Check that its status is **Stopped**; stop it if it is running.
2. Open **Job topology → Outputs**, select **+ Add output** and choose **Power BI**.

   ![Add output menu with Power BI selected, above the existing Blob output]({{ '/assets/images/sensor-data-visualisation-analytics/add-output-power-bi.png' | relative_url }}){: width="795"}

3. Use the entries below. Fill in every field first, then select **Authorize** and sign in with your university account in the window that opens. Select **Save** straight after the sign-in.

   | Field | Entry |
   | --- | --- |
   | Output alias | `PowerBIOutput` |
   | Power BI settings | **Select Power BI from your subscriptions** |
   | Group workspace | **My workspace** |
   | Authentication mode | **User token** |
   | Dataset name | `ee5127-sensor-data` |
   | Table name | `sensor-records` |

   ![Power BI output form with the alias, My workspace, User token, the dataset and table names and the Authorize button]({{ '/assets/images/sensor-data-visualisation-analytics/power-bi-output-form.png' | relative_url }}){: width="310"}

The portal fills **Output alias** with the name of your first Power BI workspace and preselects that workspace; replace both with the entries in the table. The portal shows a notice at the top of the form that the Stream Analytics Power BI output will be retired on 31 October 2027. The output works normally until that date.

**Authorize** gives the job permission to write to your Power BI workspace with your account. The job creates the semantic model and its table itself when it writes the first records, so you do not create them in Power BI. After saving, the portal tests the connection and reports **Successful connection test**, and `PowerBIOutput` appears in the outputs list beside `IoTHubBlobOutput`.

## 3. Write the query

1. Open **Job topology → Query** and replace the query with:

   ```sql
   SELECT
       nodeId,
       CAST(counter AS bigint) AS counter,
       CAST(temperatureC AS float) AS temperatureC,
       CAST(humidityPct AS float) AS humidityPct,
       CAST(pressureHpa AS float) AS pressureHpa,
       CAST(sentAt AS datetime) AS sentAt,
       EventEnqueuedUtcTime AS enqueuedAt
   INTO PowerBIOutput
   FROM IoTHubInput

   SELECT *
   INTO IoTHubBlobOutput
   FROM IoTHubInput
   ```

2. Select **Save query**.

![Query editor with the first SELECT sending named fields to PowerBIOutput and the second storing every record in IoTHubBlobOutput]({{ '/assets/images/sensor-data-visualisation-analytics/query-power-bi-output.png' | relative_url }}){: width="800"}

Power BI builds the table's columns from the first records it receives. Naming each field and its type in the query gives the table a fixed set of columns: one text column, four numbers and two times. The `CAST` functions make each number and time arrive with the same type in every record.

`enqueuedAt` is the time at which IoT Hub received each message. The dashboard uses it as the time axis, because replayed records carry the `receivedAt` time of the session in which the gateway collected them. `sentAt` is the gateway's send time added by the replay program.

## 4. Start the job and replay the records

1. On the job's **Overview** page, select **Start job**, keep **Now** and select **Start**. Wait until the status is **Running**; this takes one to two minutes.
2. In a gateway terminal, run the replay program as in the storage lab:

   ```bash
   cd ~/Documents/ee5127-ble
   source .venv/bin/activate
   python replay_sensor_data.py
   ```

3. In Power BI, open **My workspace**. Within a minute of the first record, the semantic model `ee5127-sensor-data` appears in the list.

![Workspace list with the ee5127-sensor-data semantic model and the time of its last update]({{ '/assets/images/sensor-data-visualisation-analytics/workspace-semantic-model.png' | relative_url }}){: width="800"}

Leave the job running for the dashboard section, so that you can watch the tiles update during a second replay.

## 5. Build a dashboard with live tiles

1. In your workspace, select **+ New item**, choose **Dashboard**, enter the name `EE5127 sensor dashboard` and select **Create**.
2. On the empty dashboard, select **Edit → Add a tile**.

   ![Dashboard toolbar with the Edit menu open at Add a tile]({{ '/assets/images/sensor-data-visualisation-analytics/dashboard-edit-add-tile.png' | relative_url }}){: width="660"}

3. Under **REAL-TIME DATA**, select **Custom Streaming Data**, then **Next**.

   ![Add a tile panel with the Custom Streaming Data source selected]({{ '/assets/images/sensor-data-visualisation-analytics/add-tile-custom-streaming-data.png' | relative_url }}){: width="483"}

4. Under **YOUR DATASETS**, select `ee5127-sensor-data`, then **Next**.

   ![Streaming dataset list with ee5127-sensor-data selected]({{ '/assets/images/sensor-data-visualisation-analytics/streaming-dataset-choice.png' | relative_url }}){: width="450"}

5. Design the tile with the entries below, then select **Next**:

   | Field | Entry |
   | --- | --- |
   | Visualization Type | **Line chart** |
   | Axis | `enqueuedAt` |
   | Legend | leave empty |
   | Values | `temperatureC` |
   | Time window to display | **Last** **10** **Minutes** |

   ![Tile design with enqueuedAt on the axis, temperatureC as the value and a ten-minute time window]({{ '/assets/images/sensor-data-visualisation-analytics/streaming-tile-line-chart.png' | relative_url }}){: width="448"}

6. In **Tile details**, enter the title `Temperature (°C)` and the subtitle `Last 10 minutes, by IoT Hub arrival time`, then select **Apply**.

   ![Tile details panel with the title and subtitle entered]({{ '/assets/images/sensor-data-visualisation-analytics/tile-details.png' | relative_url }}){: width="453"}

7. Repeat steps 2 to 6 for a second tile with `humidityPct` as the value and the title `Relative humidity (%)`.

A streaming tile shows the records that arrived within its time window, measured back from the current time, and redraws each time a record arrives. The unit belongs in the title, because the tile shows only the field name on its axis.

Run the replay program a second time and watch the tiles. The new records appear within a few seconds of being sent.

![Dashboard with the temperature and relative humidity tiles after two replays]({{ '/assets/images/sensor-data-visualisation-analytics/dashboard-live-tiles.png' | relative_url }}){: width="440"}

## 6. Summarise the records in a report

A report reads all the records stored in the semantic model, so the job does not need to run while you build it. Stop the job now to limit charges: on its **Overview** page, select **Stop job** and confirm.

1. In your workspace, select **More options** (**…**) beside `ee5127-sensor-data`, then **Create report**.

   ![More options menu of the semantic model with Create report at the top]({{ '/assets/images/sensor-data-visualisation-analytics/semantic-model-create-report.png' | relative_url }}){: width="800"}

2. In the **Data** pane, expand `sensor-records`. Numeric fields carry the **Σ** symbol, which means that Power BI summarises them.
3. Select an empty part of the canvas, select the **Card** visual in the **Visualizations** pane, then tick `temperatureC` in the **Data** pane. The card shows **Sum of temperatureC**.
4. Under **Value** in the **Visualizations** pane, open the menu beside **Sum of temperatureC** and choose **Average**.

   ![Value field menu listing the aggregations Sum, Average, Minimum, Maximum, Count and others]({{ '/assets/images/sensor-data-visualisation-analytics/report-aggregation-menu.png' | relative_url }}){: width="278"}

5. Add three more cards in the same way: `temperatureC` with **Minimum**, `temperatureC` with **Maximum**, and `counter` with **Count**.
6. Select an empty part of the canvas, select the **Line chart** visual, then tick `enqueuedAt` and `temperatureC`. Under **Y-axis**, change **Sum of temperatureC** to **Average**. Drag a corner of the chart to enlarge it.
7. Select **Save**, enter the name `EE5127 sensor report` and select **Save** in the dialog.

![Report with cards for the minimum, maximum and average temperature and the record count, and a line chart of average temperature against IoT Hub arrival time]({{ '/assets/images/sensor-data-visualisation-analytics/report-cards-line-chart.png' | relative_url }}){: width="800"}

Power BI adds numeric fields by default, so a new card shows the sum of all temperatures. A sum of temperatures has no physical meaning; the average, minimum and maximum describe the measurement, and the count of `counter` gives the number of records in the semantic model.

Check the statistics against the source. Compare the count with the number of records the gateway sent in all your replays, and compare the minimum and maximum with the temperatures in `near.jsonl`:

```bash
cat ~/Documents/ee5127-ble/near.jsonl
```

## Sending predictions to Power BI

If you completed [Integrating a Machine Learning Model with the IoT Data Stream]({{ '/labs/ml-model-stream-integration/' | relative_url }}), the same job can send the model's predictions to Power BI. Add a second Power BI output named `PredictionsPowerBI` with its own dataset name, such as `ee5127-predictions`, because each Power BI dataset holds a single table and two outputs must not write to the same dataset. Then replace the integration lab's query with the one below. It keeps the `Features` step, calls the model once for each record in a new `Scored` step, and sends the results from that step to both prediction outputs, while the raw records continue to go to Blob storage:

```sql
WITH Features AS (
    SELECT
        CAST(receivedAt AS datetime) AS date,
        CAST(temperatureC AS float) AS Temperature,
        CAST(humidityPct AS float) AS Humidity,
        CAST(420.0 AS float) AS Light,
        CAST(700.0 AS float) AS CO2,
        CAST(0.0048 AS float) AS HumidityRatio,
        CAST(0 AS bigint) AS Occupancy
    FROM IoTHubInput
),
Scored AS (
    SELECT date, Temperature, Humidity, udf.score(Features) AS result
    FROM Features
)

SELECT date, Temperature, Humidity, result
INTO PredictionsBlob
FROM Scored

SELECT
    date,
    Temperature,
    Humidity,
    CAST(result.[Scored Labels] AS float) AS predictedOccupancy,
    CAST(result.[Scored Probabilities] AS float) AS occupancyProbability
INTO PredictionsPowerBI
FROM Scored

SELECT *
INTO IoTHubBlobOutput
FROM IoTHubInput
```

The second statement selects the prediction fields by name; the square brackets are needed because the model's field names contain spaces. The endpoint from [Deploying a Machine Learning Model as a Web Service]({{ '/labs/ml-model-deployment/' | relative_url }}) must be **Healthy** while the job runs. Its cluster is charged for as long as it exists, so stop the job and delete the cluster when you finish.

## Observations and reflection

- After the second replay, what does each tile draw between the last record of the first replay and the first record of the second? What does that line suggest about the room during a period with no measurements?
- The report's line chart joins the same two groups of records with a curve. Where does the curve go above the maximum or below the minimum on the cards, and why can a smoothed line show values that were never measured?
- Did the count, minimum and maximum agree with the records the gateway sent? What would a difference in the count tell you about the path from the gateway to Power BI?
- Which time is on the axis of your tiles, and how would the dashboard change if it used the gateway's `receivedAt` time from the original collection session?
- In this lab the laptop's browser displays a dashboard held in the cloud. Where in the IoT reference model does the dashboard sit, and what would a user need from it to act on the data?

## Troubleshooting and finishing

- **The Group workspace list does not load and shows an error:** the Azure portal and Power BI are signed in with different accounts. Sign in to both with your university account. Alternatively, select **Provide Power BI settings manually** and enter the workspace ID, which is the part of the Power BI address after `groups/` when the workspace is open.
- **Saving the output fails with a message containing AADSTS70008:** the authorisation expired before you saved. Close the output panel without saving, open a new Power BI output, fill in every field, select **Authorize**, and select **Save** straight after the sign-in.
- **No semantic model appears in Power BI:** check that the job is **Running**, that you replayed after it started, and that the query writes to `PowerBIOutput`. Look for errors under **Monitoring → Troubleshooting** on the job's **Overview** page. The semantic model appears only after the job has written at least one record.
- **A tile stays empty:** the tile shows only records that arrived within its time window. Replay the records again while the job is running, or choose a longer time window in the tile's settings.
- **The job stops with an authentication error some days later:** Power BI authorisation expires after a period when your account uses multi-factor authentication. Stop the job, open `PowerBIOutput`, select **Renew authorization**, save, and start the job again.

When you finish:

1. Stop the Stream Analytics job.
2. Keep the Power BI output and query if you will use the dashboard again. Otherwise, restore the storage-only query and delete `PowerBIOutput`:

   ```sql
   SELECT *
   INTO IoTHubBlobOutput
   FROM IoTHubInput
   ```

3. The dashboard, report and semantic model in Power BI do not incur charges and can stay in your workspace.

## References

[Power BI output from Azure Stream Analytics](https://learn.microsoft.com/en-us/azure/stream-analytics/power-bi-output), [Real-time streaming in Power BI](https://learn.microsoft.com/en-us/power-bi/connect-data/service-real-time-streaming), [Create a report in the Power BI service](https://learn.microsoft.com/en-us/power-bi/create-reports/service-report-create-new), [Create a card visual in Power BI](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-card).
