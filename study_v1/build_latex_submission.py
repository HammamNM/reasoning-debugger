import re

# 1. Append Mandatory medRxiv / Journal Declarations to Markdown if not already present
md_path = "study_v1/PAPER_MANUSCRIPT_V1.md"
with open(md_path, "r", encoding="utf-8") as f:
    md_text = f.read()

declarations_block = """

---

## 9. Declarations (Mandatory Ethics, Data, and Competing Interests)

* **Ethics Statement and Human Subjects Research:** This study exclusively evaluates artificial intelligence models using synthetic, expert-curated clinical emergency vignettes (`SCEN_01`--`SCEN_50`). No real patient data, electronic health records, protected health information (PHI), or human subjects were involved at any stage of this research. Institutional Review Board (IRB) approval and informed consent were therefore not required.
* **Data and Code Availability:** All 50 clinical scenario specifications (15 development, 35 held-out test), the frozen Deterministic-First Hybrid Clinical Auditor codebase (`v0.2-frozen-rules`), all 420 raw model evaluation logs, and statistical reproduction scripts are publicly available without restriction at `https://github.com/HammamNM/reasoning-debugger`.
* **Competing Interests:** The author declares no competing financial or non-financial interests.
* **Funding Statement:** This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.
* **Author Contributions:** H.O. conceived the study, designed the Deterministic-First Hybrid Clinical Auditor architecture, curated the clinical emergency benchmark, executed the multi-ecosystem evaluations and statistical analyses, and wrote the manuscript.
"""

if "## 9. Declarations" not in md_text:
    # Insert right before References
    if "## References" in md_text:
        md_text = md_text.replace("## References", declarations_block.strip() + "\n\n---\n\n## References")
    else:
        md_text += declarations_block
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_text)
    with open("PAPER_MANUSCRIPT_V1.md", "w", encoding="utf-8") as f:
        f.write(md_text)
    print("✅ Added Section 9 (Mandatory medRxiv/Journal Declarations) to Markdown manuscript.")

# 2. Convert full Markdown manuscript to clean, compilable arXiv/Overleaf LaTeX (.tex)
def escape_tex(s):
    s = s.replace("\\", "\\textbackslash{}")
    for ch in ["&", "%", "$", "#", "_", "{", "}"]:
        s = s.replace(ch, "\\" + ch)
    s = s.replace("~", "\\textasciitilde{}").replace("^", "\\textasciicircum{}")
    s = s.replace("->", "$\\rightarrow$").replace("<->", "$\\leftrightarrow$")
    s = s.replace(">=", "$\\ge$").replace("<=", "$\\le$")
    # Restore bold and code formatting
    s = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", s)
    s = re.sub(r"\*(.+?)\*", r"\\textit{\1}", s)
    s = re.sub(r"`(.+?)`", r"\\texttt{\1}", s)
    return s

tex_lines = [
    r"\documentclass[10pt,a4paper]{article}",
    r"\usepackage[utf8]{inputenc}",
    r"\usepackage[T1]{fontenc}",
    r"\usepackage[margin=0.85in]{geometry}",
    r"\usepackage{booktabs,longtable,array}",
    r"\usepackage{amsmath,amssymb}",
    r"\usepackage{hyperref}",
    r"\usepackage{fancyvrb}",
    r"\hypersetup{colorlinks=true,linkcolor=blue,urlcolor=blue,citecolor=blue}",
    r"\title{\textbf{Beyond Surface Fluency: A Deterministic-First Hybrid Clinical Auditor Exposes LLM-as-a-Judge Blindness and Behavioral Shifts Under Emergency Clinical Pressure}}",
    r"\author{\textbf{Hammam Omer}\thanks{Correspondence: Hammam Omer. Repository: \url{https://github.com/HammamNM/reasoning-debugger} (Tag: \texttt{v0.2-frozen-rules}).}\\Faculty of Medicine, Omdurman Islamic University, Omdurman, Sudan\\Independent Clinical AI Safety Researcher (NexoraMed)}",
    r"\date{October 2026}",
    r"\begin{document}",
    r"\maketitle"
]

in_code = False
in_table = False
in_list = False

for raw_line in md_text.splitlines():
    line = raw_line.rstrip()
    if line.startswith("# Beyond Surface Fluency") or line.startswith("**Authors:**") or line.startswith("(1) Faculty") or line.startswith("(*) Correspondence"):
        continue
    if line.strip() == "---" or line.strip().startswith("===="):
        continue

    # Handle code blocks (Figures, Algorithms, Case Study Boxes)
    if line.strip().startswith("```"):
        if in_list:
            tex_lines.append(r"\end{itemize}")
            in_list = False
        if not in_code:
            tex_lines.append(r"\begin{footnotesize}\begin{verbatim}")
            in_code = True
        else:
            tex_lines.append(r"\end{verbatim}\end{footnotesize}")
            in_code = False
        continue

    if in_code:
        tex_lines.append(line)
        continue

    # Handle Markdown Tables
    if line.strip().startswith("|"):
        if in_list:
            tex_lines.append(r"\end{itemize}")
            in_list = False
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(set(c) <= set(":- ") for c in cells):
            tex_lines.append(r"\midrule")
            continue
        if not in_table:
            col_spec = "l" + "c" * (len(cells) - 1)
            tex_lines.append(r"\begin{center}\scriptsize\begin{longtable}{" + col_spec + r"}")
            tex_lines.append(r"\toprule")
            in_table = True
        row_tex = " & ".join(escape_tex(c) for c in cells) + r" \\"
        tex_lines.append(row_tex)
        continue
    else:
        if in_table:
            tex_lines.append(r"\bottomrule")
            tex_lines.append(r"\end{longtable}\end{center}")
            in_table = False

    # Handle Headings
    if line.startswith("## "):
        if in_list:
            tex_lines.append(r"\end{itemize}")
            in_list = False
        h = escape_tex(line[3:].strip())
        tex_lines.append(r"\section*{" + h + r"}")
        continue
    if line.startswith("### "):
        if in_list:
            tex_lines.append(r"\end{itemize}")
            in_list = False
        h = escape_tex(line[4:].strip())
        tex_lines.append(r"\subsection*{" + h + r"}")
        continue
    if line.startswith("#### "):
        if in_list:
            tex_lines.append(r"\end{itemize}")
            in_list = False
        h = escape_tex(line[5:].strip())
        tex_lines.append(r"\subsubsection*{" + h + r"}")
        continue

    # Handle Bullet / Numbered Lists
    if re.match(r"^(\*|-|\d+\.)\s+", line.strip()):
        if not in_list:
            tex_lines.append(r"\begin{itemize}")
            in_list = True
        item_txt = re.sub(r"^(\*|-|\d+\.)\s+", "", line.strip())
        tex_lines.append(r"  \item " + escape_tex(item_txt))
        continue
    else:
        if in_list and line.strip() == "":
            tex_lines.append(r"\end{itemize}")
            in_list = False

    if line.strip() == "":
        tex_lines.append("")
    else:
        tex_lines.append(escape_tex(line))

if in_list:
    tex_lines.append(r"\end{itemize}")
if in_table:
    tex_lines.append(r"\bottomrule\end{longtable}\end{center}")

tex_lines.append(r"\end{document}")

tex_path = "study_v1/PAPER_MANUSCRIPT_V1.tex"
with open(tex_path, "w", encoding="utf-8") as f:
    f.write("\n".join(tex_lines))

print(f"✅ Generated official arXiv/Overleaf LaTeX source: {tex_path} ({len(tex_lines)} lines)")
