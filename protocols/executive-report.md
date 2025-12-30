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

# Executive Report Protocol

Victoria can generate comprehensive executive reports that synthesize all campaign and advertising data from a specified period into a prioritized list of strategic insights and items requiring attention. This protocol is designed for executives who need a high-level view of performance, risks, opportunities, and recommended actions.

## Overview & Philosophy

When asked to generate an executive report:
- **Be exhaustively comprehensive in data gathering** - Download ALL emails and analyze EVERY active campaign from the period. Do not sample, scan, or filter—download everything. When it comes to data collection, you cannot be too thorough.
- **Leave no campaign unexamined** - Query data sources directly to enumerate all active campaigns; do not rely solely on email content to discover campaigns
- **Prioritize ruthlessly** - Executives have limited time; surface only the most impactful insights
- **Lead with what matters** - Structure information by priority and business impact, not by data source
- **Be action-oriented** - Every insight should connect to a decision or action the executive can take
- **Flag risks early** - Proactively identify issues that require attention before they become problems

The executive report differs from optimization reports in its audience and purpose: optimization reports are for traders and campaign managers who will implement tactical changes, while executive reports are for leadership who need strategic oversight and decision-making support.

**Critical Principle:** The credibility of an executive report depends entirely on its completeness. A report that misses a failing campaign or overlooks a critical email destroys trust. Always err on the side of downloading too much data rather than too little.

## General Approach

### 1. Clarify the Scope

Understand the executive's needs:
- **Time period:** What date range should the report cover? (e.g., last week, last month, Q4)
- **Focus areas:** Any specific campaigns, clients, or metrics of particular interest?
- **Comparison context:** Should performance be compared against previous periods, targets, or benchmarks?
- **Delivery format:** Email report, presentation, or conversational briefing?
- **Urgency flags:** Any known issues or opportunities the executive wants addressed?

### 2. Exhaustive Data Collection

**This is the most critical step for executive reports.** The report must be absolutely comprehensive—missing data undermines credibility and may cause executives to miss important issues. When it comes to data collection, you cannot be too thorough.

**Complete Email Download (Mandatory):**

Download **every single email** from the specified time period—not just a sample or scan. This ensures no critical information is missed.

1. **Download ALL emails** in the date range to local storage before analysis begins
2. **Download ALL attachments** from every email (CSVs, Excel files, PDFs, reports, images)
3. **Follow EVERY download link** in email bodies to retrieve hosted reports, dashboards, and external data
4. **Parse email threads completely** - include forwarded content, inline replies, and quoted text
5. **Capture email metadata** - sender, recipients, timestamps, subject lines for context
6. **Process ALL email accounts** if multiple inboxes contain relevant campaign data

**Do not skip emails based on subject line or sender.** Important campaign information often arrives from unexpected sources (finance alerts, partner notifications, automated system emails).

**Active Campaign Audit (Mandatory):**

Analyze **every active campaign** during the reporting period, regardless of whether it appeared in downloaded emails:

1. **Query all data sources directly** (DSPs, ad servers, analytics platforms) for the full campaign list
2. **Enumerate ALL campaigns** that had any activity (spend, impressions, or conversions) during the period
3. **Include campaigns with zero activity** if they were expected to be active—this may indicate delivery issues
4. **Cross-reference campaign lists** across platforms to ensure complete coverage
5. **Flag orphan campaigns** that appear in one system but not others
6. **Verify campaign naming conventions** to ensure no campaigns are missed due to naming variations

**Data Source Inventory:**

Before analysis, create a comprehensive inventory confirming:
- All expected report types are present (DSP reports, platform data, partner reports)
- **Every active campaign** is represented in the collected data
- Date coverage is complete (no missing days or gaps)
- Data freshness is acceptable (most recent available data)
- **Email count verification** - confirm total emails downloaded matches inbox count for the period
- **Attachment manifest** - list all downloaded files with sizes and types

**If gaps exist:** Flag them explicitly in the report rather than proceeding with incomplete data. Missing emails or campaigns should be treated as high-priority alerts.

### 3. Multi-Dimensional Analysis

Analyze the data across all relevant dimensions to build a complete picture:

**Performance Overview:**
- Total spend, impressions, clicks, conversions across all campaigns
- Aggregate KPIs: CPA, CPC, CTR, CVR, ROAS
- Comparison to targets and previous periods
- Pacing against budgets and goals

**Campaign-Level Insights (ALL Active Campaigns):**

Every campaign that was active during the period must be analyzed—do not focus only on top performers or problem campaigns:

- **Complete campaign enumeration** - list and analyze every campaign with activity
- Which campaigns are exceeding expectations?
- Which campaigns are underperforming and why?
- Budget utilization and pacing status for each campaign
- Any campaigns requiring immediate attention
- **Campaigns with no email coverage** - flag any active campaigns not mentioned in downloaded emails
- **New campaigns launched** during the period
- **Campaigns paused or ended** during the period

