# Execution Graph Contract

Node fields:
- `node_id`
- `role`
- `input_artifact_ids`
- `output_artifact_type`
- `prerequisites`
- `review_type`
- `join_owner`

Edge fields:
- `from_node_id`
- `to_node_id`
- `handoff_required`
- `blocking`

Default v1 graph:
1. intake-normalizer
2. orchestrator-plan
3. parallel: research / strategy / asset-planner
4. join: script-selection
5. storyboard
6. parallel: edit-packager / qa-preflight
7. join: qa-compliance
8. human-approval
9. publish-packager
10. analytics-learning
11. memory-capture

Rules:
- build DAG first, then dispatch workers
- every join point has one merge owner
- non-winning branches become `superseded`, not deleted
