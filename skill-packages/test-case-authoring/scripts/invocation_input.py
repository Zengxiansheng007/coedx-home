"""Render a step's complete submitted value as a single copyable Markdown block."""
import json


def json_input(record):
    """Structured input is native JSON. A scalar JSON box can declare its format."""
    return 'value' in record and (isinstance(record['value'], (dict, list))
                                  or record.get('input_format') == 'json')


def json_block(value, indent=''):
    payload = json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2)
    # XMind may preserve Markdown fences as literal clipboard text. An indented
    # CommonMark code block consists solely of JSON, including under a list item.
    return ['', *[indent + '    ' + line for line in payload.split('\n')]]
