#!/usr/bin/env python3
"""Batch metric extraction for CSV, JSON, and Excel snippet datasets.

This wrapper intentionally leaves the 20 metric implementations unchanged. It
adds format-neutral I/O, deterministic ID handling, strict validation, and a
reproducibility manifest suitable for research datasets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from metrics.all_metrics import METRICS, ALIASES

ALL_KEYS = [
    "loc", "nom", "nop", "cc", "mnd", "nof", "cr", "now", "mnw", "sccl",
    "sstc", "pbm", "fac", "mc", "api", "dbc", "syncio", "imgc", "asyncui", "tmrstr",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head(start: Path) -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=start, stderr=subprocess.DEVNULL, text=True
        ).strip()
        return out or None
    except Exception:
        return None


def normalize_key(k: str) -> str:
    kk = k.strip().lower()
    if kk in METRICS:
        return kk
    return ALIASES.get(kk, kk)


def _read_json_payload(path: Path, json_data_key: str) -> pd.DataFrame:
    with path.open("r", encoding="utf-8") as f:
        obj = json.load(f)
    if isinstance(obj, list):
        rows = obj
    elif isinstance(obj, dict):
        if json_data_key not in obj:
            raise SystemExit(
                f"JSON object does not contain data key '{json_data_key}'. "
                f"Top-level keys: {list(obj.keys())}"
            )
        rows = obj[json_data_key]
        if not isinstance(rows, list):
            raise SystemExit(f"JSON key '{json_data_key}' must contain a list of records.")
    else:
        raise SystemExit("JSON input must be a list of records or an object containing a record list.")
    return pd.DataFrame.from_records(rows)


def read_dataset(path: Path, fmt: str, sheet: str | int, json_data_key: str) -> pd.DataFrame:
    fmt = fmt.lower()
    if fmt == "auto":
        ext = path.suffix.lower()
        fmt = {
            ".csv": "csv",
            ".json": "json",
            ".xlsx": "excel",
            ".xls": "excel",
        }.get(ext, "")
        if not fmt:
            raise SystemExit(f"Cannot infer input format from extension '{ext}'. Use --format.")

    if fmt == "csv":
        # dtype=str protects IDs with leading zeros. Code remains exact text.
        return pd.read_csv(path, dtype=str, keep_default_na=False)
    if fmt == "json":
        return _read_json_payload(path, json_data_key=json_data_key)
    if fmt == "excel":
        return pd.read_excel(path, sheet_name=sheet, dtype=str, keep_default_na=False)
    raise SystemExit(f"Unsupported format: {fmt}")


def compute_for_code(code: Any, keys: list[str]) -> tuple[dict[str, Any], list[str]]:
    if code is None or (isinstance(code, float) and math.isnan(code)):
        return ({METRICS[k][0]: 0 for k in keys}, [])
    s = str(code)
    out: dict[str, Any] = {}
    errors: list[str] = []
    for key in keys:
        label, func = METRICS[key]
        try:
            out[label] = func(s)
        except Exception as exc:
            out[label] = float("nan")
            errors.append(f"{label}:{type(exc).__name__}:{exc}")
    return out, errors


def write_output(df: pd.DataFrame, path: Path, fmt: str) -> str:
    fmt = fmt.lower()
    if fmt == "auto":
        ext = path.suffix.lower()
        fmt = {".csv": "csv", ".json": "json", ".xlsx": "excel", ".xls": "excel"}.get(ext, "")
        if not fmt:
            raise SystemExit("Cannot infer output format; use --output-format.")
    path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "csv":
        df.to_csv(path, index=False, encoding="utf-8", lineterminator="\n")
    elif fmt == "json":
        path.write_text(df.to_json(orient="records", force_ascii=False, indent=2), encoding="utf-8")
    elif fmt == "excel":
        df.to_excel(path, index=False)
    else:
        raise SystemExit(f"Unsupported output format: {fmt}")
    return fmt


def default_output_path(input_path: Path) -> Path:
    return input_path.with_name(input_path.stem + ".metrics.csv")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Compute the 20 Dart/Flutter snippet metrics from CSV, JSON, or Excel datasets."
    )
    ap.add_argument("--input", "-i", required=True)
    ap.add_argument("--format", choices=["auto", "csv", "json", "excel"], default="auto")
    ap.add_argument("--sheet", default=0, help="Excel worksheet index/name; ignored for CSV/JSON")
    ap.add_argument("--json-data-key", default="data", help="Record-list key for object-style JSON")
    ap.add_argument("--id-col", default="sample_id")
    ap.add_argument("--code-col", default="code_snippet")
    ap.add_argument("--output", "-o")
    ap.add_argument("--output-format", choices=["auto", "csv", "json", "excel"], default="auto")
    ap.add_argument("--manifest", help="Manifest path (default: <output>.manifest.json)")
    ap.add_argument("--metrics", help="Comma-separated metric labels/keys")
    ap.add_argument("--metric", action="append", help="Repeatable metric label/key")
    ap.add_argument("--all", action="store_true", help="Use all 20 metrics (default)")
    ap.add_argument("--include-code", action="store_true")
    ap.add_argument("--allow-duplicate-ids", action="store_true")
    ap.add_argument("--allow-empty-code", action="store_true")
    ap.add_argument("--allow-metric-errors", action="store_true")
    args = ap.parse_args()

    keys: list[str] = []
    if args.metrics:
        keys.extend(normalize_key(m) for m in args.metrics.split(",") if m.strip())
    if args.metric:
        keys.extend(normalize_key(m) for m in args.metric)
    if args.all or not keys:
        keys = list(ALL_KEYS)
    bad = [k for k in keys if k not in METRICS]
    if bad:
        raise SystemExit(f"Unknown metric key(s): {bad}")

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    sheet: str | int = args.sheet
    if isinstance(sheet, str) and sheet.isdigit():
        sheet = int(sheet)

    df = read_dataset(input_path, args.format, sheet, args.json_data_key)
    if args.id_col not in df.columns:
        raise SystemExit(f"ID column '{args.id_col}' not found. Columns: {list(df.columns)}")
    if args.code_col not in df.columns:
        raise SystemExit(f"Code column '{args.code_col}' not found. Columns: {list(df.columns)}")

    # Canonicalize IDs as text; never coerce to integer.
    ids = df[args.id_col].map(lambda x: "" if x is None else str(x))
    codes = df[args.code_col].map(lambda x: "" if x is None else str(x))

    if (ids == "").any():
        raise SystemExit(f"Found {(ids == '').sum()} empty sample IDs.")
    dup_mask = ids.duplicated(keep=False)
    if dup_mask.any() and not args.allow_duplicate_ids:
        examples = ids[dup_mask].head(10).tolist()
        raise SystemExit(f"Found {dup_mask.sum()} rows with duplicate sample IDs. Examples: {examples}")
    empty_code = codes.str.len().eq(0)
    if empty_code.any() and not args.allow_empty_code:
        raise SystemExit(f"Found {int(empty_code.sum())} rows with empty code snippets.")

    labels = [METRICS[k][0] for k in keys]
    records: list[dict[str, Any]] = []
    metric_error_rows: list[dict[str, Any]] = []

    total = len(df)
    for idx, (sid, code) in enumerate(zip(ids.tolist(), codes.tolist()), start=1):
        vals, errors = compute_for_code(code, keys)
        row: dict[str, Any] = {"sample_id": sid}
        row.update(vals)
        if args.include_code:
            row["code_snippet"] = code
        records.append(row)
        if errors:
            metric_error_rows.append({"sample_id": sid, "errors": errors})
        if total >= 1000 and (idx % 500 == 0 or idx == total):
            print(f"Processed {idx}/{total}", file=sys.stderr)

    if metric_error_rows and not args.allow_metric_errors:
        preview = metric_error_rows[:5]
        raise SystemExit(
            f"Metric computation errors occurred for {len(metric_error_rows)} rows; "
            f"refusing partial scientific output. Examples: {preview}. "
            "Use --allow-metric-errors only for debugging."
        )

    out_df = pd.DataFrame.from_records(records)
    col_order = ["sample_id"] + labels + (["code_snippet"] if args.include_code else [])
    out_df = out_df[col_order]

    out_path = Path(args.output).expanduser().resolve() if args.output else default_output_path(input_path)
    if args.output is None:
        out_path = out_path.resolve()
    output_fmt = write_output(out_df, out_path, args.output_format)

    manifest_path = (
        Path(args.manifest).expanduser().resolve()
        if args.manifest
        else Path(str(out_path) + ".manifest.json")
    )

    script_path = Path(__file__).resolve()
    repo_guess = script_path.parents[3] if len(script_path.parents) >= 4 else script_path.parent
    manifest = {
        "schema": "dart_metrics_batch_dataset_manifest_v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "input": {
            "path": str(input_path),
            "filename": input_path.name,
            "sha256": sha256_file(input_path),
            "format": args.format,
            "id_col": args.id_col,
            "code_col": args.code_col,
            "json_data_key": args.json_data_key if input_path.suffix.lower() == ".json" else None,
        },
        "output": {
            "path": str(out_path),
            "filename": out_path.name,
            "sha256": sha256_file(out_path),
            "format": output_fmt,
        },
        "dataset": {
            "row_count": int(len(out_df)),
            "unique_sample_ids": int(out_df["sample_id"].nunique(dropna=False)),
            "duplicate_id_rows": int(out_df["sample_id"].duplicated(keep=False).sum()),
            "empty_code_rows": int(empty_code.sum()),
        },
        "metrics": {
            "keys": keys,
            "labels": labels,
            "count": len(labels),
            "metric_error_rows": len(metric_error_rows),
        },
        "implementation": {
            "script": str(script_path),
            "script_sha256": sha256_file(script_path),
            "git_commit": git_head(repo_guess),
            "python": sys.version,
            "pandas": pd.__version__,
        },
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"PASS: wrote {len(out_df)} rows x {len(labels)} metrics to {out_path}")
    print(f"Output SHA256: {manifest['output']['sha256']}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
