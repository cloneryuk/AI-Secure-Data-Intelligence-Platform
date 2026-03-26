import re
import logging
from typing import List,Optional
from app.models.schemas import Finding
logger=logging.getLogger("ai_platform")
PATTERNS=[
    (
        "email",
        re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z0-9-.]+"),
        "low",
        True,
    ),
    (
        "phone",
        re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}"),
        "low",
        True,
    ),
    (
        "api_key",
        re.compile(r"AKIA[0-9A-Z]{16}"),
        "high",
        False,
    ),   
    (
        "api_key",
        re.compile(r"(?:api[_-]?key|secret[_-]?key|access[_-]?token|sk-)"
        r"[\s=:\"']*([A-Za-z0-9\-_]{8,})",
        re.IGNORECASE,
        ),
        "high",
        False,
    ),
    (
        "password",
        re.compile(r"(?:password|passwd|pwd|pass)[\s=:\"']+(\S+)",
            re.IGNORECASE,
        ),
        "critical",
        False,
    ),
    (
        "token",
        re.compile(r"(?:bearer|token|authorization)[\s=:\"']+([A-Za-z0-9\-_.~+/]{20,})",
            re.IGNORECASE,
        ),
        "high",
        False,
    ),
    (
        "stack_trace",
        re.compile(r"(?:Exception|Error|Traceback|at\s+[\w$.]+\([\w]+\.java:\d+\))",
            re.IGNORECASE,
        ),
        "medium",
        True,
    ),
    (
        "ip_address",
        re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
        "low",
        True,
    ),
    (
        "credit_card",
        re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
        "critical",
        False,
    ),
    (
        "ssn",
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "critical",
        False,
    ),

]    

def scan_content(content: str) -> list[Finding]:
    findings = []
    seen = set()
    lines = content.splitlines()
    for line_num, line in enumerate(lines, start=1):
        for name, pattern, risk, show_value in PATTERNS:
            match=pattern.search(line)
            if match:
                key=(name,line_num)
                if key in seen:
                    continue
                seen.add(key)
                value = match.group(0) if show_value else None
                findings.append(Finding(
                    type=name,
                    value=value,
                    risk=risk,
                    line=line_num,
                ))
    logger.info("Scanner found %d findings across %d lines",len(findings),len(lines))
    return findings           