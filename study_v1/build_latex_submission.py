import os, re, urllib.request, urllib.parse

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
    if "## References" in md_text:
        md_text = md_text.replace("## References", declarations_block.strip() + "\n\n---\n\n## References")
    else:
        md_text += declarations_block
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_text)
    with open("PAPER_MANUSCRIPT_V1.md", "w", encoding="utf-8") as f:
        f.write(md_text)
    print("✅ Added Section 9 (Mandatory medRxiv/Journal Declarations) to Markdown.")

def escape_tex(s):
    # Clean ASCII transliteration first
    repl = {"—": "--", "–": "-", "’": "'", "‘": "'", "“": "``", "”": "''", "→": "->", "↔": "<->", "≥": ">=", "≤": "<="}
    for k, v in repl.items():
        s = s.replace(k, v)
    s = s.encode("ascii", "ignore").decode("ascii")
    
    # Extract inline code and bold/italic tokens before escaping special chars
    tokens = {}
    def save_tok(match, prefix, wrap_l, wrap_r):
        key = f"ZZZ{prefix}{len(tokens)}ZZZ"
        inner = match.group(1)
        for ch in ["\\", "&", "%", "$", "#", "_", "{", "}"]:
            inner = inner.replace(ch, "\\" + ch if ch != "\\" else "\\textbackslash{}")
        tokens[key] = f"{wrap_l}{inner}{wrap_r}"
        return key

    s = re.sub(r"`([^`]+)`", lambda m: save_tok(m, "CODE", r"\texttt{", "}"), s)
    s = re.sub(r"\*\*([^*]+)\*\*", lambda m: save_tok(m, "BOLD", r"\textbf{", "}"), s)
    s = re.sub(r"\*([^*]+)\*", lambda m: save_tok(m, "ITAL", r"\textit{", "}"), s)

    for ch in ["\\", "&", "%", "$", "#", "_", "{", "}"]:
        s = s.replace(ch, "\\" + ch if ch != "\\" else "\\textbackslash{}")
    s = s.replace("~", "\\textasciitilde{}").replace("^", "\\textasciicircum{}")
    s = s.replace("<->", "$\\leftrightarrow$").replace("->", "$\\rightarrow$")
    s = s.replace(">=", "$\\ge$").replace("<=", "$\\le$")

    for k, v in tokens.items():
        s = s.replace(k, v)
    return s

