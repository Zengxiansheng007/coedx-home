# Validation and known limits

Offline tests exercise routing, missing Key fallback, quota classification, service-failure Codex handoff, explicit-choice/no-fallback precedence, permission/security pause, no hidden retry, partial batch preservation, manual resume, guided lineage, credential filtering, state integrity, source/coverage gates, interruption recovery and exclusive CLI locks. They use injected transports and temporary directories, never real Key values or public requests.

Run the standard-library unittest suite in scripts/test_research_runtime.py. Installation integrity and upstream source hashes must be checked using references/upstream-manifest.json. Full candidate evidence and deployment review live in the development workspace, outside the deployed Skill payload.

No live AnySearch call or Claude call is implied by this candidate's tests. New provider messages use the service-failure route unless a permission/security boundary applies. Host semantic research review, actual authorization provenance and external provider availability cannot be proven solely by the router script.

The direct official anysearch entry remains an upstream Skill. The governed workflow requires research as the entry and the boundary CLI; this is not a machine-wide interception mechanism. Deployment review must ensure the common research entry is used.
