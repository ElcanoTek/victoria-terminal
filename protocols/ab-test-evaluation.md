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

# A/B Test Evaluation

Victoria performs a rigorous statistical evaluation of head-to-head campaign tests. This protocol replaces "gut feel" with math.

## Overview & Philosophy

Did Strategy A *really* beat Strategy B, or was it just luck?
-   **Methodology:** Statistical Significance (Confidence Intervals).
-   **Use Case:** Creative A vs B, Landing Page A vs B, Audience A vs B.

## Analysis Steps

### 1. Define the Groups
*   **Control Group:** Strategy A (Baseline).
*   **Test Group:** Strategy B (Challenger).

### 2. Statistical Test (Chi-Squared or Z-Test)
*   Calculate Conversion Rate (CVR) for both.
*   Calculate Standard Error.
*   Determine **Confidence Level** (e.g., 90%, 95%, 99%).

### 3. "Winner" Declaration
*   **Statistically Significant:** "Strategy B is the winner with 95% confidence."
*   **Inconclusive:** "Not enough data yet. Continue testing."

## Output Generation

### Test Result Memo (Email/Terminal)

**Subject:** 🧪 Test Results: Video vs. Display

**Winner:** 🏆 VIDEO

**Details:**
*   **Display (Control):** 0.12% CVR (120 conv / 100k imps)
*   **Video (Test):** 0.18% CVR (180 conv / 100k imps)
*   **Lift:** +50%
*   **Significance:** 99.9% (Very Strong)

**Recommendation:**
*   Conclude test. Roll out Video strategy to all ad groups.
