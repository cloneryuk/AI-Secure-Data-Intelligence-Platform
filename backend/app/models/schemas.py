from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field

class AnalyzeOptions(BaseModel):
    mask: bool=Field(False,description="Replace detected secrets with [MASKED]")
    block_high_risk:bool=Field(False, description="Block response if risk is high/critical")
    log_analysis:bool=Field(True,description="Enable AI powered log analysis")

class AnalyzeRequest(BaseModel):
    input_type: str = Field(..., description="One of: text, file, sql, chat, log")
    content: str = Field(..., description="Raw content or base64-encoded file")
    options: AnalyzeOptions = Field(default_factory=AnalyzeOptions)

class Finding(BaseModel):
    type:str=Field(...,description="e.g. email, password, api_key")
    value: Optional[str]=Field(None, description="Matched value (omitted for critical)")
    risk: str=Field(...,description="low/medium/high/critical")
    line: Optional[int]=Field(None,description="1-based line number")

class AnalyzeResponse(BaseModel):
    summary: str
    content_type: str
    findings: list[Finding] = Field(default_factory=list)
    risk_score: int = Field(0)
    risk_level: str = Field("none")
    action: str = Field("allowed")
    masked_content: Optional[str] = Field(None, description="New masked copy, original preserved")
    insights: list[str] = Field(default_factory=list)