#!/usr/bin/env python3
"""Strictly validate metric output against its source dataset and manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

EXPECTED_METRICS = [
    "LoC", "NoM", "NoP", "CC", "MND", "NoF", "CR", "NoW", "MNW", "SCCL",
    "sStC", "PBM", "FAC", "MC", "API", "DbC", "SyncIO", "ImgC", "AsyncUI", "TmrStr",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_ids(path: Path, id_col: str, json_data_key: str) -> list[str]:
    ext = path.suffix.lower()
    if ext == ".csv":
        df = pd.read_csv(path, dtype=str, keep_default_na=False, usecols=[id_col])
    elif ext in (".xlsx", ".xls"):
        df = pd.read_excel(path, dtype=str, keep_default_na=False, usecols=[id_col])
    elif ext == ".json":
        obj = json.loads(path.read_text(encoding="utf-8"))
        rows = obj if isinstance(obj, list) else obj[json_data_key]
        df = pd.DataFrame.from_records(rows)[[id_col]]
    else:
        raise SystemExit(f"Unsupported source extension: {ext}")
    return df[id_col].map(str).tolist()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--metrics", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--id-col", default="sample_id")
    ap.add_argument("--json-data-key", default="data")
    args = ap.parse_args()

    source = Path(args.source).expanduser().resolve()
    metrics = Path(args.metrics).expanduser().resolve()
    manifest_path = Path(args.manifest).expanduser().resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if metrics.suffix.lower() == ".csv":
        mdf = pd.read_csv(metrics, dtype={"sample_id": str})
    elif metrics.suffix.lower() == ".json":
        mdf = pd.read_json(metrics, dtype={"sample_id": str})
    elif metrics.suffix.lower() in (".xlsx", ".xls"):
        mdf = pd.read_excel(metrics, dtype={"sample_id": str})
    else:
        raise SystemExit(f"Unsupported metrics extension: {metrics.suffix}")

    source_ids = read_ids(source, args.id_col, args.json_data_key)
    metric_ids = mdf["sample_id"].map(str).tolist()
    errors: list[str] = []

    if len(source_ids) != len(metric_ids):
        errors.append(f"row count mismatch source={len(source_ids)} metrics={len(metric_ids)}")
    if source_ids != metric_ids:
        errors.append("sample_id order/content differs from source")
    if len(set(metric_ids)) != len(metric_ids):
        errors.append("duplicate sample_id in metrics output")

    missing_cols = [c for c in EXPECTED_METRICS if c not in mdf.columns]
    if missing_cols:
        errors.append(f"missing metric columns: {missing_cols}")
    else:
        numeric = mdf[EXPECTED_METRICS].apply(pd.to_numeric, errors="coerce")
        bad = int(numeric.isna().sum().sum())
        if bad:
            errors.append(f"found {bad} non-numeric/NaN metric cells")

    if sha256_file(source) != manifest["input"]["sha256"]:
        errors.append("source SHA256 differs from manifest")
    if sha256_file(metrics) != manifest["output"]["sha256"]:
        errors.append("metrics SHA256 differs from manifest")
    if len(metric_ids) != int(manifest["dataset"]["row_count"]):
        errors.append("metrics row count differs from manifest")

    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        raise SystemExit(1)

    print("PASS")
    print(f"rows={len(metric_ids)}")
    print(f"unique_sample_ids={len(set(metric_ids))}")
    print(f"metrics={len(EXPECTED_METRICS)}")
    print(f"source_sha256={sha256_file(source)}")
    print(f"metrics_sha256={sha256_file(metrics)}")


if __name__ == "__main__":
    main()
