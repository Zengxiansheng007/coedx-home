"""Read a local native XMind return into the existing feedback review gate."""
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

from feedback import prepare_feedback

MAX_FILE_BYTES = 16 * 1024 * 1024


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


def prepare_xmind_feedback(batch, returned_file, *, actual_reply):
    """Keep unsupported returns pending; never infer edits from a filename."""
    path = Path(returned_file)
    source = {'filename': path.name}
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            raise ValueError('Native file exceeds supported size')
        raw = path.read_bytes()
        source.update(sha256=hashlib.sha256(raw).hexdigest(), size_bytes=len(raw))
        markdown = _markdown(raw)
        pending = prepare_feedback(batch, 'markdown', markdown=markdown, actual_reply=actual_reply)
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
    args = parser.parse_args()
    batch = json.loads(Path(args.batch).read_text(encoding='utf-8-sig'))
    result = prepare_xmind_feedback(batch, args.returned_file, actual_reply=args.reply)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=False)
    (output / 'feedback.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(result['status'] + ': native input retained; no candidate changes applied.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
