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

# Daily Health Check Protocol

Victoria can perform a rapid, automated morning health check across all active campaigns. This protocol is designed to be the "first cup of coffee" routine for traders—identifying pacing issues, zero-spend anomalies, and significant performance drops before they become emergencies.

## Overview & Philosophy

The Daily Health Check is not a deep dive; it is a **triage system**.
- **Speed is key:** The goal is to scan everything quickly.
- **Exception-based:** Only surface what needs attention. If a campaign is running fine, it doesn't need to be in the main alert list.
- **Proactive:** Catch "zero delivery" issues within 24 hours.

## Analysis Steps

### 1. Data Collection
*   **Timeframe:** Look at "Yesterday" vs. "Day Before Yesterday" (DoD) and "Last 7 Days" trend.
*   **Scope:** ALL active campaigns (status = Active/Live).

### 2. The Checklist (Automated Checks)

Victoria will check for the following specific conditions:

**A. The "Zero" Checks (Critical Severity)**
*   **Zero Spend:** Campaigns marked "Active" that spent $0 yesterday.
*   **Zero Conversions:** Campaigns with >$500 spend yesterday but 0 conversions.
*   **Zero Impressions:** Active campaigns with 0 impressions (indicates potential creative rejection or bid floor issues).

**B. Pacing Alarms (High Severity)**
*   **Under-pacing:** Campaigns < 80% of daily flight budget or pacing to underspend total budget by > 10%.
*   **Over-pacing:** Campaigns > 120% of daily cap (if flexible) or risking premature exhaustion.

**C. Performance Drops (Medium Severity)**
*   **CPA Spike:** Daily CPA > 50% higher than 7-day average.
*   **CTR Drop:** Daily CTR < 50% of 7-day average (potential creative fatigue or tech issue).
*   **Spend Velocity Change:** Significant unexplained drop in daily spend (-30% DoD).

### 3. Output Generation

The output should be a concise "Morning Brief" email or terminal report.

**Prioritization:**
1.  **CRITICAL:** Zero delivery/spend.
2.  **URGENT:** Major pacing issues.
3.  **WARNING:** Performance fluctuation.

## Output Format

### Terminal Output
A simple color-coded table using `rich`:
- 🔴 **CRITICAL**
- 🟠 **URGENT**
- 🟡 **WARNING**
- 🟢 **ALL CLEAR** (Summary count only)

### Email Brief (SendGrid)
A scannable HTML email sent to the trader's inbox.

```python
# Example SendGrid call for Daily Health Check
sendgrid.send_email(
    to_email="trader@company.com",
    subject="☕ Morning Health Check: 3 Critical Alerts",
    content=html_content,
    content_type="text/html"
)
```

**HTML Content Structure:**
*   **Header:** "Morning Health Check - [Date]"
*   **Scorecard:** Total Spend Yesterday, Total Conversions, Pacing % Overall.
*   **Red Alerts Section:** List of campaigns with Zero Spend/Impressions.
*   **Yellow Alerts Section:** Pacing and CPA anomalies.
*   **Links:** Direct links to DSP console if available.
