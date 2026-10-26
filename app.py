import json
from pathlib import Path

import streamlit as st

from build import compile_pdf, pdflatex_available, render_tex
from utils import latex_escape

DATA = Path(__file__).parent / "data"

# Wizard order. Each section has a page title, a data file, and a template slot.
SECTIONS = [
    {"title": "Technical Skills", "file": "skills.json", "slot": "skills"},
    {"title": "Relevant Coursework", "file": "coursework.json", "slot": "coursework"},
]
PAGES = [s["title"] for s in SECTIONS] + ["Export"]


def load_groups(section):
    """Return a list of {label, items} groups for a section."""
    data = json.loads((DATA / section["file"]).read_text())
    if isinstance(data, list):  # plain list = one group named after the section
        return [{"label": section["title"], "items": data}]
    return data["groups"]


def build_block(groups, picked):
    """One '\\textbf{Label}: {a, b, c} \\\\' line per group that has picks."""
    lines = []
    for g in groups:
        chosen = [latex_escape(i["text"]) for i in g["items"] if picked[i["id"]]]
        if chosen:
            label = latex_escape(g["label"])
            lines.append(f"    \\textbf{{{label}}}: {{{', '.join(chosen)}}} \\\\")
    if not lines:
        return ""
    return (
        "\\begin{itemize}[leftmargin=0.15in, label={}]\n"
        "    \\small{\\item{\n"
        + "\n".join(lines)
        + "\n    }}\n"
        "\\end{itemize}"
    )


# ---------- State ----------
groups_by_slot = {s["slot"]: load_groups(s) for s in SECTIONS}

st.session_state.setdefault("page", 0)
st.session_state.setdefault("picked", {})
picked = st.session_state.picked
for groups in groups_by_slot.values():
    for g in groups:
        for i in g["items"]:
            picked.setdefault(i["id"], i.get("default", False))  # new items get their default


def go(step):
    st.session_state.page += step


# ---------- Page ----------
page = st.session_state.page
st.title("Resume Picker")
st.progress((page + 1) / len(PAGES), text=f"Step {page + 1} of {len(PAGES)}: {PAGES[page]}")

if page < len(SECTIONS):
    section = SECTIONS[page]
    groups = groups_by_slot[section["slot"]]
    st.header(section["title"])
    for g in groups:
        if len(groups) > 1:
            st.subheader(g["label"])
        for i in g["items"]:
            picked[i["id"]] = st.checkbox(i["text"], value=picked[i["id"]], key=f"cb-{i['id']}")

    block = build_block(groups, picked)
    if block:
        st.subheader("LaTeX output")
        st.code(block, language="latex")
    else:
        st.info("Nothing selected, so this section will be skipped.")

else:
    st.header("Export")
    blocks = {slot: build_block(groups, picked) for slot, groups in groups_by_slot.items()}
    tex = render_tex(**blocks)

    st.download_button("Download .tex", tex, file_name="resume.tex", mime="text/x-tex")

    if not pdflatex_available():
        st.warning("pdflatex isn't installed, so PDF export is off. Download the .tex and compile it in Overleaf.")
    elif st.button("Build PDF"):
        with st.spinner("Compiling..."):
            pdf, log = compile_pdf(tex)
        if pdf:
            st.download_button("Download PDF", pdf, file_name="resume.pdf", mime="application/pdf")
        else:
            st.error("LaTeX failed to compile. The end of the log is below.")
            st.code(log[-2000:])

# ---------- Navigation ----------
st.divider()
back, _, nxt = st.columns([1, 3, 1])
back.button("← Back", on_click=go, args=(-1,), disabled=page == 0, use_container_width=True)
nxt.button("Next →", on_click=go, args=(1,), disabled=page == len(PAGES) - 1, use_container_width=True)