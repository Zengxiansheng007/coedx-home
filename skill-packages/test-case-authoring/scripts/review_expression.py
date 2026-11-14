"""Conservative human projection; semantic authoring remains an Agent decision."""


def title(case):
    return str(case.get('priority', '待核对')) + ' ' + case.get('title', '待核对')  # Priority is presentation, never identity.


def unique_checks(expected, checks):
    return list(dict.fromkeys(check for check in checks if check not in expected))  # Only exact projected meaning is mechanically removable.
