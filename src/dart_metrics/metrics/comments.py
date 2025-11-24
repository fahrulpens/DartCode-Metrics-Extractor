
from .common import count_loc, comment_lines

__all__ = ["comment_ratio"]

def comment_ratio(code: str) -> float:
    loc = count_loc(code)
    com = comment_lines(code)
    return round((com / loc) if loc else 0.0, 3)
