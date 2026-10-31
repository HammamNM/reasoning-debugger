from fpdf import FPDF
import shutil
import os

class CVPDF(FPDF):
    def header(self):
        # Dark slate top banner
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 32, "F")
        # Blue accent bottom line on banner
        self.set_fill_color(2, 132, 199)
        self.rect(0, 32, 210, 1.2, "F")

        self.set_y(6)
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(255, 255, 255)
        self.cell(0, 7, "HAMMAM OMER", new_x="LMARGIN", new_y="NEXT", align="L")

        self.set_font("Helvetica", "B", 10.5)
        self.set_text_color(56, 189, 248)
        self.cell(0, 5.5, "Medical AI Researcher & LLM Safety Evaluation Engineer", new_x="LMARGIN", new_y="NEXT", align="L")

        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(203, 213, 225)
        self.write(5, "Omdurman, Sudan  |  GitHub: ")
        self.set_text_color(125, 211, 252)
        self.write(5, "github.com/HammamNM", "https://github.com/HammamNM")
        self.set_text_color(203, 213, 225)
        self.write(5, "  |  Live Explorer: ")
        self.set_text_color(125, 211, 252)
        self.write(5, "hammamnm.github.io/reasoning-debugger", "https://hammamnm.github.io/reasoning-debugger/")
        self.set_text_color(203, 213, 225)
        self.write(5, "  |  Blog: ")
        self.set_text_color(125, 211, 252)
        self.write(5, "nexoramed.online", "https://nexoramed.online")
        self.ln(10)

    def section_title(self, title):
        self.ln(2)
        self.set_fill_color(2, 132, 199)
        y = self.get_y()
        self.rect(12, y + 0.8, 2.5, 4.8, "F")
        self.set_x(16)
        self.set_font("Helvetica", "B", 10.5)
        self.set_text_color(15, 23, 42)
        self.cell(0, 6, title.upper(), new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def bullet(self, bold_prefix, text):
        self.set_x(14)
        self.set_font("Helvetica", "B", 8.8)
        self.set_text_color(2, 132, 199)
        self.write(4.3, "- ")
        self.set_text_color(15, 23, 42)
        self.write(4.3, bold_prefix + " ")
        self.set_font("Helvetica", "", 8.8)
        self.set_text_color(30, 41, 59)
        self.write(4.3, text)
        self.ln(4.8)

pdf = CVPDF(orientation="P", unit="mm", format="A4")
pdf.set_margins(12, 10, 12)
pdf.set_auto_page_break(auto=True, margin=10)
pdf.add_page()

# Executive Summary Box
pdf.set_y(36)
pdf.set_fill_color(248, 250, 252)
pdf.set_draw_color(203, 213, 225)
pdf.rect(12, 36, 186, 17, "DF")
pdf.set_xy(14, 37.5)
pdf.set_font("Helvetica", "B", 8.8)
pdf.set_text_color(15, 23, 42)
pdf.write(4.3, "Executive Profile: ")
pdf.set_font("Helvetica", "", 8.8)
pdf.set_text_color(51, 65, 85)
pdf.write(4.3, "Medical AI researcher and Python framework architect specializing in Clinical LLM Safety Auditing, Neuro-Symbolic Verification, and Automated Rubric Engineering. Creator of the Deterministic-First Hybrid Clinical Auditor, exposing systematic surface-fluency blindness in standalone LLM-as-a-Judge pipelines across 420 emergency clinical evaluations. Bridges clinical training with test-driven software engineering (TDD) and zero-leakage benchmark design.")
pdf.set_y(55)

# 4 Metric Callout Boxes
metrics = [
    ("71.7% (38/53)", "JUDGE BLINDNESS EXPOSED"),
    ("0 / 1,767", "PARSER HALLUCINATIONS"),
    ("100% / 100%", "CRITERION RECALL & SPEC."),
    ("< 2 ms CPU", "STAGE II AUDIT LATENCY"),
]
box_w = 45
gap = 2
start_x = 12
y_top = pdf.get_y()
for i, (val, lbl) in enumerate(metrics):
    x = start_x + i * (box_w + gap)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_draw_color(203, 213, 225)
    pdf.rect(x, y_top, box_w, 12.5, "DF")
    pdf.set_xy(x, y_top + 1.8)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(3, 105, 161)
    pdf.cell(box_w, 5, val, align="C")
    pdf.set_xy(x, y_top + 7)
    pdf.set_font("Helvetica", "", 6.8)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(box_w, 4, lbl, align="C")

pdf.set_y(y_top + 14.5)

# Section: Research Projects
pdf.section_title("Research Projects & Core Engineering Deliverables")

# Project 1
pdf.set_font("Helvetica", "B", 9.8)
pdf.set_text_color(15, 23, 42)
pdf.write(5, "1. Deterministic-First Hybrid Clinical Auditor (v0.2-frozen-rules)   ")
pdf.set_font("Helvetica", "B", 8.2)
pdf.set_text_color(2, 132, 199)
pdf.write(5, "[GitHub Repo]", "https://github.com/HammamNM/reasoning-debugger")
pdf.write(5, "  |  ")
pdf.write(5, "[Interactive 420-Trace Explorer]", "https://hammamnm.github.io/reasoning-debugger/")
pdf.write(5, "  |  ")
pdf.write(5, "[50-Scenario Specs]", "https://github.com/HammamNM/reasoning-debugger/blob/main/CLINICAL_SPECIFICATIONS.md")
pdf.ln(4.8)

pdf.set_font("Helvetica", "I", 8.4)
pdf.set_text_color(71, 85, 105)
pdf.cell(0, 4.5, "Lead Architect & Sole Author | Python, Neuro-Symbolic Extraction, Clinical Safety Verification", new_x="LMARGIN", new_y="NEXT")
pdf.ln(0.8)

pdf.bullet("Two-Stage Decoupled Architecture:", "Engineered a neuro-symbolic evaluation framework isolating constrained semantic extraction (Stage I) from pure-Python deterministic clinical rule verification (Stage II) across 420 paired clinical management plans on 6 models (openai/gpt-oss-120b, gemini-3.5/3.1-flash-lite, gemma-4-26b-a4b-it, qwen/qwen3.8-27b, openai/gpt-oss-20b).")
pdf.bullet("Exposed LLM-as-a-Judge Blindness:", "Demonstrated empirically that standalone LLM judges missed 38 of 53 criterion-unsafe responses (71.7% false-pass rate; 95% Wilson CI: 58.4%-82.0%), including 100% of failures (27/27) produced by fluent flagship/large generators under emergency pressure.")
pdf.bullet("Resolved Lexical False-Alarm Collapse:", "Eliminated the 48.2% false-alarm rate (177/367) of untyped keyword matchers via a canonical Assertion/Negation Gate (PROPOSED vs. NEGATED), rescuing safe clinicians who explicitly document contraindicated drugs to withhold them (100.0% specificity, Youden's J = 1.000).")
pdf.bullet("Zero-Hallucination Substring Gate:", "Built a deterministic Verbatim Substring Verification Gate enforcing character-level grounding (norm(source_span) in norm(R)), achieving 0 hallucinated extractions across 1,767 verified clinical events.")
pdf.bullet("Guideline-Grounded Benchmark:", "Authored 50 emergency medicine scenarios (15 dev, 35 strictly held-out test) anchored to Class I recommendations from AHA/ACC, ESC, BTS, EAST, and Surviving Sepsis Campaign guidelines.")

pdf.ln(1.5)

# Project 2
pdf.set_font("Helvetica", "B", 9.8)
pdf.set_text_color(15, 23, 42)
pdf.write(5, "2. Reasoning Debugger & Domain-Independent Execution Kernel   ")
pdf.set_font("Helvetica", "B", 8.2)
pdf.set_text_color(2, 132, 199)
pdf.write(5, "[Live Cloud App]", "https://hammam16.pythonanywhere.com/")
pdf.write(5, "  |  ")
pdf.write(5, "[Architecture Spec]", "https://github.com/HammamNM/reasoning-debugger/blob/main/ARCHITECTURE.md")
pdf.write(5, "  |  ")
pdf.write(5, "[Kernel Source]", "https://github.com/HammamNM/reasoning-debugger/tree/main/kernel")
pdf.ln(4.8)

pdf.set_font("Helvetica", "I", 8.4)
pdf.set_text_color(71, 85, 105)
pdf.cell(0, 4.5, "Creator & System Architect | Python, Directed Graph Modeling, Automated Contract Testing", new_x="LMARGIN", new_y="NEXT")
pdf.ln(0.8)

pdf.bullet("Structured Reasoning Graph Engine:", "Built a modular Python kernel transforming unstructured chain-of-thought and clinical decision traces into directed acyclic reasoning graphs with explicit hypothesis-evidence provenance links.")
pdf.bullet("Cognitive Bias & Failure Detectors:", "Implemented deterministic graph analyzers to localize epistemic failure patterns including anchoring bias, premature diagnostic closure, unsupported inference, and temporal prerequisite violations.")
pdf.bullet("Production-Grade Contract Testing:", "Enforced strict API boundary isolation, serialization round-trip guarantees, and zero-leakage contracts across 30+ automated pytest contract suites.")

# Section: Technical Skills
pdf.section_title("Technical & Clinical Arsenal")
pdf.bullet("AI Safety & LLM Evaluation:", "Multi-Ecosystem Benchmarking, LLM-as-a-Judge Failure Auditing, Sycophancy & Behavioral Shift Analysis, Rubric & Protocol Engineering, Statistical Verification (Wilson 95% CIs, Exact McNemar Tests, Ablation Design).")
pdf.bullet("Software Engineering:", "Python (OOP, Type-Safe Data Models, CLI & REST APIs), Neuro-Symbolic Pipelines, Deterministic Substring & Regex Engines, JSON Schema Constrained Decoding, Git/GitHub, Linux/Termux CLI Workflows.")
pdf.bullet("Clinical Domain Expertise:", "Emergency Medicine Triage & Resuscitation Protocols, AHA/ACC, ESC, BTS & ATLS Guideline Interpretation, Differential Diagnosis Modeling, Contraindication & Temporal Prerequisite Auditing.")

# Section: Publication
pdf.section_title("Research Publications & Preprints")
pdf.set_x(14)
pdf.set_font("Helvetica", "B", 8.8)
pdf.set_text_color(15, 23, 42)
pdf.write(4.3, "Omer, H. (2026). ")
pdf.set_font("Helvetica", "I", 8.8)
pdf.write(4.3, "Beyond Surface Fluency: A Deterministic-First Hybrid Clinical Auditor Exposes LLM-as-a-Judge Blindness and Behavioral Shifts Under Emergency Clinical Pressure. ")
pdf.set_font("Helvetica", "", 8.8)
pdf.write(4.3, "Zenodo Preprint (DOI: 10.5281/zenodo.23835945). Code & Interactive Explorer: ")
pdf.set_text_color(2, 132, 199)
pdf.write(4.3, "github.com/HammamNM/reasoning-debugger", "https://github.com/HammamNM/reasoning-debugger")
pdf.ln(5.5)

# Section: Education
pdf.section_title("Education & Scientific Communication")
pdf.bullet("MBBS Candidate (3rd Year):", "Faculty of Medicine, Omdurman Islamic University - Omdurman, Sudan (Ongoing, 2026).")
pdf.bullet("Founder & Technical Author - NexoraMed (nexoramed.online):", "Publishing technical analyses in English on Medical AI evaluation, clinical reasoning frameworks, and AI tools in medical education (2026 - Present).")

output_name = "CV_HAMMAM_OMER.pdf"
pdf.output(output_name)
print(f"✅ Generated {output_name} successfully (Pages: {pdf.page})!")

# Copy to Android Downloads folder if accessible so user can attach it easily from phone
dl_dir = os.path.expanduser("~/storage/downloads")
if os.path.isdir(dl_dir):
    shutil.copy(output_name, os.path.join(dl_dir, output_name))
    print(f"📲 Also copied to your phone's Downloads folder: {dl_dir}/{output_name}")
