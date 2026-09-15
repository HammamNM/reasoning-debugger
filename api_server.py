from flask import Flask, request, jsonify
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

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reasoning Debugger</title>
    <style>
        :root { --primary: #2563eb; --bg: #f8fafc; --surface: #ffffff; --text: #0f172a; --border: #e2e8f0; }
        [data-theme="dark"] { --primary: #3b82f6; --bg: #0f172a; --surface: #1e293b; --text: #f8fafc; --border: #334155; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: var(--bg); margin: 0; padding: 20px; color: var(--text); transition: all 0.3s ease; }
        .container { max-width: 1000px; margin: auto; position: relative; }
        .header { text-align: center; margin-bottom: 30px; }
        .logo { font-size: 28px; font-weight: 800; color: var(--primary); letter-spacing: -0.5px; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .logo span { color: var(--text); }
        .badges { display: flex; justify-content: center; align-items: center; gap: 10px; margin-top: 12px; flex-wrap: wrap; }
        .badge { display: inline-block; background: #e0e7ff; color: #4338ca; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; text-decoration: none; border: none; }
        .badge-docs { background: var(--text); color: var(--bg); }
        .theme-toggle { background: var(--surface); border: 1px solid var(--border); border-radius: 20px; cursor: pointer; padding: 4px 12px; font-size: 16px; color: var(--text); display: flex; align-items: center; justify-content: center; height: 32px; }
        [data-theme="dark"] .badge { background: #3730a3; color: #e0e7ff; }
        [data-theme="dark"] .badge-docs { background: var(--primary); color: white; }
        .input-section { background: var(--surface); padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid var(--border); margin-bottom: 25px; }
        .file-upload { margin-bottom: 15px; font-weight: 600; }
        textarea { width: 100%; height: 220px; padding: 15px; border: 1px solid var(--border); border-radius: 8px; font-family: 'Consolas', monospace; box-sizing: border-box; background: var(--bg); color: var(--text); resize: vertical; margin-top: 10px; }
        textarea:focus { outline: none; border-color: var(--primary); }
        .btn-group { display: flex; gap: 10px; margin-top: 15px; }
        button { flex: 1; background: var(--primary); color: white; border: none; padding: 12px; font-size: 16px; font-weight: 600; border-radius: 8px; cursor: pointer; transition: 0.2s; }
        button:hover { opacity: 0.9; }
        .btn-secondary { background: transparent; border: 2px solid var(--primary); color: var(--primary); }
        [data-theme="dark"] .btn-secondary { border-color: var(--text); color: var(--text); }
        #graph-container { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 25px; margin-top: 20px; min-height: 100px; text-align: center; overflow: auto; }
        #error-msg { color: #ef4444; font-weight: 600; margin-top: 15px; text-align: center; }
        #download-btn { display: none; margin-top: 15px; width: 100%; }
        
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); align-items: center; justify-content: center; z-index: 1000; }
        .modal-content { background: var(--surface); padding: 30px; border-radius: 12px; width: 90%; max-width: 500px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border: 1px solid var(--border); position: relative; }
        .close-btn { position: absolute; top: 15px; right: 15px; background: none; border: none; font-size: 24px; cursor: pointer; color: var(--text); }
        .modal-title { color: #ef4444; margin-top: 0; font-size: 20px; font-weight: bold; }
        .modal-desc { margin-top: 15px; line-height: 1.5; font-size: 15px;}
        .node { cursor: pointer; transition: filter 0.2s; }
        .node:hover { filter: drop-shadow(0 0 5px rgba(37,99,235,0.4)); }
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
            <div class="badges">
                <div class="badge">Powered by nexoramed.online</div>
                <a href="/docs" class="badge badge-docs">API Docs</a>
                <button class="theme-toggle" onclick="window.toggleTheme()">Theme</button>
            </div>
        </div>
        
        <div class="input-section">
            <div class="file-upload">
                <label for="file-input">Upload Trace File: </label>
                <input type="file" id="file-input" accept=".json,.traj,.txt" onchange="window.handleFileUpload(event)">
            </div>
            <textarea id="trace-input" placeholder='{"events": []}'></textarea>
            <div class="btn-group">
                <button onclick="window.loadSample()" class="btn-secondary">Load Sample</button>
                <button onclick="window.processTrace()">Debug Trace</button>
            </div>
            <div id="error-msg"></div>
        </div>

        <div id="graph-container">Trace Graph will appear here...</div>
        <button id="download-btn" class="btn-secondary" onclick="window.downloadSVG()">Download Graph as SVG</button>
    </div>

    <div id="failure-modal" class="modal">
        <div class="modal-content">
            <button class="close-btn" onclick="window.closeModal()">X</button>
            <div class="modal-title" id="modal-title">Failure Detected</div>
            <div class="modal-desc" id="modal-desc">Details...</div>
        </div>
    </div>

    <script>
        window.currentFindings = [];

        window.toggleTheme = function() {
            const html = document.documentElement;
            if (html.getAttribute('data-theme') === 'light') {
                html.setAttribute('data-theme', 'dark');
            } else {
                html.setAttribute('data-theme', 'light');
            }
        };

        window.loadSample = function() {
            const sampleData = {
                "steps": [
                    { "tool": "Search", "tool_input": "error code 500" },
                    { "observation": "No results found" },
                    { "tool": "Search", "tool_input": "error code 500" },
                    { "observation": "No results found" },
                    { "tool": "Search", "tool_input": "error code 500" }
                ]
            };
            document.getElementById('trace-input').value = JSON.stringify(sampleData, null, 4);
        };

        window.handleFileUpload = function(event) {
            const file = event.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function(e) { document.getElementById("trace-input").value = e.target.result; };
            reader.readAsText(file);
        };

        window.processTrace = async function() {
            const inputData = document.getElementById("trace-input").value;
            const errorMsg = document.getElementById("error-msg");
            const graphContainer = document.getElementById("graph-container");
            const downloadBtn = document.getElementById("download-btn");
            
            if (!inputData.trim()) { errorMsg.innerText = "Please provide trace data."; return; }
            errorMsg.innerText = "";
            graphContainer.innerHTML = "Processing...";
            downloadBtn.style.display = 'none';
            window.currentFindings = [];

            let parsedData;
            try {
                parsedData = JSON.parse(inputData);
            } catch(e) {
                errorMsg.innerText = "Invalid JSON format: " + e.message;
                graphContainer.innerHTML = "";
                return;
            }

            try {
                try {
                    const apiResponse = await fetch("/api/v1/debug", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(parsedData)
                    });
                    const apiResult = await apiResponse.json();
                    if (apiResponse.ok && apiResult.findings) {
                        window.currentFindings = apiResult.findings;
                    }
                } catch(e) {
                    console.log("API info fetch failed, continuing to graph render.");
                }
                
                const uiResponse = await fetch("/debug", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(parsedData)
                });
                
                const result = await uiResponse.json();
                if (!uiResponse.ok) throw new Error(result.error || "Server processing error");

                let viz = new Viz();
                viz.renderSVGElement(result.dot_graph).then(function(element) {
                    graphContainer.innerHTML = "";
                    element.style.width = "100%";
                    element.style.height = "auto";
                    graphContainer.appendChild(element);
                    downloadBtn.style.display = 'block';
                    window.makeNodesInteractive(element);
                }).catch(error => { errorMsg.innerText = "Graph rendering failed."; });
            } catch (err) {
                errorMsg.innerText = "Error: " + err.message;
                graphContainer.innerHTML = "";
            }
        };

        window.makeNodesInteractive = function(svgElement) {
            const nodes = svgElement.querySelectorAll('.node');
            nodes.forEach(node => {
                node.addEventListener('click', () => {
                    const titleEl = node.querySelector('title');
                    if (!titleEl) return;
                    const nodeId = titleEl.textContent.trim();
                    const finding = window.currentFindings.find(f => f.event_id === nodeId);
                    
                    if (finding) {
                        document.getElementById('modal-title').innerText = "Failure: " + finding.failure_type.replace(/_/g, ' ');
                        document.getElementById('modal-desc').innerText = finding.explanation;
                        document.getElementById('failure-modal').style.display = 'flex';
                    }
                });
            });
        };

        window.closeModal = function() {
            document.getElementById('failure-modal').style.display = 'none';
        };

        window.downloadSVG = function() {
            const svg = document.querySelector("#graph-container svg");
            if (!svg) return;
            const serializer = new XMLSerializer();
            let source = serializer.serializeToString(svg);
            if (source.indexOf('xmlns="http://www.w3.org/2000/svg"') === -1) {
                source = source.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"');
            }
            source = '<?xml version="1.0" standalone="no"?>\\n' + source;
            const blob = new Blob([source], {type: "image/svg+xml;charset=utf-8"});
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "reasoning_trace.svg";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        };
    </script>
</body>
</html>"""

API_DOCS_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Documentation - Reasoning Debugger</title>
    <style>
        body { font-family: 'Segoe UI', system-ui, sans-serif; padding: 40px 20px; background: #f8fafc; color: #0f172a; line-height: 1.6; max-width: 900px; margin: auto; }
        .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }
        h1, h2, h3 { color: #2563eb; margin-top: 1.5em;}
        pre { background: #1e293b; color: #f8fafc; padding: 15px; border-radius: 8px; overflow-x: auto; font-family: 'Consolas', monospace; font-size: 14px; }
        .endpoint { display: inline-block; background: #2563eb; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-family: monospace; font-size: 16px; margin-bottom: 10px; }
        a { color: #2563eb; text-decoration: none; font-weight: bold; }
        a:hover { text-decoration: underline; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14.5px;}
        th, td { padding: 12px; border: 1px solid #e2e8f0; text-align: left; vertical-align: top; }
        th { background: #f1f5f9; color: #0f172a;}
        .badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 13px; font-weight: bold; font-family: monospace; }
        .badge-fail { background: #fee2e2; color: #ef4444; border: 1px solid #fca5a5; }
        .badge-prop { background: #e0e7ff; color: #4338ca; border: 1px solid #a5b4fc; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📖 API Documentation (v1.0)</h1>
        <p>Integrate the Reasoning Debugger into your CI/CD pipeline or Agent workflows to formally validate reasoning traces and visually map dependency failures based on strict causal graphs.</p>
        
        <h2>Authentication</h2>
        <p>To use the API in production, pass your assigned API key in the request headers:</p>
        <pre><code>Authorization: Bearer YOUR_API_KEY_HERE</code></pre>

        <h2>Analyze Trace Endpoint</h2>
        <div class="endpoint">POST /api/v1/debug</div>
        <p>Expects a JSON payload containing the agent's execution trace. Each event must strictly define an <code>id</code> and <code>event_type</code>.</p>
        
        <h3>Validated Contracts & Capabilities (v1.0)</h3>
        <table>
            <tr><th>Feature / Failure Type</th><th>Description & Formal Contract</th></tr>
            <tr>
                <td><span class="badge badge-fail">unsupported_inference</span></td>
                <td><strong>Contract:</strong> An <code>INFERENCE</code> event requires support (<code>support_required = true</code>) but lacks a valid causal edge (<code>DERIVED_FROM</code>) to an <code>EVIDENCE</code> or prior <code>INFERENCE</code> node in the graph.</td>
            </tr>
            <tr>
                <td><span class="badge badge-prop">Failure Propagation</span></td>
                <td><strong>Contract:</strong> Automatically tracks causal dependencies. If a node fails, the failure cascades downstream to any actions holding a direct explicit dependency on it.</td>
            </tr>
        </table>

        <h3>Request Body Example</h3>
        <pre><code>{
  "events": [
    { "id": "e1", "event_type": "INVESTIGATION", "content": "Query DB for patient records" },
    { "id": "e2", "event_type": "OBSERVATION", "content": "Database Error 500: Timeout" },
    { "id": "e3", "event_type": "INFERENCE", "content": "Patient has diabetes based on records" }
  ]
}</code></pre>
        
        <h3>Success Response Example (200 OK)</h3>
        <pre><code>{
  "status": "success",
  "total_events": 3,
  "failures_detected": 1,
  "findings": [
    {
      "event_id": "e3",
      "failure_type": "unsupported_inference",
      "explanation": "Inference lacks valid evidence or causal support.",
      "affected_actions_count": 0
    }
  ]
}</code></pre>
        <br><br>
        <a href="/">&larr; Back to Dashboard</a>
    </div>
</body>
</html>"""

@app.route('/')
def index():
    return DASHBOARD_HTML, 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/docs')
def api_docs():
    return API_DOCS_HTML, 200, {'Content-Type': 'text/html; charset=utf-8'}

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
                {"event_id": f.event_id, "failure_type": f.failure_type, "explanation": f.explanation, "affected_event_ids": list(f.affected_event_ids)} for f in findings
            ]
        }

        if findings:
            response_data["dot_graph"] = export_trace_to_dot(trace, findings)

        return jsonify(response_data), 200

    except InvalidTraceSchemaError as e:
        return jsonify({"error": f"Schema Error: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/debug', methods=['POST'])
def api_debug():
    try:
        raw_data = request.get_json()
        if not raw_data:
            return jsonify({"error": "No JSON data provided"}), 400

        normalized_data = normalize_agent_trace(raw_data)
        trace = ReasoningTrace.model_validate(normalized_data)

        debugger = ReasoningDebugger()
        findings = debugger.debug(trace)

        results = []
        for f in findings:
            results.append({
                "event_id": f.event_id,
                "failure_type": f.failure_type,
                "explanation": f.explanation,
                "affected_actions_count": len(f.affected_event_ids)
            })

        return jsonify({
            "status": "success",
            "total_events": len(trace.events),
            "failures_detected": len(results),
            "findings": results
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
