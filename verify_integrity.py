import os
import json
import hashlib

def calculate_sha512(file_path):
    hash_sha512 = hashlib.sha512()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha512.update(chunk)
        return hash_sha512.hexdigest()
    except Exception:
        return None

def verify_system_integrity():
    home_dir = os.path.expanduser('~')
    registry_path = os.path.join(home_dir, "civic_advocate_os", "state_registry.json")

    if not os.path.exists(registry_path):
        print("[ERROR] State registry missing. Run ingestion script first.")
        return

    with open(registry_path, 'r') as f:
        registry = json.load(f)

    print("=== BEGIN INTEGRITY VERIFICATION ===")
    print(f"Registry Version: {registry.get('version', 'UNKNOWN')}")
    print("--------------------------------------------------")
    
    tamper_flag = False

    for filename, metadata in registry.get("files", {}).items():
        target_path = metadata.get("path")
        expected_hash = metadata.get("sha512")

        # Check if file has been deleted or moved
        if not os.path.exists(target_path):
            print(f"[CRITICAL FAILURE] File missing: {filename}")
            print(f"  -> Expected Hash: {expected_hash}")
            tamper_flag = True
            continue

        # Recalculate current hash
        current_hash = calculate_sha512(target_path)

        if current_hash == expected_hash:
            print(f"[PASS] {filename}")
            print(f"  -> Node Integrity Verified.")
        else:
            print(f"[CRITICAL ALERT] TAMPER DETECTED: {filename}")
            print(f"  -> Expected: {expected_hash}")
            print(f"  -> Current:  {current_hash}")
            tamper_flag = True

    print("--------------------------------------------------")
    if not tamper_flag:
        print("[STATUS] SYSTEM GREEN: State registry matches local ledger state.")
    else:
        print("[STATUS] SYSTEM RED: Integrity compromise detected.")

if __name__ == "__main__":
    verify_system_integrity()
