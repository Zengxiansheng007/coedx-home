"""Render a formal single-case Markdown from UI-Test's validated work order."""

import argparse
from copy import deepcopy
from hashlib import sha256
import html
import json
from pathlib import Path


def _cell(value):
    if value == '':
        return '留空'
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return html.escape(str(value)).replace('|', '\\|').replace('\r\n', '<br>').replace('\n', '<br>').replace('\r', '<br>')


def render_formal_human_view(request):
    identity = request['identity']
    if (request['schema_version'] != 'ui-test.tca-human-view-request.v1'
            or identity['renderer_version'] != 'tca-human-view-v1'):
        raise ValueError('Unsupported formal Human View request')
    lines = [
        '<!-- do_not_edit: true -->',
        f'<!-- build_fingerprint: {identity["build_fingerprint"]} -->',
        f'<!-- tca_request: {request["request_hash"]} -->',
        '# ' + _cell(request['display_name']),
        '',
        '| 序号 | 操作 | 参数/数据 | 预期结果 |',
        '| --- | --- | --- | --- |',
    ]
    for step in request['steps']:
        params = '；'.join(_cell(item['label']) + '：' + _cell(item['value']) for item in step['parameters'])
        asserted = '；'.join(' '.join(_cell(condition[key]) for key in ('id', 'operator', 'value'))
                            for condition in step['assertions'])
        expected = _cell(step['expected']) + ('；断言：' + asserted if asserted else '')
        lines.append(f"| {step['sequence']} | {_cell(step['operation'])} | {params or '-'} | {expected} |")
    markdown = '\n'.join(lines) + '\n'
    return {
        'schema_version': 'tca.formal-human-view.v1',
        'identity': deepcopy(identity),
        'request_hash': request['request_hash'],
        'markdown': markdown,
        'sha256': 'sha256:' + sha256(markdown.encode('utf-8')).hexdigest(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    request = json.loads(Path(args.request).read_text(encoding='utf-8-sig'))
    artifact = render_formal_human_view(request)
    with Path(args.output).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(artifact, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
