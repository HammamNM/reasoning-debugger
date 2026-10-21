import re
import io

file_name = "api_server.py"
with io.open(file_name, "r", encoding="utf-8") as f:
    content = f.read()

honest_docs = """<!DOCTYPE html>
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

def replace_docs(match):
    return 'API_DOCS_HTML = """' + honest_docs + '"""'

content = re.sub(r"API_DOCS_HTML\s*=\s*([\'\"]{3})(.*?)\1", replace_docs, content, flags=re.DOTALL)

with io.open(file_name, "w", encoding="utf-8") as f:
    f.write(content)
print("تم تصحيح وثائق الـ API لتطابق عقود v1.0 الحقيقية بدقة هندسية صارمة!")
