from flask import Flask, request, jsonify
from kernel.api import ReasoningDebugger, ReasoningTrace, InvalidTraceSchemaError, export_trace_to_dot, export_compact_trace_to_dot
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
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reasoning Debugger</title>
<style>
:root{
--bg:#f6f8fb;
--surface:#fff;
--surface2:#f1f4f8;
--text:#172033;
--muted:#667085;
--border:#dfe4ea;
--primary:#2563eb;
--success:#15803d;
--warning:#b45309;
--danger:#dc2626;
--shadow:0 8px 30px rgba(15,23,42,.07)
}
[data-theme="dark"]{
--bg:#0b1120;
--surface:#111827;
--surface2:#1a2333;
--text:#e5e7eb;
--muted:#9ca3af;
--border:#293548;
--primary:#60a5fa;
--success:#4ade80;
--warning:#fbbf24;
--danger:#f87171;
--shadow:0 10px 35px rgba(0,0,0,.25)
}
*{box-sizing:border-box}
body{
margin:0;
background:var(--bg);
color:var(--text);
font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif
}
button,textarea,input{font:inherit}
button{cursor:pointer}
.app{max-width:1180px;margin:auto;padding:24px}
header{
display:flex;
align-items:center;
justify-content:space-between;
gap:20px;
margin-bottom:28px
}
.brand{display:flex;align-items:center;gap:12px}
.logo{
width:42px;height:42px;display:grid;place-items:center;
border-radius:12px;background:var(--primary);
color:white;font-weight:800
}
h1{margin:0;font-size:22px}
.subtitle{margin:4px 0 0;color:var(--muted);font-size:13px}
.header-actions{display:flex;gap:8px}
.header-actions a,.icon-btn{
border:1px solid var(--border);
background:var(--surface);
color:var(--text);
padding:9px 13px;
border-radius:9px;
text-decoration:none
}
.hero{margin-bottom:22px}
.hero h2{margin:0 0 6px;font-size:30px}
.hero p{margin:0;color:var(--muted)}
.panel{
background:var(--surface);
border:1px solid var(--border);
border-radius:14px;
box-shadow:var(--shadow);
margin-bottom:20px;
overflow:hidden
}
.panel-head{
padding:16px 18px;
border-bottom:1px solid var(--border);
display:flex;
justify-content:space-between;
align-items:center;
gap:12px
}
.panel-title{
font-size:13px;
font-weight:800;
letter-spacing:.06em
}
.panel-body{padding:18px}
textarea{
width:100%;
min-height:260px;
resize:vertical;
border:1px solid var(--border);
border-radius:10px;
background:var(--surface2);
color:var(--text);
padding:14px;
outline:none;
font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
font-size:13px;
line-height:1.55
}
textarea:focus{border-color:var(--primary)}
.toolbar{
display:flex;
flex-wrap:wrap;
gap:9px;
margin-top:12px
}
.btn{
border:1px solid var(--border);
background:var(--surface);
color:var(--text);
padding:10px 14px;
border-radius:9px;
font-weight:600
}
.btn-primary{
background:var(--primary);
border-color:var(--primary);
color:white
}
.btn-danger{color:var(--danger)}
input[type=file]{display:none}
.file-label{
display:inline-flex;
align-items:center;
padding:10px 14px;
border:1px solid var(--border);
border-radius:9px;
cursor:pointer;
font-weight:600
}
.status{margin-top:12px;min-height:20px;color:var(--muted);font-size:13px}
.results{display:none}
.stats{
display:grid;
grid-template-columns:repeat(3,1fr);
gap:12px
}
.stat{
padding:18px;
border:1px solid var(--border);
border-radius:12px;
background:var(--surface)
}
.stat-label{color:var(--muted);font-size:12px;margin-bottom:8px}
.stat-value{font-size:25px;font-weight:800}
.status-ok{color:var(--success)}
.status-warning{color:var(--warning)}
.status-error{color:var(--danger)}
.finding{
border:1px solid var(--border);
border-left:4px solid var(--warning);
border-radius:10px;
padding:14px;
margin-bottom:10px;
background:var(--surface);
cursor:pointer
}
.finding:hover{background:var(--surface2)}
.finding-type{font-weight:800;margin-bottom:5px}
.finding-meta{color:var(--muted);font-size:12px;margin-bottom:7px}
.finding-text{font-size:13px;line-height:1.5}
.empty{color:var(--muted);text-align:center;padding:30px 10px}
.graph-wrap{
overflow:auto;
min-height:360px;
background:var(--surface2);
border-radius:10px;
padding:12px
}
#graph{min-height:330px}
.error-box{
display:none;
padding:13px;
border:1px solid var(--danger);
color:var(--danger);
background:var(--surface2);
border-radius:9px;
margin-top:12px
}
.spinner{
display:inline-block;
width:14px;
height:14px;
border:2px solid rgba(255,255,255,.45);
border-top-color:white;
border-radius:50%;
animation:spin .7s linear infinite;
vertical-align:-2px
}
@keyframes spin{to{transform:rotate(360deg)}}
.modal{
display:none;
position:fixed;
inset:0;
background:rgba(0,0,0,.55);
z-index:20;
padding:20px
}
.modal-card{
max-width:620px;
margin:8vh auto;
background:var(--surface);
border:1px solid var(--border);
border-radius:14px;
box-shadow:var(--shadow);
padding:20px
}
.modal-card h3{margin-top:0}
@media(max-width:700px){
.app{padding:15px}
.hero h2{font-size:24px}
.stats{grid-template-columns:1fr}
.header-actions a{display:none}
}
</style>
</head>
<body>
<div class="app">

