from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.resource import Resource, ResourceStatus, ResourcePriority
from ..schemas.resource import ResourceCreate, ResourceUpdate, Resource as ResourceSchema, ResourceResponse
from ..services.resource_service import ResourceService
import logging
from datetime import datetime

router = APIRouter(prefix="/resources", tags=["resources"])
logger = logging.getLogger(__name__)

@router.post("", response_model=ResourceResponse)
async def create_resource(
    resource: ResourceCreate,
    db: Session = Depends(get_db)
):
    """
    创建新的资源
    """
    try:
        db_resource = Resource(**resource.dict())
        db.add(db_resource)
        db.commit()
        db.refresh(db_resource)
        
        return ResourceResponse(
            success=True,
            message="Resource created successfully",
            data=db_resource
        )
    except Exception as e:
        logger.error(f"Error creating resource: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[ResourceSchema])
async def get_resources(
    script_id: Optional[int] = None,
    status: Optional[ResourceStatus] = None,
    priority: Optional[ResourcePriority] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取资源列表，支持多种过滤条件
    """
    query = db.query(Resource)
    
    if script_id:
        query = query.filter(Resource.script_id == script_id)
    if status:
        query = query.filter(Resource.status == status)
    if priority:
        query = query.filter(Resource.priority == priority)
    if type:
        query = query.filter(Resource.type == type)
        
    return query.all()

@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: int,
    db: Session = Depends(get_db)
):
    """
    获取单个资源的详细信息
    """
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
        
    return ResourceResponse(
        success=True,
        message="Resource retrieved successfully",
        data=resource
    )

@router.put("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: int,
    resource_update: ResourceUpdate,
    db: Session = Depends(get_db)
):
    """
    更新资源信息
    """
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # 只更新提供的字段
    update_data = resource_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_resource, field, value)
    
    try:
        db.commit()
        db.refresh(db_resource)
        return ResourceResponse(
            success=True,
            message="Resource updated successfully",
            data=db_resource
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating resource: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{resource_id}", response_model=ResourceResponse)
async def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db)
):
    """
    删除资源
    """
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    try:
        db.delete(resource)
        db.commit()
        return ResourceResponse(
            success=True,
            message="Resource deleted successfully",
            data=None
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting resource: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{resource_id}/status", response_model=ResourceResponse)
async def update_resource_status(
    resource_id: int,
    status: ResourceStatus,
    db: Session = Depends(get_db)
):
    """
    更新资源状态
    """
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    try:
        resource.status = status
        db.commit()
        db.refresh(resource)
        return ResourceResponse(
            success=True,
            message=f"Resource status updated to {status}",
            data=resource
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating resource status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export")
async def export_resources(
    format: str = Query("xlsx", regex="^(xlsx|csv)$"),
    script_id: Optional[int] = None,
    status: Optional[ResourceStatus] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    导出资源列表为Excel或CSV文件
    """
    try:
        resource_service = ResourceService()
        output = resource_service.export_resources(
            db=db,
            script_id=script_id,
            status=status,
            resource_type=type,
            format=format
        )
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resources_{timestamp}.{format}"
        
        # 设置正确的媒体类型
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if format == "xlsx" else "text/csv"
        
        # 返回文件流
        return StreamingResponse(
            output,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting resources: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_resource_statistics(
    script_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取资源统计信息
    """
    try:
        resource_service = ResourceService()
        statistics = resource_service.get_resource_statistics(db, script_id)
        return {
            "success": True,
            "message": "Statistics retrieved successfully",
            "data": statistics
        }
    except Exception as e:
        logger.error(f"Error getting resource statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/export")
async def export_resource_statistics(
    format: str = Query("xlsx", regex="^(xlsx|csv)$"),
    script_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    导出资源统计报告
    """
    try:
        resource_service = ResourceService()
        output = resource_service.export_statistics(
            db=db,
            script_id=script_id,
            format=format
        )
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resource_statistics_{timestamp}.{format}"
        
        # 设置正确的媒体类型
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if format == "xlsx" else "text/csv"
        
        # 返回文件流
        return StreamingResponse(
            output,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting resource statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 