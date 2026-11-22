"""Parse a batch of browser cURLs as data. No command execution."""
from dataclasses import dataclass
import re
import shlex
from urllib.parse import unquote_plus, urlsplit, urlunsplit


@dataclass
class Target:
    titles: list
    method: str
    url: str
    headers: list
    body: str | None
    encoding: str = "UTF-8"
    follow: bool = False
    raw_url: str = ""
    captured_session: str = ""


class BatchError(ValueError):
    pass


def cmd_words(command):
    # Chrome cmd uses ^" for delimiters and ^\" or ^\^" for literal quotes.
    words, word, quoted, started = [], [], False, False
    i = 0
    while i < len(command):
        c = command[i]
        if command.startswith(('^\\^"', '^\\"', '\\"'), i):
            width = 4 if command.startswith('^\\^"', i) else (3 if c == '^' else 2)
            word.append('"')
            i += width
        elif command.startswith('^"', i) or c == '"':
            quoted = not quoted
            i += 2 if c == '^' else 1
        elif c == '^':
            if i + 1 == len(command):
                raise ValueError("cmd 转义不完整")
            word.append(command[i + 1])
            i += 2
        elif c.isspace() and not quoted:
            if started:
                words.append(''.join(word))
            word, started = [], False
            i += 1
            continue
        else:
            word.append(c)
            i += 1
        started = True
    if quoted:
        raise ValueError("cmd 引号不完整")
    if started:
        words.append(''.join(word))
    return words


def bash_words(command):
    # Replace ANSI-C literals with safely quoted text before POSIX tokenization.
    output = []
    i = 0
    quote = None
    escapes = {"n": "\n", "r": "\r", "t": "\t", "'": "'", '"': '"', "\\": "\\"}
    while i < len(command):
        ch = command[i]
        if quote is None and command.startswith("$'", i):
            value = []
            i += 2
            while i < len(command) and command[i] != "'":
                if command[i] == "\\":
                    i += 1
                    if i >= len(command) or command[i] not in escapes:
                        raise ValueError("请提供明确的正文转义")
                    value.append(escapes[command[i]])
                else:
                    value.append(command[i])
                i += 1
            if i == len(command):
                raise ValueError("正文引号不完整")
            output.append(shlex.quote("".join(value)))
        elif ch == "\\" and quote != "'" and i + 1 < len(command):
            output.append(command[i:i + 2])
            i += 1
        else:
            output.append(ch)
            if ch in ("'", '"') and quote in (None, ch):
                quote = None if quote else ch
        i += 1
    return shlex.split("".join(output))


def parse_one(command, title):
    if any(x in command for x in ("\x00", "\x01", chr(36)+"{", "$(", chr(96))):
        raise ValueError("需要静态文本，不能使用动态表达式")
    cmd = '^"' in command or (command.startswith("curl.exe ") and "'" not in command)
    words = (cmd_words(command) if cmd else bash_words(command))[1:]
    if any("${" in word for word in [title, *words]):
        raise ValueError("请求包含 JMeter 表达式，请提供字面值")
    tokens = iter(words)
    url, method, body, headers, follow = None, None, None, [], False
    encoding = "UTF-8"
    captured_session = ""
    for arg in tokens:
        if arg in ("-L", "--location"):
            follow = True
        elif arg == "--compressed":
            continue
        elif arg.startswith(("https://", "http://")) and url is None:
            url = arg
        elif arg in ("-X","--request","-H","--header","-d","--data","--data-raw","-b","--cookie","--url"):
            value = next(tokens, None)
            if value is None:
                raise ValueError("选项缺少值")
            if arg in ("-b","--cookie"):
                if captured_session or any(ord(c)<32 for c in value):
                    raise ValueError("请提供唯一完整 Cookie")
                captured_session = value
                if "=" not in value:
                    raise ValueError("请提供完整的本地 Cookie 行")
            elif arg in ("-X","--request"):
                method = value
            elif arg == "--url":
                if url:
                    raise ValueError("每条 cURL 需要唯一地址")
                url = value
            elif arg in ("-H","--header"):
                key, sep, val = value.partition(":")
                name = key.lower()
                if not sep or not re.fullmatch(r"[A-Za-z0-9!#$%&'*+.^_|~-]+",key):
                    raise ValueError("需要完整的请求头")
                if re.search(r"authorization|api[-_]?key|token|secret|signature|credential|session|^x-sign$",name):
                    raise ValueError("需要本地凭据引用或静态签名约定")
                if re.search(r"[\r\n]", val):
                    raise ValueError("请求头含非法换行")
                if name != "cookie" and re.search(
                    r"(?:[?&#;]|^)\s*[^?&#;=]*(?:token|secret|password|api[-_]?key|signature|credential|session)[^?&#;=]*=|://[^/\s]*@",
                    unquote_plus(val), re.I
                ):
                    raise ValueError("请求头包含凭据，需要脱敏地址")
                if name not in ("cookie","content-length","host"):
                    headers.append((key,val.lstrip()))
                if name == "cookie":
                    if captured_session:
                        raise ValueError("请提供唯一完整 Cookie")
                    captured_session = val.lstrip()
                if name == "content-type":
                    if re.search("multipart/|octet-stream", val, re.I):
                        raise ValueError("需提供可重放的文本正文")
                    match = re.search(r'charset\s*=\s*"?([\w.-]+)', val, re.I)
                    if match:
                        encoding = match[1]
            else:
                if body is not None or (arg != "--data-raw" and value.startswith("@")):
                    raise ValueError("请提供完整的单段内联文本正文")
                body = value
        else:
            raise ValueError("上传、二进制或未识别选项，需提供完整静态文本请求")
    parts = urlsplit(url or "")
    if parts.scheme not in ("http","https") or not parts.hostname or parts.username is not None or parts.password is not None:
        raise ValueError("需要明确的 HTTP(S) 地址")
    if parts.port == 0:
        raise ValueError("端口无效")
    if follow and method and method not in ("GET", "HEAD"):
        raise ValueError("显式方法与跳转组合需要确认各跳的方法和正文，请提供最终目标的完整 cURL")
    method = method or ("POST" if body is not None else "GET")
    if method not in ("GET","POST","PUT","PATCH","DELETE","HEAD","OPTIONS") or (body is not None and method in ("GET","HEAD","OPTIONS")):
        raise ValueError("请确认方法及正文传输方式")
    if body is not None:
        try:
            body.encode(encoding)
        except (LookupError, UnicodeError):
            raise ValueError("正文编码无效") from None
        if not any(k.lower()=="content-type" for k,v in headers):
            headers.append(("Content-Type","application/x-www-form-urlencoded"))
    query = []
    for item in parts.query.split("&"):
        key = unquote_plus(item.partition("=")[0]).lower()
        if key == "ctoken":
            continue
        elif re.search(r"signature|^sign$|token|secret|password|api[-_]?key",key):
            raise ValueError("查询串凭据或动态签名需另行提供本地引用")
        else:
            query.append(item)
    clean = urlunsplit(parts._replace(query="&".join(query),fragment=""))
    identity = method, parts._replace(fragment=""), tuple(sorted(((k.lower(),v) for k,v in headers), key=lambda pair: pair[0])),body, encoding.lower(),follow
    return (*identity, captured_session), Target([title],method,clean,headers,body,encoding,follow,parts._replace(fragment="").geturl(),captured_session)


