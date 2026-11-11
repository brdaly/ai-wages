"""Offline integrity checks for the frozen, attributed analysis inputs."""
import csv
import hashlib
import io
import json
from pathlib import Path


def validate_inputs(data_dir=Path("data")):
    """Reject an altered or truncated snapshot before publishing any results."""
    data_dir = Path(data_dir)
    manifest_bytes = (data_dir / "input_manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    for entry in manifest["files"]:
        path = data_dir / entry["filename"]
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != entry["sha256"]:
            raise ValueError(f"Input checksum mismatch: {path}; see data/SOURCES.md")
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8")))
        if reader.fieldnames != entry["columns"]:
            raise ValueError(f"Unexpected columns: {path}")
        rows = list(reader)
        if len(rows) != entry["rows"] or any(
            None in row or any(value is None for value in row.values()) for row in rows
        ):
            raise ValueError(f"Truncated or unexpected rows: {path}")
    return {
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "source_revision": manifest["source_revision"],
        "verified_on": manifest["verified_on"],
    }
