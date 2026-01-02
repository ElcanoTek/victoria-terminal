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

# Quarterly Business Review (QBR) Prep

Victoria prepares the comprehensive dataset and narrative for a Quarterly Business Review. This is a strategic deep-dive, looking at macro trends over 3 months.

## Overview & Philosophy

A QBR is not just a big weekly report. It's about **Strategy** and **Partnership**.
-   **Focus:** "What did we learn this quarter?" and "What is the plan for next quarter?"
-   **Scope:** All campaigns for a specific client over the last 90 days.

## Analysis Steps

### 1. The Macro View
*   **Total Investment:** $ Spend.
*   **Total Return:** ROAS / Conversions.
*   **Year-over-Year (YoY) Growth:** Compare Q3 2025 vs Q3 2024.

### 2. The Strategic Pillars
Analyze performance against specific strategic themes:
*   **Audience Growth:** Did we reach new users? (New % vs Returning %).
*   **Creative Innovation:** Did the new video assets work?
*   **Platform Diversification:** How did the test on CTV perform?

### 3. Benchmarking
*   Compare Client performance vs. Industry Benchmarks (if available) or internal agency benchmarks.

## Output Generation

### The QBR Deck (Gamma)
A high-polish presentation.

```python
gamma.generate_standard_presentation(
    input_text="""
    # Q3 2025 Quarterly Business Review
    ## Client: Acme Corp

    ## Executive Summary
    - **Record Quarter:** Highest conversion volume in history (+15% YoY).
    - **Efficiency:** CPA decreased by 10% despite rising CPMs.
    - **Key Driver:** Successful launch of Connected TV campaigns.

    ## Strategic Pillar: Video Expansion
    - [Chart: Video Spend vs. Search Interest]
    - Insight: Video campaigns drove a 20% lift in branded search volume.

    ## Q4 Planning & Roadmap
    - **Goal:** Capture holiday demand.
    - **Strategy:** Scale CTV, launch dynamic creative optimization (DCO).
    - **Budget Request:** +20% investment to maximize Q4 peak.
    """
)
```

### The Data Pack (Excel/CSV)
A clean, consolidated raw data file for the client's internal analytics team.
