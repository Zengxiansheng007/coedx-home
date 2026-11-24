"""Read a local native XMind return into the existing feedback review gate."""
import argparse
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

from feedback import prepare_feedback
from incremental_review import LAYOUT, TITLE_PREFIX, version_of

MAX_FILE_BYTES = 16 * 1024 * 1024
NATIVE_LINK = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')


class NativeLocationError(ValueError):
    """A return has a known location that still needs interpretation."""

    def __init__(self, code, location):
        super().__init__(code)
        self.code = code
        self.location = location


def inspect_xmind_feedback(returned_file, *, batch=None, companion_base=None):
    """Read supported native content for agent-side business clarification."""
    from aggregation import feedback_topics
    path = Path(returned_file)
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError('Native file exceeds supported size')
    markdown = _markdown(path.read_bytes(), batch=batch, companion_base=companion_base)  # Reuse the exact supported parser; no guessed topic identities.
    return {'markdown': markdown, 'topics': feedback_topics(markdown)}


def _sheet(raw):
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
    return sheet


def _native_version(sheet):
    root = sheet['rootTopic']
    if not ('# ' + root['title']).startswith(TITLE_PREFIX):
        return None  # 历史布局继续用旧格式识别。
    scope = root.get('children', {}).get('attached', [])[0]
    version = scope.get('children', {}).get('attached', [])[0]
    return version_of(f"# {root['title']}\n- {scope['title']}\n  - {version['title']}")


def _known_links(markdown):
    from aggregation import _parse

    def visit(node, parents):
        link = NATIVE_LINK.fullmatch(node['text'])
        if link and ('资料与 Agent 交接说明' in parents or link[1] == '查看关联用例详情'):
            yield (parents, link[1]), link[2]  # 材料入口同时绑定祖先、标题和目标。
        for child in node['children']:
            yield from visit(child, (*parents, node['text']))

    return dict(visit(_parse(markdown.splitlines()[1:]), ()))


def _markdown(raw, *, batch=None, companion_base=None, source_catalog=None, sheet=None):
    sheet = _sheet(raw) if sheet is None else sheet
    incremental = batch is not None and batch.get('review_layout') == LAYOUT
    links = {}
    expected_header = None
    if incremental:
        from scoped_review import render_review_batch
        expected = render_review_batch(batch, source_catalog=source_catalog, companion_base=companion_base)
        links = _known_links(expected['xmind_markdown'])
    elif batch is not None:
        from authoring import render_batch
        expected_header = render_batch(batch)['xmind_markdown'].splitlines()[:3]  # Exact current generated header, never a caller supplied whitelist.
    canonical_header = list(expected_header) if expected_header else None  # Preserve canonical feedback semantics.
    if expected_header and companion_base is not None:
        from module_handoff import entrance
        expected_header[2] = expected_header[2].partition('配套资料：')[0] + entrance(batch, base_path=companion_base)  # Reconstruct from trusted batch and explicit origin.
    lines, identities = [], set()
    def visit(topic, depth, parents):
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
        plain_title = title
        if topic.get('href') and incremental:
            target = links.get((parents, title))
            if target is None or topic['href'] != target:
                location = '资料与 Agent 交接说明' if '资料与 Agent 交接说明' in parents else '业务操作节点'
                raise NativeLocationError('native_material_link', location)
            title = f'[{title}]({target})'  # 只还原已核对的同版资料入口。
        elif topic.get('href'):
            expected = expected_header[2] if expected_header and depth == 1 and len(lines) == 2 else ''
            legacy_links = list(NATIVE_LINK.finditer(expected))
            if len(legacy_links) != 1 or topic['href'] != legacy_links[0][2] or '- ' + title != expected.replace(legacy_links[0][0], legacy_links[0][1]) or lines[:2] != expected_header[:2]:
                raise ValueError('Unbound native link needs explicit interpretation')
            title = canonical_header[2][2:]  # Restore only the exact self-authored header link.
        for key in ('notes', 'labels', 'markers', 'callout', 'summaries', 'boundaries', 'image', 'equation'):
            if topic.get(key):
                raise ValueError('Additional topic annotation needs explicit interpretation')
        children = topic.get('children', {})
        if not isinstance(children, dict) or any(value for key, value in children.items() if key != 'attached'):
            raise ValueError('Detached or unsupported topic children')
        lines.append('# ' + title if depth == 0 else '  ' * (depth - 1) + '- ' + title)
        for child in children.get('attached', []):
            visit(child, depth + 1, (*parents, plain_title) if depth else ('',))
    visit(sheet['rootTopic'], 0, ())
    return '\n'.join(lines) + '\n'


