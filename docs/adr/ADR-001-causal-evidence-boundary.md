# ADR-001: Causal Evidence Boundary for External Agent Traces

## Status

Accepted

## Context

Reasoning Debugger can ingest execution traces produced by external
agent frameworks.

The SWE-agent public `.traj` trajectory used during Phase 21 contains
structured execution information such as thoughts, actions,
observations, responses, and state.

However, the trace is primarily sequential. Temporal ordering alone
does not establish that one reasoning event causally depends on another.

Inferring causal relationships solely from event order would allow an
adapter to manufacture `derived_from` relationships that are not
supported by the source trace.

That would undermine the evidence-based and deterministic guarantees
of the Reasoning Debugger.

## Decision

External trace adapters MUST NOT invent causal relationships that are
not explicitly supported by the source trace.

In particular:

- Temporal ordering MUST NOT be treated as causal dependency.
- Adapters MUST NOT manufacture `derived_from` metadata merely because
  one event follows another.
- Source information MUST be preserved wherever possible.
- Adapter-specific interpretation MUST remain outside the Kernel.
- If the available trace does not contain sufficient causal evidence,
  the Debugger MUST prefer producing no unsupported finding rather
  than asserting an unproven root failure.

Sequential ordering may be preserved as provenance, but it is not itself
evidence of causal dependency.

## Phase 21 Evidence

A publicly published SWE-agent `.traj` trajectory was ingested without
modifying the raw artifact.

The artifact was preserved with provenance metadata and SHA256:

- Instance: `marshmallow-code__marshmallow-1867`
- Format: `.traj` JSON
- SHA256:
  `8856076ec31832f20aefa7f0a2714e3ad6bc752f14815d94d2e852e50213a459`

A blind external adapter converted the trajectory into the existing
`ReasoningTrace` representation.

The adapter:

- extracted 41 events;
- preserved step ordering through metadata;
- classified available thought/action/observation fields;
- did not generate `derived_from` relationships.

The existing Debugger processed the resulting trace and produced zero
findings.

This demonstrates successful external-trace ingestion without
requiring changes to the Kernel or fabricating causal evidence.

## Consequences

### Positive

The architecture maintains a strict separation between:

1. source trace representation;
2. external-format adaptation;
3. Reasoning IR;
4. causal analysis;
5. Debug findings.

The system avoids false causal claims when source traces are
insufficiently expressive.

### Limitation

A sequential trace may be insufficient to localize a causal root
failure.

This is an explicit capability boundary, not a reason for an adapter to
guess.

Future trace sources that provide explicit dependency, provenance, or
causal information may support stronger localization.

## Phase 21 Exit Interpretation

Phase 21 establishes:

- synthetic benchmark coverage;
- negative-control coverage;
- adversarial coverage;
- ingestion of a published external agent trajectory;
- provenance preservation;
- blind adapter translation;
- protection against fabricated causal relationships.

It does NOT claim universal empirical proof of domain-agnosticism across
all agent frameworks.

The result is therefore recorded as:

**Phase 21 — Completed with Causal Boundary Discovery**
