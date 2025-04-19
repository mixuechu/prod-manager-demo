from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base

class ScriptAnalysis(Base):
    __tablename__ = "script_analyses"

    id = Column(Integer, primary_key=True, index=True)
    script_id = Column(Integer, ForeignKey("scripts.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 角色分析
    character_analysis = Column(JSON, nullable=True)  # 存储角色详细信息，包括性格特征、关系网络等
    
    # 资源分析
    resource_analysis = Column(JSON, nullable=True)  # 存储各类资源的统计和详细信息
    
    # 场景分析
    scene_analysis = Column(JSON, nullable=True)  # 存储场景的统计信息和关键点
    
    # 错误信息
    error = Column(Text, nullable=True)
    
    # 关联关系
    script = relationship("Script", back_populates="analyses")

    class Config:
        orm_mode = True 