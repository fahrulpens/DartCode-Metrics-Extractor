# DartCode Metrics Extractor

## Overview
This toolkit extracts 20 Dart/Flutter UI metrics from code snippets (not whole projects). You can:
•	analyze a single snippet from stdin or a .dart file, and
•	batch-process an Excel sheet with sample_id and code_snippet columns.

## layout
```
data_examples/
  rawdata.xlsx
  rawdata.metrics.xlsx
src/
  dart_metrics/
    metrics/
      common.py        # helpers (comment stripping, brace/paren matchers)
      methods.py       # NoM, NoP (linear scanner – Flutter-safe)
      complexity.py    # CC (McCabe baseline 1 by default)
      nesting.py       # MND
      fields.py        # NoF
      comments.py      # CR
      widgets.py       # NoW, MNW, SCCL
      side_effects.py  # sStC, PBM, FAC, MC, API
      runtime_effects.py # DbC, SyncIO, ImgC, AsyncUI, TmrStr
      all_metrics.py   # central registry (labels, aliases)
    cli/
      get_metric.py    # print a single metric
      get_metrics.py   # print selected metrics (supports --all)
      batch_excel.py   # NEW: compute metrics for every row in an Excel file
```

## Install (macOS Terminal)
```bash
# Python 3.9+ recommended
python3 -m pip install pandas openpyxl
```

## How to run (single snippet)
```bash
# 1) All metrics in one shot
python3 -m cli.get_metrics --all --stdin <<'DART'
Widget build(BuildContext c) {
  return MaterialApp(home: Splash());
}
DART

# 2) Custom metric set (order preserved)
python3 -m cli.get_metrics --metrics LoC,NoM,NoP,CC,MND,NoF,CR,NoW,MNW,SCCL --file snippet.dart

# You can also repeat flags:
python3 -m cli.get_metrics --metric LoC --metric DbC --metric API --stdin <<'DART'
...snippet...
DART

# 3) Single metric (quiet)
python3 -m cli.get_metric --metric CC --file snippet.dart
```

## How to run (Excel batch)
### Required input
An Excel file (.xlsx/.xls) with at least:
•	sample_id
•	code_snippet

```bash
# All 20 metrics on sheet index 0
python3 -m cli.batch_excel --input /path/to/data.xlsx
Output: /path/to/data.metrics.xlsx with columns:
sample_id, LoC, NoM, NoP, CC, MND, NoF, CR, NoW, MNW, SCCL,
sStC, PBM, FAC, MC, API, DbC, SyncIO, ImgC, AsyncUI, TmrStr

Options you’ll use
# Select a sheet by name or index
python3 -m cli.batch_excel --input data.xlsx --sheet "Sheet1"
python3 -m cli.batch_excel --input data.xlsx --sheet 2

# Custom column names
python3 -m cli.batch_excel --input data.xlsx --id-col ID --code-col snippet

# Save to a specific file
python3 -m cli.batch_excel --input data.xlsx --output results.metrics.xlsx

# Include the original code in the output
python3 -m cli.batch_excel --input data.xlsx --include-code

# Only a subset of metrics (order preserved)
python3 -m cli.batch_excel --input data.xlsx --metrics LoC,CC,API,DbC
```

