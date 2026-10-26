import re

# Characters that break LaTeX unless escaped
_LATEX_SPECIAL = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}

_PATTERN = re.compile("|".join(re.escape(ch) for ch in _LATEX_SPECIAL))


def latex_escape(text: str) -> str:
    """Escape special LaTeX characters in plain text."""
    return _PATTERN.sub(lambda m: _LATEX_SPECIAL[m.group()], text)