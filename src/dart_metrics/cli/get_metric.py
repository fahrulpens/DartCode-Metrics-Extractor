
#!/usr/bin/env python3
import argparse, sys
from pathlib import Path
from metrics.all_metrics import METRICS, ALIASES

def normalize_key(k: str) -> str:
    kk = k.strip().lower()
    if kk in METRICS: return kk
    return ALIASES.get(kk, kk)

def main():
    ap = argparse.ArgumentParser(description="Print a single metric value for a Dart/Flutter snippet")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--stdin", action="store_true")
    src.add_argument("--file", type=str)
    ap.add_argument("--metric", required=True, help="e.g., LoC, NoF, CR, ...")
    args = ap.parse_args()

    code = sys.stdin.read() if args.stdin else Path(args.file).read_text(encoding="utf-8")
    key = normalize_key(args.metric)
    if key not in METRICS:
        raise SystemExit(f"ERROR: metric '{args.metric}' not implemented")
    label, func = METRICS[key]
    print(f"{label} : {func(code)}")

if __name__ == "__main__":
    main()
