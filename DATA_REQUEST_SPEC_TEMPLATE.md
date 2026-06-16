# Data Request Specification Template (AI-Ready)

**Purpose:** This document is a standardized template for other departments to request new data extractions. It is designed to be highly structured so that an AI Coding Assistant can read this document and automatically generate the necessary Python extraction scripts.

---

## 1. Request Meta-Information
- **Requester Name/Department:** [e.g., Marketing, Sales, Product]
- **Date Requested:** [YYYY-MM-DD]
- **Business Goal:** [Why is this data needed? E.g., "To track conversion rates of the new summer campaign"]

## 2. Data Source Details
- **Data Source / API:** [e.g., Google Analytics 4 (GA4), Mixpanel, Custom Database]
- **Property ID / Account ID:** [If applicable, e.g., GA4 Property ID]

## 3. Dimensions & Metrics (The 'What')
*Please list the exact dimensions and metrics required.*

### Dimensions (Fields to group by)
- `[Dimension 1, e.g., date]`
- `[Dimension 2, e.g., sessionSource]`
- `[Dimension 3, e.g., campaignName]`

### Metrics (Numerical values)
- `[Metric 1, e.g., activeUsers]`
- `[Metric 2, e.g., totalPurchases]`
- `[Metric 3, e.g., purchaseRevenue]`

## 4. Filters & Date Ranges (The 'Constraints')
- **Date Range:** [e.g., "Last 30 days", "Current Month", "Fixed: 2024-01-01 to 2024-01-31"]
- **Dimension Filters:**
  - `[e.g., sessionSource == 'google']`
  - `[e.g., campaignName contains 'summer']`
- **Metric Filters:**
  - `[e.g., activeUsers > 10]`

## 5. Output Format & Destination
- **Output File Type:** [e.g., CSV, Excel (.xlsx), JSON]
- **File Naming Convention:** [e.g., `summer_campaign_data_YYYYMMDD.xlsx`]
- **Destination:** [e.g., Local Folder, S3 Bucket, Google Drive]

## 6. Execution Frequency
- **Schedule:** [e.g., One-off, Daily, Weekly on Mondays]

---
*AI Prompt Note: Please parse the Dimensions, Metrics, and Filters to create a new module in `src/` following the existing `data_fetcher.py` pattern.*
