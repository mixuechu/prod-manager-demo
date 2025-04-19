from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from ..models.resource import ResourceStatus, ResourcePriority

class ResourceBase(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    status: ResourceStatus = ResourceStatus.PENDING
    priority: ResourcePriority = ResourcePriority.MEDIUM
    estimated_budget: Optional[float] = None
    actual_budget: Optional[float] = None
    responsible_person: Optional[str] = None
    notes: Optional[str] = None
    needed_by: Optional[datetime] = None
    scene_number: Optional[int] = None

class ResourceCreate(ResourceBase):
    script_id: int

class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ResourceStatus] = None
    priority: Optional[ResourcePriority] = None
    estimated_budget: Optional[float] = None
    actual_budget: Optional[float] = None
    responsible_person: Optional[str] = None
    notes: Optional[str] = None
    needed_by: Optional[datetime] = None
    scene_number: Optional[int] = None

class Resource(ResourceBase):
    id: int
    script_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ResourceResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Resource] = None 