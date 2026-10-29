---
title: "Data Analytics and Machine Learning in the IoT Cloud"
nav_order: 8
permalink: /labs/data-analytics-machine-learning/
---

## Aim

Train a machine-learning model on sensor data in Azure Machine Learning. Build a pipeline in Azure Machine Learning designer that selects the features, splits the data, trains a classifier and evaluates it on records it has not seen.

## Learning outcomes

You can create an Azure Machine Learning workspace and a compute cluster, upload a dataset as a data asset, build and run a training pipeline in the designer, and read the evaluation results of a two-class classifier.

## Equipment and starting point

You need a browser and the Azure for Students subscription that hosts your group's IoT Hub. Create the resources in this lab in the same resource group and region as the Hub.

The worked example uses the Occupancy Detection dataset. Its records come from sensors in an office room, recorded once a minute, with an `Occupancy` label of 1 when the room was occupied and 0 when it was empty. Download [occupancy_training.csv]({{ '/assets/downloads/data-analytics-machine-learning/occupancy_training.csv' | relative_url }}) to your computer. It has 8,143 records and these columns:

| Column | Meaning |
| --- | --- |
| `date` | Time of the record |
| `Temperature` | Air temperature in °C |
| `Humidity` | Relative humidity in % |
| `Light` | Illuminance in lux |
| `CO2` | Carbon dioxide concentration in ppm |
| `HumidityRatio` | Mass of water vapour per mass of dry air, derived from temperature and humidity, in kg/kg |
| `Occupancy` | 1 for occupied, 0 for empty |

If your group has chosen a different dataset for its project, you can use it in place of the example. Prepare it as a CSV file with one header row, one column holding the value you want to predict, and numeric columns for the features. The steps below point out where your column names replace the example's.

The model in this lab predicts `Occupancy` from `Temperature`, `Humidity`, `Light`, `CO2` and `HumidityRatio`.

## 1. Create an Azure Machine Learning workspace

A workspace holds everything you create in Azure Machine Learning: data assets, compute, pipelines, trained models and endpoints. When you create one, Azure also creates a storage account for its files, a key vault for its secrets, and an Application Insights resource with a Log Analytics workspace for monitoring.

