
from .common import remove_comments

__all__ = ["max_nesting_depth"]

def max_nesting_depth(code: str) -> int:
    s = remove_comments(code)
    depth = 0
    max_depth = 0
    in_q = None
    i = 0
    while i < len(s):
        ch = s[i]
        if in_q:
            if ch == in_q:
                in_q = None
            i += 1
            continue
        if ch in ("'", '"'):
            in_q = ch
        elif ch == '{':
            depth += 1
            if depth > max_depth:
                max_depth = depth
        elif ch == '}':
            depth = max(0, depth - 1)
        i += 1
    return max(0, max_depth - 1)
