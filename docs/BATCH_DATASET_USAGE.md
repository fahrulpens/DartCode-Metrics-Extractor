# Batch Dataset Metric Extraction

This repository historically exposed `cli.batch_excel`. The added `cli.batch_dataset`
keeps all 20 metric implementations unchanged while accepting CSV, JSON, or Excel.

## Recommended research workflow

Run from `src/dart_metrics`:

```bash
python3 -m cli.batch_dataset \
  --input /path/to/final_dataset.csv \
  --id-col sample_id \
  --code-col snippet \
  --output /path/to/final_dataset.metrics.csv
```

Object-style JSON such as `{ "metadata": ..., "data": [...] }` is supported:

```bash
python3 -m cli.batch_dataset \
  --input /path/to/final_dataset.json \
  --json-data-key data \
  --id-col sample_id \
  --code-col snippet \
  --output /path/to/final_dataset.metrics.csv
```

The default scientific behavior is strict:

- sample IDs are preserved as strings;
- duplicate sample IDs are rejected;
- empty snippets are rejected;
- metric exceptions abort the run instead of silently accepting NaN;
- output defaults to CSV;
- a SHA-256 reproducibility manifest is written beside the output.

Validate after extraction:

```bash
python3 -m cli.validate_metrics_output \
  --source /path/to/final_dataset.csv \
  --metrics /path/to/final_dataset.metrics.csv \
  --manifest /path/to/final_dataset.metrics.csv.manifest.json
```

Do not join annotation labels into the metric extraction input merely to compute
metrics. Join by `sample_id` only after both the annotation dataset and metric artifact
are independently frozen and validated.
