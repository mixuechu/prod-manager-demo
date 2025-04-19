from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
from ..services.statistics_service import StatisticsService
from ..core.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/statistics", tags=["statistics"])
statistics_service = StatisticsService()

@router.get("/scripts/{script_id}")
async def get_script_statistics(
    script_id: int,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Get comprehensive statistics for a script.
    """
    try:
        return await statistics_service.get_script_statistics(script_id)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate statistics: {str(e)}"
        )

@router.get("/scripts/{script_id}/scenes")
async def get_scene_statistics(
    script_id: int,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Get scene-related statistics for a script.
    """
    try:
        stats = await statistics_service.get_script_statistics(script_id)
        return stats["scene_statistics"]
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate scene statistics: {str(e)}"
        )

@router.get("/scripts/{script_id}/characters")
async def get_character_statistics(
    script_id: int,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Get character-related statistics for a script.
    """
    try:
        stats = await statistics_service.get_script_statistics(script_id)
        return stats["character_statistics"]
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate character statistics: {str(e)}"
        )

@router.get("/scripts/{script_id}/resources")
async def get_resource_statistics(
    script_id: int,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Get resource-related statistics for a script.
    """
    try:
        stats = await statistics_service.get_script_statistics(script_id)
        return stats["resource_statistics"]
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate resource statistics: {str(e)}"
        )

@router.get("/scripts/{script_id}/timeline")
async def get_timeline_statistics(
    script_id: int,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """
    Get timeline-related statistics for a script.
    """
    try:
        stats = await statistics_service.get_script_statistics(script_id)
        return stats["timeline_statistics"]
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate timeline statistics: {str(e)}"
        ) 