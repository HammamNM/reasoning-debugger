import re

file_name = "api_server.py"
with open(file_name, "r") as f:
    content = f.read()

new_html = """<!DOCTYPE html>
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
        .theme-toggle { position: absolute; top: 0; right: 0; background: none; border: 1px solid var(--border); font-size: 20px; cursor: pointer; padding: 8px; border-radius: 50%; color: var(--text); }
        .header { text-align: center; margin-bottom: 30px; }
        .logo { font-size: 28px; font-weight: 800; color: var(--primary); letter-spacing: -0.5px; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .logo span { color: var(--text); }
        .badges { display: flex; justify-content: center; gap: 10px; margin-top: 8px; }
        .badge { display: inline-block; background: #e0e7ff; color: #4338ca; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; text-decoration: none; }
        .badge-docs { background: var(--text); color: var(--bg); }
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
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/viz.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/full.render.js"></script>
</head>
<body>
    <div class="container">
        <button class="theme-toggle" onclick="toggleTheme()" title="Toggle Dark Mode">🌙</button>
        <div class="header">
            <div class="logo">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
                Reasoning<span>Debugger</span>
            </div>
            <div class="badges">
                <div class="badge">Powered by nexoramed.online</div>
                <a href="/docs" class="badge badge-docs">📖 API Docs</a>
            </div>
        </div>
        
        <div class="input-section">
            <div class="file-upload">
                <label for="file-input">📂 Upload Trace File: </label>
                <input type="file" id="file-input" accept=".json,.traj,.txt" onchange="handleFileUpload(event)">
            </div>
            <textarea id="trace-input" placeholder='{"events": [...]}'></textarea>
            <div class="btn-group">
                <button onclick="loadSample()" class="btn-secondary">Load Sample</button>
                <button onclick="processTrace()">Debug Trace</button>
            </div>
            <div id="error-msg"></div>
        </div>

        <div id="graph-container">Trace Graph will appear here...</div>
        <button id="download-btn" class="btn-secondary" onclick="downloadSVG()">📥 Download Graph as SVG</button>
    </div>

    <script>
        function toggleTheme() {
            const html = document.documentElement;
            const toggle = document.querySelector('.theme-toggle');
            if (html.getAttribute('data-theme') === 'light') {
                html.setAttribute('data-theme', 'dark');
                toggle.textContent = '☀️';
            } else {
                html.setAttribute('data-theme', 'light');
                toggle.textContent = '🌙';
            }
        }

        function loadSample() {
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
        }

        function handleFileUpload(event) {
            const file = event.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function(e) { document.getElementById("trace-input").value = e.target.result; };
            reader.readAsText(file);
        }

        async function processTrace() {
            const inputData = document.getElementById("trace-input").value;
            const errorMsg = document.getElementById("error-msg");
            const graphContainer = document.getElementById("graph-container");
            const downloadBtn = document.getElementById("download-btn");
            
            if (!inputData.trim()) { errorMsg.innerText = "Please provide trace data."; return; }
            errorMsg.innerText = "";
            graphContainer.innerHTML = "Processing...";
            downloadBtn.style.display = 'none';

            try {
                const response = await fetch("/api/v1/debug", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(JSON.parse(inputData))
                });
                
                const uiResponse = await fetch("/debug", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(JSON.parse(inputData))
                });
                
                const result = await uiResponse.json();
                if (!uiResponse.ok) throw new Error(result.error || "Unknown error occurred");

                let viz = new Viz();
                viz.renderSVGElement(result.dot_graph).then(function(element) {
                    graphContainer.innerHTML = "";
                    element.style.width = "100%";
                    element.style.height = "auto";
                    graphContainer.appendChild(element);
                    downloadBtn.style.display = 'block';
                }).catch(error => { errorMsg.innerText = "Error rendering graph."; });
            } catch (err) {
                errorMsg.innerText = "Error: " + err.message;
                graphContainer.innerHTML = "";
            }
        }

        function downloadSVG() {
            const svg = document.querySelector("#graph-container svg");
            if (!svg) return;
            const serializer = new XMLSerializer();
            let source = serializer.serializeToString(svg);
            if(!source.match(/^<svg[^>]+xmlns="http\:\/\/www\.w3\.org\/2000\/svg"/)){
                source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
            }
            source = '<?xml version="1.0" standalone="no"?>\r\n' + source;
            const url = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(source);
            const a = document.createElement("a");
            a.href = url;
            a.download = "reasoning_trace.svg";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }
    </script>
</body>
</html>"""

content = re.sub(r"DASHBOARD_HTML\s*=\s*([\'\"]{3})(.*?)\1", f"DASHBOARD_HTML = \"\"\"\n{new_html}\n\"\"\"", content, flags=re.DOTALL)

api_docs_code = """
API_DOCS_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Documentation - Reasoning Debugger</title>
    <style>
        body { font-family: 'Segoe UI', system-ui, sans-serif; padding: 40px 20px; background: #f8fafc; color: #0f172a; line-height: 1.6; max-width: 800px; margin: auto; }
        .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }
        h1, h2, h3 { color: #2563eb; }
        pre { background: #1e293b; color: #f8fafc; padding: 15px; border-radius: 8px; overflow-x: auto; font-family: 'Consolas', monospace; font-size: 14px; }
        .endpoint { display: inline-block; background: #2563eb; color: white; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-family: monospace; font-size: 16px; margin-bottom: 10px; }
        a { color: #2563eb; text-decoration: none; font-weight: bold; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📖 API Documentation</h1>
        <p>Integrate the Reasoning Debugger into your CI/CD pipeline or AI agent workflows to automatically detect reasoning failures and infinite loops.</p>
        
        <h2>Analyze Trace Endpoint</h2>
        <div class="endpoint">POST /api/v1/debug</div>
        <p>Expects a JSON payload containing the reasoning trace to be analyzed.</p>
        
        <h3>Request Body Example</h3>
        <pre><code>{
  "events": [
    { "event_type": "INVESTIGATION", "content": "Search database" },
    { "event_type": "INFERENCE", "content": "Database is hacked" }
  ]
}</code></pre>
        
        <h3>Success Response Example (200 OK)</h3>
        <pre><code>{
  "status": "success",
  "failures_detected": 1,
  "findings": [
    {
      "event_id": "e2",
      "failure_type": "UNSUPPORTED_ASSUMPTION",
      "explanation": "No evidence found to support the assumption.",
      "affected_actions_count": 0
    }
  ],
  "total_events": 2
}</code></pre>
        <br>
        <a href="/">&larr; Back to Dashboard</a>
    </div>
</body>
</html>'''

@app.route('/docs')
def api_docs():
    return API_DOCS_HTML
"""

if "@app.route('/docs')" not in content:
    content = content.replace("if __name__ == '__main__':", api_docs_code + "\n\nif __name__ == '__main__':")

with open(file_name, "w") as f:
    f.write(content)
print("تم تنفيذ المرحلة الثانية: زر التنزيل وصفحة التوثيق بنجاح!")
