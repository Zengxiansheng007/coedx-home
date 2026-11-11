"""Business display only; candidate identities remain unchanged."""
import re


def display_text(batch, text):
    cases = {c['id']: c for c in batch.get('initial_copy_baseline', {}).get('cases', [])} if batch.get('initial_copy_baseline') else {}  # Retain names for prior references.
    cases.update({c['id']: c for c in batch['cases']})  # Current titles win after a rename.
    text = re.sub(r'用例编号：([^\n；<]+)', lambda m: '用例名称：' + cases[m[1]].get('title', '待核对用例') if m[1] in cases else '用例名称：关联用例（名称待核对）', text)  # Missing external titles require clarification, not exposed codes.
    for identity in sorted(cases, key=len, reverse=True):
        title = cases[identity].get('title', '待核对用例')
        text = re.sub(r'(?<![\w-])' + re.escape(identity) + r'(?![\w-])', lambda _: title, text)  # Replace explicit identity tokens, not substrings in business words.
    return text.replace('用例编号', '用例名称')  # References remain business-readable.
