import re
import logging
from app.models.schemas import Finding, AnalyzeOptions

logger = logging.getLogger("ai_platform")


def apply_policy(
    content: str,
    findings: list[Finding],
    options: AnalyzeOptions,
) -> tuple[str, str | None]:
    """
    Apply policy based on options.
    Returns: (action, masked_content)
    """

    # Check if we should block
    if options.block_high_risk:
        has_high = any(f.risk in ("high", "critical") for f in findings)
        if has_high:
            logger.info("Policy: BLOCKED due to high/critical findings")
            return ("blocked", None)

    # Check if we should mask
    if options.mask and findings:
        masked = _mask_content(content, findings)
        logger.info("Policy: MASKED content generated")
        return ("masked", masked)

    # Default: allow
    logger.info("Policy: ALLOWED")
    return ("allowed", None)


def _mask_content(content: str, findings: list[Finding]) -> str:
    """
    Create a NEW copy of the content with sensitive values replaced by [MASKED].
    The original content string is never modified.
    """
    lines = content.splitlines()

    for f in findings:
        if f.line is None:
            continue
        
        idx = f.line - 1
        if idx < 0 or idx >= len(lines):
            continue

        if f.value:
            # Direct replacement if we stored the value
            lines[idx] = lines[idx].replace(f.value, "[MASKED]")
        else:
            # Pattern-based masking for secrets where value was hidden
            if f.type == "password":
                lines[idx] = re.sub(
                    r"((?:password|passwd|pwd|pass)[\s=:\"']+)\S+",
                    r"\1[MASKED]",
                    lines[idx],
                    flags=re.IGNORECASE,
                )
            elif f.type == "api_key":
                lines[idx] = re.sub(
                    r"((?:api[_-]?key|secret[_-]?key|access[_-]?token|sk-)[\s=:\"']*)[A-Za-z0-9\-_]{8,}",
                    r"\1[MASKED]",
                    lines[idx],
                    flags=re.IGNORECASE,
                )
            elif f.type == "credit_card":
                lines[idx] = re.sub(
                    r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
                    "[MASKED]",
                    lines[idx],
                )
            elif f.type == "ssn":
                lines[idx] = re.sub(
                    r"\b\d{3}-\d{2}-\d{4}\b",
                    "[MASKED]",
                    lines[idx],
                )
            elif f.type == "token":
                lines[idx] = re.sub(
                    r"((?:bearer|token|authorization)[\s=:\"']+)[A-Za-z0-9\-_.~+/]{20,}",
                    r"\1[MASKED]",
                    lines[idx],
                    flags=re.IGNORECASE,
                )

    return "\n".join(lines)
