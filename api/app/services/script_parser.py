import os
import json
import asyncio
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import aiofiles
from sqlalchemy.orm import Session
from ..models.models import Script, Scene, Resource, ScriptStatus
from ..core.config import settings
from ..core.database import SessionLocal
from datetime import datetime

class ScriptParser:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.content: Optional[str] = None
        self.metadata: Dict = {}
        self.scenes: List[Dict] = []
        self.characters: List[str] = []
        self.resources: List[Dict] = []

    async def parse(self) -> Dict:
        """Parse the script file and extract information."""
        try:
            # Read the file content
            self.content = await self._read_file()
            
            # Extract basic metadata
            self.metadata = await self._extract_metadata()
            
            # Extract scenes
            self.scenes = await self._extract_scenes()
            
            # Extract characters
            self.characters = await self._extract_characters()
            
            # Extract resources
            self.resources = await self._extract_resources()
            
            return {
                "metadata": self.metadata,
                "scenes": self.scenes,
                "characters": self.characters,
                "resources": self.resources,
                "parsed_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise ScriptParsingError(f"Failed to parse script: {str(e)}")

    async def _read_file(self) -> str:
        """Read the content of the script file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise ScriptParsingError(f"Failed to read file: {str(e)}")

    async def _extract_metadata(self) -> Dict:
        """Extract metadata from the script content."""
        metadata = {
            "title": "",
            "author": "",
            "version": "1.0",
            "created_at": datetime.utcnow().isoformat()
        }
        
        if not self.content:
            return metadata
            
        # Try to find title (first line or specified by "Title:")
        title_match = re.search(r"Title:\s*(.+)", self.content)
        if title_match:
            metadata["title"] = title_match.group(1).strip()
        else:
            first_line = self.content.split('\n')[0].strip()
            if first_line:
                metadata["title"] = first_line

        # Try to find author
        author_match = re.search(r"Author:\s*(.+)", self.content)
        if author_match:
            metadata["author"] = author_match.group(1).strip()

        return metadata

    async def _extract_scenes(self) -> List[Dict]:
        """Extract scenes from the script content."""
        scenes = []
        if not self.content:
            return scenes

        # Simple scene detection (lines starting with "Scene" or "INT./EXT.")
        scene_pattern = r"(?:Scene|INT\.|EXT\.)\s*[^\\n]+"
        scene_matches = re.finditer(scene_pattern, self.content)
        
        for i, match in enumerate(scene_matches):
            scene_text = match.group(0)
            scenes.append({
                "id": f"scene_{i+1}",
                "name": scene_text.strip(),
                "order": i+1,
                "content": scene_text
            })

        return scenes

    async def _extract_characters(self) -> List[str]:
        """Extract character names from the script content."""
        characters = set()
        if not self.content:
            return list(characters)

        # Look for character names (in all caps followed by dialogue)
        character_pattern = r"^[A-Z][A-Z\s]+(?=:)"
        character_matches = re.finditer(character_pattern, self.content, re.MULTILINE)
        
        for match in character_matches:
            character_name = match.group(0).strip()
            characters.add(character_name)

        return list(characters)

    async def _extract_resources(self) -> List[Dict]:
        """Extract resource references from the script content."""
        resources = []
        if not self.content:
            return resources

        # Look for resource references like images, sounds, props
        resource_patterns = {
            "image": r"\[(IMAGE|IMG|PHOTO):([^\]]+)\]",
            "sound": r"\[(SOUND|SFX|MUSIC):([^\]]+)\]",
            "prop": r"\[(PROP|ITEM):([^\]]+)\]"
        }

        for resource_type, pattern in resource_patterns.items():
            matches = re.finditer(pattern, self.content)
            for i, match in enumerate(matches):
                resources.append({
                    "id": f"{resource_type}_{i+1}",
                    "type": resource_type,
                    "name": match.group(2).strip(),
                    "reference": match.group(0)
                })

        return resources


class ScriptParsingError(Exception):
    """Custom exception for script parsing errors."""
    pass

async def parse_script(script_id: int):
    """解析脚本的入口函数"""
    parser = ScriptParser(script_id)
    return await parser.parse() 