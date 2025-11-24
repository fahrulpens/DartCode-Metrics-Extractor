# dart_metrics_modular/metrics/side_effects.py
import re
from .common import remove_comments

__all__ = [
    "setstate_call_count",
    "provider_bloc_mutation_count",
    "field_assignment_count",
    "mutable_collection_mod_count",
    "api_call_count",
]

# --- sStC: setState() calls ---------------------------------------------------
_SETSTATE_RE = re.compile(r'\bsetState\s*\(')

def setstate_call_count(code: str) -> int:
    s = remove_comments(code)
    return len(_SETSTATE_RE.findall(s))

# --- PBM: Provider/Bloc/Riverpod mutations -----------------------------------
_PBM_RE = re.compile(
    r'''
    (                                         # group of patterns indicating mutations/dispatch
      context\.(?:read|watch)\s*<[^>]+>\s*\([^)]*\)\s*\.\s*(?:add|emit)\s*\(   # context.read<T>(...).add/emit(...)
    | context\.(?:read|watch)\s*<[^>]+>\s*\([^)]*\)\s*\.\s*[A-Za-z_]\w*\s*=    # context.read<T>(...).prop =
    | BlocProvider\.of\s*<[^>]+>\s*\([^)]*\)\s*\.\s*(?:add|emit)\s*\(          # BlocProvider.of<T>(...).add/emit(...)
    | Provider\.of\s*<[^>]+>\s*\([^)]*\)\s*\.\s*[A-Za-z_]\w*\s*=               # Provider.of<T>(...).prop =
    | ref\.read(?:<[^>]+>)?\s*\([^)]*\)\.state\s*=                             # Riverpod: ref.read(...).state =
    )
    ''',
    re.IGNORECASE | re.VERBOSE,
)

def provider_bloc_mutation_count(code: str) -> int:
    s = remove_comments(code)
    return len(_PBM_RE.findall(s))

# --- FAC: assignments to class fields in UI code ------------------------------
# Heuristic: count assignments to 'this.<field> =' or 'widget.<field> ='
_FAC_RE = re.compile(r'\b(?:this|widget)\s*\.\s*[A-Za-z_]\w*\s*=')

def field_assignment_count(code: str) -> int:
    s = remove_comments(code)
    return len(_FAC_RE.findall(s))

# --- MC: mutable collection modifications -------------------------------------
# list.add/insert/remove/clear, map[...] = ..., list[index] = ...
_MC_RE = re.compile(
    r'''
    \.(?:add|addAll|insert|remove|removeWhere|clear)\s*\(
    | \[[^\]]+\]\s*=
    ''',
    re.VERBOSE,
)

def mutable_collection_mod_count(code: str) -> int:
    s = remove_comments(code)
    return len(_MC_RE.findall(s))

# --- API: network calls in UI code --------------------------------------------
_API_RE = re.compile(
    r'''
    \bhttp\.(?:get|post|put|delete|patch|head)\s*\(
    | \bDio\s*\(\s*\)\s*\.\s*(?:get|post|put|delete|patch)\s*\(
    | \bdio\.(?:get|post|put|delete|patch)\s*\(
    | \bWebSocket\.connect\s*\(
    ''',
    re.IGNORECASE | re.VERBOSE,
)

def api_call_count(code: str) -> int:
    s = remove_comments(code)
    return len(_API_RE.findall(s))
