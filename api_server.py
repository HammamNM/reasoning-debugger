from flask import Flask, request, jsonify, render_template_string
from kernel.api import ReasoningDebugger, ReasoningTrace, InvalidTraceSchemaError, export_trace_to_dot
import json

app = Flask(__name__)

def normalize_agent_trace(raw_data):
    """
    Adapter Layer: Translates Real-World Agent traces into Canonical Kernel Trace.
    Strictly follows the Conservatism Principle: No causal links are hallucinated.
    """
    normalized_events = []
    
    # 1. Native Kernel Format (Pass-through)
    if isinstance(raw_data, dict) and 'events' in raw_data and isinstance(raw_data['events'], list):
        if raw_data['events'] and 'event_type' in raw_data['events'][0]:
            return raw_data
            
    events_list = raw_data.get('steps', raw_data.get('messages', raw_data)) if isinstance(raw_data, dict) else raw_data
    
    if isinstance(events_list, list) and len(events_list) > 0:
        # 2. OpenAI / Chat-based Format
        if 'role' in events_list[0]:
            for i, msg in enumerate(events_list):
                event_id = msg.get('id', f"msg_{i+1}")
                metadata = msg.get('metadata', {})
                
                if msg.get('role') == 'assistant' and msg.get('tool_calls'):
                    normalized_events.append({"id": event_id, "event_type": "INVESTIGATION", "content": str(msg['tool_calls']), "metadata": metadata})
                elif msg.get('role') == 'tool':
                    normalized_events.append({"id": event_id, "event_type": "EVIDENCE", "content": msg.get('content', ''), "metadata": metadata})
                elif msg.get('role') == 'assistant' and msg.get('content'):
                    normalized_events.append({"id": event_id, "event_type": "INFERENCE", "content": msg['content'], "metadata": metadata})
                    
        # 3. Generic LangChain / ReAct Format
        elif 'thought' in events_list[0] or 'action' in events_list[0]:
            for i, step in enumerate(events_list):
                event_id = step.get('id', f"step_{i+1}")
                metadata = step.get('metadata', {})
                
                if 'action' in step or 'tool_call' in step:
                    normalized_events.append({"id": event_id, "event_type": "INVESTIGATION", "content": str(step.get('action', step.get('tool_call'))), "metadata": metadata})
                elif 'observation' in step or 'result' in step:
                    normalized_events.append({"id": event_id, "event_type": "EVIDENCE", "content": str(step.get('observation', step.get('result'))), "metadata": metadata})
                elif 'thought' in step or 'reasoning' in step:
                    normalized_events.append({"id": event_id, "event_type": "INFERENCE", "content": str(step.get('thought', step.get('reasoning'))), "metadata": metadata})
                
    return {"events": normalized_events}

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reasoning Debugger</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; background: #f8f9fa; margin: 0; padding: 20px; color: #333; }
        .container { max-width: 1200px; margin: auto; }
        .header { text-align: center; margin-bottom: 20px; }
        .input-section { background: white; padding: 20px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 20px; }
        .file-upload { margin-bottom: 15px; font-weight: bold; }
        textarea { width: 100%; height: 200px; padding: 10px; border: 1px solid #ccc; border-radius: 8px; font-family: monospace; box-sizing: border-box; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 8px; cursor: pointer; margin-top: 15px; width: 100%; }
        button:hover { background: #0056b3; }
        #graph-container { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-top: 20px; min-height: 400px; text-align: center; overflow: auto; }
        #error-msg { color: #dc3545; font-weight: bold; margin-top: 10px; text-align: center; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/viz.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/full.render.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Reasoning Debugger</h1>
            <p>Upload a trace file or paste JSON below</p>
        </div>
        
        <div class="input-section">
            <div class="file-upload">
                <label for="file-input">📂 Upload Trace File: </label>
                <input type="file" id="file-input" accept=".json,.traj,.txt" onchange="handleFileUpload(event)">
            </div>
            <textarea id="trace-input" placeholder='{"events": [...]}'></textarea>
            <button onclick="processTrace()">Debug Trace</button>
            <div id="error-msg"></div>
        </div>

        <div id="graph-container">Trace Graph will appear here...</div>
    </div>

    <script>
        function handleFileUpload(event) {
            const file = event.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById("trace-input").value = e.target.result;
            };
            reader.readAsText(file);
        }

        async function processTrace() {
            const inputData = document.getElementById("trace-input").value;
            const errorMsg = document.getElementById("error-msg");
            const graphContainer = document.getElementById("graph-container");
            
            if (!inputData.trim()) {
                errorMsg.innerText = "Please provide trace data.";
                return;
            }

            errorMsg.innerText = "";
            graphContainer.innerHTML = "Processing...";

            try {
                const parsedData = JSON.parse(inputData);
                const response = await fetch("/debug", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(parsedData)
                });

                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.error || "Unknown error occurred");
                }

                let viz = new Viz();
                viz.renderSVGElement(result.dot_graph)
                .then(function(element) {
                    graphContainer.innerHTML = "";
                    element.style.width = "100%";
                    element.style.height = "auto";
                    graphContainer.appendChild(element);
                })
                .catch(error => {
                    viz = new Viz();
                    errorMsg.innerText = "Error rendering graph.";
                    console.error(error);
                });

            } catch (err) {
                errorMsg.innerText = "Error: " + err.message;
                graphContainer.innerHTML = "";
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML)

@app.route('/debug', methods=['POST'])
def debug_trace():
    try:
        raw_data = request.get_json()
        if not raw_data:
            return jsonify({"error": "Empty JSON payload"}), 400
            
        canonical_data = normalize_agent_trace(raw_data)
        
        if 'events' not in canonical_data or not canonical_data['events']:
            return jsonify({"error": "Adapter could not extract valid reasoning events from this trace format."}), 400
            
        trace = ReasoningTrace.from_dict(canonical_data)
        debugger = ReasoningDebugger()
        findings = debugger.debug(trace)
        
        response_data = {
            "status": "success",
            "findings_count": len(findings),
            "findings": [
                {"event_id": f.event_id, "failure_type": f.failure_type, "explanation": f.explanation, "affected_event_ids": list(f.affected_event_ids)}
                for f in findings
            ]
        }
        
        if findings:
            response_data["dot_graph"] = export_trace_to_dot(trace, findings)
            
        return jsonify(response_data), 200
        
    except InvalidTraceSchemaError as e:
        return jsonify({"error": f"Schema Error: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
