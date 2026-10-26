import shutil
import subprocess
import tempfile
from pathlib import Path

import jinja2

TEMPLATES = Path(__file__).parent / "templates"

# LaTeX is full of { } and %, so use ((( ))) for templates slots instead of {{ }}
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES),
    variable_start_string="(((",
    variable_end_string=")))",
    block_start_string="((*",
    block_end_string="*))",
    comment_start_string="((=",
    comment_end_string="=))",
    trim_blocks=True,
    autoescape=False,
)


def render_tex(**sections) -> str:
    """Fill the resume templates with each section's LaTeX block."""
    return env.get_template("resume.tex.j2").render(**sections)


def pdflatex_available() -> bool:
    return shutil.which("pdflatex") is not None


def compile_pdf(tex: str) -> tuple[bytes | None, str]:
    """Compile LaTeX to PDF. Returns (pdf_bytes, log). pdf_bytes is None on failure."""
    with tempfile.TemporaryDirectory() as tmp:
        tex_path = Path(tmp) / "resume.tex"
        tex_path.write_text(tex, encoding="utf-8")
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "resume.tex"],
            cwd=tmp,
            capture_output=True,
            text=True,
            timeout=60,
        )
        pdf_path = Path(tmp) / "resume.pdf"
        if result.returncode == 0 and pdf_path.exists():
            return pdf_path.read_bytes(), result.stdout
        return None, result.stdout