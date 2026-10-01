"""Download metadata and index files from PhysioNet SCG-RHC database.
"""
import os
import requests
from pathlib import Path

BASE_URL = "https://physionet.org/files/scg-rhc-wearable-database/1.0.0/"
META_DIR = Path("data/raw/meta_information")
META_DIR.mkdir(parents=True, exist_ok=True)

FILES_TO_DOWNLOAD = [
    ("RECORDS", Path("data/raw/RECORDS")),
    ("meta_information/RHC_values.csv", META_DIR / "RHC_values.csv"),
    ("meta_information/clinic_names_RHC.csv", META_DIR / "clinic_names_RHC.csv"),
    ("meta_information/HO_names_RHC.csv", META_DIR / "HO_names_RHC.csv"),
    ("meta_information/acronyms_RHC.csv", META_DIR / "acronyms_RHC.csv"),
    ("meta_information/PAM_PCWP_timestamp_in_TBME.json", META_DIR / "PAM_PCWP_timestamp_in_TBME.json"),
    ("meta_information/list_exported_recs.txt", META_DIR / "list_exported_recs.txt"),
    ("meta_information/list_coarsely_aligned.txt", META_DIR / "list_coarsely_aligned.txt"),
]

def main():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "HeartFailureTwin-Research/1.0"
    })
    
    for rel_path, dest_path in FILES_TO_DOWNLOAD:
        url = BASE_URL + rel_path
        print(f"Downloading {url} -> {dest_path}...")
        try:
            resp = session.get(url, timeout=30)
            if resp.status_code == 200:
                dest_path.write_bytes(resp.content)
                print(f"  Successfully saved {dest_path.name} ({len(resp.content)} bytes)")
            else:
                print(f"  Failed (Status {resp.status_code}): {url}")
        except Exception as e:
            print(f"  Error downloading {url}: {e}")

if __name__ == "__main__":
    main()
