import re

file_name = "api_server.py"
with open(file_name, "r") as f:
    content = f.read()

api_route = """
@app.route('/api/v1/debug', methods=['POST'])
def api_debug():
    try:
        raw_data = request.get_json()
        if not raw_data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        # 1. Normalize data
        normalized_data = normalize_agent_trace(raw_data)
        
        # 2. Parse trace
        trace = ReasoningTrace.model_validate(normalized_data)
        
        # 3. Initialize debugger
        debugger = ReasoningDebugger()
        findings = debugger.debug(trace)
        
        # 4. Format output
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
"""

# حقن مسار الـ API قبل تشغيل التطبيق (app.run)
if "/api/v1/debug" not in content:
    content = content.replace("if __name__ == '__main__':", api_route + "\nif __name__ == '__main__':")
    with open(file_name, "w") as f:
        f.write(content)
    print("تمت إضافة API المطورين بنجاح!")
else:
    print("المسار موجود مسبقاً.")