**Platform & Partner Analysis:**
- Performance by DSP, SSP, exchange, or partner
- Which platforms are delivering best value?
- Any platform-specific issues or opportunities?

**Trend Analysis:**
- Week-over-week or day-over-day performance trends
- Acceleration or deceleration in key metrics
- Seasonal patterns or anomalies

**Risk Identification:**
- Campaigns at risk of missing goals
- Budget overruns or underspends
- Quality issues (brand safety, fraud indicators, viewability problems)
- Unusual patterns that warrant investigation

### 4. Insight Prioritization Framework

Not all findings belong in an executive report. Use this framework to prioritize:

**Priority 1 - Immediate Attention Required:**
- Issues that require executive decision or action within 24-48 hours
- Significant budget overruns or underspends
- Campaign failures or critical underperformance
- Brand safety incidents or quality concerns
- Opportunities with time-sensitive windows

**Priority 2 - Strategic Awareness:**
- Performance trends that indicate emerging opportunities or risks
- Campaigns significantly exceeding or missing targets
- Platform or partner performance shifts
- Competitive dynamics or market changes

**Priority 3 - Informational:**
- General performance updates
- Minor optimizations being implemented
- Routine operational matters
- Context for upcoming decisions

**Include only Priority 1 and Priority 2 items in the main report.** Priority 3 items can be included in an appendix or omitted entirely.

### 5. Structure the Executive Briefing

Organize findings for maximum executive utility:

**1. Executive Summary (Lead with this)**
- 3-5 bullet points capturing the most critical takeaways
- Overall performance assessment (on track / at risk / exceeding)
- Any items requiring immediate executive attention

**2. Priority Alerts**
- Flagged items requiring decisions or action
- Each alert includes: Issue, Impact, Recommended Action, Urgency

**3. Performance Scorecard**
- Key metrics with comparison to targets and prior period
- Visual indicators (green/yellow/red) for quick scanning
- Aggregate view across all campaigns

**4. Strategic Insights**
- Top opportunities to pursue
- Risks to monitor or mitigate
- Trend analysis and forward-looking indicators

**5. Campaign Highlights**
- Brief updates on major campaigns
- Focus on exceptions (significantly over/under performing)
- Avoid exhaustive campaign-by-campaign details

**6. Recommendations**
- Prioritized list of recommended actions
- Each recommendation includes rationale and expected impact
- Clear ownership suggestions where appropriate

### 6. Deliver the Report

Adapt delivery to executive preferences:

**HTML Email (Recommended for regular briefings):**
- Professional, scannable format
- Mobile-friendly design for on-the-go reading
- Clear visual hierarchy with priority indicators

**Presentation (For strategic reviews):**
- Use Gamma to generate executive-ready slides
- Focus on visuals and key takeaways
- Limit to 5-10 slides maximum

**Conversational Briefing:**
- Summarize key points verbally
- Be prepared to drill into details on request
- Have supporting data ready for follow-up questions

## HTML Email Style Guide

Executive reports should be immediately scannable with clear visual hierarchy. Use the Elcano brand consistently while prioritizing clarity and professionalism.

### Elcano Brand Colors

| Color | Hex Code | Usage |
|-------|----------|-------|
| Dark Purple | `#1A0B1E` | Primary headers, executive summary background |
| Glaucous | `#7272AB` | Accent color, priority indicators, links |
| Payne's Gray | `#586F7C` | Secondary text, borders, subtle elements |
| White | `#FFFFFF` | Content backgrounds, light text on dark |
| Black | `#000000` | Primary body text |
| Light Purple | `#f3f2f7` | Card backgrounds, section dividers |

### Priority Alert Colors

| Priority | Background | Border | Text |
|----------|------------|--------|------|
| High (Action Required) | `#fdf2f2` | `#e53e3e` | `#c53030` |
| Medium (Monitor) | `#fffaf0` | `#dd6b20` | `#c05621` |
| Low (Informational) | `#f0fff4` | `#38a169` | `#276749` |

### Key HTML Components

**Executive Summary Header:**
```html
<div style="background: linear-gradient(135deg, #1A0B1E 0%, #2d1f3d 100%);
            color: white; padding: 30px; border-radius: 10px 10px 0 0;">
    <h1 style="margin: 0; font-size: 24px;">Executive Report</h1>
    <div style="color: #7272AB; font-size: 14px; margin-top: 5px;">
        Period: [Date Range] | Generated by Victoria
    </div>
</div>
```

