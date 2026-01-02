<!--
Copyright (c) 2025 ElcanoTek

This file is part of Victoria Terminal.

This software is licensed under the Business Source License 1.1.
You may not use this file except in compliance with the license.
You may obtain a copy of the license at

    https://github.com/ElcanoTek/victoria-terminal/blob/main/LICENSE

Change Date: 2027-09-20
Change License: GNU General Public License v3.0 or later

License Notes: 2025-12-30
-->

# Supply Path Optimization (SPO)

Victoria analyzes the efficiency of different paths to the same inventory. It answers: "Which Exchange/SSP is the most efficient way to buy NYTimes.com?"

## Overview & Philosophy

The same impression is often available via multiple exchanges (e.g., Google AdX, Magnite, PubMatic, OpenX). Prices and fees vary.
-   **Goal:** Consolidate spend on the most efficient paths.
-   **Metric:** "Effective CPM" (eCPM) and Win Rate.

## Analysis Steps

### 1. Publisher x Exchange Pivot
*   **Group By:** Publisher (or Domain) AND Exchange (Supply Source).
*   **Metrics:** eCPM, CPA, Win Rate.

### 2. Efficiency Comparison
For top 20 domains:
*   Identify all exchanges selling that domain.
*   Compare average eCPM.
*   *Example:* CNN.com is $5.00 on Exchange A and $4.50 on Exchange B.

### 3. "Take Rate" Estimation
*   If Win Rates are similar but CPMs differ, the higher CPM path likely has higher fees (tech tax).

## Output Generation

### SPO Recommendation Table
A list of "Path Preferences" to implement.

| Domain | Preferred Path | Avoid Path | Savings Est. |
| :--- | :--- | :--- | :--- |
| cnn.com | Magnite | Google AdX | 10% |
| weather.com | Index | OpenX | 5% |

### Implementation Guide
"To implement: Update Supply Source targeting on Line Items targeting these domains to exclude the 'Avoid' paths."
