from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.models import Project, Script, Scene, Resource, ProjectUser, UserRole
from ..core.database import SessionLocal

class ProjectManager:
    def __init__(self, project_id: Optional[int] = None):
        self.project_id = project_id
        self.db = SessionLocal()
        if project_id:
            self.project = self.db.query(Project).filter(Project.id == project_id).first()
        
    def __del__(self):
        self.db.close()

    def get_project_overview(self) -> Dict[str, Any]:
        """
        获取项目概览信息
        """
        if not self.project:
            raise ValueError("Project not found")
        
        # 获取脚本信息
        scripts = self.db.query(Script).filter(Script.project_id == self.project_id).all()
        script_stats = {
            "total": len(scripts),
            "parsed": len([s for s in scripts if s.status == "parsed"]),
            "analyzing": len([s for s in scripts if s.status == "generating"]),
            "completed": len([s for s in scripts if s.status == "completed"])
        }
        
        # 获取场景信息
        scenes = []
        for script in scripts:
            script_scenes = self.db.query(Scene).filter(Scene.script_id == script.id).all()
            scenes.extend(script_scenes)
        
        # 获取资源信息
        resources = self.db.query(Resource).filter(
            Resource.script_id.in_([s.id for s in scripts])
        ).all()
        
        resource_stats = {}
        for resource in resources:
            if resource.type not in resource_stats:
                resource_stats[resource.type] = 0
            resource_stats[resource.type] += 1
        
        return {
            "project": {
                "id": self.project.id,
                "name": self.project.name,
                "description": self.project.description,
                "start_date": self.project.start_date,
                "end_date": self.project.end_date,
                "progress": self.project.metadata.get("progress", {}) if self.project.metadata else {}
            },
            "scripts": script_stats,
            "scenes": {
                "total": len(scenes),
                "breakdown": self._get_scene_breakdown(scenes)
            },
            "resources": resource_stats
        }
    
    def _get_scene_breakdown(self, scenes: List[Scene]) -> Dict[str, Any]:
        """
        获取场景分布统计
        """
        breakdown = {
            "interior": 0,
            "exterior": 0,
            "day": 0,
            "night": 0,
            "locations": set()
        }
        
        for scene in scenes:
            # 统计内外景
            if "内景" in scene.location or "interior" in scene.location.lower():
                breakdown["interior"] += 1
            elif "外景" in scene.location or "exterior" in scene.location.lower():
                breakdown["exterior"] += 1
            
            # 统计日夜戏
            time = scene.time_of_day.lower()
            if any(t in time for t in ["日", "早", "上午", "下午", "白天", "day", "morning", "afternoon"]):
                breakdown["day"] += 1
            elif any(t in time for t in ["夜", "晚", "night", "evening"]):
                breakdown["night"] += 1
            
            # 统计场景地点
            breakdown["locations"].add(scene.location)
        
        breakdown["locations"] = list(breakdown["locations"])
        return breakdown

    def get_resource_requirements(self) -> Dict[str, Any]:
        """
        获取项目资源需求
        """
        if not self.project:
            raise ValueError("Project not found")
        
        scripts = self.db.query(Script).filter(Script.project_id == self.project_id).all()
        resources = self.db.query(Resource).filter(
            Resource.script_id.in_([s.id for s in scripts])
        ).all()
        
        # 按类型分组资源
        grouped_resources = {}
        for resource in resources:
            if resource.type not in grouped_resources:
                grouped_resources[resource.type] = []
            grouped_resources[resource.type].append({
                "name": resource.name,
                "description": resource.description,
                "metadata": resource.metadata
            })
        
        return {
            "resources": grouped_resources,
            "statistics": {
                "total": len(resources),
                "by_type": {k: len(v) for k, v in grouped_resources.items()}
            }
        }

    def get_shooting_schedule(self) -> Dict[str, Any]:
        """
        获取拍摄计划建议
        """
        if not self.project:
            raise ValueError("Project not found")
        
        scripts = self.db.query(Script).filter(Script.project_id == self.project_id).all()
        scenes = []
        for script in scripts:
            script_scenes = self.db.query(Scene).filter(Scene.script_id == script.id).all()
            scenes.extend(script_scenes)
        
        # 按场景地点分组
        location_groups = {}
        for scene in scenes:
            if scene.location not in location_groups:
                location_groups[scene.location] = []
            location_groups[scene.location].append({
                "scene_number": scene.scene_number,
                "time_of_day": scene.time_of_day,
                "summary": scene.summary,
                "characters": scene.characters,
                "props": scene.props
            })
        
        # 生成拍摄建议
        schedule = []
        for location, location_scenes in location_groups.items():
            # 按时间段分组
            day_scenes = [s for s in location_scenes if self._is_day_scene(s["time_of_day"])]
            night_scenes = [s for s in location_scenes if not self._is_day_scene(s["time_of_day"])]
            
            if day_scenes:
                schedule.append({
                    "location": location,
                    "time": "day",
                    "scenes": day_scenes,
                    "estimated_duration": len(day_scenes) * 2  # 假设每个场景平均2小时
                })
            
            if night_scenes:
                schedule.append({
                    "location": location,
                    "time": "night",
                    "scenes": night_scenes,
                    "estimated_duration": len(night_scenes) * 2
                })
        
        return {
            "schedule": schedule,
            "statistics": {
                "total_scenes": len(scenes),
                "total_locations": len(location_groups),
                "estimated_days": sum(s["estimated_duration"] for s in schedule) / 12  # 假设每天12小时工作
            }
        }
    
    def _is_day_scene(self, time_of_day: str) -> bool:
        """
        判断是否为日景
        """
        time = time_of_day.lower()
        return any(t in time for t in ["日", "早", "上午", "下午", "白天", "day", "morning", "afternoon"])

    def update_project_status(self, status_update: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新项目状态
        """
        if not self.project:
            raise ValueError("Project not found")
        
        if not self.project.metadata:
            self.project.metadata = {}
        
        self.project.metadata.update(status_update)
        self.project.updated_at = datetime.utcnow()
        
        self.db.commit()
        return self.project.metadata 