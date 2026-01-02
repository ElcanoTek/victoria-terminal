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

# PMP Deal Troubleshooting

Victoria diagnoses why Private Marketplace (PMP) or Programmatic Guaranteed (PG) deals are not spending or delivering as expected. This is a common pain point for traders.

## Overview & Philosophy

Deals fail for specific technical reasons:
1.  **Not bidding:** We aren't seeing the requests or our criteria doesn't match.
2.  **Not winning:** We are bidding but losing (price too low).
3.  **No inventory:** The publisher isn't sending requests.

## Analysis Steps

### 1. The Funnel Diagnosis
Analyze the Deal Health Report (if available) or raw bid logs:
*   **Deal Requests (Avails):** Is the publisher sending inventory?
    *   *If No:* Publisher issue. Contact Pub.
*   **Bid Rate:** Are we bidding on the requests?
    *   *If Low:* Targeting mismatch. Check Geo, Device, Audience restrictions on the Line Item vs. the Deal.
*   **Win Rate:** Are we winning the bids?
    *   *If Low:* Price floor issue. The fixed price might be set incorrectly, or we are being outbid in a Private Auction.

### 2. Targeting Conflict Check
*   Compare Line Item targeting settings against Deal parameters.
*   **Common Errors:**
    *   Line Item targets "Desktop" but Deal is "Mobile App".
    *   Brand Safety settings blocking the specific publisher URL.
    *   Creative format (Video) targeted to Display deal.

## Output Generation

### Diagnostic Report (Terminal/Email)

**Status:** 🔴 STALLED

**Diagnosis:**
*   **Issue:** Low Bid Rate (5%).
*   **Root Cause:** Line Item targeting is set to "NY Only" but Deal is sending "National" traffic. 95% of requests are filtered out by Geo targeting.

**Recommendation:**
*   Remove Geo targeting on Line Item [ID: 12345] to align with Deal terms.
*   *Alternatively:* Ask Publisher to create a NY-specific deal ID.
