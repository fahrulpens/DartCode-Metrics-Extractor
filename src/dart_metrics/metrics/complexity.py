
import re
from .common import remove_comments

__all__ = ["cyclomatic_complexity"]

CC_TOKENS = re.compile(r'\bif\b|\bfor\b|\bwhile\b|\bcase\b|\bcatch\b|&&|\|\|', re.MULTILINE)
TERNARY = re.compile(r'(?<!\?)\?(?!\?)')

def cyclomatic_complexity(code: str) -> int:
    code_nc = remove_comments(code)
    decisions = len(CC_TOKENS.findall(code_nc))
    for m in TERNARY.finditer(code_nc):
        if ':' in code_nc[m.end(): m.end()+200]:
            decisions += 1
    return 1 + decisions
