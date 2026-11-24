"""Build both XMind Markdown views from precisely the same active releases."""

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

from .path_utils import canonical_display_path, io_path
from .case_contracts import validate_document
from .compiler_v2 import _display_postcondition
from .file_lock import exclusive_file_lock
from .human_view_handoff import RUNTIME_REFS
from .product_aggregate import AggregateError, _safe_filename
from .release_verifier import verify_release
from .strict_json import load_strict_json


TOTAL_FILE = 'total-cases.xmind.md'
LEGACY_INDEX_PREFIX = '<!-- ui-test-case-maps: '  # 只用于读取旧总图。
INDEX_DIRECTORY = '.case-map-index'  # 刷新索引存放在导图文件之外。


@dataclass(frozen=True)
class ActiveCase:
    case_ir: dict
    steps: list
    build: str
    branch: Path
    pointer: dict
    view: Path

    @property
    def case_id(self):
        return self.case_ir['case_id']


def _read_case(branch):
    display = canonical_display_path(branch)
    folder = io_path(display)
    try:
        pointer = load_strict_json(folder / 'active.json')
        identity = pointer['case_id']
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise AggregateError(f'E_MAP_ACTIVE_POINTER:{display.name}') from error
    try:
        build = pointer['build_fingerprint']
        if re.fullmatch(r'sha256:[0-9a-f]{64}', build) is None:
            raise AggregateError(f'E_MAP_ACTIVE_BUILD:{identity}')
        commit_dir = 'releases/' + build.removeprefix('sha256:')
        if pointer['manifest_ref'] != commit_dir + '/manifest.json':
            raise AggregateError(f'E_MAP_ACTIVE_REFERENCE:{identity}')
        release = folder / commit_dir
        if verify_release(release, active_pointer=pointer)['release_integrity'] != 'valid':
            raise AggregateError(f'E_MAP_RELEASE_INVALID:{identity}')
        case_ir = load_strict_json(release / 'case-ir.json')
        resolved = load_strict_json(release / 'resolved-ir.json')
        if validate_document(case_ir, 'case-ir-v2.schema.json') or validate_document(resolved, 'resolved-ir-v2.schema.json'):
            raise AggregateError(f'E_MAP_INVALID_STRUCTURED_CASE:{identity}')
        manifest = load_strict_json(release / 'manifest.json')
        for field in ('case_id', 'branch_id', 'source_hash', 'test_data_hash', 'parameter_manifest_hash'):
            if case_ir[field] != manifest[field] or resolved[field] != manifest[field]:
                raise AggregateError(f'E_MAP_RELEASE_BINDING:{identity}:{field}')
        steps = resolved['resolved_steps']
        if [step['source_step_id'] for step in steps] != [step['step_id'] for step in case_ir['steps']]:
            raise AggregateError(f'E_MAP_RESOLVED_ORDER:{identity}')
        parameters = load_strict_json(release / 'case-parameter-manifest.json')['parameters']
        references = {param['parameter_id']: param['ref'] for param in parameters}
        for step in steps:
            for assertion in step['postconditions']:
                prefix, _, key = assertion['expected_ref'].partition(':')
                if prefix == 'parameter' and references[key].startswith(RUNTIME_REFS):
                    assertion['expected_reference'] = references[key]  # 展示断言保留治理引用。
                    assertion['reference_only'] = True
        view = display / 'views' / 'human.md'
        if io_path(view).read_bytes() != (release / 'human.md').read_bytes():
            raise AggregateError(f'E_MAP_HUMAN_VIEW_DRIFT:{identity}')
        return ActiveCase(case_ir, steps, build, display, pointer, view)
    except (OSError, KeyError, TypeError, AttributeError, ValueError) as error:
        if isinstance(error, AggregateError):
            raise
        raise AggregateError(f'E_MAP_CASE_UNREADABLE:{identity}') from error


def _labels(scope, display):
    def label(group, value):
        return display.get(group, {}).get(value, value)

    product = label('products', scope['product'])
    system = label('systems', scope['system'])
    product_path = [(scope['product'], product)] if product != system and product != scope['product'] else []
    return [
        *product_path, (scope['system'], system),
        *((module, label('modules', module)) for module in scope['module_path']),
        (scope['function'], label('functions', scope['function'])),
    ]


