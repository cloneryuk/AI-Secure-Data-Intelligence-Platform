import re
import logging
from collections import Counter
from app.models.schemas import Finding
logger = logging.getLogger("ai_platform")
FAILED_LOGIN_PATTERN = re.compile(r"(?:failed|unauthorized|denied|invalid|401|403)",
    re.IGNORECASE,   
)
IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
DEBUG_PATTERN=re.compile(r"\bDEBUG\b",re.IGNORECASE)      

def analyze_log(content:str)->list[Finding]:
    findings=[]
    lines=content.splitlines()
    failed_count=0
    failed_lines=[]
    ip_counter=Counter()
    debug_lines=[]
    for line_num,line in enumerate(lines,start=1):
        if FAILED_LOGIN_PATTERN.search(line):
            failed_count+=1
            failed_lines.append(line_num)
        ip_matches=IP_PATTERN.findall(line)
        for ip in ip_matches:
            ip_counter[ip]+=1
        if DEBUG_PATTERN.search(line):
            debug_lines.append(line_num)
    if failed_count > 3:
        findings.append(Finding(
            type="brute_force_attempt",
            value=f"{failed_count} failed attempts detected",
            risk="high",
            line=failed_lines[0] if failed_lines else None,
        ))
    for ip, count in ip_counter.items():
        if count > 5:
            findings.append(Finding(
                type="suspicious_ip",
                value=f"{ip} appears {count} times",
                risk="high",
                line=None,
            ))
    if debug_lines:
        findings.append(Finding(
            type="debug_mode_leak",
            value=f"DEBUG entries on {len(debug_lines)} lines",
            risk="medium",
            line=debug_lines[0] if debug_lines else None,
        ))
    logger.info("Log analyzer found %d extra findings",len(findings))
    return findings        