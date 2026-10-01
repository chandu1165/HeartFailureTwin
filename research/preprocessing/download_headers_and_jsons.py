"""Download all .json and .hea metadata files for all records in SCG-RHC database.
These contain the complete clinical, demographic, decompensation status, and signal definitions.
"""
import requests
from pathlib import Path

BASE_URL = "https://physionet.org/files/scg-rhc-wearable-database/1.0.0/"
OUT_DIR = Path("data/raw/processed_data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    records_file = Path("data/raw/RECORDS")
    with open(records_file, "r") as f:
        records = [line.strip() for line in f if line.strip()]

    print(f"Total records found in RECORDS: {len(records)}")
    session = requests.Session()
    session.headers.update({"User-Agent": "HeartFailureTwin-Research/1.0"})

    success_count = 0
    for rec in records:
        # e.g., processed_data/TRM107-RHC1
        rec_name = Path(rec).name
        for ext in [".json", ".hea"]:
            dest = OUT_DIR / f"{rec_name}{ext}"
            if dest.exists() and dest.stat().st_size > 0:
                continue
            url = f"{BASE_URL}processed_data/{rec_name}{ext}"
            try:
                r = session.get(url, timeout=15)
                if r.status_code == 200:
                    dest.write_bytes(r.content)
                    success_count += 1
                else:
                    print(f"  Warning: HTTP {r.status_code} for {url}")
            except Exception as e:
                print(f"  Error fetching {url}: {e}")

    print(f"Download complete. Downloaded {success_count} files.")
    total_jsons = len(list(OUT_DIR.glob("*.json")))
    total_heas = len(list(OUT_DIR.glob("*.hea")))
    print(f"Total .json files in {OUT_DIR}: {total_jsons}")
    print(f"Total .hea files in {OUT_DIR}: {total_heas}")

if __name__ == "__main__":
    main()