<header>
<div class="brand">
<div class="logo">◈</div>
<div>
<h1>Reasoning Debugger</h1>
<div class="subtitle">Deterministic analysis of AI reasoning traces</div>
</div>
</div>

<div class="header-actions">
<a href="/docs" target="_blank">API Docs</a>
<button class="icon-btn" onclick="toggleTheme()" title="Toggle theme">☾</button>
</div>
</header>

<section class="hero">
<h2>Analyze AI reasoning traces</h2>
<p>Detect reasoning failures, inspect findings, and explore the causal reasoning graph.</p>
</section>

<section class="panel">
<div class="panel-head">
<div class="panel-title">INPUT TRACE</div>
</div>
<div class="panel-body">
<textarea id="traceInput" placeholder="Paste a JSON reasoning trace here..."></textarea>

<div class="toolbar">
<label class="file-label" for="fileInput">Upload JSON</label>
<input id="fileInput" type="file" accept=".json,application/json" onchange="handleFileUpload(event)">

<button class="btn" onclick="loadSample()">Load Sample</button>
<button class="btn btn-danger" onclick="clearTrace()">Clear</button>
<button class="btn btn-primary" id="analyzeBtn" onclick="processTrace()">Analyze Trace</button>
</div>

<div id="status" class="status"></div>
<div id="errorBox" class="error-box"></div>
</div>
</section>

<section id="results" class="results">

<section class="panel">
<div class="panel-head">
<div class="panel-title">ANALYSIS</div>
</div>
<div class="panel-body">
<div class="stats">

<div class="stat">
<div class="stat-label">EVENTS</div>
<div class="stat-value" id="eventCount">—</div>
</div>

<div class="stat">
<div class="stat-label">FINDINGS</div>
<div class="stat-value" id="findingCount">—</div>
</div>

<div class="stat">
<div class="stat-label">STATUS</div>
<div class="stat-value" id="analysisStatus">—</div>
</div>

</div>
</div>
</section>

<section class="panel">
<div class="panel-head">
<div class="panel-title">FINDINGS</div>
</div>
<div class="panel-body">
<div id="findingsList"></div>
</div>
</section>

<section class="panel">
<div class="panel-head">
<div class="panel-title">REASONING GRAPH</div>
<button class="btn" onclick="downloadSVG()">Download SVG</button>
</div>
<div class="panel-body">
<div class="graph-wrap">
<div id="graph"></div>
</div>
</div>
</section>

</section>

</div>

<div id="findingModal" class="modal" onclick="closeModal(event)">
<div class="modal-card">
<h3 id="modalTitle">Finding</h3>
<div id="modalBody"></div>
<div class="toolbar">
<button class="btn" onclick="document.getElementById('findingModal').style.display='none'">Close</button>
</div>
</div>
</div>

<script src="https://cdn.jsdelivr.net/npm/viz.js@2.1.2/viz.js"></script>
<script src="https://cdn.jsdelivr.net/npm/viz.js@2.1.2/full.render.js"></script>
<script>
window.currentFindings = [];
window.currentSvg = null;
window.currentTrace = null;

function toggleTheme(){
  const root=document.documentElement;
  const dark=root.getAttribute("data-theme")==="dark";
  root.setAttribute("data-theme",dark?"light":"dark");
  localStorage.setItem("reasoning-debugger-theme",dark?"light":"dark");
}

(function(){
  if(localStorage.getItem("reasoning-debugger-theme")==="dark"){
    document.documentElement.setAttribute("data-theme","dark");
  }
})();

function setStatus(text){
  document.getElementById("status").textContent=text||"";
}

