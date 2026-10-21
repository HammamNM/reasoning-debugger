import json

# بناء مسار يحمل تصريحاً دلالياً واضحاً بحاجته للدعم (Positive Control)
failing_trace = {
  "events": [
    {"id": "e1", "event_type": "INVESTIGATION", "content": "query db", "metadata": {}},
    {"id": "e2", "event_type": "INFERENCE", "content": "user exists", "metadata": {"support_required": True}}
  ]
}

with open('failing_trace.json', 'w') as f:
    json.dump(failing_trace, f, indent=2)
print("Failing JSON trace generated.")
