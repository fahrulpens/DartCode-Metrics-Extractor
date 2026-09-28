#!/usr/bin/env python3
from pathlib import Path
import json
import subprocess
import sys
import tempfile

import pandas as pd


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main():
    repo = Path(__file__).resolve().parents[1]
    work = Path(tempfile.mkdtemp(prefix="dartmetrics_test_"))
    rows = [
        {"sample_id": "000000001", "snippet": "Widget build(BuildContext c) { return Text('a'); }"},
        {"sample_id": "000000002", "snippet": "void f(){ if (x) { print(x); } }"},
    ]
    csvp = work / "sample.csv"
    jsonp = work / "sample.json"
    xlsp = work / "sample.xlsx"
    pd.DataFrame(rows).to_csv(csvp, index=False)
    jsonp.write_text(json.dumps({"metadata": {"test": True}, "data": rows}), encoding="utf-8")
    pd.DataFrame(rows).to_excel(xlsp, index=False)

    dart_dir = repo / "src" / "dart_metrics"
    outs = []
    for src in (csvp, jsonp, xlsp):
        out = work / f"{src.stem}_{src.suffix[1:]}.metrics.csv"
        cmd = [sys.executable, "-m", "cli.batch_dataset", "--input", str(src), "--code-col", "snippet", "--output", str(out)]
        p = run(cmd, dart_dir)
        if p.returncode != 0:
            print(p.stdout); print(p.stderr, file=sys.stderr); return 1
        df = pd.read_csv(out, dtype={"sample_id": str})
        assert df["sample_id"].tolist() == ["000000001", "000000002"]
        assert len(df.columns) == 21
        manifest = Path(str(out) + ".manifest.json")
        v = run([sys.executable, "-m", "cli.validate_metrics_output", "--source", str(src), "--metrics", str(out), "--manifest", str(manifest)], dart_dir)
        if v.returncode != 0:
            print(v.stdout); print(v.stderr, file=sys.stderr); return 1
        outs.append(out)

    # Metric output should be identical across input encodings.
    dfs = [pd.read_csv(p, dtype={"sample_id": str}) for p in outs]
    assert dfs[0].equals(dfs[1]) and dfs[1].equals(dfs[2])
    print("PASS: CSV/JSON/Excel produce identical metric tables and preserve IDs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
