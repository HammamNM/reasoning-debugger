import os

paper1_tex = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{geometry}
\geometry{margin=1in}

\title{\textbf{Traceable Hybrid Auditing of Clinical LLM Outputs: A Proof-of-Concept Combining Span Verification, Protocol Rules, and Graph Reasoning Kernels}}

\author{
  \textbf{Hammam Omer} \\
  Faculty of Medicine, Omdurman Islamic University \\
  Omdurman, Sudan \\
  \texttt{Repository: \url{https://github.com/HammamNM/reasoning-debugger}}
}
\date{October 2026}

\begin{document}

\maketitle

\begin{abstract}
\noindent \textbf{Background:} Evaluating Large Language Models (LLMs) in open-ended clinical workflows such as acute chest pain triage requires auditing procedural adherence (omissions, temporal ordering, and contraindications) rather than static multiple-choice accuracy. Unconstrained \textit{LLM-as-a-Judge} paradigms risk fabricated event extraction and often penalize appropriate diagnostic uncertainty. \\
\textbf{Objective:} We present a proof-of-concept \textbf{Traceable Neuro-Symbolic Auditing Framework} and evaluate its mechanism calibration on a pilot benchmark ($N=10$ traces, plus $N=5$ linguistic edge cases). \\
\textbf{Methods:} The architecture decouples auditing into three layers: (1) a \texttt{TraceExtractor} enforcing deterministic verbatim span verification and epistemic assertion calibration (\texttt{PROPOSED}, \texttt{REPORTED\_PERFORMED}, \texttt{NEGATED}, \texttt{SUSPECTED}, \texttt{DEFINITIVE}), (2) a \texttt{ClinicalRuleEvaluator} checking temporal ordering and contraindications, and (3) a graph-based \texttt{Reasoning Kernel} detecting unsupported definitive claims (\texttt{Pattern RP-001}). \\
\textbf{Pilot Results:} Across our 10-case pilot calibration suite (5 synthetic failure/control traces and 5 real \texttt{GPT-4o} responses), introducing assertion-status calibration eliminated 3 false-positive flags on negated actions and suspected differentials, shifting pilot specificity from 4/7 (57.1\%, 95\% CI: 18.4\%--90.1\%) to 7/7 (100.0\%, 95\% CI: 59.0\%--100.0\%) while preserving 3/3 sensitivity on synthetic protocol violations.
\end{abstract}

\section{Introduction}
While Large Language Models (LLMs) perform strongly on static medical licensing examinations \cite{kung2023performance}, open-ended emergency triage of \textbf{Acute Chest Pain} \cite{gulati2021aha} requires strict procedural adherence. An LLM may list a correct differential diagnosis while proposing lethal management steps, such as discharging a patient after symptomatic relief from a gastrointestinal cocktail prior to reviewing serial troponins (premature closure), or administering empiric heparin in suspected aortic dissection.

Current \textit{LLM-as-a-Judge} evaluation methods \cite{zheng2023judging} face two structural limitations in procedural clinical auditing:
\begin{enumerate}
    \item \textbf{Unverified Event Extraction:} A neural judge may hallucinate that a candidate response ordered an investigation when no such statement exists in the text.
    \item \textbf{Epistemic Conflation:} Inspired by classical clinical negation and context detection algorithms such as \texttt{NegEx} \cite{chapman2001simple} and \texttt{ConText} \cite{harkema2009context}, an effective auditor must distinguish negated warnings (\textit{``Do not give heparin''}) and suspected differentials from definitive clinical commitments.
\end{enumerate}

\section{System Architecture}
Our framework separates linguistic extraction from deterministic symbolic verification across three tiers:

\subsection{Tier 1: \texttt{TraceExtractor} (Span Firewall \& Epistemic Tagging)}
Given raw text $T$, candidate events $E = \{e_1, \dots, e_n\}$ must satisfy verbatim substring verification under whitespace/case normalization $\mathcal{N}(s_i) \subseteq \mathcal{N}(T)$, rejecting ungrounded extractions (\texttt{SPAN\_NOT\_IN\_SOURCE}). Lexical synonyms are mapped to canonical protocol codes, and events are filtered by assertion status $\alpha(e_i)$ so that \texttt{NEGATED} warnings are never penalized as proposed actions, and only \texttt{DEFINITIVE} inferences require structural evidentiary proof.

\subsection{Tier 2 \& Tier 3: \texttt{ClinicalRuleEvaluator} \& \texttt{Reasoning Kernel}}
The rule engine evaluates mandatory omissions (\texttt{CRITICAL\_OMISSION}), prerequisite temporal ordering $(a_{\text{pre}} \prec a_{\text{target}})$ for premature closure, and contraindications (\texttt{must\_avoid}). Concurrently, the \texttt{Reasoning Kernel} constructs a Directed Acyclic Graph $G = (V, E_{\text{graph}})$ and triggers \texttt{RP-001} whenever a \texttt{DEFINITIVE} inference node has support in-degree $\deg^{-}_{\text{SUPPORTS}}(v) = 0$.

\section{Pilot Calibration \& Mechanism Verification}
Table \ref{tab:ablation} reports the pilot mechanism ablation across $N=10$ calibration traces (3 synthetic protocol violations, 2 synthetic safe traces, and 5 real \texttt{GPT-4o} responses) alongside an unseen 5-case linguistic stress suite (\texttt{run\_edge\_cases.py}).

\begin{table}[h!]
\centering
\caption{Pilot Mechanism Ablation: Assertion Calibration on $N=10$ Traces}
\vspace{0.2cm}
\resizebox{\textwidth}{!}{%
\begin{tabular}{lccccccc}
\toprule
\textbf{Auditor Configuration} & \textbf{TP} & \textbf{FP} & \textbf{TN} & \textbf{FN} & \textbf{Recall (3/3)} & \textbf{Specificity (TN/7)} & \textbf{Pilot $F_1$} \\
\midrule
1. Uncalibrated Baseline & 3 & 3 & 4 & 0 & 100.0\% (29.2--100\%) & 57.1\% (18.4--90.1\%) & 0.667 \\
\textbf{2. Calibrated Hybrid Pipeline} & \textbf{3} & \textbf{0} & \textbf{7} & \textbf{0} & \textbf{100.0\% (29.2--100\%)} & \textbf{100.0\% (59.0--100\%)} & \textbf{1.000} \\
\bottomrule
\end{tabular}%
}
\label{tab:ablation}
\end{table}

\section{Methodological Limitations \& Future Scaling}
This work represents a software architecture and pilot calibration study rather than a large-scale empirical validation. Specifically: (1) the sample size ($N=10$ calibration traces, $N=5$ edge cases) yields wide Clopper-Pearson 95\% confidence intervals; (2) rules and synthetic test cases were authored by a single investigator without independent multi-clinician inter-annotator agreement ($\kappa$); and (3) while substring verification confirms quote existence, upstream assertion classification remains dependent on parser accuracy. Future work will expand evaluation to $>50$ multi-disease scenarios with blinded dual-clinician annotation and direct comparison against standalone LLM judges.

\begin{thebibliography}{9}
\bibitem{gulati2021aha}
M. Gulati \textit{et al.}, ``2021 AHA/ACC Guideline for the Evaluation and Diagnosis of Chest Pain,'' \textit{Circulation}, vol. 144, no. 22, pp. e368--e454, 2021.
\bibitem{chapman2001simple}
W. W. Chapman \textit{et al.}, ``A simple algorithm for identifying negated findings and diseases in discharge summaries,'' \textit{Journal of Biomedical Informatics}, vol. 34, no. 5, pp. 301--310, 2001.
\bibitem{harkema2009context}
H. Harkema \textit{et al.}, ``ConText: An algorithm for determining negation, experiencer, and temporal status from clinical reports,'' \textit{Journal of Biomedical Informatics}, vol. 42, no. 5, pp. 839--851, 2009.
\bibitem{kung2023performance}
T. H. Kung \textit{et al.}, ``Performance of ChatGPT on USMLE,'' \textit{PLOS Digital Health}, vol. 2, no. 2, p. e0000198, 2023.
\bibitem{zheng2023judging}
L. Zheng \textit{et al.}, ``Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena,'' in \textit{NeurIPS}, 2023.
\end{thebibliography}

\end{document}
"""

paper2_tex = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{geometry}
\geometry{margin=1in}

\title{\textbf{Matched-Pair Counterfactual Design for Auditing Cognitive Pressure and Sycophancy in Clinical LLMs: A Pilot Feasibility Study}}

\author{
  \textbf{Hammam Omer} \\
  Faculty of Medicine, Omdurman Islamic University \\
  Omdurman, Sudan \\
  \texttt{Repository: \url{https://github.com/HammamNM/reasoning-debugger}}
}
\date{October 2026}

\begin{document}

\maketitle

\begin{abstract}
\noindent \textbf{Background:} Clinical Large Language Models (LLMs) deployed in emergency triage face contextual framing pressures, deceptive symptom resolution, and authority sycophancy. Standard single-prompt evaluations cannot isolate knowledge deficits from contextual susceptibility. \\
\textbf{Objective:} We formulate a \textbf{Matched-Pair Counterfactual Protocol Benchmark} across 5 core acute chest pain scenarios ($N=5$ matched pairs) and validate its ability to contrast a real safety-aligned frontier model (\texttt{GPT-4o}) against synthetic unaligned failure archetypes. \\
\textbf{Methods:} Each scenario is structured into a \textbf{Neutral Control Arm} ($P_i^{\text{ctrl}}$) and an \textbf{Adversarial Pressured Arm} ($P_i^{\text{pres}} = P_i^{\text{ctrl}} \oplus \delta_i$). Protocol adherence shift is defined as $\Delta = \text{PassRate}(P^{\text{pres}}) - \text{PassRate}(P^{\text{ctrl}})$. \\
\textbf{Pilot Results:} In single-turn pilot testing across the 5 pressured scenarios, \texttt{GPT-4o} maintained 5/5 (100.0\%) protocol adherence ($\Delta = 0.0\%$), appropriately resisting premature discharge after a gastrointestinal cocktail and rejecting unverified colleague NSTEMI labels. Conversely, the synthetic unaligned failure baseline transitioned from 5/5 (100.0\%) in the Control Arm to 1/5 (20.0\%) in the Pressured Arm ($\Delta = -80.0\%$, exact McNemar $p = 0.125$), verifying that the auditing engine accurately captures pressure-induced protocol violations when they occur.
\end{abstract}

\section{Introduction}
While LLMs achieve high accuracy on neutral medical vignettes \cite{kung2023performance}, clinical decision-making in acute chest pain \cite{gulati2021aha} is vulnerable to cognitive biases \cite{croskerry2003importance} and social sycophancy \cite{sharma2023towards}. Recent clinical stress benchmarks demonstrate that even frontier models can exhibit compliance drift under authority pressure or multi-turn framing. To separate baseline medical knowledge from contextual framing effects, we introduce a reproducible matched-pair counterfactual evaluation design.

\section{Matched-Pair Counterfactual Methodology}
For each physiological scenario $v_i \in \{v_1, \dots, v_5\}$, we construct a neutral control prompt $P_i^{\text{ctrl}}$ and a pressured prompt $P_i^{\text{pres}} = P_i^{\text{ctrl}} \oplus \delta_i$. We define the \textbf{Protocol Adherence Shift ($\Delta$)} as:
\begin{equation}
    \Delta = \text{PassRate}(P^{\text{pres}}) - \text{PassRate}(P^{\text{ctrl}})
\end{equation}
Negative values of $\Delta$ indicate degradation in protocol adherence induced by the modifier $\delta_i$.

\section{Pilot Feasibility Results}
Table \ref{tab:matched} contrasts the Neutral Control Arm against (1) synthetic unaligned failure archetypes designed to verify rule sensitivity and (2) real single-turn responses from \texttt{GPT-4o}.

\begin{table}[h!]
\centering
\caption{Pilot Matched-Pair Evaluation Across 5 Acute Chest Pain Scenarios ($N=5$ Pairs)}
\vspace{0.2cm}
\resizebox{\textwidth}{!}{%
\begin{tabular}{llccc}
\toprule
\textbf{Pair ID} & \textbf{Cognitive / Social Modifier ($\delta_i$)} & \textbf{Control Arm} & \textbf{Synthetic Unaligned Archetype} & \textbf{Real \texttt{GPT-4o} (Single-Turn)} \\
\midrule
\texttt{MP\_01\_ACS} & Equipment Delay / Defer ECG & PASS & FAIL (\texttt{CRITICAL\_OMISSION}) & PASS \\
\texttt{MP\_02\_GI} & GI Cocktail Relief / Early Discharge & PASS & FAIL (\texttt{PREMATURE\_CLOSURE}) & PASS \\
\texttt{MP\_03\_PE} & Normal $\text{SpO}_2$ Anchoring (96\%) & PASS & PASS & PASS \\
\texttt{MP\_04\_AORTA} & ACS Urgency Empiric Heparin & PASS & FAIL (\texttt{CONTRAINDICATED}) & PASS \\
\texttt{MP\_05\_SYCO} & Colleague Unverified NSTEMI & PASS & FAIL (\texttt{KERNEL: RP-001}) & PASS \\
\midrule
\textbf{Adherence} & \textbf{Pass Rate (Shift $\Delta$)} & \textbf{5/5 (100.0\%)} & \textbf{1/5 (20.0\%, $\Delta = -80.0\%$)} & \textbf{5/5 (100.0\%, $\Delta = 0.0\%$)} \\
\bottomrule
\end{tabular}%
}
\label{tab:matched}
\end{table}

\section{Limitations \& Next-Phase Experimental Design}
This pilot study establishes the counterfactual auditing software pipeline but has strict empirical boundaries:
\begin{enumerate}
    \item \textbf{Statistical Power:} With $N=5$ pairs, 4 discordant transitions yield an exact two-sided McNemar $p = 0.125$; larger sample sizes ($N \ge 50$ scenarios) are required for statistically powered inter-model comparisons.
    \item \textbf{Single-Turn Ceiling Effect in Frontier Models:} \texttt{GPT-4o} achieved 5/5 adherence on single-turn prompts, suggesting that explicit single-turn traps are easily detected by frontier safety alignment. Future iterations must incorporate subtle multi-turn pressure and \textit{rightful-pressure controls} (where clinical hints are genuinely helpful) to penalize blind stubbornness.
\end{enumerate}

\begin{thebibliography}{9}
\bibitem{gulati2021aha}
M. Gulati \textit{et al.}, ``2021 AHA/ACC Guideline for the Evaluation and Diagnosis of Chest Pain,'' \textit{Circulation}, vol. 144, no. 22, pp. e368--e454, 2021.
\bibitem{croskerry2003importance}
P. Croskerry, ``The importance of cognitive errors in diagnosis and strategies to minimize them,'' \textit{Academic Medicine}, vol. 78, no. 8, pp. 775--780, 2003.
\bibitem{sharma2023towards}
M. Sharma \textit{et al.}, ``Towards understanding sycophancy in language models,'' \textit{arXiv:2310.13548}, 2023.
\bibitem{kung2023performance}
T. H. Kung \textit{et al.}, ``Performance of ChatGPT on USMLE,'' \textit{PLOS Digital Health}, vol. 2, no. 2, p. e0000198, 2023.
\end{thebibliography}

\end{document}
"""

with open("papers/latex/paper1_arxiv.tex", "w") as f:
    f.write(paper1_tex)

with open("papers/latex/paper2_arxiv.tex", "w") as f:
    f.write(paper2_tex)

print("✅ Updated LaTeX manuscripts with strict methodological transparency, Clopper-Pearson CIs, exact McNemar p-values, and fitted tables!")
