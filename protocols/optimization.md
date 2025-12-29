<!--
Copyright (c) 2025 ElcanoTek

This file is part of Victoria Terminal.

This software is licensed under the Business Source License 1.1.
You may not use this file except in compliance with the license.
You may obtain a copy of the license at

    https://github.com/ElcanoTek/victoria-terminal/blob/main/LICENSE

Change Date: 2027-09-20
Change License: GNU General Public License v3.0 or later

License Notes: 2025-12-29
-->

# Optimization Protocol

Victoria can analyze campaign performance data and generate comprehensive optimization recommendations. This protocol serves as a rough guide for conducting thorough analysis—use your best judgment to adapt the approach based on available data and the user's specific needs.

## Overview & Philosophy

When asked to perform optimization analysis:
- **Be extremely thorough** - The goal is to surface insights traders wouldn't have time to find themselves
- **Use best judgment** - Adapt your analysis approach based on what data is available and what will be most valuable
- **Think dimensionally** - Explore every available dimension of the data to find optimization opportunities
- **Make it actionable** - Connect insights to specific, implementable recommendations with quantified impact

The user may provide specific deals/campaigns to analyze, target KPIs, and data sources (email attachments, local files, databases, etc.). Your job is to uncover optimization opportunities and deliver strategic recommendations.

## General Approach

### 1. Understand the Scope

Get clarity on:
- **What to analyze:** Which deals, campaigns, or inventory to focus on
- **Target KPIs:** What metrics to optimize towards (CPA, ROAS, CTR, etc.)
- **Data sources:** Where to get the data (emails, local files, databases)
- **Output format:** How to deliver findings (email report, presentation, conversation, etc.)

### 2. Gather Data Comprehensively

**Be thorough in data collection** - missing data means missing insights. Depending on the data source:

**If analyzing emailed data:**
- Check emails from an appropriate time window (typically 1-2 weeks)
- Download all relevant attachments (CSVs, Excel files, etc.)
- Extract files from embedded links when appropriate
- Use the most recent data when you have duplicates from the same source
- Deduplicate based on date + campaign identifiers before analysis

**If analyzing local files or databases:**
- Explore available tables and files to understand what data is accessible
- Validate data quality and freshness before diving into analysis
- Confirm you're looking at the right time period

### Dataset Acquisition Must Be Exhaustive (Discovery-First)

When a task depends on "the latest dataset" (reports/exports/attachments) and filenames are unknown, you must treat acquisition as a discovery problem and be deliberately over-thorough:

1. **Search broadly before filtering:** scan the full relevant inbox history (not just "since last check") and the local attachment directory; identify candidate emails by sender/subject keywords/time window, then confirm via attachment content signatures (expected columns/sheet names), not filenames.

2. **Download defensively:** for every matching candidate email, download **all CSV/XLSX attachments** and download all "likely download links" in the email body; do not assume only one attachment is relevant.

3. **Normalize + verify:** convert XLSX → CSV (first sheet), build a simple manifest (file path, received date, report type guess, min/max date, key columns present), and prove coverage meets the requested window; explicitly flag any missing days/report-types.

