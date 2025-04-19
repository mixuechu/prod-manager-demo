from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from ..core.database import get_db
from ..models.models import Project, Script, ProjectUser, UserRole
from ..services.project_manager import ProjectManager

router = APIRouter(prefix="/projects", tags=["projects"])

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    """
    创建新项目
    """
    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/", response_model=List[ProjectResponse])
def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    获取项目列表，支持分页
    """
    projects = db.query(Project).offset(skip).limit(limit).all()
    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    获取项目详情
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """
    更新项目信息
    """
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    for key, value in project_update.model_dump(exclude_unset=True).items():
        setattr(db_project, key, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    删除项目
    """
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    db.delete(db_project)
    db.commit()
    return {"message": "项目已删除"}

# 项目脚本管理
class ScriptAssignment(BaseModel):
    script_id: int

@router.post("/{project_id}/scripts")
def assign_script_to_project(
    project_id: int,
    script_assignment: ScriptAssignment,
    db: Session = Depends(get_db)
):
    """
    将脚本分配到项目
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    script = db.query(Script).filter(Script.id == script_assignment.script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="脚本不存在")
    
    script.project_id = project_id
    db.commit()
    return {"message": "脚本已分配到项目"}

@router.get("/{project_id}/scripts", response_model=List[dict])
def get_project_scripts(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    获取项目下的所有脚本
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    scripts = db.query(Script).filter(Script.project_id == project_id).all()
    return [
        {
            "id": script.id,
            "filename": script.filename,
            "status": script.status,
            "created_at": script.created_at,
            "updated_at": script.updated_at,
            "metadata": script.metadata
        }
        for script in scripts
    ]

# 项目进度管理
class ProjectProgress(BaseModel):
    current_scene: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

@router.post("/{project_id}/progress")
def update_project_progress(
    project_id: int,
    progress: ProjectProgress,
    db: Session = Depends(get_db)
):
    """
    更新项目进度
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 更新项目元数据中的进度信息
    if not project.metadata:
        project.metadata = {}
    
    project.metadata["progress"] = progress.model_dump()
    project.updated_at = datetime.utcnow()
    
    db.commit()
    return {"message": "项目进度已更新"}

@router.get("/{project_id}/progress")
def get_project_progress(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    获取项目进度
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    return project.metadata.get("progress", {}) if project.metadata else {}

# 项目分析和管理
@router.get("/{project_id}/overview")
def get_project_overview(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    获取项目概览信息
    """
    try:
        manager = ProjectManager(project_id)
        return manager.get_project_overview()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}/resources")
def get_project_resources(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    获取项目资源需求
    """
    try:
        manager = ProjectManager(project_id)
        return manager.get_resource_requirements()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}/schedule")
def get_project_schedule(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    获取项目拍摄计划建议
    """
    try:
        manager = ProjectManager(project_id)
        return manager.get_shooting_schedule()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 