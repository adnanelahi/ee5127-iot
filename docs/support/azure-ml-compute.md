---
title: "Azure Machine Learning Compute"
parent: Support
permalink: /support/azure-ml-compute/
---

# Azure Machine Learning Compute

Azure Machine Learning runs training jobs and notebooks on compute resources that you create or select in the studio. [Data Analytics and Machine Learning in the IoT Cloud]({{ '/labs/data-analytics-machine-learning/' | relative_url }}) uses a compute cluster, because it starts machines only while a pipeline runs. This page summarises the other kinds of compute and the situations in which each is used.

## Compute for training and development

| Compute | What it is | Typical use |
| --- | --- | --- |
| Compute cluster | A group of virtual machines of one size that Azure Machine Learning starts when a job is submitted and stops after an idle time, down to a minimum number of nodes that can be zero | Designer pipelines and training jobs that run from time to time, such as retraining a model on newly stored sensor records |
| Serverless compute | Compute that Azure Machine Learning provisions for a single job and removes afterwards, with no cluster to create or manage | Occasional jobs where you only choose a virtual machine size and do not need a persistent resource |
| Compute instance | A single virtual machine for one user, with Jupyter, JupyterLab and VS Code already installed | Writing and testing code in notebooks, exploring a dataset, and preparing scripts before running them as jobs |
| Kubernetes cluster | An Azure Kubernetes Service cluster, or a Kubernetes cluster elsewhere connected through Azure Arc, attached to the workspace | Organisations that already run Kubernetes and want to share it between training and deployed models |
| Attached compute | Existing resources, such as an Azure virtual machine or an Azure Databricks or Synapse Spark workspace, registered with the workspace | Reusing machines or data-processing platforms that a project already has, for example Spark for very large sets of stored records |

A compute instance is charged for every hour it runs, whether or not you use it, so stop it when you finish or set its idle shutdown option. A compute cluster with a minimum of zero nodes, and serverless compute, are charged only while jobs run.

Each of these can use central processing unit (CPU) or graphics processing unit (GPU) virtual machine sizes. CPU sizes suit tabular sensor data and models such as the decision trees and logistic regression used in the labs. GPU sizes, such as the NC series, are used to train neural networks on images, audio or long time series. Azure for Students has a small quota of processor cores per region and usually none for GPU sizes, so the labs use small CPU sizes.

## References

[What are compute targets in Azure Machine Learning?](https://learn.microsoft.com/en-us/azure/machine-learning/concept-compute-target), [create a compute instance](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-create-compute-instance), [create a compute cluster](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-create-attach-compute-cluster), [model training on serverless compute](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-use-serverless-compute).