**Acceptance gate (don't proceed until passed):** you can list the files used and show min/max date coverage for each required report type (e.g., Domain/App, Time-of-Day, OS/Device, DSP rollup).

### 3. Find the Specified Campaigns

Focus your analysis on what the user asked for. Search for the specified deals/campaigns by name, ID, or other identifiers. Use flexible matching (case-insensitive, partial matches) to ensure you don't miss relevant data.

### 4. Analyze Performance Thoroughly

For each campaign, go beyond surface-level metrics. The goal is to uncover insights that wouldn't be immediately obvious.

**Start with overall performance:**
- Calculate key metrics (spend, impressions, clicks, conversions, CPC, CPA, CTR, CVR, ROAS, etc.)
- Compare against target KPIs provided by the user
- Identify which campaigns are meeting goals and which need optimization

**Use standard ratio calculation patterns** (aggregate first, then divide):
- CPA: `SUM(spend) / NULLIF(SUM(conversions), 0)`
- CPC: `SUM(spend) / NULLIF(SUM(clicks), 0)`
- CTR: `100.0 * SUM(clicks) / NULLIF(SUM(impressions), 0)`
- CVR: `100.0 * SUM(conversions) / NULLIF(SUM(clicks), 0)`
- ROAS: `SUM(revenue) / NULLIF(SUM(spend), 0)`

### 5. Explore Dimensions Thoroughly

**Think creatively about which dimensions to analyze** - explore every angle that might reveal optimization opportunities. Use your best judgment based on available data.

**Common dimensions to consider:**

- **Inventory:** Domains, site categories, app bundles, CTV channels, publishers, placements
- **Temporal:** Hour of day, day of week, date trends, campaign lifecycle stages
- **Geographic:** DMA, state, region, country, zip code
- **Audience:** Segments, demographics, behaviors, retargeting vs. prospecting
- **Technical:** Device type (mobile/desktop/tablet/CTV), browser, OS, connection type
- **Supply Path:** SSPs, exchanges, deal types (guaranteed vs. open exchange)
- **Creative:** Creative ID, format, size, message variant, video vs. static
- **Performance Bands:** High/medium/low performers within each dimension

**Analytical patterns to use:**

For each dimension, look for:
- **Top performers:** What's working exceptionally well vs. target KPIs?
- **Underperformers:** What's consuming spend without delivering results?
- **Hidden gems:** Low-spend segments with exceptional efficiency that could be scaled
- **Outliers:** Unusual patterns that might indicate opportunities or issues
- **Concentration:** Is spend/performance too concentrated or too fragmented?

**Example dimensional query pattern:**
```sql
SELECT [dimension_field],
       SUM(spend) as spend,
       SUM(conversions) as conversions,
       SUM(spend) / NULLIF(SUM(conversions), 0) as cpa,
       100.0 * SUM(clicks) / NULLIF(SUM(impressions), 0) as ctr
FROM campaign_data
GROUP BY [dimension_field]
HAVING SUM(spend) > [meaningful_threshold]
ORDER BY conversions DESC;
```

**Adapt your analysis** based on the campaign type, available data fields, and what's most likely to yield actionable insights.

### 6. Generate Actionable Recommendations

Transform your findings into specific, implementable actions. For each recommendation:
- **Be specific:** Don't just say "improve domain performance" - specify which domains to block, which to scale, by how much
- **Quantify impact:** Estimate the expected improvement (e.g., "Expected to reduce CPA by 15%")
- **Prioritize:** Mark as high/medium/low priority based on potential impact and ease of implementation
- **Provide context:** Explain why this recommendation makes sense based on the data

**Common optimization types:**
- Budget reallocation between segments
- Blocklists (domains, apps, placements to exclude)
- Allowlists (high-performers to scale)
- Bid adjustments (dayparting, geography, device, audience)
- Creative optimizations (refresh, rotate, pause)
- Targeting refinements
- Pacing corrections

### 7. Deliver Findings

Adapt your delivery format based on user preference:
- **HTML Email:** Professional formatted report sent via SendGrid
- **Conversation:** Discuss findings directly in the terminal
- **Presentation:** Generate a Gamma presentation for stakeholder meetings
- **Data Export:** Provide CSV/Excel files with detailed breakdowns

## HTML Email Style Guide

When delivering optimization reports via email, use professional HTML formatting that reflects the Elcano brand while remaining flexible and readable. Here's a style guide rather than a rigid template - adapt as needed for your specific report.

### Elcano Brand Colors

Use these colors consistently to maintain brand identity:

| Color | Hex Code | Usage |
|-------|----------|-------|
| Dark Purple | `#1A0B1E` | Primary headers, dark backgrounds |
| Glaucous | `#7272AB` | Accent color, highlights, CTAs, links |
| Payne's Gray | `#586F7C` | Secondary text, borders, subtle elements |
| White | `#FFFFFF` | Content backgrounds, light text on dark |
| Black | `#000000` | Primary body text |
| Light Purple | `#f3f2f7` | Card backgrounds, subtle highlights |

### General Styling Principles

**Typography:**
- Use clean sans-serif fonts: Segoe UI, Helvetica, Arial, or system defaults
- Maintain clear hierarchy: larger headers, readable body text (~14-16px)
- Keep line height comfortable for reading (1.5-1.7)

**Color Usage:**
- Dark Purple for major headers and primary branding elements
- Glaucous for interactive elements, links, and accents
- Payne's Gray for supporting text and subtle dividers
- High contrast for accessibility (dark text on light backgrounds)

**Layout:**
- Maximum width ~800px for optimal email readability
- Generous padding and whitespace - let content breathe
- Use cards/boxes to group related information
- Mobile-responsive design

**Visual Hierarchy:**
- Lead with executive summary or key findings
- Use clear section headers
- Tables for structured data
- Highlight boxes for important callouts
- Color-coded priority indicators (red=high, orange=medium, green=low)

### Key HTML Components

**CSS Variables for Brand Colors:**
```css
:root {
    --elcano-dark-purple: #1A0B1E;
    --elcano-glaucous: #7272AB;
    --elcano-paynes-gray: #586F7C;
    --elcano-white: #FFFFFF;
    --elcano-black: #000000;
    --elcano-light-purple: #f3f2f7;
}
```

**Branded Header Example:**
```html
<div style="background: linear-gradient(135deg, #1A0B1E 0%, #2d1f3d 100%);
            color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
    <h1 style="margin: 0; font-size: 24px;">Campaign Optimization Report</h1>
    <div style="color: #7272AB; font-size: 14px; margin-top: 5px;">Generated by Victoria | December 18, 2025</div>
</div>
```

**Callout/Highlight Box Example:**
```html
<div style="background: #f3f2f7; border-left: 4px solid #7272AB;
            padding: 15px 20px; margin: 20px 0; border-radius: 0 8px 8px 0;">
    <strong>Key Finding:</strong> This is an important callout that draws attention.
</div>
```

**Metric Cards Example:**
```html
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px; margin: 20px 0;">
    <div style="background: #f3f2f7; padding: 15px; border-radius: 8px; text-align: center;">
        <div style="font-size: 24px; font-weight: bold; color: #1A0B1E;">$12,450</div>
        <div style="font-size: 12px; color: #586F7C;">Total Spend</div>
    </div>
    <!-- Repeat for other metrics -->
</div>
```

**Data Table Example:**
```html
<table style="width: 100%; border-collapse: collapse; margin: 15px 0;">
    <tr>
        <th style="background: #1A0B1E; color: white; padding: 10px; text-align: left;">Metric</th>
        <th style="background: #1A0B1E; color: white; padding: 10px; text-align: left;">Value</th>
    </tr>
    <tr style="background: #f3f2f7;">
        <td style="padding: 10px;">CPA</td>
        <td style="padding: 10px;">$45.00</td>
    </tr>
    <tr>
        <td style="padding: 10px;">CTR</td>
        <td style="padding: 10px;">2.4%</td>
    </tr>
</table>
```

**Priority-Coded Recommendation Example:**
```html
<div style="background: #fdf2f2; border-left: 4px solid #e53e3e;
            padding: 12px 15px; margin: 10px 0; border-radius: 0 6px 6px 0;">
    <span style="color: #e53e3e; font-weight: bold;">HIGH PRIORITY:</span>
    Block underperforming domains - Expected CPA reduction: 15%
</div>
```

### Sending HTML Emails

Use SendGrid to send professionally formatted HTML reports:

```python
# Send HTML-formatted optimization report
sendgrid.send_email(
    to_email="recipient@company.com",
    subject="Campaign Optimization Report - December 2025",
    content=html_report_content,
    content_type="text/html",  # IMPORTANT: Specify HTML content type
    cc_emails=["team@company.com"],  # Optional
)
```

**Important:** Always set `content_type="text/html"` when sending HTML emails to ensure proper rendering with colors, formatting, and layout.

## Summary

This protocol is a guide, not a script. Use your best judgment to:
- Adapt data collection based on what's available and relevant
- Focus dimensional analysis on the most promising areas
- Tailor recommendations to the user's specific needs and constraints
- Choose the right delivery format (email, conversation, presentation)

The goal is **thoroughness and insight** - surface optimization opportunities that wouldn't be obvious from standard reporting. Think like a seasoned analyst who has time to dig deep into the data.