tex_lines = [
    r"\documentclass[10pt,a4paper]{article}",
    r"\usepackage[utf8]{inputenc}",
    r"\usepackage[T1]{fontenc}",
    r"\usepackage[margin=0.8in]{geometry}",
    r"\usepackage{booktabs,longtable,array}",
    r"\usepackage{amsmath,amssymb}",
    r"\usepackage{hyperref}",
    r"\hypersetup{colorlinks=true,linkcolor=blue,urlcolor=blue,citecolor=blue}",
    r"\setlength{\parskip}{0.4em}",
    r"\setlength{\parindent}{0pt}",
    r"\title{\Large\textbf{Beyond Surface Fluency: A Deterministic-First Hybrid Clinical Auditor Exposes LLM-as-a-Judge Blindness and Behavioral Shifts Under Emergency Clinical Pressure}}",
    r"\author{\textbf{Hammam Omer}\thanks{Correspondence: Hammam Omer. Official Benchmark Repository: \url{https://github.com/HammamNM/reasoning-debugger} (Frozen Tag: \texttt{v0.2-frozen-rules}).}\\ \small Faculty of Medicine, Omdurman Islamic University, Omdurman, Sudan\\ \small Independent Clinical AI Safety Researcher (NexoraMed)}",
    r"\date{\small October 2026}",
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
        clean_code = line.encode("ascii", "ignore").decode("ascii")
        tex_lines.append(clean_code[:102])
        continue

    if line.strip().startswith("|"):
        if in_list:
            tex_lines.append(r"\end{itemize}")
            in_list = False
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(set(c) <= set(":- ") for c in cells):
            tex_lines.append(r"\midrule")
            continue
        if not in_table:
            n_cols = len(cells)
            if n_cols == 3:
                col_spec = r"p{0.18\textwidth}p{0.34\textwidth}p{0.40\textwidth}"
            elif n_cols == 5:
                col_spec = r"p{0.34\textwidth}cccc"
            elif n_cols == 6:
                col_spec = r"p{0.30\textwidth}cp{0.20\textwidth}p{0.18\textwidth}cc"
            elif n_cols == 8:
                col_spec = r"p{0.18\textwidth}p{0.14\textwidth}cccccc"
            else:
                col_spec = "l" + "c" * (n_cols - 1)
            tex_lines.append(r"{\scriptsize\setlength{\tabcolsep}{3.5pt}\begin{longtable}{" + col_spec + r"}")
            tex_lines.append(r"\toprule")
            in_table = True
        row_tex = " & ".join(escape_tex(c) for c in cells) + r" \\"
        tex_lines.append(row_tex)
        continue
    else:
        if in_table:
            tex_lines.append(r"\bottomrule")
            tex_lines.append(r"\end{longtable}}")
            in_table = False

    if line.startswith("## "):
        if in_list:
            tex_lines.append(r"\end{itemize}")
            in_list = False
        tex_lines.append(r"\section*{" + escape_tex(line[3:].strip()) + r"}")
        continue
    if line.startswith("### "):
        if in_list:
            tex_lines.append(r"\end{itemize}")
            in_list = False
        tex_lines.append(r"\subsection*{" + escape_tex(line[4:].strip()) + r"}")
        continue
    if line.startswith("#### "):
        if in_list:
            tex_lines.append(r"\end{itemize}")
            in_list = False
        tex_lines.append(r"\subsubsection*{" + escape_tex(line[5:].strip()) + r"}")
        continue

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
    tex_lines.append(r"\bottomrule\end{longtable}}")

tex_lines.append(r"\end{document}")
tex_content = "\n".join(tex_lines)

for path in ["study_v1/PAPER_MANUSCRIPT_V1.tex", "PAPER_MANUSCRIPT_V1.tex"]:
    with open(path, "w", encoding="utf-8") as f:
        f.write(tex_content)
print(f"✅ Saved standard LaTeX source to PAPER_MANUSCRIPT_V1.tex ({len(tex_lines)} lines)")

# Attempt cloud LaTeX compilation (TeXLive.net CGI) to produce genuine typeset PDF
compiled_ok = False
try:
    print("⏳ Compiling genuine LaTeX PDF via TeXLive.net API...")
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = []
    for name, val in [("engine", "pdflatex"), ("return", "pdf")]:
        body.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{val}\r\n")
    body.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"filecontents[]\"; filename=\"document.tex\"\r\nContent-Type: text/plain\r\n\r\n{tex_content}\r\n")
    body.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"filename[]\"\r\n\r\ndocument.tex\r\n")
    body.append(f"--{boundary}--\r\n")
    payload = "".join(body).encode("utf-8")
    req = urllib.request.Request(
        "[https://texlive.net/cgi-bin/latexcgi](https://texlive.net/cgi-bin/latexcgi)",
        data=payload,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        pdf_data = resp.read()
        if pdf_data.startswith(b"%PDF"):
            for p_out in ["study_v1/PAPER_MANUSCRIPT_V1.pdf", "PAPER_MANUSCRIPT_V1.pdf"]:
                with open(p_out, "wb") as pf:
                    pf.write(pdf_data)
            print(f"✅ SUCCESS! Genuine Typeset LaTeX PDF compiled ({len(pdf_data)/1024:.1f} KB)!")
            compiled_ok = True
        else:
            print("⚠️ Cloud returned log instead of PDF; using pure-Python PDF builder as fallback.")
except Exception as e:
    print(f"⚠️ Cloud TeXLive unreachable ({e}); using local pure-Python PDF builder.")

if not compiled_ok:
    os.system("python study_v1/build_academic_pdf.py")
    os.system("cp study_v1/PAPER_MANUSCRIPT_V1.pdf ./PAPER_MANUSCRIPT_V1.pdf")
