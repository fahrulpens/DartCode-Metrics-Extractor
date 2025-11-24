# dart_metrics_modular/metrics/runtime_effects.py
import re
from .common import remove_comments

__all__ = [
    "database_call_count",     # DbC
    "sync_io_count",           # SyncIO
    "image_codec_count",       # ImgC
    "async_await_ui_count",    # AsyncUI
    "timer_stream_init_count", # TmrStr
]

# --- DbC: Database call count (sqflite, Hive, SharedPreferences, Drift, Sembast, generic db.*) ---
_DBC_RE = re.compile(
    r"""
    (
      \b(?:db|database)\s*\.\s*(?:rawQuery|query|insert|update|delete|execute|transaction)\s*\(   # generic db.*
    | \bHive\s*\.\s*(?:openBox|box)\s*\(                                                         # Hive
    | \bbox\s*\.\s*(?:put|get|add|delete|clear|putAll|deleteAll)\s*\(
    | \bSharedPreferences\s*\.\s*getInstance\s*\(                                               # shared_prefs
    | \b(?:prefs|preferences)\s*\.\s*(?:get|set|remove|clear)\w*\s*\(
    | \binto\s*\([^)]+\)\s*\.\s*(?:insert|insertReturning|insertReturningOrThrow)\s*\(          # Drift/Moor
    | \bselect\s*\([^)]+\)\s*\(
    | \bcustom(?:Select|Insert|Update)\s*\(
    | \bupdate\s*\([^)]+\)\s*\.\s*write\s*\(
    | \bdelete\s*\([^)]+\)\s*\.\s*(?:go|where)\s*\(
    | \bstore\s*\.\s*record\s*\([^)]+\)\s*\.\s*(?:put|get|delete)\s*\(                           # Sembast
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

def database_call_count(code: str) -> int:
    s = remove_comments(code)
    return len(_DBC_RE.findall(s))

# --- SyncIO: Synchronous I/O (dart:io) ---
_SYNCIO_RE = re.compile(
    r"""
    \b(?:readAsBytesSync|readAsStringSync|readSync|writeAsStringSync|
       writeAsBytesSync|writeSync|flushSync|openSync|renameSync|deleteSync|
       createSync|existsSync|statSync|copySync)\s*\(
    | \bsleep\s*\(
    """,
    re.VERBOSE,
)

def sync_io_count(code: str) -> int:
    s = remove_comments(code)
    return len(_SYNCIO_RE.findall(s))

# --- ImgC: Image decoding / codec usage ---
_IMGC_RE = re.compile(
    r"""
    \b(?:instantiateImageCodec|decodeImageFromList|decodeImage)\s*\(
    | \bImageDescriptor\.encoded\s*\(
    """,
    re.VERBOSE,
)

def image_codec_count(code: str) -> int:
    s = remove_comments(code)
    return len(_IMGC_RE.findall(s))

# --- AsyncUI: await occurrences (UI path) ---
_AWAIT_RE = re.compile(r"\bawait\b")

def async_await_ui_count(code: str) -> int:
    s = remove_comments(code)
    return len(_AWAIT_RE.findall(s))

# --- TmrStr: Timer / Stream initialization ---
_TMRSTR_RE = re.compile(
    r"""
    \bTimer(?:\.periodic)?\s*\(
    | \bStreamController(?:<[^>]+>)?\s*\(
    | \bStream\.periodic\s*\(
    | \b(?:BehaviorSubject|PublishSubject|ReplaySubject)\s*\(     # RxDart
    """,
    re.VERBOSE,
)

def timer_stream_init_count(code: str) -> int:
    s = remove_comments(code)
    return len(_TMRSTR_RE.findall(s))
