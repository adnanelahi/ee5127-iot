---
title: "Integrating a Machine Learning Model with the IoT Data Stream"
nav_order: 10
permalink: /labs/ml-model-stream-integration/
---

## Aim

Call the deployed occupancy model from the Stream Analytics job, so that each sensor record replayed from the gateway is scored by the model and the prediction is stored in Blob Storage.

## Learning outcomes

You can add a machine-learning function to a Stream Analytics job, prepare records in the query so that they match the model's input schema, run the job, and inspect the predictions it stores.

## Equipment and starting point

You need:

- the Stream Analytics job, storage account and container from [Streaming and Storing Sensor Data in the IoT Cloud]({{ '/labs/sensor-data-streaming-storage/' | relative_url }});
- the gateway with `replay_sensor_data.py` and `near.jsonl`, or a Feather streaming live records through the gateway to IoT Hub;
- a **Healthy** endpoint from [Deploying a Machine Learning Model as a Web Service]({{ '/labs/ml-model-deployment/' | relative_url }}).

The data path in this lab, with replayed records, is:

```text
near.jsonl → gateway replay program → IoT Hub → Stream Analytics query → model endpoint → private Blob container
```

With live records, the Feather and the gateway take the place of `near.jsonl` and the replay program; the rest of the path is the same.

This lab tests that the pipeline works from end to end. The occupancy model expects `Temperature`, `Humidity`, `Light`, `CO2` and `HumidityRatio`.

Both the Stream Analytics job and the AKS cluster are charged while they run. Start the job only when the steps ask you to, and stop the job and delete the cluster when you finish.

## 1. Check the endpoint

In the Azure Machine Learning studio, open **Endpoints** and check that your endpoint's **Deployment state** is **Healthy**.

If you deleted the endpoint and cluster at the end of the deployment lab, recreate them first: follow section 4 of that lab to create the cluster, then section 5 to deploy the completed inference job to it. Together these take about 20 minutes.

## 2. Add an output for the predictions

The predictions go to the same container as the raw records, under a separate folder.

1. In the Azure portal, open your Stream Analytics job. Check that its status is **Stopped**; stop it if it is running.
2. Open **Job topology → Outputs**, select **+ Add output** and choose **Blob storage/ADLS Gen2**.
3. Use the entries below and select **Save**:

| Field | Entry |
| --- | --- |
| Output alias | `PredictionsBlob` |
| Storage account | Your storage account, for example `ee5127g001store1234` |
| Container | **Use existing**: `sensor-data` |
| Authentication mode | **Connection string** |
| Event serialization format | **JSON** |
| Format | **Line separated** |
| Encoding | **UTF-8** |
| Write mode | **Append, as results arrive** |
| Path pattern | `predictions/{date}/{time}` |
| Date format | `YYYY/MM/DD` |
| Time format | `HH` |

![Blob storage output form for PredictionsBlob: alias, storage account and container]({{ '/assets/images/ml-model-stream-integration/predictions-output-1.png' | relative_url }}){: width="400"}

![Blob storage output form for PredictionsBlob: write mode and the predictions path pattern]({{ '/assets/images/ml-model-stream-integration/predictions-output-2.png' | relative_url }}){: width="400"}

The path pattern begins with `predictions/`, so the prediction blobs sit in their own folder beside the date folders of the raw records.

## 3. Add the model as a function

A Stream Analytics function lets the query call code or a service outside the job. An **Azure ML Service** function sends records to a deployed model and returns its predictions.

1. Open **Job topology → Functions**, select **+ Add function** and choose **Azure ML Service**.

   ![Add function menu with Azure ML Service, Azure ML Studio, Javascript UDA and Javascript UDF]({{ '/assets/images/ml-model-stream-integration/add-function-menu.png' | relative_url }}){: width="790"}

2. Use the entries below and select **Save**:

| Field | Entry |
| --- | --- |
| Function alias | `score` |
| Selection | **Select Azure ML Service from your subscriptions** |
| Azure ML workspace | Your workspace, for example `ee5127-g001-mlw` |
| Deployments | Your endpoint, for example `occupancy-g001` |
| Number of parallel requests per partition | **1** |
| Max batch count | **10000** |

![Azure Machine Learning Service function form with the score alias and the loaded function signature]({{ '/assets/images/ml-model-stream-integration/ml-function-form.png' | relative_url }}){: width="429"}

When you select the deployment, the form reads the endpoint's description and shows the **Function signature** `score(input1: record) returns record`: the function takes one record and returns one record. If the form reports an error retrieving the swagger definition, the endpoint is not yet **Healthy**; wait and select the deployment again. After saving, the portal tests the connection and reports **Successful connection test**, and the function appears in the **Functions** list.

![Functions list with the score function, one parameter and record output type]({{ '/assets/images/ml-model-stream-integration/functions-list.png' | relative_url }}){: width="800"}

