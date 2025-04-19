from sqlalchemy import Column, Integer, String, Enum, Text, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class ResourceStatus(str, enum.Enum):
    PENDING = "pending"  # 待确认
    CONFIRMED = "confirmed"  # 已确认
    IN_PREPARATION = "in_preparation"  # 准备中
    READY = "ready"  # 已就绪
    COMPLETED = "completed"  # 已完成

class ResourcePriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    script_id = Column(Integer, ForeignKey("scripts.id"))
    
    # 基本信息
    name = Column(String, index=True)  # 资源名称
    type = Column(String)  # 资源类型（prop, location, costume等）
    description = Column(Text, nullable=True)  # 详细描述
    
    # 状态和优先级
    status = Column(Enum(ResourceStatus), default=ResourceStatus.PENDING)
    priority = Column(Enum(ResourcePriority), default=ResourcePriority.MEDIUM)
    
    # 管理信息
    estimated_budget = Column(Float, nullable=True)  # 预估预算
    actual_budget = Column(Float, nullable=True)  # 实际预算
    responsible_person = Column(String, nullable=True)  # 负责人
    notes = Column(Text, nullable=True)  # 备注
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    needed_by = Column(DateTime, nullable=True)  # 需要日期
    
    # 场景关联（可选）
    scene_number = Column(Integer, nullable=True)  # 首次出现的场景编号
    
    # 关联关系
    script = relationship("Script", back_populates="resources")

    class Config:
        orm_mode = True 