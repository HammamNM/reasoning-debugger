import argparse
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
            print(f"\n[Finding {i+1}] {finding.failure_type}")
            print(f"Target: {finding.event_id}")
            print(f"Explanation: {finding.explanation}")
            
        if args.export_dot:
            dot_str = export_trace_to_dot(trace, findings)
            with open(args.export_dot, 'w') as f:
                f.write(dot_str)
            print(f"\nExported graph to {args.export_dot}")
            
    except InvalidTraceSchemaError as e:
        print(f"Schema Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Execution Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
