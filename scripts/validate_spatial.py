#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def validate_spatial_records(file_path="audit_summary.json"):
    path = Path(file_path)
    if not path.exists():
        print(f"Error: Ledger file '{file_path}' not found.")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("records", [])
    spatial_flags = 0

    print("--- Abstract 544 Spatial & Cadastral Verification ---")
    for record in records:
        rec_id = record.get("recordId", "UNKNOWN")
        category = record.get("category", "")

        if "Cadastral Boundary" in category:
            recorded = record.get("recordedAcreage", 0.0)
            gis = record.get("gisCalculatedAcreage", 0.0)
            delta = record.get("discrepancyDelta", 0.0)
            print(f"[{rec_id}] Cadastral Check: Recorded={recorded} acres | GIS={gis} acres | Delta={delta}")
            
        elif "Closure Error" in category:
            ratio = record.get("closureErrorRatio", "N/A")
            call = record.get("callVector", "N/A")
            print(f"[{rec_id}] Metes-and-Bounds Check: Call [{call}] | Closure Ratio [{ratio}]")
            spatial_flags += 1

        elif "Mineral Extraction" in category:
            lease = record.get("leaseIdentifier", "N/A")
            status = record.get("auditStatus", "N/A")
            print(f"[{rec_id}] Mineral Severance Check: Lease [{lease}] | Status [{status}]")

    print(f"--- Verification Complete. Total Flagged Spatial Anomalies: {spatial_flags} ---")

if __name__ == "__main__":
    validate_spatial_records()
