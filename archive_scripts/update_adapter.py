import re

file_name = "api_server.py"
with open(file_name, "r") as f:
    content = f.read()

new_func = """def normalize_agent_trace(raw_data):
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
            
        event_type = "ACTION"
        content = item.get("content", str(item))
        
        if "thought" in item or "reasoning" in item or "plan" in item:
            event_type = "INFERENCE"
            content = item.get("thought", item.get("reasoning", item.get("plan", content)))
        elif "observation" in item or "obs" in item or "output" in item:
            event_type = "OBSERVATION"
            content = item.get("observation", item.get("obs", item.get("output", content)))
        elif "action" in item or "tool" in item:
            event_type = "ACTION"
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
        
    return {"events": events}"""

# استبدال الدالة القديمة بالدالة الجديدة الذكية
content = re.sub(r'def normalize_agent_trace\(raw_data\):.*?(?=DASHBOARD_HTML\s*=|@app\.route)', new_func + '\n\n', content, flags=re.DOTALL)

with open(file_name, "w") as f:
    f.write(content)
print("تمت ترقية طبقة التكيف (Adapter) لتدعم LangChain و SWE-agent!")
