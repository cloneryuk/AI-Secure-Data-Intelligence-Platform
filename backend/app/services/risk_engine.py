import logging
from app.models.schemas import Finding
logger = logging.getLogger("ai_platform")
RISK_POINTS ={
    "critical": 7,
    "high": 4,
    "medium": 2,
    "low": 1,
}
def compute_risk(findings: list[Finding]) -> tuple[int, str]:
    if not findings:
        return (0, "none")
    total=0
    for f in findings:
        if f.type == "stack_trace":
            continue # Stack trace doesn't add to numeric score in the spec
        total+=RISK_POINTS.get(f.risk,1)
        
    if total>=15:
        level="critical"
    elif total>=10:
        level="high"
    elif total>=5:
        level="medium"
    else:
        level = "low"
    logger.info("Risk score=%d, level=%s", total, level)
    return (total, level)