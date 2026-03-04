"""
Approvals Pydantic schemas.
"""

from datetime import datetime
from pydantic import BaseModel


class ApprovalRequestResponse(BaseModel):
    id: str
    action_type: str
    target_resource_type: str
    target_resource_id: str
    description: str
    preview_json: str
    status: str
    idempotency_key: str
    approved_at: datetime | None
    rejected_at: datetime | None
    executed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CreateApprovalRequest(BaseModel):
    action_type: str
    target_resource_type: str
    target_resource_id: str
    description: str = ""
    preview_json: str = "{}"


class ApprovalDecision(BaseModel):
    decision: str  # approve | reject