1. In the [Azure portal](https://portal.azure.com/), select **Azure Machine Learning** under **Azure services** on the home page, or type `Azure Machine Learning` in the search box at the top of the page and select it under **Services**. On the **Azure Machine Learning** page, select **+ Create**, then **New workspace**.

   ![Azure Machine Learning page with Create and New workspace]({{ '/assets/images/data-analytics-machine-learning/workspace-create.png' | relative_url }})

2. On **Basics**, use the entries below. Replace `g001` with your group ID.

| Field | Entry |
| --- | --- |
| Subscription | **Azure for Students** |
| Resource group | The resource group that holds your IoT Hub |
| Name | `ee5127-g001-mlw` |
| Region | The region of your IoT Hub |
| Storage account, Key vault, Application insights | Leave the new names that the portal proposes |
| Container registry | **None** |

![Azure Machine Learning workspace form, Basics tab]({{ '/assets/images/data-analytics-machine-learning/workspace-basics.png' | relative_url }})

The screenshot shows the names used by one group; use your own group ID.

3. Leave the settings on the other tabs at their defaults. Select **Review + create**, then **Create**. Deployment takes a few minutes.
4. When deployment finishes, select **Go to resource**, then **Launch studio**. Azure Machine Learning studio opens in a new tab.

## 2. Create a compute cluster

The designer runs each pipeline on compute in the cloud. A compute cluster starts virtual machines when a pipeline is submitted and shuts them down after a set idle time, so it uses subscription credit only while pipelines run.

1. In the studio, open **Compute** in the left menu (under **Manage**), select the **Compute clusters** tab and select **+ New**.
2. On **Virtual Machine**, use the entries below and select **Next**:

| Field | Entry |
| --- | --- |
| Location | The region of your workspace |
| Virtual machine tier | **Dedicated** |
| Virtual machine type | **CPU** |
| Virtual machine size | **Select from recommended options**, then **Standard_F4s_v2** (4 cores, 8 GB RAM) |

![Create compute cluster, Virtual Machine page with Standard_F4s_v2 selected]({{ '/assets/images/data-analytics-machine-learning/compute-cluster-vm.png' | relative_url }})

Standard_F4s_v2 has the lowest hourly cost of the recommended sizes, and its 4 cores and 8 GB of memory are ample for a dataset of a few thousand rows. The **Available quota** column shows how many cores of each family your subscription can still use in this region.

3. On **Advanced Settings**, use the entries below and select **Create**:

| Field | Entry |
| --- | --- |
| Compute name | `cpu-cluster` |
| Minimum number of nodes | `0` |
| Maximum number of nodes | `1` |
| Idle seconds before scale down | `120` |

![Create compute cluster, Advanced Settings page with the name and node settings]({{ '/assets/images/data-analytics-machine-learning/compute-cluster-settings.png' | relative_url }})

A minimum of 0 nodes lets the cluster shut down completely when no pipeline is running. The cluster shows **Succeeded** when it has been created; it starts a node only when you submit a pipeline.

## 3. Upload the dataset as a data asset

A data asset gives a dataset a name and a version in the workspace, so that pipelines can refer to it. The designer's classic components read tabular data assets created with the Azure ML v1 dataset types.

1. In the studio, open **Data** (under **Assets**) and select **+ Create** on the **Data assets** tab.
2. On **Data type**, enter the name `occupancy-training`. Open the **Type** list and choose **Tabular**, listed under **Dataset types (from Azure ML v1 APIs)**. Select **Next**.

   ![Create data asset, Data type page with the name occupancy-training and the type Tabular]({{ '/assets/images/data-analytics-machine-learning/data-asset-type.png' | relative_url }})

3. On **Data source**, choose **From local files** and select **Next**.

   ![Create data asset, Data source page with From local files selected]({{ '/assets/images/data-analytics-machine-learning/data-asset-source.png' | relative_url }})

4. On **Destination storage type**, keep **Azure Blob Storage** and the datastore **workspaceblobstore**, which is the workspace's default storage, and select **Next**.

   ![Create data asset, Destination storage type page with workspaceblobstore selected]({{ '/assets/images/data-analytics-machine-learning/data-asset-datastore.png' | relative_url }})

5. On **File or folder selection**, select **Upload files or folder → Upload files**, choose `occupancy_training.csv`, wait until the **Upload list** shows the file with a green tick, and select **Next**.

   ![Create data asset, File or folder selection page with occupancy_training.csv uploaded]({{ '/assets/images/data-analytics-machine-learning/data-asset-upload.png' | relative_url }})

6. On **Settings**, the portal detects the format of the file. Check that **File format** is **Delimited**, **Delimiter** is **Comma**, **Column headers** is **All files have same headers**, and that the **Data preview** shows the seven columns. Select **Next**.

   ![Create data asset, Settings page with the detected format and the data preview]({{ '/assets/images/data-analytics-machine-learning/data-asset-settings.png' | relative_url }})

7. On **Schema**, check the detected column types: `date` as **Date**, the five sensor columns as **Decimal**, and `Occupancy` as **Integer**. Leave the extra **Path** column switched off. Select **Next**.

   ![Create data asset, Schema page with the detected column types]({{ '/assets/images/data-analytics-machine-learning/data-asset-schema.png' | relative_url }})

8. On **Review**, check the summary and select **Create**.

The new data asset opens on its **Details** tab. Select **Explore** to see the first records; the page reports 7 columns and 8,143 rows. If you use your own dataset, give the asset your own name and check its columns in the same way.

![The occupancy-training data asset, Explore tab with the first records]({{ '/assets/images/data-analytics-machine-learning/data-asset-explore.png' | relative_url }})

## 4. Build the training pipeline

1. In the studio, open **Designer**. On the **Classic prebuilt** tab, select **Create a new pipeline using classic prebuilt components**. An empty canvas opens, with the asset library on its left.

   ![Designer page with the option to create a pipeline using classic prebuilt components]({{ '/assets/images/data-analytics-machine-learning/designer-new-pipeline.png' | relative_url }})

2. Add the components below to the canvas and connect them as listed. Find the dataset on the **Data** tab of the asset library and each component on its **Component** tab, using the search box, and drag it onto the canvas. Each component has input ports at the top and output ports at the bottom; drag from an output port to an input port to connect them.

| Component | Connect its input from | Purpose |
| --- | --- | --- |
| `occupancy-training` (data asset) | — | The uploaded records |
| **Select Columns in Dataset** | the data asset | Keeps the features and the label |
| **Split Data** | Select Columns in Dataset | Divides the records into a training set and a test set |
| **Two-Class Logistic Regression** | — | The untrained classifier |
| **Train Model** | left input: Two-Class Logistic Regression; right input: the left output of Split Data | Fits the classifier to the training set |
| **Score Model** | left input: Train Model; right input: the right output of Split Data | Predicts the label for each test record |
| **Evaluate Model** | left input: Score Model | Compares the predictions with the true labels |

![The connected occupancy pipeline from the data asset to Evaluate Model]({{ '/assets/images/data-analytics-machine-learning/designer-pipeline-connections.png' | relative_url }})

Use the zoom controls under the canvas, or drag an empty part of the canvas, if the pipeline does not fit in view. The **Collapse left panel** arrow (**«**) at the top of the asset library hides it when you need more room.

3. Configure the components. Double-click a component on the canvas to open its settings panel, and close the panel with the arrow in its top-right corner.

- **Select Columns in Dataset:** select **Edit column**. Keep **With rules** and **Include** → **Column names**, type `Temperature,Humidity,Light,CO2,HumidityRatio,Occupancy` in the box and press Enter, so that each name appears as a tag. Select **Save**. The `date` column is left out. The time of a record would let the model learn the office timetable, and this model is meant to learn the relation between the sensor readings and occupancy.

  ![Select columns dialog with the five features and Occupancy as tags]({{ '/assets/images/data-analytics-machine-learning/designer-select-columns.png' | relative_url }})

- **Split Data:** set **Fraction of rows in the first output dataset** to `0.7`, keep **Randomized split** at **True** and set **Random seed** to `1`. Seventy per cent of the records go to the left output for training, and the rest go to the right output for testing. A fixed seed makes the split the same each time the pipeline runs.

  ![Split Data settings panel with the fraction 0.7 and random seed 1]({{ '/assets/images/data-analytics-machine-learning/designer-split-data.png' | relative_url }})

- **Two-Class Logistic Regression:** leave the default settings. Logistic regression calculates a weighted sum of the features and converts it into a probability between 0 and 1 that the room is occupied.
- **Train Model:** select **Edit column** under **Label column**, type `Occupancy`, press Enter and select **Save**. This is the column the model learns to predict.

  ![Label column dialog of Train Model with Occupancy selected]({{ '/assets/images/data-analytics-machine-learning/designer-label-column.png' | relative_url }})

If you use your own dataset, select your feature and label columns in **Select Columns in Dataset** and your label in **Train Model**. A label with more than two values needs a multiclass component, such as **Multiclass Logistic Regression**, in place of the two-class one; a numeric quantity to predict needs a regression component, such as **Linear Regression**.

4. Check that no component shows a red warning icon. A warning usually means an unconnected input or a missing setting.

## 5. Submit the pipeline

1. Select **Configure & Submit** above the canvas. The **Set up pipeline job** panel opens.
2. On **Basics**, select **Create new** under **Experiment name** and enter `occupancy-classifier`. An experiment groups the runs of a pipeline so that you can compare them later. Select **Next**.

   ![Set up pipeline job, Basics page with the new experiment occupancy-classifier]({{ '/assets/images/data-analytics-machine-learning/submit-basics.png' | relative_url }})

3. On **Inputs & outputs**, there is nothing to set. Select **Next**.
4. On **Runtime settings**, keep **Compute cluster** as the compute type and select `cpu-cluster` under **Select Azure ML compute cluster**. Keep **workspaceblobstore** as the datastore. Select **Next**.

   ![Set up pipeline job, Runtime settings page with cpu-cluster selected]({{ '/assets/images/data-analytics-machine-learning/submit-runtime-settings.png' | relative_url }})

5. On **Review + Submit**, check the summary and select **Submit**. A message confirms that the pipeline job has been submitted.
6. Open **Jobs** in the left menu, select the `occupancy-classifier` experiment and then the newest job to follow its progress. Each component turns green when it completes.

The first run takes longer than later ones, because the cluster has to start a node and prepare its software. Allow 10 to 20 minutes.

## 6. Inspect the results

When the job shows **Completed** and every component has a green tick:

![The completed pipeline job with a green tick on every component]({{ '/assets/images/data-analytics-machine-learning/job-completed.png' | relative_url }})

1. Right-click **Score Model** and select **Preview data → Scored dataset**. Select the expand icon at the top right of the panel to see all the columns.

   ![Right-click menu of Score Model with Preview data and Scored dataset]({{ '/assets/images/data-analytics-machine-learning/score-preview-menu.png' | relative_url }})

   The scored dataset holds the test records, 30% of the data, with two extra columns: **Scored Labels**, the predicted class, and **Scored Probabilities**, the model's probability that the room is occupied. A record is predicted as occupied when its probability is 0.5 or more. Compare **Scored Labels** with `Occupancy` for several records, and look for a record where they differ.

   ![Scored dataset with the Occupancy, Scored Labels and Scored Probabilities columns]({{ '/assets/images/data-analytics-machine-learning/scored-dataset.png' | relative_url }})

2. Close the panel. Right-click **Evaluate Model** and select **Preview data → Evaluation results**, then expand the panel.

   ![Right-click menu of Evaluate Model with Preview data and Evaluation results]({{ '/assets/images/data-analytics-machine-learning/evaluate-preview-menu.png' | relative_url }})

   The results show the ROC, precision-recall and lift curves, a **Threshold** slider, the metrics and the confusion matrix for the chosen threshold:

   ![Evaluation results with the curves, the threshold slider, the metrics and the confusion matrix]({{ '/assets/images/data-analytics-machine-learning/evaluation-results.png' | relative_url }})

| Metric | Meaning |
| --- | --- |
| Accuracy | Fraction of test records predicted correctly |
| Precision | Of the records predicted occupied, the fraction that were occupied |
| Recall | Of the occupied records, the fraction predicted occupied |
| F1 score | Harmonic mean of precision and recall |
| AUC | Area under the ROC curve; 1 means the probabilities separate the two classes perfectly, and 0.5 means they separate them no better than chance |

In the confusion matrix, the columns are the actual classes and the rows are the predicted classes. A false positive is an empty room predicted as occupied; a false negative is an occupied room predicted as empty. Move the **Threshold** slider and watch how the metrics and the confusion matrix change. Consider which of the two errors would matter more if the model controlled the lighting or heating of the room.

## 7. Keep your work

The completed pipeline job holds the trained model in the output of **Train Model**. Keep the workspace, the `occupancy-training` data asset and the completed job in the `occupancy-classifier` experiment for later labs.

The compute cluster scales down to zero nodes 120 seconds after the pipeline finishes, so it needs no action to stop it. In **Compute → Compute clusters**, its state shows **Resizing (1 -> 0 nodes)** and then **Succeeded**; check that it has reached zero nodes before you leave.

## Observations and reflection

- How many records were in the training set and the test set? Check the outputs of **Split Data**.
- What were the accuracy, precision and recall of your model? How many false positives and false negatives did the confusion matrix show?
- About 21% of the records in the example dataset are labelled occupied. What accuracy would a model reach by predicting "empty" for every record, and how does your model compare with that?
- The records were taken once a minute, so neighbouring records are very similar. With a randomised split, many test records have a near-identical neighbour in the training set. How might this affect the accuracy you measured?

## Troubleshooting

- **The workspace cannot be created in your region:** check that the region is allowed by your subscription's policy and offers Azure Machine Learning, as you checked for IoT Hub. Ask the demonstrator before choosing a region that differs from your Hub's.
- **No virtual machine size can be selected, or the cluster fails with a quota error:** Azure for Students limits the number of processor cores per region. Choose a smaller size, or ask the demonstrator.
- **The data asset does not appear in the designer:** check that you chose the **Tabular** type from the v1 dataset types when creating it, and refresh the **Data** list in the designer.
- **A column cannot be found in Select Columns in Dataset or Train Model:** open the data asset's **Explore** tab and copy the exact column name; names are case-sensitive.
- **The pipeline cannot be submitted:** check that every component input is connected, every component has its required settings, and the compute cluster is selected in **Settings**.
- **The pipeline stays in the queue or the first component waits for a long time:** the cluster is starting a node. Check the cluster's state under **Compute**; a first start can take several minutes.
- **A component fails:** select it, open **Outputs + logs** and read the error at the end of the log.

## References

[What is an Azure Machine Learning workspace?](https://learn.microsoft.com/en-us/azure/machine-learning/concept-workspace), [create an Azure Machine Learning compute cluster](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-create-attach-compute-cluster), [designer component reference](https://learn.microsoft.com/en-us/azure/machine-learning/component-reference/component-reference), [Two-Class Logistic Regression component](https://learn.microsoft.com/en-us/azure/machine-learning/component-reference/two-class-logistic-regression), [Evaluate Model component](https://learn.microsoft.com/en-us/azure/machine-learning/component-reference/evaluate-model).

The example data is the Occupancy Detection dataset by Luis Candanedo, from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/357/occupancy+detection), doi:[10.24432/C5X01N](https://doi.org/10.24432/C5X01N), licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). `occupancy_training.csv` is the dataset's training file with its row-number column removed. The dataset is described in L. M. Candanedo and V. Feldheim, "Accurate occupancy detection of an office room from light, temperature, humidity and CO2 measurements using statistical learning models," *Energy and Buildings*, vol. 112, pp. 28–39, 2016.
