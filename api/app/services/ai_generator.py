import json
from typing import List, Dict, Any, Optional
import os
from openai import AzureOpenAI
from sqlalchemy.orm import Session
from ..models.models import Script, Scene, Resource, ScriptStatus
from ..core.config import settings
from ..core.database import SessionLocal
from .script_service import ScriptService
from pathlib import Path
from datetime import datetime

# 配置Azure OpenAI
client = AzureOpenAI(
    api_key=settings.OPENAI_API_KEY,
    api_version=settings.OPENAI_API_VERSION,
    azure_endpoint=settings.OPENAI_API_ENDPOINT
)

class AIGenerator:
    def __init__(self):
        self.script_service = ScriptService()
        self.output_dir = Path(settings.UPLOAD_DIR) / "ai_analysis"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate_analysis(self, script_id: int) -> Dict:
        """Generate AI analysis for a script."""
        db = SessionLocal()
        try:
            # Get script and parsed data
            script = db.query(Script).filter(Script.id == script_id).first()
            if not script:
                raise ValueError(f"Script {script_id} not found")

            # Get parsed results
            parsed_data = await self.script_service.get_script_analysis(script_id)
            if not parsed_data:
                raise ValueError("Script parsing results not found")

            # Update status
            script.status = ScriptStatus.ANALYZING
            db.commit()

            try:
                # Generate different types of analysis
                analysis_result = {
                    "story_analysis": await self._analyze_story_structure(parsed_data),
                    "character_analysis": await self._analyze_characters(parsed_data),
                    "scene_analysis": await self._analyze_scenes(parsed_data),
                    "resource_analysis": await self._analyze_resources(parsed_data),
                    "recommendations": await self._generate_recommendations(parsed_data),
                    "generated_at": datetime.utcnow().isoformat()
                }

                # Save analysis results
                await self._save_analysis_results(script_id, analysis_result)

                # Update script status
                script.status = ScriptStatus.COMPLETED
                script.metadata.update({
                    "analysis_completed_at": datetime.utcnow().isoformat(),
                    "analysis_summary": {
                        "total_insights": len(analysis_result["recommendations"]),
                        "analyzed_elements": list(analysis_result.keys())
                    }
                })
                db.commit()

                return analysis_result

            except Exception as e:
                script.status = ScriptStatus.ERROR
                script.metadata["error"] = str(e)
                db.commit()
                raise AIGenerationError(f"Failed to generate analysis: {str(e)}")

        finally:
            db.close()

    async def _analyze_story_structure(self, parsed_data: Dict) -> Dict:
        """Analyze the story structure and plot elements."""
        scenes = parsed_data.get("scenes", [])
        
        # 分析故事结构
        return {
            "structure": {
                "total_scenes": len(scenes),
                "estimated_duration": len(scenes) * 3,  # 粗略估计每个场景3分钟
                "pacing_analysis": self._analyze_pacing(scenes),
            },
            "plot_elements": {
                "main_locations": self._extract_main_locations(scenes),
                "time_periods": self._analyze_time_periods(scenes),
            },
            "narrative_flow": self._analyze_narrative_flow(scenes)
        }

    async def _analyze_characters(self, parsed_data: Dict) -> Dict:
        """Analyze character relationships and development."""
        characters = parsed_data.get("characters", [])
        scenes = parsed_data.get("scenes", [])
        
        return {
            "character_list": characters,
            "main_characters": self._identify_main_characters(characters, scenes),
            "character_relationships": self._analyze_character_relationships(characters, scenes),
            "character_arcs": self._analyze_character_arcs(characters, scenes)
        }

    async def _analyze_scenes(self, parsed_data: Dict) -> Dict:
        """Analyze individual scenes and their connections."""
        scenes = parsed_data.get("scenes", [])
        
        return {
            "scene_breakdown": [
                {
                    "scene_id": scene["id"],
                    "intensity": self._calculate_scene_intensity(scene),
                    "key_elements": self._extract_scene_elements(scene),
                    "suggested_improvements": self._generate_scene_suggestions(scene)
                }
                for scene in scenes
            ],
            "scene_transitions": self._analyze_scene_transitions(scenes),
            "pacing_suggestions": self._generate_pacing_suggestions(scenes)
        }

    async def _analyze_resources(self, parsed_data: Dict) -> Dict:
        """Analyze required resources and their usage."""
        resources = parsed_data.get("resources", [])
        
        return {
            "resource_summary": self._summarize_resources(resources),
            "resource_categories": self._categorize_resources(resources),
            "resource_complexity": self._analyze_resource_complexity(resources),
            "production_considerations": self._generate_production_considerations(resources)
        }

    async def _generate_recommendations(self, parsed_data: Dict) -> List[Dict]:
        """Generate overall recommendations for improvement."""
        return [
            {
                "category": "structure",
                "suggestions": self._generate_structure_suggestions(parsed_data),
                "priority": "high"
            },
            {
                "category": "character_development",
                "suggestions": self._generate_character_suggestions(parsed_data),
                "priority": "medium"
            },
            {
                "category": "dialogue",
                "suggestions": self._generate_dialogue_suggestions(parsed_data),
                "priority": "medium"
            },
            {
                "category": "production",
                "suggestions": self._generate_production_suggestions(parsed_data),
                "priority": "low"
            }
        ]

    async def _save_analysis_results(self, script_id: int, analysis: Dict):
        """Save analysis results to a file."""
        analysis_file = self.output_dir / f"script_{script_id}_analysis.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)

    def _analyze_pacing(self, scenes: List[Dict]) -> Dict:
        """分析场景节奏."""
        return {
            "overall_pacing": "balanced",
            "pacing_distribution": {
                "fast_paced": len([s for s in scenes if self._is_fast_paced(s)]),
                "medium_paced": len([s for s in scenes if self._is_medium_paced(s)]),
                "slow_paced": len([s for s in scenes if self._is_slow_paced(s)])
            }
        }

    def _extract_main_locations(self, scenes: List[Dict]) -> List[str]:
        """提取主要场景地点."""
        locations = {}
        for scene in scenes:
            location = self._extract_location(scene)
            locations[location] = locations.get(location, 0) + 1
        return [loc for loc, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]]

    def _analyze_time_periods(self, scenes: List[Dict]) -> List[str]:
        """分析场景时间分布."""
        time_periods = set()
        for scene in scenes:
            time_period = self._extract_time_period(scene)
            if time_period:
                time_periods.add(time_period)
        return list(time_periods)

    def _analyze_narrative_flow(self, scenes: List[Dict]) -> Dict:
        """分析叙事流程."""
        return {
            "flow_quality": "coherent",
            "potential_issues": self._identify_narrative_issues(scenes),
            "suggested_improvements": self._suggest_narrative_improvements(scenes)
        }

    def _identify_main_characters(self, characters: List[str], scenes: List[Dict]) -> List[str]:
        """识别主要角色."""
        character_appearances = {char: 0 for char in characters}
        for scene in scenes:
            scene_chars = self._extract_scene_characters(scene)
            for char in scene_chars:
                if char in character_appearances:
                    character_appearances[char] += 1
        
        # 返回出现次数最多的角色
        return [char for char, count in sorted(character_appearances.items(), 
                                             key=lambda x: x[1], 
                                             reverse=True)[:3]]

    def _analyze_character_relationships(self, characters: List[str], scenes: List[Dict]) -> List[Dict]:
        """分析角色关系."""
        relationships = []
        for i, char1 in enumerate(characters):
            for char2 in characters[i+1:]:
                interaction_count = self._count_character_interactions(char1, char2, scenes)
                if interaction_count > 0:
                    relationships.append({
                        "characters": [char1, char2],
                        "interaction_count": interaction_count,
                        "relationship_type": self._determine_relationship_type(char1, char2, scenes)
                    })
        return relationships

    def _analyze_character_arcs(self, characters: List[str], scenes: List[Dict]) -> List[Dict]:
        """分析角色发展弧线."""
        character_arcs = []
        for char in characters:
            arc = {
                "character": char,
                "development_points": self._identify_character_development(char, scenes),
                "arc_type": self._determine_arc_type(char, scenes)
            }
            character_arcs.append(arc)
        return character_arcs

    def _calculate_scene_intensity(self, scene: Dict) -> str:
        """计算场景强度."""
        # 实现场景强度计算逻辑
        return "medium"

    def _extract_scene_elements(self, scene: Dict) -> List[str]:
        """提取场景关键元素."""
        # 实现场景元素提取逻辑
        return ["element1", "element2"]

    def _generate_scene_suggestions(self, scene: Dict) -> List[str]:
        """生成场景改进建议."""
        # 实现场景建议生成逻辑
        return ["suggestion1", "suggestion2"]

    def _analyze_scene_transitions(self, scenes: List[Dict]) -> List[Dict]:
        """分析场景转换."""
        transitions = []
        for i in range(len(scenes) - 1):
            transitions.append({
                "from_scene": scenes[i]["id"],
                "to_scene": scenes[i + 1]["id"],
                "transition_quality": self._evaluate_transition(scenes[i], scenes[i + 1])
            })
        return transitions

    def _generate_pacing_suggestions(self, scenes: List[Dict]) -> List[str]:
        """生成节奏改进建议."""
        # 实现节奏建议生成逻辑
        return ["pacing_suggestion1", "pacing_suggestion2"]

    def _summarize_resources(self, resources: List[Dict]) -> Dict:
        """汇总资源使用情况."""
        return {
            "total_resources": len(resources),
            "resource_types": self._count_resource_types(resources)
        }

    def _categorize_resources(self, resources: List[Dict]) -> Dict:
        """对资源进行分类."""
        categories = {}
        for resource in resources:
            category = resource.get("type", "other")
            if category not in categories:
                categories[category] = []
            categories[category].append(resource["name"])
        return categories

    def _analyze_resource_complexity(self, resources: List[Dict]) -> str:
        """分析资源复杂度."""
        # 实现资源复杂度分析逻辑
        return "medium"

    def _generate_production_considerations(self, resources: List[Dict]) -> List[str]:
        """生成制作建议."""
        # 实现制作建议生成逻辑
        return ["consideration1", "consideration2"]

    def _generate_structure_suggestions(self, parsed_data: Dict) -> List[str]:
        """生成结构改进建议."""
        # 实现结构建议生成逻辑
        return ["structure_suggestion1", "structure_suggestion2"]

    def _generate_character_suggestions(self, parsed_data: Dict) -> List[str]:
        """生成角色改进建议."""
        # 实现角色建议生成逻辑
        return ["character_suggestion1", "character_suggestion2"]

    def _generate_dialogue_suggestions(self, parsed_data: Dict) -> List[str]:
        """生成对话改进建议."""
        # 实现对话建议生成逻辑
        return ["dialogue_suggestion1", "dialogue_suggestion2"]

    def _generate_production_suggestions(self, parsed_data: Dict) -> List[str]:
        """生成制作改进建议."""
        # 实现制作建议生成逻辑
        return ["production_suggestion1", "production_suggestion2"]

    # Helper methods
    def _is_fast_paced(self, scene: Dict) -> bool:
        return False  # 实现具体逻辑

    def _is_medium_paced(self, scene: Dict) -> bool:
        return True  # 实现具体逻辑

    def _is_slow_paced(self, scene: Dict) -> bool:
        return False  # 实现具体逻辑

    def _extract_location(self, scene: Dict) -> str:
        return scene.get("name", "").split()[0]

    def _extract_time_period(self, scene: Dict) -> Optional[str]:
        return None  # 实现具体逻辑

    def _identify_narrative_issues(self, scenes: List[Dict]) -> List[str]:
        return []  # 实现具体逻辑

    def _suggest_narrative_improvements(self, scenes: List[Dict]) -> List[str]:
        return []  # 实现具体逻辑

    def _extract_scene_characters(self, scene: Dict) -> List[str]:
        return []  # 实现具体逻辑

    def _count_character_interactions(self, char1: str, char2: str, scenes: List[Dict]) -> int:
        return 0  # 实现具体逻辑

    def _determine_relationship_type(self, char1: str, char2: str, scenes: List[Dict]) -> str:
        return "neutral"  # 实现具体逻辑

    def _identify_character_development(self, character: str, scenes: List[Dict]) -> List[Dict]:
        return []  # 实现具体逻辑

    def _determine_arc_type(self, character: str, scenes: List[Dict]) -> str:
        return "flat"  # 实现具体逻辑

    def _evaluate_transition(self, scene1: Dict, scene2: Dict) -> str:
        return "smooth"  # 实现具体逻辑

    def _count_resource_types(self, resources: List[Dict]) -> Dict:
        type_counts = {}
        for resource in resources:
            res_type = resource.get("type", "other")
            type_counts[res_type] = type_counts.get(res_type, 0) + 1
        return type_counts


class AIGenerationError(Exception):
    """Custom exception for AI generation errors."""
    pass

async def generate_analysis(script_id: int) -> Dict[str, Any]:
    """生成分析的入口函数"""
    generator = AIGenerator()
    return await generator.generate_analysis(script_id) 