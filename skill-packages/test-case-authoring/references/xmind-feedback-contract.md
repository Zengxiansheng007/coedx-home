# Native XMind return v1

Read this branch when the user returns an actual `.xmind` review file. Continue
the [feedback contract](feedback-contract.md) for all clarification, agreement,
application and final-review actions. Read the file itself with the public entry:

```python
from xmind_feedback import prepare_xmind_feedback
pending = prepare_xmind_feedback(batch, returned_file, actual_reply=actual_reply)
```

The file entry is also available as:

```text
python -B scripts/xmind_feedback.py --batch candidate.json --returned-file returned.xmind --reply "User's actual feedback" --output-dir new-feedback-output
```

Retain the returned input unchanged. Inspect `status` before using the result.
`pending_verification` contains source identity and a reason, with no candidate
or proposed write. Explain the ambiguity and ask for the affected case/field or
a supported file; do not guess which case a changed ID or module should replace.
`ready_for_clarification` is an ordinary feedback proposal for the existing
`respond`, `summarize`, `apply_feedback`, `review_feedback` sequence. Show the
before/latest/proposed values and affected paths from its changes. Source hash,
size and channel are preserved in accepted feedback history. Final review binds
the complete regenerated content version. None of these steps authorizes merge,
execution or formal synchronization.

Supported files are local ZIP archives with exactly one `content.json` review
sheet, its root topic and ordered `children.attached` tree. Root title, version,
module paths, case IDs, labels and topology correspond to the generated scoped
review Markdown. Scalar edits and whole-case removal follow the Markdown
feedback rules, including repeated shared-data agreement and three-way conflict
checks. Native topic IDs are storage identities, never business case identities.
Generated operation topics use `步骤 1：...` rather than a Markdown numbered-list
marker: the target client otherwise creates an empty wrapper above operation,
data and expectation, changing the required parent/child relationship.
Legacy XML, multiple sheets, detached topics, additional notes/markers/images or
unsupported annotations, changed identity/path and structural ambiguities remain
pending. Input and expanded archive bounds limit parsing; no ZIP is extracted.
This adapter does not claim compatibility with every historical XMind format.

Development acceptance requires the generated Markdown to be imported in the
target client, checked for complete hierarchy/content, saved before edits, edited
and saved as a distinct native return. Compare native content with the original
Markdown, then use the actual return through this entry and inspect both revised
views after simulated agreement and final review. Record client version and
provenance of the operator/evidence. Synthetic archives in unit tests establish
parser behavior only; they never substitute for client evidence. Keep these
local development artifacts outside the public package and mark simulated
business answers explicitly.
