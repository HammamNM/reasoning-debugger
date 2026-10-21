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
</html>"""

content = re.sub(r"DASHBOARD_HTML\s*=\s*([\'\"]{3})(.*?)\1", f"DASHBOARD_HTML = \"\"\"\n{new_html}\n\"\"\"", content, flags=re.DOTALL)

with open(file_name, "w") as f:
    f.write(content)
print("تم دمج ميزة رفع الملفات مع مربع النص بنجاح!")
