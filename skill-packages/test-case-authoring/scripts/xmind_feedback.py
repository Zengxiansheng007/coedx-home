"""Read a local native XMind return into the existing feedback review gate."""
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

from feedback import prepare_feedback

MAX_FILE_BYTES = 16 * 1024 * 1024


def inspect_xmind_feedback(returned_file):
    """Read supported native content for agent-side business clarification."""
    from aggregation import feedback_topics
    path = Path(returned_file)
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError('Native file exceeds supported size')
    markdown = _markdown(path.read_bytes())  # Reuse the exact supported parser; no guessed topic identities.
    return {'markdown': markdown, 'topics': feedback_topics(markdown)}


def _markdown(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries = archive.infolist()
        if len(entries) > 200 or sum(e.file_size for e in entries) > 64 * 1024 * 1024:
            raise ValueError('Archive exceeds supported size')
        matches = [e for e in entries if e.filename == 'content.json']
        if len(matches) != 1 or matches[0].file_size > MAX_FILE_BYTES:
            raise ValueError('One bounded content.json is required; legacy XML is unsupported')
        sheets = json.loads(archive.read(matches[0]))
    if not isinstance(sheets, list) or len(sheets) != 1:
        raise ValueError('Exactly one review sheet required')
    sheet = sheets[0]
    if any(sheet.get(key) for key in ('relationships', 'summaries', 'boundaries')):
        raise ValueError('Additional sheet annotations need explicit interpretation')
    lines, identities = [], set()
    def visit(topic, depth):
        if depth > 64 or len(lines) >= 50000:
            raise ValueError('Topic tree exceeds supported limits')
        title = topic['title']
        if not isinstance(title, str) or '\n' in title or '\r' in title:
            raise ValueError('Multiline topic needs explicit interpretation')
        identity = topic.get('id')
        if identity:
            if identity in identities:
                raise ValueError('Duplicate topic identity')
            identities.add(identity)
        for key in ('notes', 'labels', 'markers', 'callout', 'summaries', 'boundaries', 'href', 'image', 'equation'):
            if topic.get(key):
                raise ValueError('Additional topic annotation needs explicit interpretation')
        children = topic.get('children', {})
        if not isinstance(children, dict) or any(value for key, value in children.items() if key != 'attached'):
            raise ValueError('Detached or unsupported topic children')
        lines.append('# ' + title if depth == 0 else '  ' * (depth - 1) + '- ' + title)
        for child in children.get('attached', []):
            visit(child, depth + 1)
    visit(sheet['rootTopic'], 0)
    return '\n'.join(lines) + '\n'


def prepare_xmind_feedback(batch, returned_file, *, actual_reply, case_bindings=None):
    """Keep unsupported returns pending; never infer edits from a filename."""
    path = Path(returned_file)
    source = {'filename': path.name}
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            raise ValueError('Native file exceeds supported size')
        raw = path.read_bytes()
        source.update(sha256=hashlib.sha256(raw).hexdigest(), size_bytes=len(raw))
        markdown = _markdown(raw)
        pending = prepare_feedback(batch, 'markdown', markdown=markdown, actual_reply=actual_reply, case_bindings=case_bindings)  # Same clarified identity contract as Markdown.
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RecursionError,
            zipfile.BadZipFile, RuntimeError, NotImplementedError):
        return {'status': 'pending_verification', 'source': source,
                'reason': 'Unsupported file, annotations, identity or conflicting edits; retain the file and clarify.'}
    pending.update(status='ready_for_clarification', channel='xmind', returned_source=source)
    return pending


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--returned-file', required=True)
    parser.add_argument('--reply', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--case-bindings', help='Agent-maintained JSON from actual business identity clarification')
    args = parser.parse_args()
    batch = json.loads(Path(args.batch).read_text(encoding='utf-8-sig'))
    bindings = json.loads(Path(args.case_bindings).read_text(encoding='utf-8-sig')) if args.case_bindings else None
    result = prepare_xmind_feedback(batch, args.returned_file, actual_reply=args.reply, case_bindings=bindings)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=False)
    (output / 'feedback.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(result['status'] + ': native input retained; no candidate changes applied.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
