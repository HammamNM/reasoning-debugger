import re

# 1. Update Debugger Integration Contract
f1 = 'tests/phase5/test_debugger_integration_contract.py'
with open(f1, 'r') as f: c1 = f.read()
c1 = c1.replace(
    'assert result[0].affected_event_ids == (\n            "decision-1",\n            "outcome-1",\n        )',
    'assert result[0].affected_event_ids == ()'
)
with open(f1, 'w') as f: f.write(c1)

# 2. Update Reasoning Failure Detector Contract
f2 = 'tests/phase5/test_reasoning_failure_detector.py'
with open(f2, 'r') as f: c2 = f.read()
c2 = c2.replace(
    'assert [finding.event_id for finding in findings] == [\n            "event-1",\n            "event-3",\n        ]',
    'assert [finding.event_id for finding in findings] == ["event-1"]'
)
with open(f2, 'w') as f: f.write(c2)

# 3. Update Failure Propagation Contract
f3 = 'tests/phase5/test_failure_propagation.py'
with open(f3, 'r') as f: c3 = f.read()

# Update sequence propagation assertions (now returns empty since SEQUENCE is ignored)
c3 = c3.replace('assert result == ("event-2",)', 'assert result == ()')
c3 = c3.replace(
    'assert result == (\n            "event-2",\n            "event-3",\n            "event-4",\n        )',
    'assert result == ()'
)
c3 = c3.replace(
    'assert set(result) == {\n            "event-2",\n            "event-3",\n            "event-4",\n        }',
    'assert set(result) == set()'
)

# Update semantic propagation test names and assertions
c3 = c3.replace('def test_propagation_follows_only_sequence_edges():', 'def test_propagation_follows_semantic_edges_only():')
parts = c3.split('def test_derived_from_edge_does_not_propagate_backward')
parts[0] = parts[0].replace('assert result == ("event-3",)', 'assert result == ("event-2",)')
parts[1] = parts[1].replace('assert result == ("event-3",)', 'assert result == ()')
c3 = 'def test_derived_from_edge_does_not_propagate_backward'.join(parts)

with open(f3, 'w') as f: f.write(c3)
print("Legacy Phase 5 contracts updated to Phase 16 standards.")
