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

# Audience Insight Analysis

Victoria analyzes audience segment performance to identify high-value users and targeting inefficiencies. This protocol answers: "Who is actually buying our product?"

## Overview & Philosophy

Audience data is often fragmented. This protocol looks at performance *by segment* and identifies overlaps.
- **Goal:** Refine targeting to improve efficiency.
- **Key Insight:** Finding "Hidden Gem" audiences with low CPA but low scale.

## Analysis Steps

### 1. Segment Performance Ranking
*   **Rank:** Sort all targeted 1st and 3rd party segments by CPA and ROAS.
*   **Identify:**
    *   **Stars:** High Volume, Low CPA.
    *   **Dogs:** High Spend, High CPA.
    *   **Hidden Gems:** Low Volume, Low CPA (Scale these!).

### 2. Overlap Analysis (If Data Available)
*   Check if the same users are being targeted in multiple Line Items.
*   *Warning Sign:* High frequency without high conversion rate often implies overlapping targeting strategies competing against each other.

### 3. Cost Analysis
*   Calculate the "Data Tax" (CPM fee for the audience data).
*   Is the expensive "Auto Intender" segment ($2.50 CPM data fee) actually performing better than the generic "News Reader" segment ($0.50 data fee) *after* factoring in the cost?

## Output Generation

### Audience Deck (Gamma)
A visual presentation of the "Ideal Customer Profile".

```python
# Gamma presentation for Audience Insights
gamma.generate_standard_presentation(
    input_text="""
    # Audience Performance Deep Dive

    ## Who is Converting?
    - **Top Segment:** "In-Market for Luxury SUVs" (CPA $45)
    - **Surprise Segment:** "DIY Home Improvement" (CPA $52)

    ## Data Cost Efficiency
    - **Recommendation:** Cut "Generic Auto" segment. The $1.50 data fee makes the CPA inefficient ($85).

    ## Strategic Shift
    - Shift budget from broad demographic targeting (Age 25-54) to behavioral segments.
    """
)
```

### Optimization List
*   **Exclude:** List of underperforming segments to remove.
*   **Bid Up:** Segments to increase bid modifiers on.