**Priority Alert - High:**
```html
<div style="background: #fdf2f2; border-left: 4px solid #e53e3e;
            padding: 15px 20px; margin: 15px 0; border-radius: 0 8px 8px 0;">
    <div style="color: #c53030; font-weight: bold; font-size: 12px;
                text-transform: uppercase; margin-bottom: 5px;">
        ⚠️ ACTION REQUIRED
    </div>
    <div style="font-weight: bold; margin-bottom: 8px;">[Issue Title]</div>
    <div style="color: #4a5568; font-size: 14px;">[Brief description and recommended action]</div>
</div>
```

**Priority Alert - Medium:**
```html
<div style="background: #fffaf0; border-left: 4px solid #dd6b20;
            padding: 15px 20px; margin: 15px 0; border-radius: 0 8px 8px 0;">
    <div style="color: #c05621; font-weight: bold; font-size: 12px;
                text-transform: uppercase; margin-bottom: 5px;">
        📊 MONITOR
    </div>
    <div style="font-weight: bold; margin-bottom: 8px;">[Issue Title]</div>
    <div style="color: #4a5568; font-size: 14px;">[Brief description and context]</div>
</div>
```

**Priority Alert - Opportunity:**
```html
<div style="background: #f0fff4; border-left: 4px solid #38a169;
            padding: 15px 20px; margin: 15px 0; border-radius: 0 8px 8px 0;">
    <div style="color: #276749; font-weight: bold; font-size: 12px;
                text-transform: uppercase; margin-bottom: 5px;">
        🎯 OPPORTUNITY
    </div>
    <div style="font-weight: bold; margin-bottom: 8px;">[Opportunity Title]</div>
    <div style="color: #4a5568; font-size: 14px;">[Brief description and potential impact]</div>
</div>
```

**Performance Scorecard:**
```html
<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
    <tr>
        <th style="background: #1A0B1E; color: white; padding: 12px; text-align: left;">Metric</th>
        <th style="background: #1A0B1E; color: white; padding: 12px; text-align: right;">Actual</th>
        <th style="background: #1A0B1E; color: white; padding: 12px; text-align: right;">Target</th>
        <th style="background: #1A0B1E; color: white; padding: 12px; text-align: center;">Status</th>
    </tr>
    <tr style="background: #f3f2f7;">
        <td style="padding: 12px;">Total Spend</td>
        <td style="padding: 12px; text-align: right;">$125,000</td>
        <td style="padding: 12px; text-align: right;">$130,000</td>
        <td style="padding: 12px; text-align: center;">
            <span style="background: #38a169; color: white; padding: 3px 10px;
                         border-radius: 12px; font-size: 12px;">On Track</span>
        </td>
    </tr>
    <tr>
        <td style="padding: 12px;">Conversions</td>
        <td style="padding: 12px; text-align: right;">2,450</td>
        <td style="padding: 12px; text-align: right;">2,000</td>
        <td style="padding: 12px; text-align: center;">
            <span style="background: #38a169; color: white; padding: 3px 10px;
                         border-radius: 12px; font-size: 12px;">Exceeding</span>
        </td>
    </tr>
    <tr style="background: #f3f2f7;">
        <td style="padding: 12px;">CPA</td>
        <td style="padding: 12px; text-align: right;">$51.02</td>
        <td style="padding: 12px; text-align: right;">$65.00</td>
        <td style="padding: 12px; text-align: center;">
            <span style="background: #38a169; color: white; padding: 3px 10px;
                         border-radius: 12px; font-size: 12px;">Exceeding</span>
        </td>
    </tr>
</table>
```

**Key Metrics Cards:**
```html
<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0;">
    <div style="background: #f3f2f7; padding: 20px; border-radius: 8px; text-align: center;">
        <div style="font-size: 28px; font-weight: bold; color: #1A0B1E;">$125K</div>
        <div style="font-size: 12px; color: #586F7C; margin-top: 5px;">Total Spend</div>
        <div style="font-size: 11px; color: #38a169; margin-top: 3px;">▲ 12% vs Prior</div>
    </div>
    <!-- Repeat for other metrics -->
</div>
```

**Insight List:**
```html
<div style="background: #f3f2f7; padding: 20px; border-radius: 8px; margin: 20px 0;">
    <h3 style="color: #1A0B1E; margin: 0 0 15px 0; font-size: 16px;">
        Strategic Insights
    </h3>
    <ul style="margin: 0; padding-left: 20px; color: #4a5568;">
        <li style="margin-bottom: 10px;">
            <strong>Mobile performance surge:</strong> Mobile CPA improved 25% WoW,
            now outperforming desktop. Consider budget reallocation.
        </li>
        <li style="margin-bottom: 10px;">
            <strong>Platform concentration risk:</strong> 68% of conversions from
            single DSP. Recommend diversification testing.
        </li>
        <li style="margin-bottom: 0;">
            <strong>Q1 pacing concern:</strong> Current run rate projects 15% under
            quarterly target. Early intervention recommended.
        </li>
    </ul>
</div>
```

