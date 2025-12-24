<!--
Copyright (c) 2025 ElcanoTek

This file is part of Victoria Terminal.

This software is licensed under the Business Source License 1.1.
You may not use this file except in compliance with the license.
You may obtain a copy of the license at

    https://github.com/ElcanoTek/victoria-terminal/blob/main/LICENSE

Change Date: 2027-09-20
Change License: GNU General Public License v3.0 or later

License Notes: 2025-12-24
-->

# Campaign Wrap-Up Protocol

Victoria can perform a comprehensive campaign wrap-up analysis, transforming raw performance data into a strategic narrative with actionable insights and a stunning visual presentation. This protocol guides you through a systematic process of standard analysis, automated quirky insight discovery, and final presentation generation.

## 1. Standard Campaign Analysis

This phase mirrors a traditional campaign wrap-up, providing a comprehensive overview of performance. The structure is inspired by best-in-class agency reports, ensuring all key aspects of the campaign are covered.

**Analysis Steps:**

1.  **Executive Summary:** Synthesize the most critical information upfront following this specific layout structure:
    - **Key Metrics (Top):** Display four primary KPIs prominently at the top of the slide:
      - Total Investment
      - Total Conversions
      - Conversion Rate
      - Cost per Acquisition
    - **Campaign Performance Highlights (Left):** A list of key performance highlights.
    - **Strategic Recommendations (Right):** A numbered list of strategic recommendations.
2.  **Platform & Partner Performance:** Analyze the performance of different platforms, exchanges, or partners. Identify top and bottom performers and provide insights into what drove their performance.
3.  **Campaign Optimization Journey:** Tell the story of the campaign's optimization. Visualize the impact of changes made during the campaign, such as site removals, budget shifts, or targeting adjustments.
4.  **Geographic Analysis:** Analyze performance by geographic location (DMA, state, country). Identify high-performing regions and opportunities for geographic targeting optimization.
5.  **Temporal Analysis (Day of Week/Hour of Day):** Look for patterns in performance based on time. Identify the most and least efficient times to run the campaign.
6.  **Creative & Content Analysis:** Analyze the performance of different creatives, ad formats, and site categories. Identify winning combinations and creative fatigue.

## 2. Automated Quirky Insight Discovery

This is where Victoria's unique analytical capabilities shine. The goal is to move beyond standard reporting and uncover non-obvious, high-impact insights that can drive significant competitive advantage. This process is designed to be systematic yet creative, encouraging the exploration of unusual patterns and correlations.

**The Process:**

1.  **Hypothesis Generation (The 'Quirky Questions'):** Start by brainstorming a list of unconventional questions to ask the data. Here are some examples to get you started:
    *   What's the weirdest time of day for conversions for this campaign?
    *   Is there a browser or OS that is unexpectedly good or bad?
    *   Are there any 'sleeper' site categories that have a surprisingly high conversion rate, even with low traffic?
    *   What happens to performance on holidays or major news events?
    *   Is there a correlation between the weather and campaign performance?
    *   Which combination of targeting parameters (geo, device, audience) is the most unexpectedly profitable?

2.  **Automated Data Exploration:** Use the full power of your Python analytics toolkit to systematically test these hypotheses. Leverage `pandas`, `polars`, `scikit-learn`, and `statsmodels` to run correlations, build small predictive models, and identify anomalies.

3.  **Insight Validation & Prioritization:** Not all quirky findings are created equal. Once you have a list of potential insights, you need to validate and prioritize them:
    *   **Statistical Significance:** Is the finding real, or just random noise? Use statistical tests to confirm the validity of your insights.
    *   **Impact Potential:** How much could this insight improve performance if acted upon? Quantify the potential impact in terms of CPA, ROAS, or other key metrics.
    *   **Actionability:** Is this an insight that can be easily acted upon? An insight is only valuable if it can be translated into a concrete optimization action.
    *   **'Quirkiness' Score:** Assign a score to each insight based on its unexpectedness and novelty. The goal is to surface the most surprising and non-obvious findings.

