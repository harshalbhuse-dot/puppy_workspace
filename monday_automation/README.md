# 📅 Address Issue Upload

**Trigger phrase:** "Address issue upload"

## What It Does

1. 🔍 **Runs BigQuery query** - Gets address issues for the previous WM week
2. 📊 **Creates new Excel sheet** - Named `Address_Issue_{WM_WK}` (e.g., `Address_Issue_202602`)
3. 📤 **Uploads to SharePoint** - Spotlight Sheet FY27 H1.xlsx

## Target File

**Excel:** [Spotlight Sheet FY27 H1.xlsx](https://teams.wal-mart.com/:x:/r/sites/Draft_OG_Prop_Del/_layouts/15/Doc.aspx?sourcedoc=%7B10C8D01A-5D35-4763-B71A-2F4B55B5BE7C%7D&file=Spotlight%20Sheet%20FY27%20H1.xlsx)

**SharePoint Site:** Draft_OG_Prop_Del (Last Mile Delivery)

## Schedule

| Day | Action | Sheet Name |
|-----|--------|------------|
| Monday Feb 17, 2026 | Upload | `Address_Issue_202602` |
| Monday Feb 24, 2026 | Upload | `Address_Issue_202603` |
| Monday Mar 3, 2026 | Upload | `Address_Issue_202604` |
| ... | ... | ... |

## Query Details

- **Source:** `wmt-driver-insights.Chirag_dx.Driver_Fraud_Defects`
- **Filter:** ABUSE_CATEGORY = 'ADDRESS_ISSUE', ADDRESSTYPE = 'HOUSE'
- **Week Logic:** Gets the **second most recent** WM_WK (previous week)
- **Join:** RTN_LINE_RATE_DTL for return reasons (lost/missing items)

## How To Run

Just tell Code Puppy:

> **"Address issue upload"**

That's it! 🐶

---

*Created by Code Puppy 🐶 | Feb 2026*
