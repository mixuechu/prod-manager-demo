from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class AnalysisBase(BaseModel):
    character_analysis: Optional[Dict[str, Any]] = None
    resource_analysis: Optional[Dict[str, Any]] = None
    scene_analysis: Optional[Dict[str, Any]] = None

class AnalysisCreate(AnalysisBase):
    script_id: int

class Analysis(AnalysisBase):
    id: int
    script_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class AnalysisResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Analysis] = None 