4.  **The Prioritized Quirky Findings List:** The output of this process is a prioritized list of the top 3-5 quirkiest, most actionable insights from the campaign.

## 3. Gamma Presentation Generation

The final step is to bring the story to life with a visually stunning presentation using Gamma AI. The presentation should be a narrative that weaves together the findings from both the standard analysis and the quirky insight discovery.

**Important:** For Campaign Wrap-Up Protocol presentations, use the dedicated template-based function:

```python
gamma.generate_wrap_up_presentation(
    client_name="[Client Name]",
    campaign_year=2025,  # Optional, defaults to current year
    client_logo_url="https://example.com/client-logo.png",  # Optional
    campaign_data="""
    EXECUTIVE SUMMARY:
    - Total Investment: $X,XXX
    - Total Conversions: X,XXX
    - Conversion Rate: X.X%
    - Cost per Acquisition: $XX

    Campaign Performance Highlights:
    - [Highlight 1: e.g., Exceeded conversion goals by 25%]
    - [Highlight 2: e.g., Reduced CPA by 15%]
    - [Highlight 3: e.g., Top platform: Paid Search (45% conversions)]

    PLATFORM PERFORMANCE:
    Platform Analysis Table:
    - [Platform 1]: X conversions, $X CPA, X% conversion rate
    - [Platform 2]: X conversions, $X CPA, X% conversion rate
    - [Platform 3]: X conversions, $X CPA, X% conversion rate

    Key Platform Insights:
    - [Insight 1]
    - [Insight 2]

    CAMPAIGN LIFECYCLE OPTIMIZATION:
    CPA Timeline (show optimization journey):
    - Week 1-2: $XX CPA (baseline)
    - Week 3-4: $XX CPA (after first optimization)
    - Week 5-6: $XX CPA (after second optimization)

    Optimization Actions Taken:
    - [Action 1: e.g., Removed underperforming sites]
    - [Action 2: e.g., Increased bid on top performers]
    - [Action 3: e.g., Adjusted dayparting strategy]

    GEOGRAPHIC INSIGHTS:
    Top Performing DMAs:
    - [DMA 1]: X conversions, $X spend, X% CTR
    - [DMA 2]: X conversions, $X spend, X% CTR
    - [DMA 3]: X conversions, $X spend, X% CTR

    TEMPORAL ANALYSIS:
    Day of Week Performance:
    - Monday: X conversions
    - Tuesday: X conversions
    - [Continue for all days]

    Key Temporal Insights:
    - [Insight 1: e.g., Weekend performance 30% higher]
    - [Insight 2: e.g., Tuesday shows lowest CPA]

    KEY LEARNINGS & STRATEGIC RECOMMENDATIONS:
    Key Learnings:
    - [Learning 1]
    - [Learning 2]

    Next Steps:
    1. [Recommendation 1: e.g., Increase budget to top DMAs]
    2. [Recommendation 2: e.g., Scale winning platforms]
    3. [Recommendation 3: e.g., Test new creative variations]
    """
)
```

This function uses Gamma's template API (v1.0 endpoint with template ID: `g_vzunwtnstnq4oag`) which includes the predefined Campaign Wrap-Up Protocol structure.

**What gets automatically handled:**
- Presentation title is set to "{Client Name} Wrap Up"
- Title slide populated with client name/logo, Elcano logo, and year
- Static template slides preserved: "How We Did It", "Meet Victoria", "Thank You"
- Data-driven slides populated with your campaign metrics

## Presentation Structure

The presentation must follow this exact sequence and layout to align with the established template:

### 1. Title Slide
- **Left**: Client name (text) or client logo image
- **Right**: Elcano logo (from the Gamma theme)
- **Bottom (centered)**: Campaign year
- **Background**: Full-width card style using an accent image from the Elcano Gamma theme

### 2. Executive Summary
- **Top row**: Four key metrics
  - Total Investment
  - Total Conversions
  - Conversion Rate
  - Cost per Acquisition
- **Bottom left**: Campaign Performance Highlights
- **Bottom right**: Strategic Recommendations

