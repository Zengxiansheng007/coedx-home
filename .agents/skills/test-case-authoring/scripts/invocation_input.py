"""Render a step's complete submitted value as a single copyable Markdown block."""
import json


def json_input(record):
    """Structured input is native JSON. A scalar JSON box can declare its format."""
    return 'value' in record and (isinstance(record['value'], (dict, list))
                                  or record.get('input_format') == 'json')


def input_label(record, step, records):
    """Use the box's business name, disambiguating repeated names in step order."""
    label = record.get('object_ref') or '输入参数'
    matches = [ref for ref in step.get('data_refs', []) if json_input(records[ref])
               and (records[ref].get('object_ref') or '输入参数') == label]
    return f'{label}（同名框 {matches.index(record["id"]) + 1}）' if len(matches) > 1 else str(label)


def json_block(value, indent=''):
    payload = json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2)
    # Five spaces after the child marker start an indented CommonMark code
    # block *inside* that item. Its only content is JSON; its parent owns the label.
    first, *rest = payload.split('\n')
    return [indent + '-     ' + first, *[indent + '      ' + line for line in rest]]
