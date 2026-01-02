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

# Creative Performance Deep Dive

Victoria performs a granular analysis of creative assets to identify fatigue, top performers, and optimization opportunities. This goes beyond simple "best creative" lists to look at format efficiency, size performance, and wear-out trends.

## Overview & Philosophy

Creative is often the biggest lever in performance. This protocol answers:
- "Which creatives are worn out?"
- "What format (Video vs. Display) is driving efficient scale?"
- "Which specific message resonates with this audience?"

## Analysis Steps

### 1. Classification & Aggregation
*   **Dimensions:** Creative ID, Creative Name, Ad Format (Video, Display, Native), Ad Size (300x250, etc.), Concept/Theme (parsed from name if possible).
*   **Metrics:** Spend, Impressions, Clicks, Conversions, CTR, CVR, CPA, Video Completion Rate (VCR).

### 2. Fatigue Analysis
*   **Trend Line:** Analyze CTR over the last 14 days for top spending creatives.
*   **Decay Detection:** Flag creatives where CTR has declined by > 20% week-over-week while spend remained constant or increased.
*   **Recommendation:** "Pause - Fatigued" or "Rotate".

### 3. Format & Size Analysis
*   **Size Efficiency:** Compare CPA across sizes (e.g., 300x250 vs 728x90). often 300x600s have higher CTR but higher CPM. Is the CPA efficient?
*   **Format Battle:** Video vs. Display. Calculate the "premium" paid for video (CPM difference) vs. the lift in conversion rate.

### 4. Head-to-Head (A/B) Check
*   If multiple concepts are running simultaneously, calculate statistical significance of performance differences (e.g., "Concept A is 95% likely to be better than Concept B").

## Output Generation

### Gamma Presentation
Generate a "Creative Review" deck for the creative team or client.

```python
# Gamma presentation for Creative Review
gamma.generate_standard_presentation(
    input_text="""
    # Creative Performance Review

    ## Executive Summary
    - **Top Performer:** 'Holiday_Promo_Video_A' (CPA $12.50)
    - **Fatigue Warning:** 'Evergreen_Banner_300x250' has seen CTR drop 30% this week.
    - **Format Insight:** Video is driving 40% lower CPA than Display.

    ## Creative Fatigue Analysis
    [Insert Data Table of Waning Performers]

    ## Format Performance
    [Insert Bar Chart: CPA by Format]

    ## Recommendations
    1. Swap out 'Evergreen_Banner' assets.
    2. Shift 20% budget from Display to Video.
    """
)
```

### Action List (Terminal/Email)
*   **PAUSE:** List of creative IDs to pause immediately.
*   **BOOST:** List of creative IDs to increase priority/bid.
