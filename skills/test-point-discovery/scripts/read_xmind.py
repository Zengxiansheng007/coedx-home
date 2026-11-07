"""Read a bounded native XMind tree; business correspondence belongs to the Agent.

Thin adaptation of test-case-authoring's public native archive reading approach.
No dependency on its case model, no extraction, no document update.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

MAX_BYTES = 16 * 1024 * 1024


def read_xmind(path):
    path = Path(path)
    source = {'filename': path.name}
    try:
        if path.stat().st_size > MAX_BYTES:
            raise ValueError('Native file exceeds 16 MiB')
        raw = path.read_bytes()
        if len(raw) > MAX_BYTES:
            raise ValueError('Native file exceeds 16 MiB')
        source.update(sha256=hashlib.sha256(raw).hexdigest(), size_bytes=len(raw))
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            entries = archive.infolist()
            if len(entries) > 200 or sum(e.file_size for e in entries) > 64 * 1024 * 1024:
                raise ValueError('Archive exceeds supported limits')
            matches = [e for e in entries if e.filename == 'content.json']
            if len(matches) != 1 or matches[0].file_size > MAX_BYTES:
                raise ValueError('Exactly one bounded content.json required; XML-only unsupported')
            sheets = json.loads(archive.read(matches[0]))
        if not isinstance(sheets, list) or len(sheets) != 1:
            raise ValueError('Exactly one sheet required')
        sheet = sheets[0]
        if any(sheet.get(k) for k in ('relationships', 'summaries', 'boundaries')):
            raise ValueError('Sheet annotations need explicit interpretation')
        topics, identities = [], set()

        def visit(topic, parent_path):
            if len(parent_path) > 64 or len(topics) >= 50000:
                raise ValueError('Topic tree exceeds supported limits')
            title = topic['title']
            if not isinstance(title, str) or not title.strip() or '\n' in title or '\r' in title:
                raise ValueError('Empty or multiline title needs explicit interpretation')
            identity = topic.get('id')
            if identity is not None:
                if not isinstance(identity, str) or identity in identities:
                    raise ValueError('Invalid or duplicate topic identity')
                identities.add(identity)
            for key in ('notes', 'labels', 'markers', 'callout', 'summaries', 'boundaries', 'href', 'image', 'equation', 'extensions'):
                if topic.get(key):
                    raise ValueError('Topic annotation needs explicit interpretation')
            children = topic.get('children', {})
            if not isinstance(children, dict) or any(v for k, v in children.items() if k != 'attached'):
                raise ValueError('Unsupported topic children')
            attached = children.get('attached', [])
            if not isinstance(attached, list):
                raise ValueError('Attached children must be an ordered list')
            current = parent_path + [title]
            topics.append({'id': identity, 'title': title, 'path': current})
            for child in attached:
                visit(child, current)

        visit(sheet['rootTopic'], [])
        return {'status': 'read_for_agent_review', 'source': source, 'topics': topics}
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RecursionError,
            zipfile.BadZipFile, RuntimeError, NotImplementedError) as error:
        return {'status': 'pending_verification', 'source': source,
                'reason': str(error) if isinstance(error, ValueError) else 'Unreadable or unsupported native structure; retain input and clarify.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('returned_file')
    args = parser.parse_args()
    print(json.dumps(read_xmind(args.returned_file), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
