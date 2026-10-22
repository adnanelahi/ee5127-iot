---
title: "Monitoring Azure IoT Hub"
parent: Support
permalink: /support/monitor-iot-hub/
---

# Monitoring Azure IoT Hub

Start a monitor before sending new messages to IoT Hub. The sender uses a **device connection string** containing `DeviceId=`. A monitor reads messages from the Hub's built-in endpoint. [Lab 5]({{ '/labs/gateway-iot-hub-telemetry/' | relative_url }}) uses Azure CLI in Cloud Shell; the methods below run on your own computer.

## Azure IoT Explorer

1. Install [Azure IoT Explorer](https://github.com/Azure/azure-iot-explorer/releases) for your computer's operating system.
2. In the [Azure portal](https://portal.azure.com/), open your IoT Hub. Under **Security settings → Shared access policies**, create a policy named `ee5127-monitor` with **Service Connect** and **Registry Read** permissions. Copy its **Primary connection string**. This **IoT Hub monitoring connection string** contains `SharedAccessKeyName=ee5127-monitor` and gives Explorer access to list devices and read incoming messages. Keep it private.
3. Open IoT Explorer, choose **Connect via IoT Hub connection string** if prompted, select **Add connection**, paste the monitoring string and select **Save**.
4. Select the device that sends telemetry. Open **Telemetry**, check that **Use built-in event hub** is **Yes** and **Consumer group** is `$Default` if those settings are shown, then select **Start**.
5. Send new messages from the device. They should appear under **Telemetry**. Select **Stop** when finished.

The simulator and gateway use the **device connection string** from **Device management → Devices**. IoT Explorer uses the **IoT Hub monitoring connection string** from **Shared access policies** because it reads messages for the Hub.

## Azure CLI installed on your computer

On Windows, open **PowerShell** and install Azure CLI:

```powershell
winget install --exact --id Microsoft.AzureCLI
```

Close PowerShell, reopen it, and check the installation with `az version`. If `winget` is unavailable, use Microsoft's [Windows installer instructions](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows?pivots=winget). For macOS or Linux, use Microsoft's [macOS](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-macos) or [Linux](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux) installation guide.

Sign in with the account that hosts the Hub, check its selected subscription, and install the Azure IoT extension:

```powershell
az login
az account show --output table
az extension add --name azure-iot
```

If another subscription is selected, use `az account list --output table` to find the Azure for Students **SubscriptionId**, then run `az account set --subscription "YOUR_SUBSCRIPTION_ID"`. If the sign-in window does not open, try `az login --use-device-code`. See [Azure CLI on Your Computer]({{ '/support/azure-cli/' | relative_url }}) for the full installation and sign-in steps.

Start monitoring. Replace `YOUR_HUB_NAME` and `YOUR_DEVICE_ID` with the values from your Hub:

```powershell
az iot hub monitor-events --hub-name YOUR_HUB_NAME --device-id YOUR_DEVICE_ID --transport amqp_ws --timeout 0
```

Leave this command running while the simulator or gateway sends **new** messages. Press **Ctrl+C** to stop. The CLI uses your Azure sign-in to access the Hub; the sender still uses its device connection string.

If the monitor shows no messages, check that the Hub and device IDs match the sender. In the Azure portal, **IoT Hub → Monitoring → Metrics → Telemetry messages sent** shows whether the Hub has received telemetry; the metric can take a few minutes to update.

For more detail, see Microsoft's [IoT Explorer tutorial](https://learn.microsoft.com/en-us/azure/iot-hub/tutorial-routing), [IoT Hub access permissions](https://learn.microsoft.com/en-us/azure/iot-hub/authenticate-authorize-sas), and [`az iot hub monitor-events` reference](https://learn.microsoft.com/en-us/cli/azure/iot/hub#az-iot-hub-monitor-events).
