
import re
from .common import remove_comments, find_matching_brace

__all__ = ["number_of_fields"]

CLASS_RE = re.compile(r'\bclass\s+[A-Za-z_]\w*[^\{]*\{', re.MULTILINE)
VAR_NAME_RE = re.compile(r'\b([A-Za-z_]\w*)\b')

def extract_class_bodies(code_nc: str):
    bodies = []
    for m in CLASS_RE.finditer(code_nc):
        open_brace = code_nc.find('{', m.end()-1)
        if open_brace == -1:
            continue
        close_brace = find_matching_brace(code_nc, open_brace)
        if close_brace == -1:
            continue
        bodies.append(code_nc[open_brace+1:close_brace])
    return bodies

def split_top_level_statements(body: str):
    stmts = []
    start = 0
    depth = 0
    in_q = None
    i = 0
    while i < len(body):
        ch = body[i]
        if in_q:
            if ch == in_q:
                in_q = None
            i += 1
            continue
        if ch in ("'", '"'):
            in_q = ch
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth = max(0, depth - 1)
        elif ch == ';' and depth == 0:
            stmts.append(body[start:i+1])
            start = i + 1
        i += 1
    tail = body[start:].strip()
    if tail:
        stmts.append(tail)
    return stmts

def count_fields_in_class(body: str) -> int:
    stmts = split_top_level_statements(body)
    count = 0
    for st in stmts:
        s = st.strip()
        if not s.endswith(';'):
            continue
        # exclude abstract methods/getters: '(' at top level
        has_paren = False
        lvl = 0
        in_q = None
        for ch in s:
            if in_q:
                if ch == in_q:
                    in_q = None
                continue
            if ch in ("'", '"'):
                in_q = ch
            elif ch == '(':
                lvl += 1
                has_paren = True
            elif ch == ')':
                lvl = max(0, lvl - 1)
        if has_paren:
            continue

        # split by top-level commas
        decl = s[:-1]
        parts = []
        buf = []
        stack = []
        in_q = None
        for ch in decl:
            if in_q:
                buf.append(ch)
                if ch == in_q:
                    in_q = None
                continue
            if ch in ("'", '"'):
                in_q = ch
                buf.append(ch)
                continue
            if ch in "<{[(":
                stack.append(ch)
                buf.append(ch)
                continue
            if ch in ">}])":
                if stack:
                    stack.pop()
                buf.append(ch)
                continue
            if ch == ',' and not stack:
                parts.append(''.join(buf).strip())
                buf = []
                continue
            buf.append(ch)
        if buf:
            parts.append(''.join(buf).strip())

        for p in parts:
            left = p.split('=')[0].strip()
            ids = VAR_NAME_RE.findall(left)
            if ids:
                name = ids[-1]
                if name not in {"get", "set", "factory"}:
                    count += 1
    return count

def number_of_fields(code: str) -> int:
    code_nc = remove_comments(code)
    total = 0
    for body in extract_class_bodies(code_nc):
        total += count_fields_in_class(body)
    return total
