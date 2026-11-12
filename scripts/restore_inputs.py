"""Restore the three byte-for-byte source snapshots from pinned public URLs.

Run explicitly from the repository root; the analysis itself never downloads data.
All downloads and hashes are checked before any local input is replaced.
"""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen


def main():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    manifest = json.loads((data_dir / "input_manifest.json").read_text())
    downloads = []
    for entry in manifest["files"]:
        with urlopen(entry["url"], timeout=30) as response:
            raw = response.read()
        if hashlib.sha256(raw).hexdigest() != entry["sha256"]:
            raise SystemExit(f"Source checksum mismatch: {entry['filename']}; no files replaced")
        downloads.append((data_dir / entry["filename"], raw))
    for path, raw in downloads:
        path.write_bytes(raw)
        print(f"Restored {path.name}")


if __name__ == "__main__":
    main()