function showError(message){
  const box=document.getElementById("errorBox");
  box.textContent=message||"An unexpected error occurred.";
  box.style.display="block";
}

function clearError(){
  document.getElementById("errorBox").style.display="none";
}

function setProcessing(active){
  const button=document.getElementById("analyzeBtn");
  button.disabled=active;

  if(active){
    button.innerHTML='<span class="spinner"></span> Analyzing...';
  }else{
    button.textContent="Analyze Trace";
  }
}

function clearTrace(){
  document.getElementById("traceInput").value="";
  document.getElementById("results").style.display="none";
  document.getElementById("graph").innerHTML="";
  document.getElementById("findingsList").innerHTML="";
  clearError();
  setStatus("");
  window.currentFindings=[];
  window.currentSvg=null;
  window.currentTrace=null;
}

function loadSample(){
  const sample={
    steps:[
      {tool:"Search",tool_input:"error code 500"},
      {observation:"No results found"},
      {tool:"Search",tool_input:"error code 500"},
      {observation:"No results found"},
      {tool:"Search",tool_input:"error code 500"}
    ]
  };

  document.getElementById("traceInput").value=JSON.stringify(sample,null,2);
  clearError();
  setStatus("Sample trace loaded.");
}

function handleFileUpload(event){
  const file=event.target.files&&event.target.files[0];
  if(!file)return;

  const reader=new FileReader();

  reader.onload=function(e){
    document.getElementById("traceInput").value=e.target.result;
    clearError();
    setStatus("Trace loaded from "+file.name);
  };

  reader.onerror=function(){
    showError("Could not read the selected file.");
  };

  reader.readAsText(file);
}

function countTraceEvents(data){
  if(Array.isArray(data))return data.length;
  if(!data||typeof data!=="object")return 0;

  for(const key of ["events","runs","trajectory","steps"]){
    if(Array.isArray(data[key]))return data[key].length;
  }

  for(const value of Object.values(data)){
    if(Array.isArray(value))return value.length;
  }

  return 0;
}

function escapeHtml(value){
  return String(value??"")
    .replace(/&/g,"&amp;")
    .replace(/</g,"&lt;")
    .replace(/>/g,"&gt;")
    .replace(/"/g,"&quot;")
    .replace(/'/g,"&#039;");
}
</script>
<script>
async function processTrace(){
  clearError();
  const input = document.getElementById("traceInput");
  const raw = input ? input.value.trim() : "";

  if(!raw){
    showError("Please provide a reasoning trace before analyzing.");
    return;
  }

  let parsedData;
  try{
    parsedData = JSON.parse(raw);
  }catch(err){
    showError("Invalid JSON. Please check the trace format and try again.");
    return;
  }

  setProcessing(true);
  window.currentFindings = [];
  window.currentSvg = null;
  window.currentTrace = parsedData;

  try{
    const apiResponse = await fetch("/api/v1/debug", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify(parsedData)
    });

    let apiResult = {};
    try{
      apiResult = await apiResponse.json();
    }catch(_){}

    if(!apiResponse.ok){
      throw new Error(apiResult.error || "Debugger API returned an error.");
    }

    if(Array.isArray(apiResult.findings)){
      window.currentFindings = apiResult.findings;
    }

    const uiResponse = await fetch("/debug", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify(parsedData)
    });

    let result = {};
    try{
      result = await uiResponse.json();
    }catch(_){}

    if(!uiResponse.ok){
      throw new Error(result.error || "Server processing error.");
    }

    if(!result.dot_graph){
      throw new Error("The debugger returned no graph.");
    }

    renderFindings();
    updateStats(parsedData, window.currentFindings);

    const graphContainer = document.getElementById("graph");
    if(!graphContainer){
      throw new Error("Graph container not found.");
    }

    graphContainer.innerHTML = "";

    const viz = new Viz();

    const svgElement = await viz.renderSVGElement(result.dot_graph);
    svgElement.removeAttribute("width");
    svgElement.removeAttribute("height");
    svgElement.style.width = "100%";
    svgElement.style.height = "auto";

    graphContainer.appendChild(svgElement);
    window.currentSvg = svgElement.outerHTML;

    const nodes = svgElement.querySelectorAll(".node");

    nodes.forEach(node => {
      node.style.cursor = "pointer";

      node.addEventListener("click", () => {
        const titleEl = node.querySelector("title");
        if(!titleEl) return;

        const nodeId = titleEl.textContent.trim();
        const finding = window.currentFindings.find(
          f => String(f.event_id) === String(nodeId)
        );

        if(finding){
          showFinding(finding);
        }
      });
    });

    document.getElementById("results").style.display = "block";

    const findingCount = window.currentFindings.length;
    setStatus(
      findingCount
        ? `${findingCount} finding${findingCount === 1 ? "" : "s"} detected`
        : "No structural findings detected",
      findingCount ? "warning" : "success"
    );

  }catch(err){
    console.error(err);
    showError(err.message || "Unable to analyze this trace.");
    const graphContainer = document.getElementById("graph");
    if(graphContainer) graphContainer.innerHTML = "";
    document.getElementById("results").style.display = "none";
  }finally{
    setProcessing(false);
  }
}