def _module(case, navigation):
    scope = case.case_ir['scope']
    path = (scope['project_group'], scope['product'], scope['system'], *scope['module_path'])
    for end in range(4, len(path) + 1):
        kind = navigation.get(path[:end])
        if kind == 'page':
            return path[:end]
        if kind not in ('menu', 'redirect'):
            raise AggregateError(f'E_MAP_PAGE_OWNERSHIP:{case.case_id}:{"/".join(path[:end])}')
    raise AggregateError(f'E_MAP_PAGE_OWNERSHIP:{case.case_id}:{"/".join(path)}')


def _text(value):
    return str(value).replace('\r', '').replace('\n', '<br>')


def _parameter(parameter):
    reference = parameter.get('ref', '')
    value = (reference if reference and not reference.startswith('test-data:')
             else parameter.get('display_value', parameter.get('value', '')))
    if value == '':
        value = '留空'
    elif isinstance(value, list):
        value = '、'.join(map(str, value))
    elif isinstance(value, dict):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return '数据 · ' + _text(parameter.get('label') or parameter.get('parameter_id')) + '：' + _text(value)


def _step_content(step):
    lines = [_parameter(parameter) for parameter in step.get('parameters', [])]
    lines.append('预期：' + _text(step['expected_result']))
    for condition in step.get('postconditions', []):
        lines.append('验证点：' + _text(_display_postcondition(condition)))
    return lines


def _list(text, depth):
    return '  ' * depth + '- ' + _text(text)


def _operations(steps, depth):
    lines = []
    for number, step in enumerate(steps, 1):
        lines.append(_list(f'操作 {number}：{step["intent"]}', depth))
        lines.extend(_list(row, depth + 1) for row in _step_content(step))
    return lines


def _common_prefix(cases):
    if len(cases) < 2:
        return []
    common = []
    for peers in zip(*(case.steps for case in cases)):
        first = peers[0]
        if (first['section'] != 'setup' or not first.get('binding_ref')
                or any((step['section'], step.get('binding_ref'), step['intent'], _step_content(step))
                       != ('setup', first['binding_ref'], first['intent'], _step_content(first))
                       for step in peers[1:])):
            break
        common.append(first)  # 仅提取相同有序访问流程，其他操作留在逐例正文。
    return common


def _tree_line(lines, path, previous):
    shared = 0
    while shared < min(len(path), len(previous)) and path[shared][0] == previous[shared][0]:
        shared += 1
    lines.extend(_list(label, i) for i, (_, label) in enumerate(path[shared:], shared))
    return path


def _dependency_lines(case, details, identities, depth):
    lines = []
    for link in details.get(case.case_id, ()):
        ref = link.get('dependency_ref')
        target = link.get('target_case_id')
        if ref not in case.case_ir['dependency_refs'] or target not in identities or target == case.case_id:
            raise AggregateError(f'E_MAP_DEPENDENCY_IDENTITY:{case.case_id}:{ref}')
        keys = ('purpose', 'inputs', 'outputs')
        if any(not link.get(key) for key in keys):
            raise AggregateError(f'E_MAP_DEPENDENCY_DETAILS:{case.case_id}:{ref}')
        lines.append(_list('关联用例：' + target, depth))
        lines.extend(_list(label + '：' + _text(link[key]), depth + 1)
                     for key, label in zip(keys, ('用途', '输入', '产出')))
    return lines


def _digest(value):
    return hashlib.sha256(value).hexdigest()


def _index_path(body):
    return Path(INDEX_DIRECTORY) / (_digest(body) + '.json')  # 由当前总图字节定位同版索引。


def _index(output):
    total = output / TOTAL_FILE
    try:
        if not total.is_file():
            return {}
        body = total.read_bytes()
        if not body:
            raise AggregateError('E_MAP_CURRENT_INDEX_EMPTY')
        last = body.decode('utf-8').rstrip('\r\n').rsplit('\n', 1)[-1]
        sidecar = output / _index_path(body)
        if last.startswith(LEGACY_INDEX_PREFIX):
            index = json.loads(last[len(LEGACY_INDEX_PREFIX):-4])  # 旧目录首次刷新仍可复用分图。
        elif sidecar.is_file():
            index = load_strict_json(sidecar)
            if index['schema_version'] != 1 or index['total_sha256'] != _digest(body):
                raise ValueError('index does not match current total Markdown')
        else:
            return {}  # 兼容无索引的旧目录，既有分图重新核对文件字节。
        if not isinstance(index['cases'], list) or not isinstance(index['modules'], dict):
            raise ValueError('wrong index types')
        return index
    except (OSError, ValueError, TypeError, KeyError) as error:
        if isinstance(error, AggregateError):
            raise
        raise AggregateError('E_MAP_CURRENT_INDEX_INVALID') from error


