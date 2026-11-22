"""Read single-column local session files without echoing credentials."""
from pathlib import Path


def read_column(path, header):
    try:
        with Path(path).open(encoding="utf-8-sig") as stream:
            rows = [line.removesuffix("\n") for line in stream]
    except (OSError, UnicodeError):
        rows = []
    if (rows[:1] != [header] or len(rows) < 2 or
            any(not row.strip() or any(ord(ch) < 32 or ord(ch) == 127 or ch in "\u0085\u2028\u2029" for ch in row)
                for row in rows[1:])):
        raise ValueError(f"需要有效的单列 {header} 文件，每个账号一行。")
    if any("${" in row for row in rows[1:]):
        raise ValueError("账号输入含 JMeter 表达式，请提供字面值。")
    if header == "cookie" and any("=" not in row for row in rows[1:]):
        raise ValueError("每行需要完整 Cookie。")
    return rows[1:]
