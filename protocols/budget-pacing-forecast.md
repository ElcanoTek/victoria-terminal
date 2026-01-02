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

# Budget Pacing & Forecast

Victoria projects month-end spend based on current run rates and recommends daily cap adjustments. This ensures campaigns deliver in full without overspending.

## Overview & Philosophy

Pacing is the #1 stressor for traders.
-   **Goal:** "Soft Landing" (hitting exactly 100% of budget).
-   **Math:** Linear projection with day-of-week weighting (optional).

## Analysis Steps

### 1. The Projection
*   **Formula:** `Spend to Date + (Avg Daily Spend * Days Remaining)`
*   **Weighted:** Adjust for weekends if historical data shows lower spend on Sat/Sun.

### 2. The Gap Analysis
*   **Budget:** $100,000
*   **Projected Spend:** $90,000
*   **Gap:** -$10,000 (Underspend Risk)

### 3. The Adjustment Calculation
*   "To hit $100k, you need to increase daily spend from $3,000/day to $3,500/day."

## Output Generation

### Pacing Table (Terminal)
A clear table showing exactly what to change.

| Campaign | Budget | Spent % | Days Left | Current Status | Rec. Daily Cap |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Brand Awareness | $50k | 45% | 15 | 🟢 On Track | Maintain $1.6k |
| Retargeting | $20k | 20% | 15 | 🔴 Under | Increase to $1.0k |

### Action Script
"I can update these daily caps for you via the API if you approve." (Future capability hook).
