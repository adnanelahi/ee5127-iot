---
title: "Deploying a Machine Learning Model as a Web Service"
nav_order: 9
permalink: /labs/ml-model-deployment/
---

## Aim

Deploy the occupancy classifier trained in [Data Analytics and Machine Learning in the IoT Cloud]({{ '/labs/data-analytics-machine-learning/' | relative_url }}) as a real-time web service, and send it test records over HTTP to check that it returns predictions.

## Learning outcomes

You can convert a designer training pipeline into a real-time inference pipeline, create a Kubernetes inference cluster, deploy the pipeline to it as an endpoint, and call the endpoint with a key-authenticated HTTP request.

## Equipment and starting point

You need the Azure Machine Learning workspace, the compute cluster `cpu-cluster` and the completed training pipeline job from the previous lab. If you trained a model on your own dataset, use that pipeline; the field names in the test request then follow your dataset.

To test the endpoint you need [Postman](https://www.postman.com/downloads/), an application that sends HTTP requests and shows the responses. Install it on your computer before the lab.

A deployed model answers requests through an endpoint, which runs on compute of its own. In this lab the endpoint runs on a small Azure Kubernetes Service (AKS) cluster. The cluster is charged for every hour it exists, whether or not requests arrive, so finish the lab in one session and delete the cluster at the end, or keep it only until you complete the integration lab.

## 1. Create a real-time inference pipeline

A training pipeline reads the whole dataset, splits it and trains a model. A real-time inference pipeline reuses the trained model to score one request at a time. The designer builds the inference pipeline from the completed training job.

1. In the studio, open **Pipelines**, select the **Pipeline jobs** tab and open your completed training job.
2. In the job's toolbar, select **…**, then **Create inference pipeline**, then **Real-time inference pipeline**.

   ![Completed training job toolbar with the Create inference pipeline submenu open]({{ '/assets/images/ml-model-deployment/create-inference-pipeline-menu.png' | relative_url }}){: width="800"}

The designer opens a new pipeline draft named after the training job, with **real time inference** at the end. It replaces the training components with the trained model, saved as a model data asset whose name begins with `MD-`, and adds a **Web Service Output**.

![Inference pipeline as created, with the model data asset, Score Model, Web Service Output and Evaluate Model]({{ '/assets/images/ml-model-deployment/inference-pipeline-created.png' | relative_url }})

## 2. Edit the inference pipeline

The draft still reads from the training data asset and has no input for requests, so a deployed service would ignore the data it receives. Make three changes:

1. Open the asset library with **»**, search for **Web Service Input** and drag it onto the canvas. Connect its output, **Web service input data**, to the **Dataset** input of **Select Columns in Dataset**, beside the connection from the data asset.
2. Select **Evaluate Model** and press **Delete**. A web service returns predictions; evaluation belongs to training.
3. Open **Select Columns in Dataset**, select **Edit column** and remove `Occupancy` with its **×**, so that only the five sensor features remain. Select **Save**.

   ![Select columns dialog with the five feature columns and Occupancy removed]({{ '/assets/images/ml-model-deployment/inference-select-columns.png' | relative_url }}){: width="771"}

The edited pipeline sends each request through **Select Columns in Dataset** to **Score Model**, and returns the scored records through **Web Service Output**.

![Edited inference pipeline with Web Service Input connected to Select Columns in Dataset]({{ '/assets/images/ml-model-deployment/inference-pipeline-edited.png' | relative_url }})

The data asset stays connected because the web service takes the names and types of its input columns from it. Requests must therefore contain every column of the data asset, including `date` and `Occupancy`, even though the pipeline removes `Occupancy` before scoring.

## 3. Submit the inference pipeline

The designer offers deployment only for an inference pipeline that has run once.

1. Select **Configure & Submit**.
2. On **Basics**, choose **Select existing** and the experiment you used for training, for example `occupancy-classifier`.
3. On **Runtime settings**, keep **Compute cluster** and `cpu-cluster`, as in the training lab.
4. Select **Review + Submit**, then **Submit**.

The job takes about 10 minutes, most of it while the cluster starts a node. Open the job from the notification, or from **Jobs**, and select **Refresh** until its status is **Completed**. The toolbar of the completed job then shows **Deploy**.

![Completed inference job with Deploy in the toolbar]({{ '/assets/images/ml-model-deployment/inference-job-deploy-button.png' | relative_url }})

## 4. Create a Kubernetes inference cluster

1. Open **Compute** in the left menu and select the **Kubernetes clusters** tab.
2. Select **+ New**, then **AksCompute**.

   ![Kubernetes clusters tab with the + New menu showing AksCompute]({{ '/assets/images/ml-model-deployment/kubernetes-clusters-new-akscompute.png' | relative_url }})

3. On **Virtual Machine**, keep **Create new**, select the region of your workspace under **Location**, search for **Standard_D2s_v3** and select it. Select **Next**.

   ![Create AksCompute, Virtual Machine page with Standard_D2s_v3 selected]({{ '/assets/images/ml-model-deployment/aks-virtual-machine.png' | relative_url }})

4. On **Advanced Settings**, use the entries below and select **Create**:

| Field | Entry |
| --- | --- |
| Compute name | `aks-g001` (replace `g001` with your group ID) |
| Cluster purpose | **Dev-test** |
| Number of nodes | **1** |
| Network configuration | **Basic** |
| Enable SSL configuration | Off |

![Create AksCompute, Advanced Settings page with Dev-test and one node]({{ '/assets/images/ml-model-deployment/aks-advanced-settings.png' | relative_url }})

The form opens with **Production** and three nodes, which would use more processor cores than an Azure for Students subscription allows. **Dev-test** permits a single node. Move the **Number of nodes** slider to the left end, or select it and press the left arrow key, until it shows 1. Standard_D2s_v3 has two cores and 8 GB of memory, which is ample for one small model.

Creating the cluster takes 10 to 15 minutes. Select **Refresh** until its state is **Succeeded**.

![Kubernetes clusters tab with the new cluster in the Succeeded state]({{ '/assets/images/ml-model-deployment/aks-cluster-succeeded.png' | relative_url }})

## 5. Deploy the real-time endpoint

1. Return to the completed inference job from section 3 and select **Deploy**.
2. In **Set up real-time endpoint**, keep **Deploy new real-time endpoint** and use the entries below. Leave the **Advanced** settings at their defaults and select **Deploy**.

| Field | Entry |
| --- | --- |
| Name | `occupancy-g001` |
| Compute type | **AksCompute** |
| Compute name | Your cluster, for example `aks-g001` |

![Set up real-time endpoint with AksCompute and the new cluster selected]({{ '/assets/images/ml-model-deployment/deploy-aks-form.png' | relative_url }}){: width="560"}

The **Compute type** list also offers **Azure Container Instance**. Use **AksCompute**: deployments to Azure Container Instance did not complete in Azure for Students subscriptions when this lab was prepared.

The first deployment builds a container image for the model, which takes up to 15 minutes; later deployments reuse it. Follow progress in the notifications (the bell icon). The message **Deployment "occupancy-g001" creation completed** marks the end; a failure is also reported there.

## 6. Inspect the endpoint

1. Open **Endpoints**, select the **Real-time endpoints** tab and open your endpoint.
2. On **Details**, check that **Deployment state** is **Healthy** and **Compute type** is **AksCompute**.

   ![Endpoint Details tab with the Healthy deployment state]({{ '/assets/images/ml-model-deployment/aks-endpoint-details.png' | relative_url }}){: width="800"}

3. Open the **Consume** tab. It shows the **REST endpoint**, the address that receives requests, and a **Primary key** and **Secondary key** for authentication.

   ![Endpoint Consume tab with the REST endpoint and the masked primary and secondary keys]({{ '/assets/images/ml-model-deployment/endpoint-consume-tab.png' | relative_url }}){: width="780"}

The **Test** tab reports that testing in the studio is not supported for this deployment, because the designer deploys with an earlier version of the Azure Machine Learning interface. Test the endpoint with Postman instead.

The endpoint uses plain HTTP, and every request must carry one of the keys. Keep the keys private, as you keep device connection strings private.

## 7. Test the endpoint with Postman

1. Open Postman and select **File → New**, then **HTTP**. A new request tab opens.
2. Open the method list on the left of the address bar, which shows **GET**, and choose **POST**. Paste the **REST endpoint** from the **Consume** tab into the address bar.
3. Open the **Authorization** tab below the address bar. Set **Auth Type** to **Bearer Token**, copy the **Primary key** with the copy icon on the **Consume** tab, and paste it into **Token**.

   ![Postman request with POST, the REST endpoint and Bearer Token selected on the Authorization tab, with the address and token hidden]({{ '/assets/images/ml-model-deployment/postman-authorization.png' | relative_url }}){: width="800"}

4. Open the **Body** tab, select **raw**, and change the list at the end of that row from **Text** to **JSON**. Postman then sends the request as JSON. Paste this request into the editor:

   ```json
   {
     "Inputs": {
       "input1": [
         {"date": "2015-02-04T17:51:00Z", "Temperature": 23.18, "Humidity": 27.272, "Light": 426.0, "CO2": 721.25, "HumidityRatio": 0.0047930, "Occupancy": 0},
         {"date": "2015-02-05T03:00:00Z", "Temperature": 20.5, "Humidity": 26.0, "Light": 0.0, "CO2": 440.0, "HumidityRatio": 0.0039, "Occupancy": 0}
       ]
     },
     "GlobalParameters": {}
   }
   ```

5. Select **Send**.

A successful call returns status **200 OK**, shown above the response pane. The response holds one entry under `Results → WebServiceOutput0` for each record you sent, with the five features the model used and two fields the model added.

![Postman Body tab with the JSON request and the 200 OK response with Scored Labels and Scored Probabilities for both records]({{ '/assets/images/ml-model-deployment/postman-request-response.png' | relative_url }}){: width="800"}

`Scored Labels` is the predicted class, 1 for occupied and 0 for empty, and `Scored Probabilities` is the model's estimate of the probability that the room is occupied. The first record describes an office with the lights on, which the model labels occupied with a probability of about 0.60, and the second the same office at night, which it labels empty with a probability of about 0.01. Change the values of `Light` and `CO2` and send the request again to see how the prediction responds.

The endpoint's request format is published as an OpenAPI (Swagger) description at the REST endpoint address with `score` replaced by `swagger.json`. Open that address in a browser to see the required fields and their types.

## Observations and reflection

- Which fields does the request require, and why must it include `date` and `Occupancy` when the model does not use them?
- What do `Scored Labels` and `Scored Probabilities` tell you about a record, and how does the probability change as you vary `Light` and `CO2`?
- What protects the endpoint from unauthorised requests, and what risk does plain HTTP add?
- Why is the endpoint charged while no requests arrive?

## Troubleshooting and finishing

- **Create inference pipeline is missing:** open the completed training job, not the pipeline draft, and look under **…** in the job's toolbar.
- **Deploy is missing:** submit the edited inference pipeline and wait until its job is **Completed**.
- **The cluster cannot be created:** check that **Cluster purpose** is **Dev-test** with one node, and that the **Available quota** column shows enough cores for the chosen size. Ask the Teaching Support Staff (TSS) if no size fits your quota.
- **The endpoint stays Transitioning:** open the notifications; a failed deployment is reported there even when the endpoint page has not updated.
- **Postman returns 401 Unauthorized:** copy the key again with the copy icon beside **Primary key**, and check that **Authorization** is set to **Bearer Token**.
- **Postman returns 400 Bad Request:** check that every record contains all seven fields with the spelling shown in the Swagger description.

If you continue with the integration lab in the same session, keep the endpoint and the cluster. Otherwise delete both now:

1. In **Endpoints**, select your endpoint and select **Delete**.
2. In **Compute → Kubernetes clusters**, select your cluster and select **Delete**. **Detach** removes the cluster from the workspace but leaves it running and charging.

The registered model, the inference pipeline and the workspace's container registry, which holds the model's image, remain at little or no cost. The integration lab explains how to recreate the cluster and endpoint.

## References

[Use the designer to deploy no-code models](https://learn.microsoft.com/en-us/previous-versions/azure/machine-learning/tutorial-designer-automobile-price-deploy?view=azureml-api-1), [create and attach Azure Kubernetes Service](https://learn.microsoft.com/en-us/previous-versions/azure/machine-learning/how-to-create-attach-kubernetes?view=azureml-api-1), [create a client for a model deployed as a web service](https://learn.microsoft.com/en-us/previous-versions/azure/machine-learning/how-to-consume-web-service?view=azureml-api-1), [Postman](https://www.postman.com/downloads/).