# The 20 metrics — what each checks
```bash
1.	Line of Code (LoC) — label LoC
What it checks: Non-empty, non-comment lines.
Counts: Any line with tokens after stripping comments.
Ignores: Blank lines, // …, /* … */.
Module: comments.py :: count_loc
2.	Number of Methods (NoM) — label NoM
What it checks: Declarations that look like name(...) { … } (functions/methods/constructors).
Counts: Any identifier ( … ) { that isn’t a control keyword (if/for/while/switch/catch/else).
Module: methods.py :: number_of_methods
3.	Number of Parameters (NoP) — label NoP
What it checks: Maximum number of parameters among all methods found by NoM.
Counts: Positional + named + optional; ignores commas inside <…>, {…}, […], (…), and strings.
Module: methods.py :: max_number_of_params
4.	Cyclomatic Complexity (CC) — label CC
What it checks: Decision points, then adds 1 (McCabe’s baseline).
Counts: if, for, while, case, catch, &&, ||, ternary ?:.
Change baseline: In complexity.py, switch return 1 + decisions → return decisions.
Module: complexity.py :: cyclomatic_complexity
5.	Maximum Nesting Depth (MND) — label MND
What it checks: Deepest {…} nesting minus the outermost scope.
Counts: Block depth within the snippet (strings are ignored correctly).
Module: nesting.py :: max_nesting_depth
6.	Number of Fields (NoF) — label NoF
What it checks: Class-level fields in class { … } bodies.
Counts: int a, b = 2;, final x = …;.
Ignores: Methods/getters/abstract signatures (we skip top-level stmts that have ().
Module: fields.py :: number_of_fields
7.	Comment Ratio (CR) — label CR
What it checks: comment_lines / LoC rounded to 3 decimals.
Module: comments.py :: comment_ratio
8.	Number of Widget (NoW) — label NoW
What it checks: Capitalized constructor calls: CapitalizedName( (heuristic).
Counts: MaterialApp(, Padding(, Splash(); also capitalized non-widgets like ThemeData(.
Module: widgets.py :: number_of_widgets
9.	Maximum Nesting Widget Tree Depth (MNW) — label MNW
What it checks: Maximum depth of capitalized constructor nesting: A(B(C())) → 3.
Module: widgets.py :: max_widget_nesting
10.	Single-Child Wrapper Chain Length (SCCL) — label SCCL
What it checks: Longest nested chain of child: CapitalizedCtor( … ).
Module: widgets.py :: child_chain_max_depth
11.	SetState Call Count (sStC) — label sStC
What it checks: setState( occurrences (after comment stripping).
Module: side_effects.py :: setstate_call_count
12.	Provider/Bloc Mutation Count (PBM) — label PBM
What it checks: State mutations through common state managers.
Counts (examples):
•	context.read<T>(...).add(...) / .emit(...)
•	context.read<T>(...).prop = …
•	BlocProvider.of<T>(context).add/emit(...)
•	Provider.of<T>(context).prop = …
•	ref.read(provider).state = … (Riverpod)
Module: side_effects.py :: provider_bloc_mutation_count
13.	Field Assignment Count (FAC) — label FAC
What it checks: Writes to class fields inside UI logic.
Counts: this.count = …;, widget.flag = …;
Ignores: Local variable assignments without this./widget.
Module: side_effects.py :: field_assignment_count
14.	Mutable Collection Modification Count (MC) — label MC
What it checks: List/Map mutations.
Counts: .add(...), .addAll(...), .insert(...), .remove(...), .removeWhere(...), .clear(...), and x[ ... ] = ....
Module: side_effects.py :: mutable_collection_mod_count
15.	API Call Count (API) — label API
What it checks: Common network calls.
Counts: http.get/post/put/delete/patch/head(…), Dio().get/post/…, dio.get/post/…, WebSocket.connect(…).
Module: side_effects.py :: api_call_count
16.	Database Call Count (DbC) — label DbC
What it checks: Typical DB/storage operations (sqflite, Hive, SharedPreferences, Drift/Moor, Sembast, generic db.*).
Counts:
•	Generic: db.insert/update/delete/query/execute/transaction(…)
•	Hive: Hive.openBox(…), box.put/get/add/delete/clear(…)
•	SharedPreferences: SharedPreferences.getInstance(), then .set*/get*
•	Drift/Moor: into(...).insert(...), select(...)(...), update(...).write(...), delete(...).go(...)
•	Sembast: store.record(...).put/get/delete(...)
Note: Your current config includes handle acquisition (openBox, getInstance) — that’s why your example was DbC : 5.
Module: runtime_effects.py :: database_call_count
17.	Synchronous I/O Count (SyncIO) — label SyncIO
What it checks: Blocking file ops from dart:io and sleep().
Counts: readAsStringSync, readAsBytesSync, writeAs*Sync, openSync, renameSync, deleteSync, createSync, existsSync, statSync, copySync, sleep(...).
Module: runtime_effects.py :: sync_io_count
18.	Image Codec Call Count (ImgC) — label ImgC
What it checks: Image decode/codec usage that may be heavy for UI.
Counts: instantiateImageCodec(...), decodeImageFromList(...), decodeImage(...), ImageDescriptor.encoded(...).
Module: runtime_effects.py :: image_codec_count
19.	Async/Await in UI (AsyncUI) — label AsyncUI
What it checks: await occurrences in the snippet (comment-stripped).
Current scope: Any await in the snippet (not limited to build() only).
Module: runtime_effects.py :: async_await_ui_count
20.	Timer/Stream Init Count (TmrStr) — label TmrStr
What it checks: Timer/stream creations (often long-lived).
Counts: Timer(...), Timer.periodic(...), StreamController(...), Stream.periodic(...), RxDart BehaviorSubject/PublishSubject/ReplaySubject(...).
Module: runtime_effects.py :: timer_stream_init_count
All detectors ignore commented-out code. Heuristics are conservative and Flutter-aware; we can tighten/extend patterns for your corpus if needed.
```

## Quick cheatsheet
```bash
# All metrics, stdin
python3 -m cli.get_metrics --all --stdin <<'DART'
...snippet...
DART

# Subset, file
python3 -m cli.get_metrics --metrics LoC,CC,API,DbC --file snippet.dart

# Single metric
python3 -m cli.get_metric --metric MNW --stdin <<'DART'
return Container(child: Padding(child: Center()));
DART

# Excel batch: all metrics
python3 -m cli.batch_excel --input data.xlsx

# Excel batch: custom sheet, custom output, include original code
python3 -m cli.batch_excel --input data.xlsx --sheet "Sheet1" --output results.xlsx --include-code
```