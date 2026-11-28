"""Check one module's outline and its recorded user decision; never write a draft."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def label(value):
    return isinstance(value, str) and bool(value.strip()) and value == value.strip()


def paths(value, missing):
    if not isinstance(value, list) or not value:
        raise ValueError(missing)
    seen = set()
    for branch in value:
        if not isinstance(branch, list) or not branch or not all(map(label, branch)):
            raise ValueError("分支需给出从模块下一级到叶节点的非空名称路径")
        key = tuple(branch)
        if key in seen:
            raise ValueError("存在重复的业务分支路径")
        seen.add(key)
    return seen


def transcript_messages(text, suffix, first_line):
    if suffix == ".jsonl":
        records = ((number, json.loads(line)) for number, line
                   in enumerate(text.splitlines(), first_line) if line.strip())
    else:
        value = json.loads(text)
        records = value.get("messages", [value]) if isinstance(value, dict) else value
        if not isinstance(records, list):
            raise ValueError("消息记录格式不可读取")
        records = enumerate(records, first_line)
    for number, record in records:
        if not isinstance(record, dict):
            continue
        if record.get("type") == "response_item":
            record = record.get("payload", {})
            if not isinstance(record, dict) or record.get("type") != "message":
                continue
        content = record.get("content", "")
        if isinstance(content, list):
            content = "\n".join(item["text"] for item in content if isinstance(item, dict)
                                and isinstance(item.get("text"), str))
        if isinstance(content, str):
            yield number, record.get("role"), content


def user_quotes_in_markdown(content, quote):
    attribution = r'(?:用户(?:回复|回答|原话|答复|指定|确认)|[Uu]ser)\s*[：:]?\s*'
    quoted = r'[“「"]' + re.escape(quote) + r'[”」"]'
    speaker_line = r'(?im)^\s*(?:用户|user)\s*[：:]\s*' + re.escape(quote) + r'\s*$'
    hits = len(re.findall(attribution + quoted, content)) + len(re.findall(speaker_line, content))
    # Some interview records attribute a whole numbered list, or a quoted
    # reply plus a separate source line in the same Markdown section.
    for section in re.split(r'(?m)(?=^#{1,6} )', content):
        if not re.search(r'(?m)^[-* ]*来源[：:][^\n]*用户[^\n]*(?:回复|答复|回答|原话)', section):
            continue
        hits += len(re.findall(r'实际(?:回复|答复)\s*[：:]\s*' + quoted, section))
        if re.match(r'^#{1,6} [^\n]*用户(?:回复|答复|原话)', section):
            for line in section.splitlines():
                numbered = re.match(r'^\s*\d+[、.．]\s*(.+)$', line)
                if numbered and quote in (line.strip(), numbered[1]):
                    hits += 1
    return hits


def check_citation(citation, directory, expected_role=None):
    if not isinstance(citation, dict) or not label(citation.get("path")):
        raise ValueError("缺少可回查的采用依据路径")
    quote = citation.get("quote")
    if not isinstance(quote, str) or not quote.strip():
        raise ValueError("缺少当时展示的范围或用户原话")
    source = directory / citation["path"]
    raw = source.read_bytes()
    if "line" in citation:
        number = citation["line"]
        lines = raw.splitlines()
        if type(number) is not int or not 1 <= number <= len(lines):
            raise ValueError("采用依据的行号不可回查")
        raw = lines[number - 1]
    if digest(raw) != citation.get("sha256"):
        raise ValueError("采用依据版本不符，请回查原始记录")
    content = raw.decode("utf-8-sig")
    suffix = source.suffix.lower()
    position = None
    if suffix in (".json", ".jsonl"):
        hits = 0
        for number, role, text in transcript_messages(content, suffix, citation.get("line", 1)):
            if quote in text and (expected_role is None or role == expected_role):
                hits += text.count(quote)
                position = number
    elif expected_role == "user":
        # Quotations in a historical Q&A are evidence only after the operator
        # verifies their provenance and meaning in the actual conversation.
        hits = user_quotes_in_markdown(content, quote)
    else:
        hits = content.count(quote)
    if hits != 1:
        raise ValueError("原范围或实际用户原话无法唯一回查，请定位原消息或原问答行")
    return source.resolve(), position


def evaluate(request, directory, result):
    if not isinstance(request, dict):
        raise ValueError("请求应为 JSON 对象")
    result.update({key: request.get(key) for key in ("task", "module", "scope")})
    if not label(result["task"]) or not label(result["module"]):
        raise ValueError("请定位当前任务与模块")
    outline = request.get("outline")
    if not isinstance(outline, dict):
        raise ValueError("缺少当前模块的大纲，请核对资料并展示大纲")
    if outline.get("module") != result["module"]:
        raise ValueError("大纲与当前模块不符")
    branches = paths(outline.get("branches"), "大纲缺少具体业务分支")
    scope = paths(result["scope"], "缺少当前拟写的具体业务范围")
    if not scope.issubset(branches):
        raise ValueError("拟写范围含当前模块大纲以外的分支")
    encoded = json.dumps(outline, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    result["version"] = digest(encoded.encode("utf-8"))
    if not label(request.get("decision")):
        raise ValueError("等待用户明确采用或确认当前版本的大纲")
    decision_path = directory / request["decision"]
    decision_bytes = decision_path.read_bytes()
    decision = json.loads(decision_bytes.decode("utf-8-sig"))
    if not isinstance(decision, dict) or decision.get("task") != result["task"]:
        raise ValueError("采用记录与当前任务不符")
    if decision.get("outline") != outline:
        raise ValueError("采用记录与当前模块或大纲版本不符")
    if decision.get("kind") not in ("adopt", "confirm"):
        raise ValueError("缺少用户明确采用或确认的决定")
    evidence = decision.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("缺少原大纲和实际用户采用或确认依据")
    for pair in evidence:
        if not isinstance(pair, dict):
            raise ValueError("请配对原大纲与实际用户答复")
        display_role = "assistant" if decision["kind"] == "confirm" else None
        basis_file, shown = check_citation(pair.get("basis"), decision_path.parent, display_role)
        reply_file, answered = check_citation(pair.get("reply"), decision_path.parent, "user")
        if (decision["kind"] == "confirm" and basis_file == reply_file
                and shown is not None and answered <= shown):
            raise ValueError("确认须来自展示本次大纲后收到的用户答复")
    # Wording may be normalized by the operator, but each source label must
    # remain independently retrievable in the versioned outline/question.
    basis = ["".join(pair["basis"]["quote"].split()).casefold() for pair in evidence]
    names = {name for branch in branches for name in branch}
    aliases = decision.get("source_labels", {})
    if not isinstance(aliases, dict) or not aliases.keys() <= names:
        raise ValueError("原文名称对照与当前大纲分支不符")
    for name in sorted(names):
        original = aliases.get(name, name)
        if not label(original) or not any("".join(original.split()).casefold() in text for text in basis):
            raise ValueError("原大纲或原问题中找不到业务分支：" + name)
    result.update(status="allow", kind=decision["kind"], decision_sha256=digest(decision_bytes))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    args = parser.parse_args()
    result = {"status": "block"}
    try:
        evaluate(read_json(args.request), args.request.parent, result)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result["reason"] = str(exc)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "allow" else 1


if __name__ == "__main__":
    sys.exit(main())
