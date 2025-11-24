
import re

__all__ = [
    "strip_block_comments", "strip_line_comments", "remove_comments",
    "count_loc", "comment_lines",
    "find_matching_brace", "find_matching_paren",
]

def strip_block_comments(code: str) -> str:
    return re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)

def strip_line_comments(code: str) -> str:
    out = []
    for line in code.splitlines():
        idx = line.find("//")
        out.append(line if idx == -1 else line[:idx])
    return "\n".join(out)

def remove_comments(code: str) -> str:
    return strip_line_comments(strip_block_comments(code))

def count_loc(code: str) -> int:
    code_wo_block = strip_block_comments(code)
    cnt = 0
    for line in code_wo_block.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("//") or s.startswith("///") or s.startswith("//!"):
            continue
        cnt += 1
    return cnt

def comment_lines(code: str) -> int:
    lines = code.splitlines()
    in_block = False
    count = 0
    for line in lines:
        s = line.strip()
        if not in_block and (s.startswith("//") or s.startswith("///") or s.startswith("//!")):
            count += 1
            continue
        if not in_block and "/*" in s:
            in_block = True
            count += 1
            if "*/" in s and s.index("*/") > s.index("/*"):
                in_block = False
            continue
        if in_block:
            count += 1
            if "*/" in s:
                in_block = False
            continue
    return count

def find_matching_brace(s: str, open_idx: int) -> int:
    depth = 0
    in_q = None
    i = open_idx
    while i < len(s):
        ch = s[i]
        if in_q:
            if ch == in_q:
                in_q = None
            i += 1
            continue
        if ch in ("'", '"'):
            in_q = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1

def find_matching_paren(s: str, open_idx: int) -> int:
    depth = 0
    in_q = None
    i = open_idx
    while i < len(s):
        ch = s[i]
        if in_q:
            if ch == in_q:
                in_q = None
            i += 1
            continue
        if ch in ("'", '"'):
            in_q = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1
