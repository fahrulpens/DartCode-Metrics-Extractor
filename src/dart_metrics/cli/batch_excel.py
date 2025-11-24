
#!/usr/bin/env python3
import argparse
import math
import sys
from pathlib import Path

import pandas as pd

from metrics.all_metrics import METRICS, ALIASES

# Default order for all 20 metrics (by internal keys in METRICS)
ALL_KEYS = [
    "loc","nom","nop","cc","mnd","nof","cr","now","mnw","sccl",
    "sstc","pbm","fac","mc","api","dbc","syncio","imgc","asyncui","tmrstr"
]

def normalize_key(k: str) -> str:
    kk = k.strip().lower()
    if kk in METRICS:
        return kk
    return ALIASES.get(kk, kk)

def compute_for_code(code: str, keys):
    if code is None or (isinstance(code, float) and math.isnan(code)):
        out = {}
        for key in keys:
            label, _ = METRICS[key]
            out[label] = 0
        return out
    s = str(code)
    out = {}
    for key in keys:
        label, func = METRICS[key]
        try:
            val = func(s)
        except Exception:
            val = float("nan")
        out[label] = val
    return out

def main():
    ap = argparse.ArgumentParser(
        description="Compute Dart/Flutter snippet metrics from an Excel dataset."
    )
    ap.add_argument("--input", "-i", required=True, help="Path to input Excel (.xlsx/.xls)")
    ap.add_argument("--sheet", default=0, help="Worksheet index or name (default: 0)")
    ap.add_argument("--id-col", default="sample_id", help="ID column name (default: sample_id)")
    ap.add_argument("--code-col", default="code_snippet", help="Code column name (default: code_snippet)")
    ap.add_argument("--output", "-o", help="Path to output Excel (default: <input>.metrics.xlsx)")
    ap.add_argument("--metrics", help="Comma-separated labels or keys (e.g., LoC,NoM,NoP,...)")
    ap.add_argument("--metric", action="append", help="Repeatable; each a label or key (order preserved)")
    ap.add_argument("--all", action="store_true", help="Use all 20 metrics (default if no list provided)")
    ap.add_argument("--include-code", action="store_true", help="Include code_snippet column in the output")
    args = ap.parse_args()

    order_keys = []
    if args.metrics:
        order_keys.extend([normalize_key(m) for m in args.metrics.split(",") if m.strip()])
    if args.metric:
        order_keys.extend([normalize_key(m) for m in args.metric])
    if args.all or not order_keys:
        order_keys = ALL_KEYS

    bad = [k for k in order_keys if k not in METRICS]
    if bad:
        raise SystemExit(f"Unknown metric key(s): {bad}")

    in_path = Path(args.input)
    if not args.output:
        out_path = in_path.with_suffix("")
        out_path = Path(str(out_path) + ".metrics.xlsx")
    else:
        out_path = Path(args.output)

    sheet = args.sheet
    try:
        if isinstance(sheet, str) and sheet.isdigit():
            sheet = int(sheet)
    except Exception:
        pass

    df = pd.read_excel(in_path, sheet_name=sheet)

    if args.id_col not in df.columns:
        raise SystemExit(f"ID column '{args.id_col}' not found in Excel columns: {list(df.columns)}")
    if args.code_col not in df.columns:
        raise SystemExit(f"Code column '{args.code_col}' not found in Excel columns: {list(df.columns)}")

    records = []
    id_vals = df[args.id_col].tolist()
    code_vals = df[args.code_col].tolist()

    labels = [METRICS[k][0] for k in order_keys]

    for sid, code in zip(id_vals, code_vals):
        row = {"sample_id": sid}
        row.update(compute_for_code(code, order_keys))
        if args.include_code:
            row["code_snippet"] = code
        records.append(row)

    out_df = pd.DataFrame.from_records(records)

    col_order = ["sample_id"] + labels + (["code_snippet"] if args.include_code else [])
    col_order = [c for c in col_order if c in out_df.columns]

    out_df = out_df[col_order]
    out_df.to_excel(out_path, index=False)
    print(f"Done. Wrote metrics for {len(out_df)} rows to: {out_path}")

if __name__ == "__main__":
    main()
