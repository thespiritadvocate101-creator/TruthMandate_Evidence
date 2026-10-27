#!/usr/bin/env python3
import json
import sys
import hashlib
from pathlib import Path

def validate_ledger(file_path="audit_summary.json"):
    path = Path(file_path)
    if not path.exists():
        print(f"Error: Ledger file '{file_path}' not found.")
        sys.exit(1)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON syntax in '{file_path}': {e}")
        sys.exit(1)

    required_keys = ["repository", "abstract", "masterStateRoot", "generatedAt", "totalRecordsExported", "records"]
    missing = [k for k in required_keys if k not in data]
    if missing:
        print(f"Error: Missing required keys in ledger: {missing}")
        sys.exit(1)

    records = data.get("records", [])
    if len(records) != data.get("totalRecordsExported"):
        print(f"Warning: Record count mismatch. Declared: {data.get('totalRecordsExported')}, Found: {len(records)}")

    # Compute raw sha256 hash of file content for verification log
    raw_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    print("✓ Ledger structure and JSON syntax valid.")
    print(f"✓ Total Records: {len(records)}")
    print(f"✓ Master State Root: {data.get('masterStateRoot')}")
    print(f"✓ SHA-256 Ledger Digest: {raw_hash}")

if __name__ == "__main__":
    validate_ledger()
