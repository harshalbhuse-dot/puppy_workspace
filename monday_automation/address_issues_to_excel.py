"""
Monday Automation: Address Issues Query → Excel
================================================

Runs the address issues BigQuery query and pushes results to
the Spotlight Sheet FY27 H1.xlsx on SharePoint.

Usage:
    python address_issues_to_excel.py

Schedule with Windows Task Scheduler for every Monday!

Author: Code Puppy 🐶
"""

import subprocess
import json
import csv
import os
from datetime import datetime
from pathlib import Path

# =============================================================================
# Configuration
# =============================================================================

# BigQuery query (gets previous WM week's address issues)
# FIXED: Uses OFFSET 1 to get actual previous week (handles fiscal year transitions)
BQ_QUERY = """
WITH PREV_WEEK AS (
    SELECT WM_WK FROM (
        SELECT DISTINCT WM_WK 
        FROM `wmt-driver-insights.Chirag_dx.Driver_Fraud_Defects`
        ORDER BY WM_WK DESC
        LIMIT 1 OFFSET 1
    )
),
ADDRESS_ISSUE AS (
    SELECT 
        ABUSE_CATEGORY,
        WM_WK,
        SALES_ORDER_NUM,
        PO_NUM,
        ADDRESSTYPE,
        RECOMMENDEDLATLONGSOURCE,
        cust_id,
        DRVR_USER_ID,
        channel,
        CUST_RQ_ADDR_LINE_1_TXT,
        CUST_RQ_ADDR_LINE_2_TXT,
        CUST_RQ_CITY_NM,
        CUST_RQ_ST_NM,
        CUST_RQ_POSTAL_CD,
        avg(DLVR_CUST_DIST) as Avg_dlvr_cust_dist,
        avg(HI_CONFIDENCE_LAT_LONG_IND) as avg_HI_CONFIDENCE_LAT_LONG_IND,
        count(case when DLVR_CUST_DIST is null then PO_NUM else null end) as null_cust_dlvr_dist
    FROM `wmt-driver-insights.Chirag_dx.Driver_Fraud_Defects`
    WHERE WM_WK = (SELECT WM_WK FROM PREV_WEEK)
    AND ABUSE_CATEGORY = 'ADDRESS_ISSUE'
    AND ADDRESSTYPE = 'HOUSE'
    GROUP BY 
        ABUSE_CATEGORY, WM_WK, SALES_ORDER_NUM, PO_NUM, ADDRESSTYPE,
        RECOMMENDEDLATLONGSOURCE, cust_id, DRVR_USER_ID, channel,
        CUST_RQ_ADDR_LINE_1_TXT, CUST_RQ_ADDR_LINE_2_TXT,
        CUST_RQ_CITY_NM, CUST_RQ_ST_NM, CUST_RQ_POSTAL_CD
    HAVING null_cust_dlvr_dist = 0
),
RTN_RSN_LKP AS (
    SELECT 
        sales_order_num,
        po_num,
        STRING_AGG(DISTINCT RTN_RSN_DESC, ", " ORDER BY RTN_RSN_DESC) AS RTN_RSN_DESC
    FROM `wmt-edw-prod.WW_RTN_DL_VM.RTN_LINE_RATE_DTL`
    WHERE RTN_RATE_TYPE_RPT_DT >= "2024-01-01"
    AND RTN_RATE_TYPE_NM = 'TER'
    AND SALES_ORDER_LINE_NUM <> 9999
    AND po_num IN (SELECT PO_NUM FROM ADDRESS_ISSUE)
    GROUP BY 1, 2
)
SELECT a.* EXCEPT(null_cust_dlvr_dist)
FROM ADDRESS_ISSUE a
LEFT JOIN RTN_RSN_LKP r ON a.PO_NUM = r.po_num
WHERE lower(r.RTN_RSN_DESC) IN ('lost after delivery', 'lost in transit', 'missing item', 'item missing')
"""

# Output directory for CSV files
OUTPUT_DIR = Path(__file__).parent / "output"


# =============================================================================
# BigQuery Functions
# =============================================================================

def run_bq_query(query: str) -> tuple[list[dict], str | None]:
    """
    Run a BigQuery query using bq CLI and return results.
    
    Returns:
        tuple: (list of row dicts, WM_WK value or None)
    """
    print("🔍 Running BigQuery query...")
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"address_issues_{timestamp}.csv"
    
    # Build bq command
    cmd = [
        "bq", "query",
        "--use_legacy_sql=false",
        "--format=csv",
        "--max_rows=100000",
        query
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            print(f"❌ BigQuery error: {result.stderr}")
            return [], None
        
        # Parse CSV output
        lines = result.stdout.strip().split("\n")
        if len(lines) < 2:
            print("⚠️ No data returned from query")
            return [], None
        
        # Save to file
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            f.write(result.stdout)
        
        print(f"✅ Query complete! {len(lines)-1} rows returned")
        print(f"📁 Saved to: {output_file}")
        
        # Parse into list of dicts
        reader = csv.DictReader(lines)
        rows = list(reader)
        
        # Extract WM_WK from first row
        wm_wk = rows[0].get("WM_WK") if rows else None
        
        return rows, wm_wk
        
    except subprocess.TimeoutExpired:
        print("❌ Query timed out after 5 minutes")
        return [], None
    except Exception as e:
        print(f"❌ Error running query: {e}")
        return [], None


# =============================================================================
# Main Execution
# =============================================================================

def main():
    """Main automation workflow."""
    print("="*60)
    print("🐶 Monday Automation: Address Issues → Excel")
    print("="*60)
    print()
    
    # Step 1: Run BigQuery query
    rows, wm_wk = run_bq_query(BQ_QUERY)
    
    if not rows:
        print("❌ No data to upload. Exiting.")
        return
    
    print(f"\n📅 WM Week: {wm_wk}")
    print(f"📊 Rows to upload: {len(rows)}")
    
    # Step 2: Display instructions for Code Puppy upload
    print("\n" + "="*60)
    print("📤 NEXT STEP: Upload to Excel")
    print("="*60)
    print()
    print("Run this in Code Puppy:")
    print()
    print(f'  "Upload the CSV at monday_automation/output/ to the')
    print(f'   Spotlight Sheet FY27 H1.xlsx as a new sheet named')
    print(f'   Address_Issue_{wm_wk}"')
    print()
    print("Or use the full automation with --upload flag (requires MS Graph auth)")
    print()


if __name__ == "__main__":
    main()
