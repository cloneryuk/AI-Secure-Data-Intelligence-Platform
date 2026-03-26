import os
import re
import logging
from app.models.schemas import Finding
logger = logging.getLogger("ai_platform")

def _redact_secrets(content: str, findings: list[Finding]) -> str:
    lines = content.splitlines()
    for f in findings:
        if f.risk in ("high", "critical") and f.line is not None:
            idx = f.line - 1
            if 0 <= idx < len(lines):
                tag = f"[REDACTED_{f.type.upper()}]"
                if f.value:
                    lines[idx] = lines[idx].replace(f.value, tag)
                else:
                    if f.type == "password":
                        lines[idx] = re.sub(r"((?:password|passwd|pwd|pass)[\s=:\"']+)\S+",
                        r"\1" + tag,
                        lines[idx],
                        flags=re.IGNORECASE,
                        )
                    elif f.type == "api_key":
                        lines[idx] = re.sub(r"((?:api[_-]?key|secret[_-]?key|access[_-]?token|sk-)[\s=:\"']+)[A-Za-z0-9\-_]{8,}",
                        r"\1" + tag,
                        lines[idx],
                        flags=re.IGNORECASE,
                        )
    return "\n".join(lines)

def _local_heuristic_insights(findings: list[Finding]) -> list[str]:
    insights = []
    types_found = {f.type for f in findings}
    if "password" in types_found:
        insights.append("Sensitive credentials exposed")
    if "stack_trace" in types_found:
        insights.append("Stack trace reveals internal system details")
    if "brute_force_attempt" in types_found:
        insights.append("Multiple failed login attempts detected — possible brute-force attack")
    if "suspicious_ip" in types_found:
        insights.append("Suspicious IP activity — repeated access from same source")
    if "debug_mode_leak" in types_found:
        insights.append("Debug mode enabled in production — information leakage risk")
    if "credit_card" in types_found:
        insights.append("Credit card numbers detected — critical PCI compliance violation")
    if "token" in types_found:
        insights.append("Authentication tokens exposed in logs")
    if not insights:
        insights.append("No significant security issues detected")
    return insights
async def generate_ai_insights(content: str, findings: list[Finding]) -> list[str]:
    redacted_content = _redact_secrets(content, findings)
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        logger.info("No OPENAI_API_KEY set — using local heuristic insights")
        return _local_heuristic_insights(findings)
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key)
        prompt = f"LOGS:\n{redacted_content[:4000]}"
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a security analyst. Provide 3-5 bullet points about the security posture of the following logs."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.3,
        )
        raw = response.choices[0].message.content or ""
        insights = [
            line.lstrip("-").strip()
            for line in raw.splitlines()
            if line.strip().startswith("-")
        ]
        if not insights:
            insights = [raw.strip()]
        logger.info("OpenAI returned %d insights", len(insights))
        return insights
    except Exception as e:
        logger.error("OpenAI call failed: %s — falling back to heuristics", e)
        return _local_heuristic_insights(findings)






    
    
