import os

print("1. Creating minimal pyproject.toml...")
with open("pyproject.toml", "w", encoding="utf-8") as f:
    f.write("""[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "clinical-reasoning-kernel"
version = "1.0.0"
description = "A deterministic, domain-agnostic reasoning compiler for clinical AI agents."
authors = [{name = "Reasoning Architect"}]
dependencies = []
requires-python = ">=3.9"

[project.scripts]
reasoning-cli = "kernel.cli:main"
""")

print("2. Securing Public API in kernel/__init__.py...")
with open("kernel/__init__.py", "w", encoding="utf-8") as f:
    f.write("""\"\"\"Public API for the Clinical Reasoning Kernel.\"\"\"
from kernel.api import (
    ReasoningDebugger,
    ReasoningTrace,
    ReasoningTraceEvent,
    DebugFinding,
    export_trace_to_dot,
    ReasoningKernelError,
    InvalidTraceSchemaError
)

__all__ = [
    "ReasoningDebugger",
    "ReasoningTrace",
    "ReasoningTraceEvent",
    "DebugFinding",
    "export_trace_to_dot",
    "ReasoningKernelError",
    "InvalidTraceSchemaError"
]
""")

print("3. Building the CLI Consumer...")
with open("kernel/cli.py", "w", encoding="utf-8") as f:
    f.write("""import argparse
import sys
import json
from kernel.api import ReasoningDebugger, ReasoningTrace, export_trace_to_dot, InvalidTraceSchemaError

def main():
    parser = argparse.ArgumentParser(description="Clinical Reasoning Kernel - CLI")
    parser.add_argument("trace_file", help="Path to the reasoning trace JSON file")
    parser.add_argument("--export-dot", help="Export failure graph to DOT file", type=str)
    
    args = parser.parse_args()
    
    try:
        with open(args.trace_file, 'r') as f:
            data = json.load(f)
            # Using from_dict to enforce strict schema boundaries
            trace = ReasoningTrace.from_dict(data)
            
        debugger = ReasoningDebugger()
        findings = debugger.debug(trace)
        
        print(f"Analysis Complete. Findings: {len(findings)}")
        for i, finding in enumerate(findings):
            print(f"\\n[Finding {i+1}] {finding.failure_type}")
            print(f"Target: {finding.event_id}")
            print(f"Explanation: {finding.explanation}")
            
        if args.export_dot:
            dot_str = export_trace_to_dot(trace, findings)
            with open(args.export_dot, 'w') as f:
                f.write(dot_str)
            print(f"\\nExported graph to {args.export_dot}")
            
    except InvalidTraceSchemaError as e:
        print(f"Schema Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Execution Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
""")

print("Stage 4 Packaging and CLI initialized.")
