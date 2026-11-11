{
  "skillRoot": "C:\\Users\\lenovo\\Documents\\ChatGPT\\ui-test\\work\\ask-test-20261111\\at02\\.agents\\skills\\ask-test",
  "frontmatter": {
    "name": "ask-test",
    "description": "测试编写顾问。Use only when the user explicitly invokes $ask-test or directly requests this skill. 提供只读材料核对、阶段与缺口判断及入口建议；普通答疑直接回答，咨询止于建议。"
  },
  "summary": {
    "P0": 0,
    "P1": 0,
    "P2": 1
  },
  "status": "validated-candidate",
  "acceptance": {
    "authority": "trusted-host-only",
    "verified": false
  },
  "findings": [
    {
      "severity": "P2",
      "rule": "description-trigger-wording",
      "file": "C:\\Users\\lenovo\\Documents\\ChatGPT\\ui-test\\work\\ask-test-20261111\\at02\\.agents\\skills\\ask-test\\SKILL.md",
      "message": "description lacks explicit trigger wording.",
      "fix": "Add 'Use when...' style trigger phrases."
    }
  ]
}
Exit code: 0
