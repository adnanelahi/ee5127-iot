---
title: Home
nav_order: 1
permalink: /
---

# EE5127 Internet of Things

## Laboratory tutorials

Explore how sensor nodes, wireless links, gateways and cloud services work together in an Internet of Things system.

These laboratories are unassessed practical activities. Use the investigations to test your assumptions, compare results and develop engineering judgement. Keep working code and data when they are needed in a later lab.

## Table of contents

{% assign lab_pages = site.pages | where_exp: "item", "item.path contains 'labs/'" | sort: "nav_order" %}
{% for lab in lab_pages %}
{% unless lab.name == "index.md" %}
  - [{{ lab.title }}]({{ lab.url | relative_url }})
{% endunless %}
{% endfor %}

- [Support]({{ '/support/' | relative_url }})
