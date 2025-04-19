from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..models.models import Script, ScriptStatus, ScriptAnalysis
from ..services.script_parser import parse_script, ScriptParser
from ..services.ai_generator import AIGenerator, AIGenerationError
from ..services.script_service import ScriptService, ScriptParsingError
from ..core.auth import get_current_user
from ..models.user import User
from ..schemas.analysis import AnalysisResponse, Analysis
from ..services.ai_analysis import AIAnalysisService
from ..services.resource_service import ResourceService
import json
import logging

router = APIRouter(prefix="/scripts", tags=["scripts"])
script_service = ScriptService()
ai_generator = AIGenerator()
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_script(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user)
) -> Script:
    """
    Upload a new script file and trigger parsing.
    """
    # Validate file type
    if not file.filename.endswith(('.txt', '.md')):
        raise HTTPException(
            status_code=400,
            detail="Only .txt and .md files are supported"
        )

    try:
        # Read file content
        content = await file.read()
        
        # Save file
        file_path = await script_service.save_uploaded_file(content, file.filename)
        
        # Create script record
        script = await script_service.create_script(
            file_path=file_path,
            original_filename=file.filename,
            user_id=current_user.id
        )

        # Trigger parsing in background
        if background_tasks:
            background_tasks.add_task(script_service.parse_script, script.id)

        return script

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process script: {str(e)}"
        )

@router.post("/{script_id}/analyze", response_model=AnalysisResponse)
async def analyze_script(
    script_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    触发脚本分析。这是一个异步操作，分析会在后台进行。
    """
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")

    # 创建新的分析记录
    analysis = ScriptAnalysis(script_id=script_id)
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # 在后台执行分析
    background_tasks.add_task(
        perform_analysis,
        script_id=script_id,
        analysis_id=analysis.id,
        db=db
    )

    return AnalysisResponse(
        success=True,
        message="Analysis started",
        data=analysis
    )

@router.get("/{script_id}/analysis", response_model=List[Analysis])
async def get_script_analyses(
    script_id: int,
    db: Session = Depends(get_db)
):
    """
    获取脚本的所有分析结果
    """
    analyses = db.query(ScriptAnalysis).filter(
        ScriptAnalysis.script_id == script_id
    ).all()
    
    if not analyses:
        raise HTTPException(status_code=404, detail="No analyses found for this script")
    
    return analyses

@router.get("/{script_id}/analysis/latest", response_model=Analysis)
async def get_latest_analysis(
    script_id: int,
    db: Session = Depends(get_db)
):
    """
    获取脚本的最新分析结果
    """
    analysis = db.query(ScriptAnalysis).filter(
        ScriptAnalysis.script_id == script_id
    ).order_by(ScriptAnalysis.created_at.desc()).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis found for this script")
    
    return analysis

@router.post("/{script_id}/parse")
async def trigger_parsing(
    script_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Manually trigger parsing for a script.
    """
    try:
        background_tasks.add_task(script_service.parse_script, script_id)
        return {"message": "Parsing started"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start parsing: {str(e)}"
        )

@router.post("/{script_id}/generate")
async def trigger_ai_generation(
    script_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Trigger AI analysis generation for a script.
    """
    try:
        # Start AI generation in background
        background_tasks.add_task(ai_generator.generate_analysis, script_id)
        return {"message": "AI analysis generation started"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start AI analysis: {str(e)}"
        )

@router.get("/{script_id}/ai-analysis")
async def get_ai_analysis(
    script_id: int,
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Get the AI-generated analysis results for a script.
    """
    try:
        # Get the analysis results
        analysis_file = ai_generator.output_dir / f"script_{script_id}_analysis.json"
        if not analysis_file.exists():
            raise HTTPException(
                status_code=404,
                detail="AI analysis not found or not yet generated"
            )

        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis = json.loads(f.read())
        return analysis

    except AIGenerationError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve AI analysis: {str(e)}"
        )

@router.delete("/{script_id}")
async def delete_script(
    script_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a script and its associated files.
    """
    try:
        await script_service.delete_script(script_id)
        
        # Also delete AI analysis if it exists
        analysis_file = ai_generator.output_dir / f"script_{script_id}_analysis.json"
        if analysis_file.exists():
            analysis_file.unlink()
            
        return {"message": "Script deleted successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete script: {str(e)}"
        )

async def perform_analysis(script_id: int, analysis_id: int, db: Session):
    """
    执行实际的分析工作
    """
    try:
        # 获取脚本内容
        script = db.query(Script).filter(Script.id == script_id).first()
        if not script:
            raise ValueError("Script not found")

        # 解析脚本
        parser = ScriptParser(script.content)
        parsed_script = parser.parse()

        # 执行AI分析
        ai_service = AIAnalysisService()
        analysis_result = ai_service.generate_complete_analysis(parsed_script)

        # 更新分析结果
        analysis = db.query(ScriptAnalysis).filter(ScriptAnalysis.id == analysis_id).first()
        if analysis:
            for key, value in analysis_result.items():
                setattr(analysis, key, value)
            db.commit()
            logger.info(f"Analysis completed successfully for script {script_id}")

            # 从分析结果创建资源
            if "resource_analysis" in analysis_result:
                resource_service = ResourceService()
                created_resources = resource_service.create_resources_from_analysis(
                    db=db,
                    script_id=script_id,
                    resource_analysis=analysis_result["resource_analysis"]
                )
                logger.info(f"Created {len(created_resources)} resources from analysis")

    except AIAnalysisError as e:
        logger.error(f"AI Analysis error for script {script_id}: {str(e)}")
        if analysis:
            analysis.error = str(e)
            db.commit()
    except Exception as e:
        logger.error(f"Unexpected error during analysis for script {script_id}: {str(e)}")
        if analysis:
            analysis.error = f"Unexpected error: {str(e)}"
            db.commit() 