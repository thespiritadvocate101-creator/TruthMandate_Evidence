import json, sys, ecdsa
from ledger_utils import HashUtility

def get_keys():
    try:
        with open("node.key", "rb") as f:
            sk = ecdsa.SigningKey.from_string(f.read())
    except FileNotFoundError:
        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        with open("node.key", "wb") as f:
            f.write(sk.to_string())
    return sk

def add_new_block(data):
    sk = get_keys()
    with open("manifest.json", "r") as f:
        blocks = json.load(f)
    
    last_hash = blocks[-1]['expected_hash']
    new_hash = HashUtility.calculate_hash(last_hash + data)
    signature = sk.sign(new_hash.encode()).hex()
    
    blocks.append({
        "id": blocks[-1]['id'] + 1,
        "data": data,
        "prev_hash": last_hash,
        "expected_hash": new_hash,
        "signature": signature,
        "pub_key": sk.verifying_key.to_string().hex()
    })
    
    with open("manifest.json", "w") as f:
        json.dump(blocks, f, indent=4)
    print(f"[*] BLOCK SIGNED AND APPENDED.")

if __name__ == "__main__":
    add_new_block(sys.argv[1])