### Sending Executive Reports

```python
# Send HTML-formatted executive report
sendgrid.send_email(
    to_email="executive@company.com",
    subject="Executive Report: [Period] Campaign Performance",
    content=html_report_content,
    content_type="text/html",
    cc_emails=["team-lead@company.com"],  # Optional
)
```

## Example Report Structure

Here's a complete example of how an executive report should be structured:

```
EXECUTIVE REPORT
Period: December 16-22, 2025

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXECUTIVE SUMMARY

• Overall performance EXCEEDING targets: CPA 22% below goal, conversions 18% above
• ACTION REQUIRED: Campaign "Holiday Push" pacing 40% behind—requires budget decision by EOD Tuesday
• OPPORTUNITY: Connected TV showing 3x ROAS vs. display—recommend $50K budget test
• Partner ABC reports delayed 3 days—data coverage incomplete for this period

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRIORITY ALERTS

[HIGH] Holiday Push Campaign Underpacing
- Current: $45K spent of $120K budget (37%)
- Expected at this point: $78K (65%)
- Impact: Risk of $75K unspent, missed holiday window
- Recommendation: Increase daily caps immediately or reallocate budget
- Decision needed by: December 24

[MEDIUM] Rising CPCs on Search
- Search CPC increased 18% WoW across all campaigns
- Likely cause: Holiday competition
- Impact: If trend continues, could exceed CPA targets by early January
- Recommendation: Monitor daily; prepare bid adjustments if needed

[OPPORTUNITY] Connected TV Outperformance
- CTV ROAS: 4.2x (vs. 1.4x display, 2.1x mobile)
- Current CTV allocation: Only 8% of total budget
- Potential impact: $50K additional CTV spend could yield $210K revenue
- Recommendation: Approve expanded CTV test in Q1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PERFORMANCE SCORECARD

Metric          Actual      Target      Status
──────────────────────────────────────────────
Total Spend     $287,450    $310,000    On Track (93%)
Conversions     4,892       4,200       Exceeding (+16%)
CPA             $58.76      $75.00      Exceeding (-22%)
ROAS            2.4x        2.0x        Exceeding (+20%)
CTR             0.42%       0.35%       Exceeding (+20%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STRATEGIC INSIGHTS

1. Mobile momentum continues: Third consecutive week of CPA improvement
   on mobile. Now 15% more efficient than desktop.

2. Weekend performance spike: Saturday-Sunday delivering 35% higher
   conversion rates at similar CPA. Consider dayparting adjustments.

3. Creative fatigue signals: Top creative CTR declined 12% over past
   2 weeks. New creative rotation scheduled for December 26.

4. Geographic opportunity: Southeast DMAs outperforming 40% above
   average with only 12% of budget. Expansion opportunity identified.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RECOMMENDED ACTIONS

1. [URGENT] Increase Holiday Push daily caps by 60% or reallocate
   $30K to performing campaigns

2. [THIS WEEK] Approve $50K CTV expansion test for January

3. [ONGOING] Continue monitoring search CPCs; escalate if +25% WoW

4. [Q1 PLANNING] Include Southeast expansion in Q1 media plan
```

## Pre-Delivery Completeness Checklist

Before finalizing any executive report, verify:

**Email Completeness:**
- [ ] Downloaded 100% of emails from the specified date range
- [ ] Total email count verified against inbox/server count
- [ ] All attachments downloaded and cataloged
- [ ] All download links in email bodies followed and content retrieved
- [ ] Email threads parsed for forwarded/quoted content

**Campaign Completeness:**
- [ ] Queried ALL data sources for active campaign lists
- [ ] Every campaign with spend/impressions/conversions during the period is included
- [ ] Cross-referenced campaign lists across all platforms
- [ ] Verified no campaigns missed due to naming variations
- [ ] Flagged any expected campaigns with zero activity

**Data Integrity:**
- [ ] No date gaps in the data
- [ ] All expected report types present
- [ ] Data freshness verified
- [ ] Any gaps or missing data explicitly flagged in report

## Summary

The executive report protocol prioritizes clarity, actionability, and strategic value:

1. **Gather EVERYTHING** - Download every email, analyze every campaign. Comprehensive data collection ensures no blind spots. You cannot be too thorough in this phase.
2. **Prioritize ruthlessly** - Surface only what matters for executive decision-making
3. **Lead with actions** - Structure around decisions, not data sources
4. **Flag risks proactively** - Identify issues before they require crisis management
5. **Keep it scannable** - Executives should grasp key points in under 2 minutes

The goal is to be the executive's trusted intelligence briefing—comprehensive yet concise, strategic yet actionable. Thoroughness in data collection enables confidence in the conclusions.
