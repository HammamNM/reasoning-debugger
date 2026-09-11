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
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/viz.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/full.render.js"></script>

    <script src="https://d3js.org/d3.v5.min.js"></script>
    <script src="https://unpkg.com/@hpcc-js/wasm@2.20.0/dist/index.min.js"></script>
    <script src="https://unpkg.com/d3-graphviz@3.0.5/build/d3-graphviz.js"></script>
</head>
<body class="bg-gray-50 p-8 font-sans">
    <div class="max-w-4xl mx-auto bg-white p-6 rounded-lg shadow-md border-t-4 border-blue-600">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">🔬 Reasoning Debugger</h1>
        <p class="text-gray-600 mb-6 font-medium">Connect your AI agent trace. We normalize the trace and detect supported reasoning failures with evidence-based explanations.</p>
        
        <input type="file" id="fileInput" accept=".json" class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 mb-6 cursor-pointer" />
        
        <div id="results" class="hidden">
            <div id="statusAlert" class="p-4 mb-4 rounded-md border"></div>
            <h3 class="text-lg font-bold text-gray-700 mb-2 mt-6" id="graphTitle" style="display:none;">Trace Graph:</h3>
            <div id="graphContainer" class="border p-4 rounded-md bg-white shadow-inner overflow-auto flex justify-center"></div>
        </div>
    </div>

    <script>
        const errorDictionary = {
            "unsupported_inference": {
                title: "The agent made an inference without supporting evidence.",
                why: "The subsequent actions depend on this unsupported inference, leading to hallucinated or incorrect outputs."
            }
        };

        document.getElementById('fileInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = async function(event) {
                try {
                    const traceData = JSON.parse(event.target.result);
                    const response = await fetch('/debug', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(traceData)
                    });
                    
                    const result = await response.json();
                    const resultsDiv = document.getElementById('results');
                    const statusAlert = document.getElementById('statusAlert');
                    const graphContainer = document.getElementById('graphContainer');
                    const graphTitle = document.getElementById('graphTitle');
                    
                    resultsDiv.classList.remove('hidden');
                    
                    if (result.error) {
                        statusAlert.className = 'p-4 mb-4 rounded-md bg-yellow-50 border border-yellow-200 text-yellow-800';
                        statusAlert.innerHTML = `<strong>Normalization Info:</strong> ${result.error}`;
                        graphContainer.innerHTML = '';
                        graphTitle.style.display = 'none';
                        return;
                    }
                    
                    if (result.findings_count > 0) {
                        statusAlert.className = 'p-5 mb-4 rounded-md bg-red-50 border border-red-200';
                        
                        let findingsHtml = result.findings.map(f => {
                            let mappedError = errorDictionary[f.failure_type] || { title: f.failure_type, why: f.explanation };
                            let impactCount = f.affected_event_ids ? f.affected_event_ids.length : 0;
                            
                            return `
                                <div class="mt-2 p-4 bg-white rounded border border-red-100 shadow-sm">
                                    <h4 class="font-bold text-red-900 text-lg">First reasoning failure</h4>
                                    <p class="text-red-700 font-medium mt-1">${mappedError.title}</p>
                                    <div class="mt-3 text-sm text-gray-700 grid grid-cols-2 gap-4">
                                        <div><strong>Started at:</strong> <span class="bg-gray-100 px-2 py-1 rounded font-mono">${f.event_id}</span></div>
                                        <div><strong>Downstream impact:</strong> ${impactCount} actions affected</div>
                                    </div>
                                    <div class="mt-4 p-3 bg-red-50 text-sm text-gray-800 border-l-4 border-red-400 rounded-r">
                                        <strong>Why this matters:</strong> ${mappedError.why}
                                    </div>
                                </div>
                            `;
                        }).join('');

                        statusAlert.innerHTML = `<h3 class="text-xl font-bold text-red-800 mb-3">⚠️ Agent Run Failed</h3>` + findingsHtml;
                        
                        if(result.dot_graph) {
                            graphTitle.style.display = 'block';
                            let viz = new Viz();
                            viz.renderSVGElement(result.dot_graph)
                            .then(function(element) {
                                graphContainer.innerHTML = '';
                                graphContainer.appendChild(element);
                            })
                            .catch(error => { console.error(error); });
                        }
                    } else {
                        statusAlert.className = 'p-4 mb-4 rounded-md bg-green-50 border border-green-200 text-green-800';
                        statusAlert.innerHTML = '<strong>✅ Trace normalized successfully. 0 Semantic Findings. (Insufficient causal metadata to prove failure).</strong>';
                        graphContainer.innerHTML = '';
                        graphTitle.style.display = 'none';
                    }
                } catch (err) {
                    alert("Error processing file: " + err);
                }
            };
            reader.readAsText(file);
        });
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