def prepare_xmind_feedback(batch, returned_file, *, actual_reply, case_bindings=None, companion_base=None, source_catalog=None, _snapshot=False):
    """Keep unsupported returns pending; never infer edits from a filename."""
    path = Path(returned_file)
    source = {'filename': path.name}
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            raise ValueError('Native file exceeds supported size')
        raw = path.read_bytes()
        source.update(sha256=hashlib.sha256(raw).hexdigest(), size_bytes=len(raw))
        sheet = _sheet(raw)
        returned_version = _native_version(sheet)
        current_version = batch['content_version']
        if returned_version is not None and returned_version != current_version:
            recorded = {batch.get('initial_display_version')}
            recorded.update(item.get('source_version') for item in batch.get('feedback_history', []))
            if returned_version not in recorded:
                return {'status': 'pending_verification', 'source': source,
                        'reason_code': 'unknown_review_version', 'location': '评审范围 / 稿件版本'}
            current = {'version': current_version}
            review_path = Path(companion_base) / 'xmind.md' if companion_base is not None else None
            if review_path is not None and review_path.is_file():
                try:
                    if version_of(review_path.read_text(encoding='utf-8-sig')) == current_version:
                        current['markdown'] = str(review_path)
                except (OSError, ValueError):
                    pass  # 仍报告已知当前版本，保留不可核验的入口。
            return {'status': 'superseded_review', 'source': source,
                    'returned_version': returned_version, 'current_review': current,
                    'reason': '在当前版本评审稿上重新标注，再回传。'}
        markdown = _markdown(raw, batch=batch, companion_base=companion_base,
                             source_catalog=source_catalog, sheet=sheet)
        pending = prepare_feedback(batch, 'markdown', markdown=markdown, actual_reply=actual_reply, case_bindings=case_bindings, companion_base=companion_base, source_catalog=source_catalog)  # Same clarified identity contract as Markdown.
    except NativeLocationError as error:
        return {'status': 'pending_verification', 'source': source,
                'reason_code': error.code, 'location': error.location}
    except (OSError, ValueError, KeyError, IndexError, TypeError, AttributeError, RecursionError,
            zipfile.BadZipFile, RuntimeError, NotImplementedError):
        return {'status': 'pending_verification', 'source': source,
                'reason': 'Unsupported file, annotations, identity or conflicting edits; retain the file and clarify.'}
    pending.update(status='ready_for_clarification', channel='xmind', returned_source=source)
    if _snapshot:
        pending['normalized_markdown'] = markdown  # 落盘政策仍由已有问答记录持有。
    return pending


def start_native_feedback(record, returned_file, *, actual_reply, clear_changes=False,
                          case_bindings=None, companion_base=None, source_catalog=None):
    """Start feedback in the existing Q&A record using exact native input bytes."""
    from qa_record import advance_record, read_record

    state = read_record(record)
    batch = state['batch']
    path = Path(returned_file)
    batch = dict(batch, questions=state['questions'])  # 与问答回放采用同一当前候选。
    opened = prepare_xmind_feedback(
        batch, path, actual_reply=actual_reply, case_bindings=case_bindings,
        companion_base=companion_base, source_catalog=source_catalog, _snapshot=True,
    )
    source = opened.get('returned_source') or opened.get('source', {})
    digest = source.get('sha256')
    sources = [item.get('returned_source', {}) for item in batch.get('feedback_history', [])]
    sources.append(state.get('feedback_pending', {}).get('returned_source', {}))
    if digest and any(item.get('sha256') == digest for item in sources):
        return {'status': 'already_recorded', 'sha256': digest}  # 复用已保存现场，不重复发起同一意见。
    if opened['status'] != 'ready_for_clarification':
        return opened
    payload = dict(channel='markdown', actual_reply=actual_reply, source_ref=str(path.resolve()),
                   markdown=opened['normalized_markdown'], native_return=source,
                   source_version=batch['content_version'], clear_changes=clear_changes)
    if companion_base is not None:
        payload['companion_base'] = str(Path(companion_base).resolve())
    if case_bindings is not None:
        payload['case_bindings'] = case_bindings
    if source_catalog is not None:
        payload['source_catalog'] = source_catalog
    current = advance_record(record, 'start_feedback', payload)
    return {'status': 'recorded', 'state': current, 'source': source}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--batch', help='Inspect feedback against a saved candidate')
    inputs.add_argument('--record', help='Save valid feedback once in the existing Q&A record')
    parser.add_argument('--returned-file', required=True)
    parser.add_argument('--reply', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--companion-base', help='Original xmind.md delivery directory; never infer it from the returned file')  # Explicit source location.
    parser.add_argument('--source-catalog', help='Actual complete parent catalog for a partial scope')  # Never reconstruct membership from visible cases.
    parser.add_argument('--case-bindings', help='Agent-maintained JSON from actual business identity clarification')
    parser.add_argument('--clear-changes', action='store_true', help='Explicitly select direct feedback summary for a clear edit')
    args = parser.parse_args()
    bindings = json.loads(Path(args.case_bindings).read_text(encoding='utf-8-sig')) if args.case_bindings else None
    source = json.loads(Path(args.source_catalog).read_text(encoding='utf-8-sig')) if args.source_catalog else None
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=False)
    context = dict(actual_reply=args.reply, case_bindings=bindings, companion_base=args.companion_base,
                   source_catalog=source)
    if args.record:
        result = start_native_feedback(args.record, args.returned_file, clear_changes=args.clear_changes, **context)
    else:
        batch = json.loads(Path(args.batch).read_text(encoding='utf-8-sig'))
        result = prepare_xmind_feedback(batch, args.returned_file, **context)
    (output / 'feedback.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(result['status'] + ': native input retained; no candidate changes applied.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
