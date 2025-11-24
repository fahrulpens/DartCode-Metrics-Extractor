
import re
from .common import remove_comments, find_matching_paren

__all__ = ["number_of_widgets", "max_widget_nesting", "child_chain_max_depth"]

WIDGET_CTOR = re.compile(r'(?<![a-z0-9_])([A-Z][A-Za-z0-9_]*)\s*\(')

def number_of_widgets(code: str) -> int:
    code_nc = remove_comments(code)
    return len(WIDGET_CTOR.findall(code_nc))

def max_widget_nesting(code: str) -> int:
    code_nc = remove_comments(code)
    tokens = re.finditer(r'[A-Za-z_]\w*|\(|\)', code_nc)
    stack = []
    depth = 0
    max_depth = 0
    prev_cap = False
    prev_token = ""
    for t in tokens:
        s = t.group(0)
        if s == '(':
            is_widget = prev_cap and bool(re.match(r'^[A-Z][A-Za-z0-9_]*$', prev_token))
            stack.append(is_widget)
            if is_widget:
                depth += 1
                if depth > max_depth:
                    max_depth = depth
            prev_cap = False
        elif s == ')':
            if stack:
                is_widget = stack.pop()
                if is_widget and depth > 0:
                    depth -= 1
            prev_cap = False
        else:
            prev_token = s
            prev_cap = bool(re.match(r'^[A-Z][A-Za-z0-9_]*$', s))
    return max_depth

CHILD_CTOR = re.compile(r'\bchild\s*:\s*([A-Z][A-Za-z0-9_]*)\s*\(')

def child_chain_max_depth(code: str) -> int:
    code_nc = remove_comments(code)
    spans = []
    for m in CHILD_CTOR.finditer(code_nc):
        open_paren = code_nc.find('(', m.end()-1)
        if open_paren == -1:
            continue
        close = find_matching_paren(code_nc, open_paren)
        if close == -1:
            continue
        spans.append((m.start(), close))
    spans.sort(key=lambda x: (x[0], -(x[1]-x[0])))
    stack = []
    maxd = 0
    for s, e in spans:
        while stack and s >= stack[-1][1]:
            stack.pop()
        stack.append((s, e))
        if len(stack) > maxd:
            maxd = len(stack)
    return maxd