### 3. Platform Performance Analysis
- **Top**: Table with platform performance metrics
- **Bottom left**: Donut chart for conversion distribution
- **Bottom right**: Key platform insights

### 4. Campaign Lifecycle Optimization
- **Left**: Line chart for CPA optimization over time
- **Right**: Section for optimization actions

### 5. Conversion Spike Analysis
- **Left**: Line chart of conversion spikes
- **Right**: Section for spike event details
- **Bottom**: Immediate Actions

### 6. Winning Inventory Combinations
- **Left**: Bar chart showing conversions by site category/theme
- **Right**: Content Theme Analysis
- **Bottom**: Recommendation

### 7. Geographic Performance Insights
- **Left**: Geographic heat map showing top 3 DMA locations
- **Right**: DMA Performance Analysis with key highlights
- **Table**: DMA locations with CTR and Spend Share

### 8. Day of Week Analysis
- **Top**: Bar chart of total conversions by day of week
- **Bottom**: Summary section with 4 key highlights in card format

### 9. Key Learnings & Next Steps
- **Two sections**:
  - Key Learnings
  - Next Steps

### 10. Thank You Slide
- **Center**: "Thank You" text
- **Bottom/Right**: Elcano logo (from Gamma theme)
- **Background**: Full-width card style using an accent image from the Elcano Gamma theme

## Presentation Best Practices

*   **Tell a Story:** Don't just present data; tell a story. Start with the big picture, drill down into the details, and end with a clear set of actionable recommendations.
*   **Create Professional Charts with Structured Briefs:** To generate publication-quality visualizations, use structured "Chart Briefs" within your presentation content. This approach transforms basic chart requests into professional, insight-driven visualizations that maintain Elcano brand consistency.

### Chart Brief Template

For every chart, include a structured brief that provides Gamma with specific instructions:

```markdown
**Chart Brief:**
- **Chart Type**: [Specific chart type - be precise]
- **Title**: "[Clear, descriptive title]"
- **X-Axis Title**: "[Axis label with units]" (if applicable)
- **Y-Axis Title**: "[Axis label with units]" (if applicable)
- **Data Labels**: [Specific instructions for labels]
- **Sorting**: [How to organize the data]
- **Color Palette**: Use Elcano brand colors
- **Purpose**: [What story the chart should tell]
- **Key Insight**: [Main takeaway to highlight]

**Data:**
[Clean markdown table with your data]
```

### Chart Type Selection Guide

Choose the most appropriate chart type based on your data relationship:

| Data Relationship | Recommended Chart Type | Best Use Case | Example |
|-------------------|----------------------|---------------|---------|
| **Compare Categories** | Horizontal Bar Chart | Platform performance, budget allocation | Ad spend by platform |
| **Show Trends Over Time** | Line Chart | Performance optimization, seasonal patterns | CTR improvement over campaign duration |
| **Display Proportions** | Donut Chart | Budget distribution, audience segments | Marketing spend by channel |
| **Reveal Correlations** | Scatter Plot | Spend vs. conversions, engagement relationships | Ad spend correlation with conversions |
| **Geographic Data** | Heatmap/Bubble Map | Regional performance, location insights | Conversion rates by state |
| **Multiple Metrics** | Dual-Axis Chart | Volume and rate metrics combined | Impressions and CTR over time |
| **Key Performance Indicators** | Big Number Callouts | Executive summaries, goal achievement | Total conversions vs. target |

### Enhanced Chart Examples by Analysis Phase

