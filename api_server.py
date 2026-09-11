from flask import Flask, request, jsonify, render_template_string
from kernel.api import ReasoningDebugger, ReasoningTrace, InvalidTraceSchemaError, export_trace_to_dot
import json

app = Flask(__name__)

def normalize_agent_trace(raw_data):
    if isinstance(raw_data, dict) and 'events' in raw_data:
        if len(raw_data['events']) > 0 and 'event_type' in raw_data['events'][0]:
            return raw_data

    events = []
    raw_events = []

    if isinstance(raw_data, list):
        raw_events = raw_data
    elif isinstance(raw_data, dict):
        if 'trajectory' in raw_data:
            raw_events = raw_data['trajectory']
        elif 'steps' in raw_data:
            raw_events = raw_data['steps']
        else:
            for k, v in raw_data.items():
                if isinstance(v, list):
                    raw_events = v
                    break

    for i, item in enumerate(raw_events):
        if not isinstance(item, dict):
            item = {"content": str(item)}
            
        event_type = "INVESTIGATION"
        content = item.get("content", str(item))
        
        if "thought" in item or "reasoning" in item or "plan" in item:
            event_type = "INFERENCE"
            content = item.get("thought", item.get("reasoning", item.get("plan", content)))
        elif "observation" in item or "obs" in item or "output" in item:
            event_type = "OBSERVATION"
            content = item.get("observation", item.get("obs", item.get("output", content)))
        elif "action" in item or "tool" in item:
            event_type = "INVESTIGATION"
            content = item.get("action", item.get("tool", content))
        elif "query" in item or "search" in item or "tool_input" in item:
            event_type = "INVESTIGATION"
            content = item.get("query", item.get("search", item.get("tool_input", content)))
        elif "event_type" in item:
            event_type = item["event_type"]

        events.append({
            "id": item.get("id", f"e{i+1}"),
            "event_type": str(event_type).upper(),
            "content": str(content),
            "metadata": item.get("metadata", item)
        })
        
    return {"events": events}

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reasoning Debugger</title>
    <style>
        :root { --primary: #2563eb; --bg: #f8fafc; --surface: #ffffff; --text: #0f172a; --border: #e2e8f0; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: var(--bg); margin: 0; padding: 20px; color: var(--text); }
        .container { max-width: 1000px; margin: auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .logo { font-size: 28px; font-weight: 800; color: var(--primary); letter-spacing: -0.5px; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .logo span { color: var(--text); }
        .badge { display: inline-block; background: #e0e7ff; color: #4338ca; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-top: 8px; letter-spacing: 0.5px; }
        .input-section { background: var(--surface); padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border: 1px solid var(--border); margin-bottom: 25px; }
        .file-upload { margin-bottom: 15px; font-weight: 600; color: #475569; }
        input[type="file"] { font-family: inherit; }
        textarea { width: 100%; height: 220px; padding: 15px; border: 1px solid var(--border); border-radius: 8px; font-family: 'Consolas', monospace; box-sizing: border-box; background: #f1f5f9; color: #334155; resize: vertical; }
        textarea:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1); }
        button { background: var(--primary); color: white; border: none; padding: 12px 24px; font-size: 16px; font-weight: 600; border-radius: 8px; cursor: pointer; margin-top: 15px; width: 100%; transition: background 0.2s; }
        button:hover { background: #1d4ed8; }
        #graph-container { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 25px; margin-top: 20px; min-height: 400px; text-align: center; overflow: auto; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
        #error-msg { color: #ef4444; font-weight: 600; margin-top: 15px; text-align: center; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/viz.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/full.render.js"></script>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
                Reasoning<span>Debugger</span>
            </div>
            <div class="badge">Powered by nexoramed.online</div>
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
