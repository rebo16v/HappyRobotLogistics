from pydantic import BaseModel
from typing import Dict, Any, Optional


class ErrorResponse(BaseModel):
    error: Dict[str, str]


class LoadResponse(BaseModel):
    loads: Dict[str, str]


class ResponseModel(BaseModel):
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, str]] = None