def _module_fingerprint(owner, filename, group, display, business_groups, dependencies):
    members = [(case.case_id, case.case_ir['branch_id'], case.build,
                _labels(case.case_ir['scope'], display), business_groups.get(case.case_id),
                dependencies.get(case.case_id)) for case in group]
    material = json.dumps([2, owner, filename, members], ensure_ascii=False, sort_keys=True)
    return _digest(material.encode('utf-8'))


def _maps(cases, output, navigation, display, business_groups, dependency_details, prior):
    by_module = {}
    root_id = cases[0].case_ir['scope']['project_group']
    root_label = display.get('project_groups', {}).get(root_id, root_id)
    for case in cases:
        scope = case.case_ir['scope']
        if scope['project_group'] != root_id or scope['product'] != cases[0].case_ir['scope']['product']:
            raise AggregateError(f'E_MAP_PRODUCT_SCOPE:{case.case_id}')
        by_module.setdefault(_module(case, navigation), []).append(case)
    total = [f'# {root_label}总用例']
    content, module_records = {}, {}
    previous = ()
    identities = {case.case_id for case in cases}
    if dependency_details.keys() - identities:
        raise AggregateError('E_MAP_DEPENDENCY_SOURCE_UNKNOWN')
    slugs = {key: _safe_filename(display.get('modules', {}).get(key[-1], key[-1])) for key in by_module}
    for owner, group in sorted(by_module.items()):
        label = display.get('modules', {}).get(owner[-1], owner[-1])
        slug = slugs[owner]
        if list(slugs.values()).count(slug) > 1:
            slug += '-' + hashlib.sha256('/'.join(owner).encode()).hexdigest()[:10]
        filename = slug + '.xmind.md'
        fingerprint = _module_fingerprint(owner, filename, group, display, business_groups, dependency_details)
        relative = (Path('modules') / fingerprint / filename).as_posix()
        target = output / relative
        saved = prior.get('modules', {}).get(fingerprint)
        if saved and (saved.get('path') != relative or not target.is_file()
                      or _digest(target.read_bytes()) != saved.get('sha256')):
            raise AggregateError(f'E_MAP_PRESERVED_MODULE_LINK:{"/".join(owner)}')
        module = None if saved else [f'# {label}完整用例']
        common = _common_prefix(group) if module is not None else []
        if common:
            module.append(_list('公共前置操作', 0))
            module.append(_list(f'适用用例（{len(group)} 条）', 1))
            module.extend(_list(case.case_id + '｜' + case.case_ir['display_name'], 2) for case in group)
            module.extend(_operations(common, 1))
        module_previous = ()
        first = True
        for case in sorted(group, key=lambda item: (*item.case_ir['scope']['module_path'],
                                                      item.case_ir['scope']['function'], item.case_id)):
            ir = case.case_ir
            directory = _labels(ir['scope'], display)
            owner_depth = len(directory) - 1 - (len(ir['scope']['module_path']) - len(owner[3:]))
            headings = tuple((f'group:{label}', label) for label in business_groups.get(case.case_id, ()))
            path = tuple(directory) + headings
            if first:
                previous = _tree_line(total, path[:owner_depth], previous)
                total.append(_list(f'[打开{label}完整用例图]({target.as_uri()})', owner_depth))
                first = False
            previous = _tree_line(total, path, previous)
            suffix = path[owner_depth:]
            title = ir['priority'] + ' ' + ir['display_name']
            total.extend([_list(title, len(path)), _list('用例 ID ' + case.case_id, len(path) + 1),
                          _list(f'[查看完整步骤与预期]({case.view.as_uri()})', len(path) + 1)])
            if module is not None:
                module_previous = _tree_line(module, suffix, module_previous)
                module.extend([_list(title, len(suffix)), _list('用例编号：' + case.case_id, len(suffix) + 1)])
                module.extend(_dependency_lines(case, dependency_details, identities, len(suffix) + 1))
                module.extend(_operations(case.steps[len(common):], len(suffix) + 1))
        if saved:
            module_records[fingerprint] = saved
        else:
            encoded = ('\n'.join(module) + '\n').encode('utf-8')
            if target.exists():
                if target.read_bytes() != encoded:
                    raise AggregateError(f'E_MAP_VERSIONED_MODULE_DRIFT:{"/".join(owner)}')
            else:
                content[relative] = encoded
            module_records[fingerprint] = {'path': relative, 'sha256': _digest(encoded)}
    case_records = [{'case_id': case.case_id, 'branch_id': case.case_ir['branch_id'],
                     'build_fingerprint': case.build} for case in cases]
    index = {'cases': case_records, 'modules': module_records}
    content[TOTAL_FILE] = ('\n'.join(total) + '\n').encode('utf-8')
    return content, index


