import os, textwrap

def create_pure_python_pdf(md_path, pdf_path):
    with open(md_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    replacements = {
        "—": "--", "–": "-", "’": "'", "‘": "'", "“": '"', "”": '"',
        "¹": "1", "→": "->", "↔": "<->", "×": "x", "≥": ">=", "≤": "<=", "≈": "~", "•": "-"
    }
    for k, v in replacements.items():
        raw_text = raw_text.replace(k, v)
    clean_text = raw_text.encode("ascii", "ignore").decode("ascii")

    # Wrap lines cleanly to fit academic A4 page width (92 chars per line)
    wrapped_lines = []
    for line in clean_text.split("\n"):
        line_s = line.strip().replace("**", "").replace("`", "")
        if not line_s:
            wrapped_lines.append("")
        elif line_s.startswith("|") or line_s.startswith("===") or line_s.startswith("---"):
            wrapped_lines.append(line_s[:105])
        else:
            wrapped_lines.extend(textwrap.wrap(line_s, width=92) or [""])

    # Paginate (52 lines per page)
    lines_per_page = 52
    pages = [wrapped_lines[i:i + lines_per_page] for i in range(0, len(wrapped_lines), lines_per_page)]

    objects = []
    def add_obj(content):
        objects.append(content)
        return len(objects)

    # 1: Catalog, 2: Pages placeholder, 3: Font (Helvetica), 4: Font Bold, 5: Font Courier
    add_obj("<< /Type /Catalog /Pages 2 0 R >>")
    add_obj("")  # Placeholder for Pages (Obj 2)
    font_reg = add_obj("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    font_bold = add_obj("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    font_mono = add_obj("<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")

    page_ids = []
    for p_idx, p_lines in enumerate(pages, 1):
        stream_cmds = ["BT", f"/F1 8 Tf 50 810 Td (Omer (2026) - Deterministic-First Hybrid Clinical Auditor Benchmark [Page {p_idx}/{len(pages)}]) Tj", "ET"]
        y = 785
        for l in p_lines:
            esc_l = l.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            if l.startswith("# ") or l.startswith("## ") or l.startswith("### "):
                clean_h = esc_l.lstrip("#").strip()
                stream_cmds.append(f"BT /F2 10 Tf 50 {y} Td ({clean_h}) Tj ET")
            elif l.startswith("|") or l.startswith("===") or l.startswith("---"):
                stream_cmds.append(f"BT /F3 7.2 Tf 50 {y} Td ({esc_l}) Tj ET")
            else:
                stream_cmds.append(f"BT /F1 9 Tf 50 {y} Td ({esc_l}) Tj ET")
            y -= 14

        stream_data = "\n".join(stream_cmds)
        content_id = add_obj(f"<< /Length {len(stream_data)} >>\nstream\n{stream_data}\nendstream")
        page_id = add_obj(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 {font_reg} 0 R /F2 {font_bold} 0 R /F3 {font_mono} 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        )
        page_ids.append(page_id)

    kids_str = " ".join(f"{pid} 0 R" for pid in page_ids)
    objects[1] = f"<< /Type /Pages /Kids [{kids_str}] /Count {len(page_ids)} >>"

    # Write valid PDF binary structure
    pdf_bytes = bytearray(b"%PDF-1.4\n")
    offsets = []
    for idx, obj in enumerate(objects, 1):
        offsets.append(len(pdf_bytes))
        pdf_bytes.extend(f"{idx} 0 obj\n{obj}\nendobj\n".encode("latin-1"))

    xref_offset = len(pdf_bytes)
    pdf_bytes.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode("latin-1"))
    for off in offsets:
        pdf_bytes.extend(f"{off:010d} 00000 n \n".encode("latin-1"))

    pdf_bytes.extend(
        f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("latin-1")
    )

    with open(pdf_path, "wb") as out_f:
        out_f.write(pdf_bytes)
    print(f"✅ Pure-Python Academic PDF Generated: {pdf_path} ({len(page_ids)} pages, {len(pdf_bytes)/1024:.1f} KB)")

create_pure_python_pdf("study_v1/PAPER_MANUSCRIPT_V1.md", "study_v1/PAPER_MANUSCRIPT_V1.pdf")
