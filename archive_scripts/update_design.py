import re

file_name = "api_server.py"
with open(file_name, "r") as f:
    content = f.read()

new_html = """<!DOCTYPE html>
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
</html>"""

content = re.sub(r"DASHBOARD_HTML\s*=\s*([\'\"]{3})(.*?)\1", f"DASHBOARD_HTML = \"\"\"\n{new_html}\n\"\"\"", content, flags=re.DOTALL)

with open(file_name, "w") as f:
    f.write(content)
print("تم تطبيق التصميم الجديد بنجاح!")
