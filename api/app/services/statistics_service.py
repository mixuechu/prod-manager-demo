from typing import Dict, List, Optional
from collections import Counter, defaultdict
from datetime import datetime

from ..models.script import Script, ScriptStatus
from ..core.database import SessionLocal
from .script_service import ScriptService

class StatisticsService:
    def __init__(self):
        self.script_service = ScriptService()

    async def get_script_statistics(self, script_id: int) -> Dict:
        """Get comprehensive statistics for a script."""
        # Get parsed data
        parsed_data = await self.script_service.get_script_analysis(script_id)
        if not parsed_data:
            raise ValueError("Script analysis not found")

        return {
            "scene_statistics": self._analyze_scenes(parsed_data),
            "character_statistics": self._analyze_characters(parsed_data),
            "resource_statistics": self._analyze_resources(parsed_data),
            "timeline_statistics": self._analyze_timeline(parsed_data),
            "generated_at": datetime.utcnow().isoformat()
        }

    def _analyze_scenes(self, parsed_data: Dict) -> Dict:
        """Analyze scene-related statistics."""
        scenes = parsed_data.get("scenes", [])
        
        # 场景时长分布
        scene_durations = self._calculate_scene_durations(scenes)
        
        # 场景类型分布
        scene_types = self._categorize_scenes(scenes)
        
        # 场景地点统计
        location_stats = self._analyze_locations(scenes)
        
        # 场景强度分布
        intensity_distribution = self._analyze_scene_intensity(scenes)

        return {
            "duration_distribution": {
                "labels": list(scene_durations.keys()),
                "data": list(scene_durations.values()),
                "type": "bar",
                "title": "场景时长分布"
            },
            "scene_types": {
                "labels": list(scene_types.keys()),
                "data": list(scene_types.values()),
                "type": "pie",
                "title": "场景类型分布"
            },
            "location_frequency": {
                "labels": list(location_stats.keys()),
                "data": list(location_stats.values()),
                "type": "bar",
                "title": "场景地点使用频率"
            },
            "intensity_distribution": {
                "labels": list(intensity_distribution.keys()),
                "data": list(intensity_distribution.values()),
                "type": "line",
                "title": "场景强度变化"
            }
        }

    def _analyze_characters(self, parsed_data: Dict) -> Dict:
        """Analyze character-related statistics."""
        characters = parsed_data.get("characters", [])
        scenes = parsed_data.get("scenes", [])
        
        # 角色出场频率
        appearance_stats = self._calculate_character_appearances(characters, scenes)
        
        # 角色对话量统计
        dialogue_stats = self._calculate_dialogue_counts(characters, scenes)
        
        # 角色互动网络
        interaction_network = self._analyze_character_interactions(characters, scenes)
        
        # 角色情感曲线
        emotion_curves = self._analyze_character_emotions(characters, scenes)

        return {
            "appearance_frequency": {
                "labels": list(appearance_stats.keys()),
                "data": list(appearance_stats.values()),
                "type": "bar",
                "title": "角色出场频率"
            },
            "dialogue_distribution": {
                "labels": list(dialogue_stats.keys()),
                "data": list(dialogue_stats.values()),
                "type": "pie",
                "title": "角色对话量分布"
            },
            "interaction_network": {
                "nodes": interaction_network["nodes"],
                "edges": interaction_network["edges"],
                "type": "network",
                "title": "角色互动网络"
            },
            "emotion_trends": {
                "labels": list(range(len(scenes))),
                "datasets": emotion_curves,
                "type": "line",
                "title": "角色情感变化趋势"
            }
        }

    def _analyze_resources(self, parsed_data: Dict) -> Dict:
        """Analyze resource-related statistics."""
        resources = parsed_data.get("resources", [])
        scenes = parsed_data.get("scenes", [])
        
        # 资源类型分布
        resource_types = self._categorize_resources(resources)
        
        # 资源使用热度
        usage_heatmap = self._calculate_resource_usage(resources, scenes)
        
        # 资源复杂度分布
        complexity_distribution = self._analyze_resource_complexity(resources)
        
        # 资源关联分析
        resource_correlations = self._analyze_resource_correlations(resources, scenes)

        return {
            "type_distribution": {
                "labels": list(resource_types.keys()),
                "data": list(resource_types.values()),
                "type": "pie",
                "title": "资源类型分布"
            },
            "usage_heatmap": {
                "data": usage_heatmap,
                "type": "heatmap",
                "title": "资源使用热度图"
            },
            "complexity_distribution": {
                "labels": list(complexity_distribution.keys()),
                "data": list(complexity_distribution.values()),
                "type": "bar",
                "title": "资源复杂度分布"
            },
            "resource_correlations": {
                "nodes": resource_correlations["nodes"],
                "edges": resource_correlations["edges"],
                "type": "network",
                "title": "资源关联网络"
            }
        }

    def _analyze_timeline(self, parsed_data: Dict) -> Dict:
        """Analyze timeline-related statistics."""
        scenes = parsed_data.get("scenes", [])
        
        # 时间线分布
        timeline_distribution = self._analyze_time_distribution(scenes)
        
        # 情节发展曲线
        plot_development = self._analyze_plot_development(scenes)
        
        # 场景转换频率
        transition_frequency = self._analyze_scene_transitions(scenes)
        
        # 节奏变化
        pacing_changes = self._analyze_pacing_changes(scenes)

        return {
            "timeline_distribution": {
                "labels": list(timeline_distribution.keys()),
                "data": list(timeline_distribution.values()),
                "type": "bar",
                "title": "时间线分布"
            },
            "plot_development": {
                "labels": list(range(len(scenes))),
                "data": plot_development,
                "type": "line",
                "title": "情节发展曲线"
            },
            "transition_frequency": {
                "labels": list(transition_frequency.keys()),
                "data": list(transition_frequency.values()),
                "type": "bar",
                "title": "场景转换频率"
            },
            "pacing_changes": {
                "labels": list(range(len(scenes))),
                "data": pacing_changes,
                "type": "line",
                "title": "节奏变化曲线"
            }
        }

    # Helper methods for scene analysis
    def _calculate_scene_durations(self, scenes: List[Dict]) -> Dict[str, int]:
        """Calculate the distribution of scene durations."""
        durations = Counter()
        for scene in scenes:
            # Estimate duration based on content length or other factors
            duration = len(scene.get("content", "")) // 100  # Simple estimation
            duration_category = f"{duration}-{duration+5} mins"
            durations[duration_category] += 1
        return dict(durations)

    def _categorize_scenes(self, scenes: List[Dict]) -> Dict[str, int]:
        """Categorize scenes by type."""
        types = Counter()
        for scene in scenes:
            scene_type = self._determine_scene_type(scene)
            types[scene_type] += 1
        return dict(types)

    def _analyze_locations(self, scenes: List[Dict]) -> Dict[str, int]:
        """Analyze the frequency of different locations."""
        locations = Counter()
        for scene in scenes:
            location = scene.get("name", "").split()[0]
            locations[location] += 1
        return dict(locations.most_common(10))

    def _analyze_scene_intensity(self, scenes: List[Dict]) -> Dict[int, float]:
        """Analyze the intensity distribution of scenes."""
        intensity_scores = {}
        for i, scene in enumerate(scenes):
            intensity_scores[i] = self._calculate_intensity_score(scene)
        return intensity_scores

    # Helper methods for character analysis
    def _calculate_character_appearances(self, characters: List[str], scenes: List[Dict]) -> Dict[str, int]:
        """Calculate how many times each character appears."""
        appearances = Counter()
        for scene in scenes:
            scene_chars = self._extract_scene_characters(scene)
            for char in scene_chars:
                if char in characters:
                    appearances[char] += 1
        return dict(appearances.most_common(10))

    def _calculate_dialogue_counts(self, characters: List[str], scenes: List[Dict]) -> Dict[str, int]:
        """Calculate the amount of dialogue for each character."""
        dialogue_counts = Counter()
        for scene in scenes:
            # Count dialogue lines or words for each character
            pass
        return dict(dialogue_counts)

    def _analyze_character_interactions(self, characters: List[str], scenes: List[Dict]) -> Dict:
        """Analyze the interaction network between characters."""
        return {
            "nodes": [{"id": char, "name": char} for char in characters],
            "edges": []  # Add interaction edges
        }

    def _analyze_character_emotions(self, characters: List[str], scenes: List[Dict]) -> List[Dict]:
        """Analyze emotional arcs for main characters."""
        emotion_data = []
        for char in characters[:5]:  # Limit to top 5 characters
            emotion_data.append({
                "label": char,
                "data": self._calculate_emotion_curve(char, scenes)
            })
        return emotion_data

    # Helper methods for resource analysis
    def _categorize_resources(self, resources: List[Dict]) -> Dict[str, int]:
        """Categorize resources by type."""
        return Counter(resource.get("type", "other") for resource in resources)

    def _calculate_resource_usage(self, resources: List[Dict], scenes: List[Dict]) -> List[List[float]]:
        """Calculate resource usage heatmap data."""
        return [[0 for _ in scenes] for _ in resources]  # Placeholder

    def _analyze_resource_complexity(self, resources: List[Dict]) -> Dict[str, int]:
        """Analyze the complexity distribution of resources."""
        complexity_levels = Counter()
        for resource in resources:
            complexity = self._calculate_resource_complexity(resource)
            complexity_levels[complexity] += 1
        return dict(complexity_levels)

    def _analyze_resource_correlations(self, resources: List[Dict], scenes: List[Dict]) -> Dict:
        """Analyze correlations between resources."""
        return {
            "nodes": [{"id": res["id"], "name": res["name"]} for res in resources],
            "edges": []  # Add correlation edges
        }

    # Helper methods for timeline analysis
    def _analyze_time_distribution(self, scenes: List[Dict]) -> Dict[str, int]:
        """Analyze the distribution of scenes across different times."""
        time_periods = Counter()
        for scene in scenes:
            period = self._extract_time_period(scene)
            if period:
                time_periods[period] += 1
        return dict(time_periods)

    def _analyze_plot_development(self, scenes: List[Dict]) -> List[float]:
        """Calculate plot development curve."""
        return [self._calculate_plot_intensity(scene) for scene in scenes]

    def _analyze_scene_transitions(self, scenes: List[Dict]) -> Dict[str, int]:
        """Analyze the frequency of different types of scene transitions."""
        transitions = Counter()
        for i in range(len(scenes) - 1):
            transition_type = self._determine_transition_type(scenes[i], scenes[i + 1])
            transitions[transition_type] += 1
        return dict(transitions)

    def _analyze_pacing_changes(self, scenes: List[Dict]) -> List[float]:
        """Calculate pacing changes throughout the script."""
        return [self._calculate_pacing_score(scene) for scene in scenes]

    # Utility methods
    def _determine_scene_type(self, scene: Dict) -> str:
        """Determine the type of a scene."""
        name = scene.get("name", "").lower()
        if "int." in name:
            return "Interior"
        elif "ext." in name:
            return "Exterior"
        else:
            return "Other"

    def _calculate_intensity_score(self, scene: Dict) -> float:
        """Calculate an intensity score for a scene."""
        # Implement intensity calculation logic
        return 0.5

    def _extract_scene_characters(self, scene: Dict) -> List[str]:
        """Extract character names from a scene."""
        # Implement character extraction logic
        return []

    def _calculate_emotion_curve(self, character: str, scenes: List[Dict]) -> List[float]:
        """Calculate emotional intensity curve for a character."""
        return [0.5 for _ in scenes]  # Placeholder

    def _calculate_resource_complexity(self, resource: Dict) -> str:
        """Calculate complexity level for a resource."""
        return "medium"

    def _extract_time_period(self, scene: Dict) -> Optional[str]:
        """Extract time period from a scene."""
        return None

    def _calculate_plot_intensity(self, scene: Dict) -> float:
        """Calculate plot intensity for a scene."""
        return 0.5

    def _determine_transition_type(self, scene1: Dict, scene2: Dict) -> str:
        """Determine the type of transition between two scenes."""
        return "cut"

    def _calculate_pacing_score(self, scene: Dict) -> float:
        """Calculate a pacing score for a scene."""
        return 0.5 