## 4. Write the query

1. Open **Job topology → Query** and replace the query with:

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
   )

   SELECT date, Temperature, Humidity, udf.score(Features) AS result
   INTO PredictionsBlob
   FROM Features

   SELECT *
   INTO IoTHubBlobOutput
   FROM IoTHubInput
   ```

2. Select **Save query**.

![Query editor with the Features step, the call to udf.score and the two outputs]({{ '/assets/images/ml-model-stream-integration/query-with-score.png' | relative_url }}){: width="800"}

The `WITH` step builds a record named `Features` for each message, with exactly the seven columns of the endpoint's input schema, in the names and types it expects. The first `SELECT` passes that whole record to `udf.score` and writes the date, the two measured features and the model's `result` to `PredictionsBlob`. The second `SELECT` keeps storing the raw records as before.

The record passed to the model must contain the schema columns and nothing else. If it carries an extra field, such as `counter`, the endpoint rejects the request and the job fails. The `date` column, taken from `receivedAt`, lets you match each prediction to its raw record.

**Test query** in the editor does not call the model. The function runs only in the running job.

## 5. Start the job and replay the records

1. On the job's **Overview** page, select **Start job**, keep **Now** and select **Start**. Wait until the status is **Running**.
2. In a gateway terminal, run the replay program as in the storage lab:

   ```bash
   cd ~/Documents/ee5127-ble
   source .venv/bin/activate
   python replay_sensor_data.py
   ```

   The replay program sends stored records, so the test can be repeated with the same data. In your project you can also stream records live from the Feather through the gateway to IoT Hub; the job processes them in the same way when they carry the same fields.

Stream Analytics sends the records to the endpoint in batches. Within a minute of the replay finishing, the job's **Overview** should still show **Running**, with no errors under **Monitoring → Troubleshooting**.

![Job Overview in the Running state with no recent errors and warnings under Monitoring]({{ '/assets/images/ml-model-stream-integration/job-running-no-errors.png' | relative_url }}){: width="780"}

## 6. Inspect the predictions

1. In the storage account, open **Data storage → Containers → sensor-data**. A `predictions` folder now sits beside the date folders.
2. Open `predictions` and the folders for today's date and the current UTC hour.

   ![Container listing with the prediction blob under predictions, date and hour folders]({{ '/assets/images/ml-model-stream-integration/predictions-blob-listing.png' | relative_url }})

3. Select the blob's name and open the **Edit** tab.

   ![Prediction blob Edit tab with one record per replayed message]({{ '/assets/images/ml-model-stream-integration/predictions-blob-edit.png' | relative_url }})

Each line holds `date`, `Temperature`, `Humidity` and a nested `result` record. Scroll to the end of a line to find the fields the model added:

![End of the prediction lines with Scored Labels and Scored Probabilities]({{ '/assets/images/ml-model-stream-integration/predictions-blob-scores.png' | relative_url }})

Count the lines and compare the number with the records the gateway sent. Match one prediction to its raw record by `date` and `receivedAt`.

## Observations and reflection

- How many predictions did the job store, and did every replayed record produce one?
- Which parts of each prediction line came from the sensor, which from the query and which from the model?
- Why does the query build a separate `Features` record instead of passing every field of the message to the model?
- Where else could the model run in an IoT system, for example on the gateway, and what would change?

## Troubleshooting and finishing

- **The function signature does not load:** check that the endpoint is **Healthy**, then select the deployment again in the function form.
- **The job fails after the replay:** open the job's **Activity log** and select the failed entry, for example **Process Events: Azure ML web service call error**. Its **JSON** tab includes the endpoint's response. A message that the input data are inconsistent with the schema means that the `Features` record has extra, missing or misspelt columns.
- **No predictions folder appears:** check that the job is **Running**, that you replayed after it started, and that the query writes to `PredictionsBlob`. Wait a few minutes for the output batch.

When you finish:

1. Stop the Stream Analytics job.
2. Restore the storage-only query, so that the job can run without the endpoint:

   ```sql
   SELECT *
   INTO IoTHubBlobOutput
   FROM IoTHubInput
   ```

   Save the query, then delete the `score` function. Keep or delete the `PredictionsBlob` output as you prefer.
3. Delete the endpoint and the AKS cluster as described at the end of the deployment lab.

## References

[Integrate Stream Analytics with Azure Machine Learning](https://learn.microsoft.com/en-us/azure/stream-analytics/machine-learning-udf), [Stream Analytics query language: WITH](https://learn.microsoft.com/en-us/stream-analytics-query/with-azure-stream-analytics), [Blob storage output from Stream Analytics](https://learn.microsoft.com/en-us/azure/stream-analytics/blob-storage-azure-data-lake-gen2-output).
