from pathlib import Path
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET
from test_v162 import parse_requests
from plan import generate

with TemporaryDirectory() as tmp:
    plan = Path(tmp) / 'plan.jmx'
    generate(parse_requests("查指南\ncurl 'http://localhost:1234/query?p=1'"), plan)
    tree = ET.parse(plan)
    assert tree.find('.//HTTPSamplerProxy').get('testname') == '查指南 [T01]'
    assert len(tree.findall('.//ResponseAssertion')) == 3
    assert not tree.findall('.//JSR223Sampler')
    assert len(tree.findall(".//ResultCollector[@enabled='false']")) == 3
