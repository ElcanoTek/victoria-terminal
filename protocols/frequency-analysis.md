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

# Frequency Analysis

Victoria analyzes the relationship between frequency (how often a user sees an ad) and performance (conversion rate). This helps determine the optimal frequency cap.

## Overview & Philosophy

Showing an ad too few times = missed opportunity. Too many times = annoyed user and wasted money.
-   **Goal:** Find the "Sweet Spot".
-   **Metric:** Conversion Rate by Frequency Bucket (1, 2-3, 4-6, 7-10, 10+).

## Analysis Steps

### 1. Bucket Performance
*   Group conversions and impressions by unique user frequency count.
*   Calculate CPA for each bucket.

### 2. The Diminishing Returns Curve
*   Identify the point where CPA starts to rise significantly.
*   *Example:* CPA is steady at $10 for freq 1-5, but jumps to $25 for freq 6+.
*   **Optimal Cap:** 5 impressions per day (or week).

## Output Generation

### Frequency Recommendation Chart (Gamma)
A visualization of the curve.

```python
gamma.generate_standard_presentation(
    input_text="""
    # Optimal Frequency Analysis

    ## The Sweet Spot
    - **Findings:** Users converting most efficiently between 3-5 exposures.
    - **Waste:** 20% of budget is spent on users with 10+ frequency, where CPA is 3x higher.

    ## Recommendation
    - **Implement Frequency Cap:** 6 per day per user.
    - **Expected Savings:** 15% of budget reallocated to new users.
    """
)
```