function updateStats(trace, findings){
  const events = countTraceEvents(trace);

  const eventsEl = document.getElementById("eventCount");
  const findingsEl = document.getElementById("findingCount");
  const statusEl = document.getElementById("traceStatus");

  if(eventsEl) eventsEl.textContent = String(events);
  if(findingsEl) findingsEl.textContent = String(findings.length);

  if(statusEl){
    statusEl.textContent = findings.length ? "Review required" : "Clean";
    statusEl.className = findings.length
      ? "stat-value status-warning"
      : "stat-value status-success";
  }
}

function renderFindings(){
  const container = document.getElementById("findingsList");
  if(!container) return;

  container.innerHTML = "";

  if(!window.currentFindings.length){
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">✓</div>
        <h3>No findings detected</h3>
        <p>The trace was processed without detected structural or cognitive findings.</p>
      </div>`;
    return;
  }

  window.currentFindings.forEach((finding, index) => {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "finding-card";

    const type = escapeHtml(
      finding.type || finding.finding_type || "Finding"
    );

    const eventId = escapeHtml(
      finding.event_id || finding.node_id || "Unknown event"
    );

    const explanation = escapeHtml(
      finding.explanation ||
      finding.message ||
      finding.description ||
      "No explanation provided."
    );

    card.innerHTML = `
      <div class="finding-top">
        <span class="finding-type">${type}</span>
        <span class="finding-event">${eventId}</span>
      </div>
      <div class="finding-title">${type}</div>
      <div class="finding-explanation">${explanation}</div>
      <div class="finding-action">View details →</div>
    `;

    card.addEventListener("click", () => showFinding(finding));
    container.appendChild(card);
  });
}

function showFinding(finding){
  const modal = document.getElementById("findingModal");
  if(!modal) return;

  const type =
    finding.type ||
    finding.finding_type ||
    "Finding";

  const eventId =
    finding.event_id ||
    finding.node_id ||
    "Unknown";

  const explanation =
    finding.explanation ||
    finding.message ||
    finding.description ||
    "No explanation provided.";

  const title = modal.querySelector("[data-finding-title]");
  const body = modal.querySelector("[data-finding-body]");

  if(title){
    title.textContent = type;
  }

  if(body){
    body.innerHTML = `
      <div class="detail-row">
        <span>Type</span>
        <strong>${escapeHtml(type)}</strong>
      </div>
      <div class="detail-row">
        <span>Event</span>
        <strong>${escapeHtml(eventId)}</strong>
      </div>
      <div class="detail-description">
        ${escapeHtml(explanation)}
      </div>
    `;
  }

  modal.classList.add("open");
}

function closeModal(event){
  const modal = document.getElementById("findingModal");
  if(!modal) return;

  if(!event || event.target === modal){
    modal.classList.remove("open");
  }
}

document.addEventListener("keydown", event => {
  if(event.key === "Escape"){
    const modal = document.getElementById("findingModal");
    if(modal) modal.classList.remove("open");
  }
});

function downloadSVG(){
  if(!window.currentSvg){
    showError("Analyze a trace first to generate an SVG.");
    return;
  }

  const blob = new Blob(
    [window.currentSvg],
    {type:"image/svg+xml;charset=utf-8"}
  );

  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = "reasoning_trace.svg";
  document.body.appendChild(link);
  link.click();
  link.remove();

  URL.revokeObjectURL(url);
}
</script>

</body>
</html>
"""

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
            renderer = (
                export_compact_trace_to_dot
                if len(trace.events) > 500
                else export_trace_to_dot
            )
            response_data["dot_graph"] = renderer(trace, findings)

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

        if 'events' not in normalized_data or not normalized_data['events']:
            return jsonify({
                "status": "error",
                "message": "Adapter could not extract valid reasoning events from this trace format."
            }), 400

        trace = ReasoningTrace.from_dict(normalized_data)

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

    except InvalidTraceSchemaError as e:
        return jsonify({
            "status": "error",
            "message": f"Schema Error: {str(e)}"
        }), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