def parse_requests(text):
    # Rich-text export escapes Markdown punctuation and encodes leading spaces.
    if re.search(r"(?m)^&#x20; ", text):
        text = re.sub(r"(?m)^&#x20; ", " ", text)
        text = re.sub(r"\\([\\:.\-])", r"\1", text)
        text = text.replace("^\\\n", "^\n").replace("^\\\r\n", "^\r\n")
        text = re.sub(r"\[(https?://[^]\s]+)\]\((https?://[^)\s]+)\)",
                      lambda m: m[1] if m[1] == m[2] else m[0], text)
    targets, errors, links = {}, [], []
    title = None
    for number, raw in enumerate(re.sub(r"[\\^]\r?\n","",text).splitlines(),1):
        line = raw.strip()
        if not line or line.startswith(chr(96)*3):
            continue
        if line.startswith("|"):
            cells = [x.strip().strip(chr(96)) for x in line.strip("|").split("|")]
            if all(re.fullmatch("[-: ]+",x) for x in cells) or cells[-1].lower() in ("curl","请求","链接"):
                continue
            if len(cells) != 2:
                errors.append(f"第 {number} 行：请将表格行重贴为标题和完整 cURL")
                continue
            title,line = cells
        link = re.fullmatch(r"\[([^]]+)\]\((https?://[^)]+)\)",line)
        if link or line.startswith(("https://","http://")):
            links.append((link[1] if link else title or f"第 {number} 行", link[2] if link else line))
            title = None
        elif re.match(r"curl(?:\.exe)?\s",line):
            label = title or f"第 {number} 行"
            try:
                key, target = parse_one(line,label)
                if key in targets:
                    if label not in targets[key].titles:
                        targets[key].titles.append(label)
                else:
                    targets[key] = target
            except (ValueError,UnicodeError) as error:
                message = str(error) if type(error) is ValueError and not str(error).isascii() and not str(error).startswith("Port") else "请核对参数、引号及地址"
                errors.append(f"{label}：{message}")
            title = None
        elif len(line) < 100 and not any(c in line for c in ("=","://"," -","@")):
            if title:
                errors.append(f"{title}：需要完整 cURL")
            title = re.sub(r"^[0-9]+、\s*", "", line.lstrip("# ").rstrip("：:"))
        else:
            errors.append(f"第 {number} 行：需要完整浏览器 cURL")
    if title:
        errors.append(f"{title}：需要完整 cURL")
    for label,url in links:
        matches = [target for key,target in targets.items() if key[1].geturl()==url]
        if len(matches) == 1:
            if label not in matches[0].titles:
                matches[0].titles.append(label)
        else:
            errors.append(f"{label}：链接需对应唯一完整 cURL，请补贴该项")
    if any("${" in name for target in targets.values() for name in target.titles):
        errors.append("标题含 JMeter 表达式，请提供字面值")
    if errors or not targets:
        accepted = ["、".join(t.titles) for t in targets.values()]
        raise BatchError("\n".join(["未执行。已解析：" + ("；".join(accepted) or "无"), *(errors or ["需要完整 cURL"])]))
    return list(targets.values())
