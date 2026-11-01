---
title: "Azure Budget Alerts"
nav_exclude: true
permalink: /support/azure-budget-alert/
---

# Azure Budget Alerts

A budget in Azure Cost Management compares the charges of a subscription with an amount you choose and emails you when the charges reach set percentages of it. Set one up as soon as you start using an Azure free account, so that you learn early if a resource is using credit.

A budget only sends emails. Resources keep running and using credit when an alert arrives, so stop or delete them yourself.

## 1. Open Budgets for your subscription

1. In the [Azure portal](https://portal.azure.com/), search for **Subscriptions** and select your free account's subscription, for example **Azure subscription 1**.
2. In the subscription's menu, open **Cost Management → Budgets**. Check that **Scope** shows your subscription, then select **+ Add**.

![Budgets page of the subscription, with Cost Management and Budgets in the menu and the subscription as the scope]({{ '/assets/images/azure/budget-subscription-budgets.png' | relative_url }}){: width="800"}

Opening **Budgets** from the subscription sets the scope for you. If you search for **Cost Management** instead, the page may open with your billing account as the scope.

## 2. Create the budget

On the **Create a budget** tab, wait until the page has finished loading; text typed earlier can be cleared when the form reloads. Then use the entries below and select **Next**.

| Field | Entry |
| --- | --- |
| Name | `ee5127-monthly-budget` |
| Reset period | **Monthly** |
| Creation date and Expiration date | Leave the dates the portal proposes |
| Amount | A monthly amount you are prepared to spend, for example `20` |

![Create a budget tab with the name, monthly reset period, dates and amount]({{ '/assets/images/azure/budget-create.png' | relative_url }}){: width="424"}

The amount is in the currency of your account, shown on the **Set alerts** tab as **Amount (EUR)** for a euro account.

## 3. Set the alerts

1. Under **Alert conditions**, set **Type** to **Actual cost** and **% of budget** to `50`. A new empty row appears; fill it with **Actual cost** and `90`, and the next one with **Actual cost** and `100`. The **Amount** column shows each threshold in your currency.
2. Under **Alert recipients (email)**, enter your email address. Until a recipient is entered, each row shows the message "Action group or at least one email address is required".
3. Select **Create**.

![Set alerts tab with Actual cost alerts at 50, 90 and 100 per cent of the budget]({{ '/assets/images/azure/budget-set-alerts.png' | relative_url }}){: width="800"}

The budget appears in the **Budgets** list. Its evaluation begins a few hours after creation, and charges take several hours to reach Cost Management, so an alert can arrive some time after the charges pass a threshold. Add `azure-noreply@microsoft.com` to your email allow list so that the alerts are not filtered as spam.

## References

[Tutorial: Create and manage budgets](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets).
