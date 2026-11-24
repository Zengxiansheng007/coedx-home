# Formal Human View handoff

Use this entry for an authorized publication candidate from UI-Test. The
compile result supplies one branch and one build with ordered resolved steps,
display-safe parameters and evaluated assertion references.

```text
python -B scripts/formal_human_view.py --request human-view-request.json --output authored-human-view.json
```

Keep the existing four-column layout. Render the visible expected result and
its machine assertions in the same cell. Use the configuration references
provided by UI-Test. The output contains the exact Markdown and its raw
UTF-8 SHA-256 with the request identity. UI-Test validates the artifact,
archives it, and applies its existing approval and activation procedure.

If the request identity or renderer version differs, report the affected
case and return to the original compile request. Retain prior reviews and
builds. Candidate authoring remains within the existing test-case-authoring
review and confirmation workflow.
