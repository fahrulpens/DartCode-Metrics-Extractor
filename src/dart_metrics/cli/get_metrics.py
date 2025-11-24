#!/usr/bin/env python3
import argparse, sys
from pathlib import Path
from metrics.all_metrics import METRICS, ALIASES

def normalize_key(k: str) -> str:
    kk = k.strip().lower()
    if kk in METRICS:
        return kk
    return ALIASES.get(kk, kk)

def main():
    ap = argparse.ArgumentParser(description="Print selected metrics for a Dart/Flutter snippet")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--stdin", action="store_true")
    src.add_argument("--file", type=str)
    ap.add_argument("--metrics", type=str, help="Comma-separated labels (e.g., LoC,NoF,CR)")
    ap.add_argument("--metric", action="append", help="Repeatable; each is a label (order preserved)")
    ap.add_argument("--all", action="store_true", help="Print all supported metrics")
    args = ap.parse_args()

    # Build ordered list of requested metrics
    order = []
    if args.all:
        order.extend(list(METRICS.keys()))         # LoC, NoM, NoP, CC, MND, NoF, CR, NoW, MNW, SCCL
    if args.metrics:
        order.extend([m.strip() for m in args.metrics.split(",") if m.strip()])
    if args.metric:
        order.extend(args.metric)

    if not order:
        raise SystemExit("ERROR: specify --metrics/--metric or use --all")

    code = sys.stdin.read() if args.stdin else Path(args.file).read_text(encoding="utf-8")

    for m in order:
        key = normalize_key(m)
        if key not in METRICS:
            raise SystemExit(f"ERROR: metric '{m}' not implemented")
        label, func = METRICS[key]
        print(f"{label} : {func(code)}")

if __name__ == "__main__":
    main()
