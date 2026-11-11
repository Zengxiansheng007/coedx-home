"""Read authorized report files before asking; retain the existing P0 checker."""
import copy  # Keep supplied catalogs and requests unchanged.
import hashlib  # Bind observations to actually read bytes.
import json  # Only parse data, never execute supplied sources.
from pathlib import Path  # Resolve exact authorized files, including symlinks.
from authoring import _credential_guard  # Existing privacy boundary.
from p0_evidence import check_extension  # One owner of full P0 evidence requirements.


def reconcile_reports(catalog, baseline, report_paths, request, *, authorized_paths, mode='production', selected_paths=None):  # Public read-only intake.
    allowed = {Path(path).resolve() for path in authorized_paths}  # Caller supplies the exact authorized files.
    sources, gaps, reports, summaries = [], [], [], []  # Observations are not business answers.
    selected = None if selected_paths is None else {str(Path(p).resolve()) for p in selected_paths}  # Explicit selection never proves success.

    def read(path):  # All report and attachment reads share the same boundary.
        path = Path(path).resolve()  # Prevent relative-path or symlink escapes.
        if path not in allowed:  # Do not read an attachment merely because a report names it.
            raise PermissionError('文件不在授权读取范围')  # Honest access gap.
        content = path.read_text(encoding='utf-8-sig')  # Unsupported binary content stays a gap.
        _credential_guard(content)  # Never copy recognizable secrets into summaries.
        sources.append({'path': str(path), 'sha256': hashlib.sha256(content.encode()).hexdigest()})  # Actual read evidence.
        return content  # Sanitized text only.

    for supplied in report_paths:  # Read every supplied report before choosing a version.
        path = Path(supplied).resolve()  # Original file identity.
        try:  # Missing or unsupported inputs remain visible.
            report = json.loads(read(path))  # Existing normalized envelope, one report per file.
            if not isinstance(report, dict):  # Never guess mappings for unsupported report layouts.
                raise ValueError('需要单份报告对象')  # Agent can normalize actual sources separately.
            _credential_guard(report)  # Check nested metadata too.
        except (OSError, UnicodeError, ValueError) as error:  # Fail closed without fabricating report contents.
            gaps.append({'path': str(path), 'case_id': None, 'reason': '报告无法读取或格式不支持', 'error_type': type(error).__name__})  # No secret error text.
            continue  # Other independently readable reports can still be inspected.
        report = copy.deepcopy(report)  # Hydration never rewrites the original report.
        local_gaps = []  # Missing attachments affect this report only.
        for evidence in report.get('evidence', []):  # Read explicitly referenced text attachments.
            if not evidence.get('path'):  # Existing source-traced inline observations remain supported.
                continue  # Semantic authenticity still belongs to the agent.
            attachment = path.parent / evidence['path']  # Relative paths are resolved against the report.
            evidence.pop('content', None)  # Stale inline content must not mask an unreadable attachment.
            try:  # Preserve the producer digest for existing checker comparison.
                evidence['content'] = read(attachment)  # Actual file content replaces any inline cache.
            except (OSError, UnicodeError, ValueError) as error:  # Access failures cannot mean pass.
                local_gaps.append({'path': str(attachment.resolve()), 'case_id': report.get('case_id'), 'reason': '必要附件无法读取', 'error_type': type(error).__name__})  # Identify affected scope.
        for name in report.get('required_attachments', []):  # Additional necessary source metadata.
            attachment = path.parent / name  # Explicit authorization still applies.
            try:  # Read before asking the user to choose reports.
                content = read(attachment)  # Generic text is available for agent semantic inspection.
                if attachment.suffix.lower() == '.json':  # Structured version metadata can reveal a conflict.
                    metadata = json.loads(content)  # Unsupported structured metadata is a gap.
                    if not isinstance(metadata, dict) or (metadata.get('tested_version') and metadata['tested_version'] != report.get('tested_version')):  # No cross-version proof.
                        raise ValueError('附件版本冲突')  # Do not silently repair evidence.
            except (OSError, UnicodeError, ValueError) as error:  # Missing metadata blocks this report.
                local_gaps.append({'path': str(attachment.resolve()), 'case_id': report.get('case_id'), 'reason': '必要附件缺失、不可读或版本冲突', 'error_type': type(error).__name__})  # Concrete impact.
        if local_gaps:  # A pass label cannot compensate for inaccessible evidence.
            report['evidence'] = []  # Existing checker returns pending_check for the scoped case.
        gaps.extend(local_gaps)  # Keep excluded reports' gaps visible too.
        case = baseline['cases'].get(report.get('case_id'), {}).get('case', {})  # Use readable business identity.
        label = case.get('title') or case.get('name') or report.get('case_id', '对象未知')  # Technical identity is only a fallback.
        summaries.append({'path': str(path), 'object': label, 'scope': report.get('module_path', []), 'version': report.get('tested_version'), 'result': report.get('result'), 'gaps': local_gaps})  # User-readable comparison.
        if (selected is None or str(path) in selected) and (not request.get('tested_version') or report.get('tested_version') == request['tested_version']):  # Reuse explicit target, never date/latest.
            reports.append(report)  # Duplicates intentionally remain ambiguous to the checker.
    checked = check_extension(catalog, baseline, reports, request, mode=mode)  # Preserve whole approved P0 scope and all entry decisions.
    needs_selection = not request.get('tested_version') or any(sum(report.get('case_id') == identity for report in reports) > 1 for identity in baseline['cases'])  # Missing facts do not reopen an unchanged target decision.
    statuses = {'passed': '通过', 'failed': '失败', 'not_run': '未执行', 'pending_check': '待核对'}  # Business-readable results.
    reasons = {'Missing or ambiguous report': '缺少报告或同范围报告仍有歧义', 'Scope, version, purpose or source mismatch': '范围、版本、验证用途或来源不匹配', 'Matching report result': '匹配报告的实际结果', 'Matching necessary evidence contents supplied': '必要证据内容齐全且匹配', 'Missing necessary evidence contents or digest mismatch': '必要证据缺失或内容摘要不匹配'}  # Preserve precise checker meanings.
    lines = ['已读取的报告比较（选择报告不代表完整 P0 通过）：']  # Plain Chinese evidence summary.
    for row in summaries:  # Include older/excluded reports and real remaining gaps.
        lines.append(f"对象：{row['object']}；范围：{' / '.join(row['scope'])}；版本：{row['version'] or '未知'}；报告结果：{statuses.get(row['result'], '未知')}；来源：{row['path']}")  # Not just opaque run IDs.
    for gap in gaps:  # Expose precise inaccessible files and their effect.
        lines.append(f"缺口：{gap['reason']}；影响：{gap['case_id'] or '完整批准 P0 范围待定位'}；来源：{gap['path']}")  # Never claim unread evidence was inspected.
    for row in checked['cases']:  # Full scope cannot shrink to selected reports.
        case = baseline['cases'][row['case_id']]['case']  # Retain business names even when no report is readable.
        label = case.get('title') or case.get('name') or row['case_id']  # Fallback identity never invents a title.
        lines.append(f"核对：{label}（{row['case_id']}）；状态：{statuses[row['execution_status']]}；依据：{reasons.get(row['reason'], row['reason'])}")  # Checker results separate from report assertions.
    return {'check': checked, 'reports': reports, 'read_sources': sources, 'gaps': gaps, 'summaries': summaries, 'needs_selection': needs_selection, 'chat': '\n'.join(lines)}  # No execution or case mutation.
