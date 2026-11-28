"""Render a step's complete submitted value as a single copyable Markdown block."""
import json


def json_input(record):
    """Structured input is native JSON. A scalar JSON box can declare its format."""
    return 'value' in record and (isinstance(record['value'], (dict, list))
                                  or record.get('input_format') == 'json')


def json_block(value, indent=''):
    payload = json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2)
    # Five spaces after the child marker start an indented CommonMark code
    # block *inside* that item. Its only content is JSON; its parent owns the label.
    first, *rest = payload.split('\n')
    return [indent + '-     ' + first, *[indent + '      ' + line for line in rest]]
