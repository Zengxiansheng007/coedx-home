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
module paths, Chinese case titles, labels and topology correspond to the generated scoped
review Markdown. Scalar edits and whole-case removal follow the Markdown
feedback rules, including repeated shared-data agreement and three-way conflict
checks. Native topic IDs are storage identities, never business case identities.
Read [the presentation identity contract](presentation-identity.md) for agent-side
inspection and business-clarified return bindings; users do not maintain technical
identity fields. Historical generated ID headings remain supported at their exact
baseline version/path. New Chinese-title client imports require fresh evidence.
Generated operation topics use `步骤 1：...` rather than a Markdown numbered-list
marker: the target client otherwise creates an empty wrapper above operation,
data and expectation, changing the required parent/child relationship.
Legacy XML, multiple sheets, detached topics, additional notes/markers/images or
unsupported annotations, changed identity/path and structural ambiguities remain
pending. Input and expanded archive bounds limit parsing; no ZIP is extracted.
This adapter does not claim compatibility with every historical XMind format.
The verified client is XMind 26.4.1327.202606142039: local Markdown import,
single-sheet native save, scalar data/expected edits and a distinct native return.
Other clients or additional editing features require their own file validation.

Development acceptance requires the generated Markdown to be imported in the
target client, checked for complete hierarchy/content, saved before edits, edited
and saved as a distinct native return. Compare native content with the original
Markdown, then use the actual return through this entry and inspect both revised
views after simulated agreement and final review. Record client version and
provenance of the operator/evidence. Synthetic archives in unit tests establish
parser behavior only; they never substitute for client evidence. Keep these
local development artifacts outside the public package and mark simulated
business answers explicitly.

For a native imported header whose Markdown link became title plus href, pass the exact current candidate as `inspect_xmind_feedback(file, batch=batch)`; prepare already supplies it. Only the one self-authored link in the third header line is restored when title, href, root heading and version match the current export exactly. Notes, arbitrary/external links, extra links, changed versions and annotations still require explicit interpretation. Synthetic archives are parser evidence only; retain the real failure baseline and recheck the actual client.

## Materialized local companion links

For a file delivered by write_artifacts(result, output), supply the original output directory as companion_base to inspect_xmind_feedback and prepare_xmind_feedback (CLI: --companion-base). Markdown prepare_feedback accepts the same optional argument. Obtain this directory from the known delivery context, never from the returned filename or href. Reconstruct the exact expected entrance from that directory and the bound batch; no arbitrary URI whitelist is accepted. The business candidate and content version do not acquire machine paths.

The native adapter still restores only one exact third-line generated link with matching title, root and version. Extra links, links on business topics, changed href/title/version, annotations and unbound targets remain pending interpretation. Historical portable relative-link returns retain their existing behavior when companion_base is omitted. Native multiple-link interpretation remains unsupported; retain and clarify such files instead of guessing.

Moving only the returned native file keeps the original companion_base. Moving the whole bundle requires materializing again at the new location and binding that new export directory. File existence, user trust prompts, operating-system file association, actual content opening and parser qualification are separate observations. Never bypass a client trust prompt; manual user selection of a local reader may be necessary.

Example public entry sequence (paths are caller-owned local delivery context):

```python
result = render_batch(batch)  # Original candidate remains authoritative.
write_artifacts(result, output, source_catalog=source_catalog)  # Supply current sources when required.
pending = prepare_xmind_feedback(batch, returned_file, actual_reply=actual_reply,
    case_bindings=case_bindings, companion_base=output)  # Source export directory, not return directory.
```
### Incremental review input

For an `incremental-v1` return, compare the full version in 「评审范围」.
The saved layout determines the topic and companion-link bindings.
A superseded version reports the current version and its verified Markdown
path when present. Retain unsupported or ambiguous return files.

Use `xmind_feedback.py --record QA.md` to start from the existing task record.
Supply the returned file, actual reply, original delivery directory and any
required parent scope. The record preserves the file digest and normalized
return. Reopening it resumes the existing summary and review. The same
original bytes cannot append a duplicate event.
