---
title: "Azure CLI on Your Computer"
parent: Support
permalink: /support/azure-cli/
---

# Azure CLI on your computer

Azure CLI lets you work with your Azure subscription from a terminal on your own computer. Sign in with the account you used for Azure for Students.

## Install on Windows

1. Open **PowerShell** and install Azure CLI with Windows Package Manager:

   ```powershell
   winget install --exact --id Microsoft.AzureCLI
   ```

2. When installation finishes, close PowerShell and open a new PowerShell window. Check that Azure CLI runs:

   ```powershell
   az version
   ```

If `winget` is unavailable, use the installer linked from Microsoft's [Azure CLI installation instructions for Windows](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows?pivots=winget). Close and reopen PowerShell after installing.

For other computers, follow Microsoft's [macOS](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-macos) or [Linux](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux) installation instructions, then use the sign-in commands below in your terminal.

## Sign in and check the subscription

1. Run:

   ```powershell
   az login
   ```

2. Complete the Microsoft sign-in window using the account linked to your Azure for Students subscription. If Azure CLI asks you to choose a subscription, select **Azure for Students**.
3. Check the selected subscription:

   ```powershell
   az account show --output table
   ```

   If it shows another subscription, list the subscriptions available to your account and select the Azure for Students subscription using its **SubscriptionId**:

   ```powershell
   az account list --output table
   az account set --subscription "YOUR_SUBSCRIPTION_ID"
   az account show --output table
   ```

If the sign-in window does not open, run `az login --use-device-code` and follow the address and code shown in the terminal. On a shared computer, run `az logout` when you finish.

The Azure IoT commands used for monitoring require the `azure-iot` extension. Install it after signing in:

```powershell
az extension add --name azure-iot
```

See [Monitoring Azure IoT Hub]({{ '/support/monitor-iot-hub/' | relative_url }}) for the command that displays incoming messages.

See Microsoft's [Azure CLI sign-in](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli-interactively) and [subscription selection](https://learn.microsoft.com/en-us/cli/azure/manage-azure-subscriptions-azure-cli) guides for more detail.
