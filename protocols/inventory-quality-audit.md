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

# Inventory Quality Audit

Victoria performs a forensic audit of where ads are running to ensure brand safety, viewability, and fraud avoidance. This protocol helps traders clean up supply paths and avoid wasting money on "Made for Advertising" (MFA) sites or bot farms.

## Overview & Philosophy

Programmatic supply chains are opaque. This protocol shines a light on the actual domains and apps receiving spend.
- **Focus:** Quality over quantity.
- **Goal:** Create a robust Blocklist and Allowlist.

## Analysis Steps

### 1. The "Red Flag" Scan
Victoria scans the domain/app report for common fraud/quality signals:
*   **CTR Anomalies:** Sites with > 1-2% CTR on display (often accidental clicks or bots).
*   **Viewability:** Sites with < 30% viewability.
*   **Placement ID Churn:** Domains with thousands of unique placement IDs (often spoofing).

### 2. Made For Advertising (MFA) Detection
*   **Keyword Scan:** Look for domain names containing "game", "free", "reward", "viral", "buzz", "quizz". (Heuristic check).
*   **Metric Triangulation:** High CTR + Extremely Low CVR (or 100% bounce rate if available) = Low Quality.

### 3. App Bundle Analysis
*   Identify "Exchange Aggregated Apps" or generic bundle IDs that mask underlying inventory.
*   Recommendation: Block opaque bundles and target specific app IDs.

## Output Generation

### Blocklist Export (CSV)
Generate a CSV file ready for upload to the DSP containing domains/apps to block.

### Quality Report (Email/Terminal)
Summary of savings found.

```
Subject: 🛡️ Inventory Quality Audit Findings

Findings:
- **High Risk Spend:** $1,200 (15% of total) spent on sites with <20% viewability.
- **Suspicious CTR:** 5 domains found with >5% CTR and 0 conversions.
- **Action:** 145 Domains added to Blocklist Candidate file.

[Download Blocklist CSV]
```
