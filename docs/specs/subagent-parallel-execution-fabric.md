# Subagent Parallel Execution Fabric

Date: 2026-04-13

## Goal

Define how Hermes runs multiple specialist agents in parallel while preserving a complete audit trail, structured handoffs, and explicit human review gates.

## Core principle

The orchestrator does not do most domain work itself.
It builds an execution graph, launches specialist subagents, merges their outputs, and advances the project only when join conditions are satisfied.

## Runtime layers

1. Orchestrator
- reads project state
- builds or updates the execution graph
- launches subagents with `delegate_task`
- records events
- requests approvals
- schedules retries / retros with cron

2. Specialist subagents
- each owns one artifact type or one narrow responsibility
- examples: research, script, storyboard, qa-preflight, publish-packager

3. Review actors
- peer review
- gate review
- escalation review
- human review

## Execution graph rules

Each node must define:
- node_id
- role
- input_artifact_ids
- output_artifact_type
- prerequisites
- review_type
- join_owner

Each edge must define:
- from_node_id
- to_node_id
- handoff_required: true|false
- blocking: true|false

## Default v1 graph

1. intake-normalizer
2. orchestrator-plan
3. parallel branch:
- research
- strategy
- asset-planner
4. join: script-selection
5. storyboard
6. parallel branch:
- edit-packager
- qa-preflight
7. join: qa-compliance
8. human-approval
9. publish-packager
10. analytics-learning
11. memory-capture

## Roles that may run in parallel

- research
- strategy
- asset-planner
- reference gathering
- qa-preflight
- script variant generation
- packaging prep

## Roles that must stay serial

- brief normalization
- execution graph freeze
- script selection
- final QA / compliance
- human approval
- publish pack closeout
- retro closeout

## Review model

### 1) Peer review
Use when one specialist hands off to another specialist.
Must verify:
- artifact completeness
- schema validity
- unresolved assumptions
- explicit next action

### 2) Gate review
Use before a project can advance to the next major phase.
Must verify:
- required artifacts exist
- risk notes are present
- no open blocking questions remain
- correct artifact version is referenced

### 3) Escalation review
Use when:
- branch outputs conflict
- risk is high
- blocker exceeds SLA
- the same node needs revision repeatedly

### 4) Human review
Required for:
- brand direction changes
- legal / rights ambiguity
- sensitive factual claims
- final publish approval

## Handoff contract requirements

Every handoff must include:
- project_id
- from_task_id
- from_role
- to_role
- handoff_status
- artifact_ids
- summary
- assumptions
- findings
- open_questions
- risks
- requested_review_type
- next_action
- accepted_by
- accepted_at

## Event logging requirements

Every one of these must emit an event row:
- node launched
- node completed
- task state changed
- handoff sent
- handoff accepted
- review requested
- review decided
- approval requested
- approval decided
- artifact written
- branch merged
- escalation raised

## Merge rules

- Every join point has one merge owner
- Merge owner selects the canonical branch output
- Non-selected branches are marked superseded, not deleted
- Merge decision must record why the winning branch was chosen

## Failure handling

- If one branch fails and it is non-blocking, the orchestrator may continue with degraded mode
- If one branch fails and it is blocking, the orchestrator moves the project or task to blocked
- If the same node fails twice, create an escalation review instead of infinite retries

## Verification checklist

- Can two specialists work simultaneously without overwriting each other?
- Can every artifact be traced to a task and a subagent run?
- Can a reviewer see exactly which version is under review?
- Can a human approve or reject without reading the whole project history?
- Can the orchestrator explain why one branch was chosen over another?
