---
title: Lab page example
parent: Labs
nav_order: 1
permalink: /labs/example/
---

# Lab N: Tutorial title
{: .no_toc }

Local template preview
{: .label .label-yellow }

This page demonstrates the tutorial layout. Replace the authoring prompts with reviewed lab content before student publication.

## On this page
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Aim

Explain what students will build or investigate, where it fits in the IoT system, and the engineering question they will explore.

## Learning outcomes

- Identify the system behaviour students will be able to explain.
- Describe the implementation or measurement they will perform.
- State the comparison or design decision they will be able to justify.

## Equipment and starting point

Name the required hardware, software and tested versions. Explain any working code, data or configuration carried forward from an earlier lab.

| Item | Purpose |
|:--|:--|
| Hardware and connections | Specify the board, cable, gateway and relevant electrical constraints. |
| Software and configuration | Specify the tools and starting state used in this lab. |

{: .warning }
Place relevant electrical, credential or resource-cost precautions beside the step where they matter.

## Practical investigation

### 1. Establish a baseline

Introduce essential setup here. Give ordered instructions and include a working example or an instructional download at the point of use.

The following Python example demonstrates code formatting using illustrative sample intervals; it does not read a physical sensor.

```python
intervals_ms = [100, 102, 99, 101, 98]
mean_ms = sum(intervals_ms) / len(intervals_ms)
spread_ms = max(intervals_ms) - min(intervals_ms)
print(f"Mean interval: {mean_ms:.1f} ms")
print(f"Peak-to-peak variation: {spread_ms} ms")
```

{: .observation }
This example prints a mean interval of 100.0 ms and a peak-to-peak variation of 4 ms. For a real measurement, explain the source of the timestamps and what the variation represents.

### 2. Change one variable

Specify a meaningful change to the baseline. Explain what stays constant, what to measure and how to compare results. Include sample counts or measurement durations only where they define the experiment.

{: .note }
Place a screenshot, diagram or explanation beside the instruction it supports. Give images descriptive alternative text and captions where needed.

### 3. Explore a failure case

Describe a safe, reversible failure to investigate. Explain the expected symptom, the diagnostic information to inspect and how to restore the working state.

## Observations and reflection

- What changed between the baseline and the modified system?
- Which measurements support your explanation?
- What limits the conclusions you can draw?

Specify any working code or data that will be useful in later labs, and explain its purpose.

## Troubleshooting

| Symptom | Check | Recovery |
|:--|:--|:--|
| Describe an observable failure | Identify a discriminating diagnostic | Give the relevant corrective action |

## Optional exploration

Offer a focused extension with a clear question. Keep the essential activity complete without this extension.

## References

Add relevant external technical documentation and required attribution. Link directly to the specific board, library, protocol or service instructions used in the lab.
