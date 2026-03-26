import os 
import logging 
import base64
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.models.schemas import AnalyzeRequest, AnalyzeResponse, AnalyzeOptions
from app.services.extractor import extract_text 
from app.services.scanner import scan_content
from app.services.log_analyzer import analyze_log
from app.services.ai_analyzer import generate_ai_insights
from app.services.risk_engine import compute_risk
from app.services.policy_engine import apply_policy

logger = logging.getLogger("ai_platform")
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 52_428_800))

@router.post("/analyze", response_model=AnalyzeResponse)
@limiter.limit("30/minute")
async def analyze(request: Request, body: AnalyzeRequest):
    content = body.content
    input_type = body.input_type.lower()
    options = body.options
    if len(content.encode("utf-8")) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="PayLoad too large")
    if input_type == "file":
        try:
            content = base64.b64decode(content).decode("utf-8", errors="replace")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 content")
    return await _run_pipeline(content, input_type, options)

@router.post("/analyze/upload", response_model=AnalyzeResponse)
@limiter.limit("20/minute")
async def analyze_upload(
    request: Request,
    file: UploadFile = File(...),
    mask: bool = Form(False),
    block_high_risk: bool = Form(False),
    log_analysis: bool = Form(True),
):
    raw_bytes = await file.read()
    if len(raw_bytes) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    if ext in (".log",):
        input_type = "log"
    elif ext in (".pdf", ".docx", ".doc"):
        input_type = "file"
    else:
        input_type = "text"
    content = extract_text(raw_bytes, ext)
    options = AnalyzeOptions(mask=mask, block_high_risk=block_high_risk, log_analysis=log_analysis)
    return await _run_pipeline(content, input_type, options)

async def _run_pipeline(content: str, input_type: str, options: AnalyzeOptions) -> AnalyzeResponse:
    finding = scan_content(content)
    if input_type == "log" or options.log_analysis:
        log_findings = analyze_log(content)
        finding.extend(log_findings)
    insights = []
    if options.log_analysis:
        insights = await generate_ai_insights(content, finding)
    
    risk_score, risk_level = compute_risk(finding)
    action, masked_content = apply_policy(content, finding, options)
    content_type = "log" if input_type == "log" else input_type

    types_found = {f.type for f in finding}
    if "password" in types_found and "stack_trace" in types_found:
        summary = "Log contains sensitive credentials and system errors"
    elif finding:
        summary = f"Detected: {', '.join(types_found)}. Risk: {risk_level}."
    else:
        summary = "No sensitive data detected"
        

    returned_findings = [f for f in finding if f.type != "stack_trace"]

    return AnalyzeResponse(
        summary=summary,
        content_type=content_type,
        findings=returned_findings,
        risk_score=risk_score,
        risk_level=risk_level,
        action=action,
        masked_content=masked_content,
        insights=insights,
    )   