| Analysis Phase | Chart Brief Example |
|----------------|-------------------|
| **Executive Summary** | `**Chart Brief:** Chart Type: Big Number Callouts, Title: "Q4 2025 Key Performance Indicators", Purpose: Highlight metrics exceeding targets, Key Insight: All KPIs surpassed goals by 15-28%` |
| **Platform Performance** | `**Chart Brief:** Chart Type: Horizontal Bar Chart, Title: "Ad Spend Distribution by Platform", Sorting: Sort from highest to lowest spend, Key Insight: Google Ads represents 52% of total spend with highest ROI` |
| **Campaign Optimization** | `**Chart Brief:** Chart Type: Line Chart, Title: "CTR Improvement Over Campaign Duration", Purpose: Show optimization success over time, Key Insight: 85% CTR improvement demonstrates successful optimization` |
| **Geographic Analysis** | `**Chart Brief:** Chart Type: Geographic Heatmap, Title: "Conversion Rate by State", Purpose: Identify regional performance patterns, Key Insight: West Coast states show 40% higher conversion rates` |
| **Temporal Analysis** | `**Chart Brief:** Chart Type: Heatmap, Title: "Performance by Hour and Day", Purpose: Reveal optimal timing patterns, Key Insight: Tuesday-Thursday 2-4 PM shows peak performance` |
| **Creative Analysis** | `**Chart Brief:** Chart Type: Bubble Chart, Title: "Creative Performance: CTR vs CVR vs Spend", Purpose: Show three-variable relationships, Key Insight: Video creatives achieve highest engagement with moderate spend` |

### Professional Chart Standards

Every chart generated through Victoria Terminal meets these quality standards:

**Content Quality:**
- Appropriate chart type for the data relationship and communication goal
- Clear, descriptive titles that immediately convey the chart's purpose
- Properly labeled axes with units and meaningful scales
- Logical data sorting (highest to lowest for comparisons, chronological for trends)
- Highlighted key insights that drive actionable conclusions

**Visual Design:**
- Consistent Elcano brand color palette throughout all visualizations
- Professional formatting with adequate spacing and readable fonts
- Uncluttered appearance that focuses attention on key data points
- Strategic use of color to highlight important information
- Data labels that enhance rather than obscure the visualization

**Data Integrity:**
- Accurate representation with appropriate scales and context
- Complete data sets that tell the full story
- Credible data sources with proper attribution when necessary
- No misleading proportions or truncated scales
- Sufficient context to support decision-making

### Implementation Example

Here's how to structure content for professional chart generation:

```markdown
# Campaign Performance Analysis

## Executive Summary
**Chart Brief:**
- **Chart Type**: Big Number Callouts
- **Title**: "Q4 2025 Key Performance Indicators"
- **Purpose**: Highlight critical metrics that exceeded targets
- **Key Insight**: All primary KPIs surpassed goals, with CTR exceeding target by 28%

**Data:**
| Metric | Actual | Target | Variance |
|--------|--------|--------|----------|
| Total Conversions | 45,600 | 40,000 | +14% |
| Average CTR | 3.2% | 2.5% | +28% |
| Cost per Conversion | $28.50 | $35.00 | -18.6% |

## Platform Performance Comparison
**Chart Brief:**
- **Chart Type**: Horizontal Bar Chart
- **Title**: "Ad Spend Distribution by Platform - Q4 2025"
- **X-Axis Title**: "Total Spend (USD)"
- **Y-Axis Title**: "Advertising Platform"
- **Data Labels**: Show spend values formatted as currency
- **Sorting**: Sort from highest to lowest spend
- **Color Palette**: Use Elcano brand colors with primary color for top performer
- **Purpose**: Compare investment levels across advertising platforms
- **Key Insight**: Google Ads represents 52% of total spend with highest ROI

**Data:**
| Platform | Spend | Conversions | ROI |
|----------|-------|-------------|-----|
| Google Ads | $1,250,000 | 24,000 | 285% |
| Facebook Ads | $750,000 | 15,200 | 245% |
| LinkedIn Ads | $300,000 | 4,800 | 195% |
| Twitter Ads | $150,000 | 1,600 | 165% |
```

*   **Leverage Enhanced Gamma Integration:** The Victoria Terminal Gamma integration now includes comprehensive chart-specific instructions that automatically guide chart type selection, ensure professional formatting, optimize data presentation, maintain visual consistency, and enhance readability. Focus on providing well-structured Chart Briefs, and let the enhanced integration handle the professional presentation standards.

By following this protocol, Victoria can deliver a campaign wrap-up that is not only comprehensive and insightful but also engaging and actionable, setting a new standard for programmatic analysis.