def _version_differences(branches, prior):
    previous = {(item['case_id'], item['branch_id']): item['build_fingerprint'] for item in prior.get('cases', [])}
    differences = []
    for branch in branches:
        try:
            pointer = load_strict_json(io_path(branch) / 'active.json')
            identity = (pointer['case_id'], pointer['branch_id'])
            latest = pointer['build_fingerprint']
        except (OSError, ValueError, KeyError, TypeError):
            continue
        old = previous.get(identity)
        if old and old != latest:
            differences.append(f'E_MAP_ACTIVE_VERSION_DIFF:{identity[0]}:{old}->{latest}')
    return differences


def _publish(output, content, index, cases):
    def check_active_cases():
        for case in cases:
            if _read_case(case.branch).pointer != case.pointer:
                raise AggregateError(f'E_MAP_ACTIVE_CHANGED:{case.case_id}')

    total_body = content[TOTAL_FILE]
    index_path = _index_path(total_body)
    index_body = (json.dumps(dict(index, schema_version=1, total_sha256=_digest(total_body)),
                             ensure_ascii=False, sort_keys=True) + '\n').encode('utf-8')
    with tempfile.TemporaryDirectory(prefix='.case-maps-', dir=output.parent) as temporary:
        delivery = Path(temporary) / 'maps'
        for filename, body in [*content.items(), (index_path, index_body)]:
            target = delivery / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
        if not output.exists():
            check_active_cases()
            os.replace(delivery, output)
            return
        for filename in content.keys() - {TOTAL_FILE}:
            target = output / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(delivery / filename, target)  # 旧总图继续引用它原有的不可变分图。
        for record in index['modules'].values():
            target = output / record['path']
            if not target.is_file() or _digest(target.read_bytes()) != record['sha256']:
                raise AggregateError(f'E_MAP_MODULE_PUBLICATION:{record["path"]}')
        total = output / TOTAL_FILE
        sidecar = output / index_path
        total_changed = not total.is_file() or total.read_bytes() != total_body
        index_changed = not sidecar.is_file() or sidecar.read_bytes() != index_body
        if index_changed:
            sidecar.parent.mkdir(exist_ok=True)
        if total_changed and index_changed:
            os.replace(delivery / index_path, sidecar)
        check_active_cases()  # 完成可能较慢的分图落盘后重新验证生效详情。
        if total_changed:
            os.replace(delivery / TOTAL_FILE, total)  # 单一可见入口在所有目标可用后切换。
        elif index_changed:
            os.replace(delivery / index_path, sidecar)  # 同正文时索引替换本身即是提交点。


def export_active_maps(active_branches, output_directory, *, navigation, display_registry,
                       business_groups=None, dependency_details=None):
    """Export a read-only selection of verified active case branches."""
    output = canonical_display_path(output_directory)
    branches = tuple(active_branches)
    output.parent.mkdir(parents=True, exist_ok=True)
    lock = output.parent / ('.' + output.name + '.case-maps.lock')
    with exclusive_file_lock(lock):
        prior = _index(output)
        try:
            cases = sorted((_read_case(branch) for branch in branches), key=lambda case: case.case_id)
            if not cases:
                raise AggregateError('E_MAP_EMPTY')
            if len({case.case_id for case in cases}) != len(cases):
                raise AggregateError('E_MAP_DUPLICATE_CASE')
            content, index = _maps(cases, output, navigation, display_registry, business_groups or {},
                                   dependency_details or {}, prior)
            _publish(output, content, index, cases)
        except (OSError, AggregateError) as error:
            differences = _version_differences(branches, prior)
            reason = str(error) if isinstance(error, AggregateError) else 'E_MAP_PUBLICATION_INTERRUPTED'
            raise AggregateError(' | '.join([reason, *differences])) from error
    modules = [output / record['path'] for record in index['modules'].values()]
    prior_modules = {output / record['path'] for record in prior.get('modules', {}).values()}
    return {
        'total': output / TOTAL_FILE,
        'modules': modules,
        'cases': index['cases'],
        'reused_modules': [path for path in modules if path in prior_modules],
        'generated_modules': [path for path in modules if path not in prior_modules],
    }
