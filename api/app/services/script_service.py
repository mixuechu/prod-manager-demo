from typing import Optional, Dict, List
from pathlib import Path
import aiofiles
import json
from datetime import datetime

from ..models.script import Script, ScriptStatus
from ..core.database import SessionLocal
from .script_parser import ScriptParser, ScriptParsingError
from ..core.config import settings

class ScriptService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR) / "scripts"
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save an uploaded script file and return its path."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        file_path = self.upload_dir / safe_filename

        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)

        return str(file_path)

    async def create_script(self, file_path: str, original_filename: str, user_id: int) -> Script:
        """Create a new script record in the database."""
        db = SessionLocal()
        try:
            script = Script(
                file_path=file_path,
                original_filename=original_filename,
                user_id=user_id,
                status=ScriptStatus.UPLOADED,
                metadata={}
            )
            db.add(script)
            db.commit()
            db.refresh(script)
            return script
        finally:
            db.close()

    async def parse_script(self, script_id: int) -> Dict:
        """Parse a script and save the results."""
        db = SessionLocal()
        try:
            script = db.query(Script).filter(Script.id == script_id).first()
            if not script:
                raise ValueError(f"Script {script_id} not found")

            # Update status to parsing
            script.status = ScriptStatus.PARSING
            db.commit()

            try:
                # Parse the script
                parser = ScriptParser(script.file_path)
                parse_result = await parser.parse()

                # Update script with parsed data
                script.status = ScriptStatus.PARSED
                script.metadata = {
                    "parsed_at": parse_result["parsed_at"],
                    "title": parse_result["metadata"]["title"],
                    "author": parse_result["metadata"]["author"],
                    "total_scenes": len(parse_result["scenes"]),
                    "total_characters": len(parse_result["characters"]),
                    "total_resources": len(parse_result["resources"])
                }
                
                # Save parse results
                await self._save_parse_results(script_id, parse_result)
                
                db.commit()
                return parse_result

            except Exception as e:
                script.status = ScriptStatus.ERROR
                script.metadata = {"error": str(e)}
                db.commit()
                raise ScriptParsingError(f"Failed to parse script: {str(e)}")

        finally:
            db.close()

    async def _save_parse_results(self, script_id: int, parse_result: Dict):
        """Save parse results to a JSON file."""
        results_dir = Path(settings.UPLOAD_DIR) / "parse_results"
        results_dir.mkdir(parents=True, exist_ok=True)
        
        results_file = results_dir / f"script_{script_id}_parsed.json"
        async with aiofiles.open(results_file, 'w') as f:
            await f.write(json.dumps(parse_result, ensure_ascii=False, indent=2))

    async def get_script_analysis(self, script_id: int) -> Optional[Dict]:
        """Retrieve the analysis results for a script."""
        results_file = Path(settings.UPLOAD_DIR) / "parse_results" / f"script_{script_id}_parsed.json"
        
        if not results_file.exists():
            return None
            
        async with aiofiles.open(results_file, 'r') as f:
            content = await f.read()
            return json.loads(content)

    async def delete_script(self, script_id: int):
        """Delete a script and its associated files."""
        db = SessionLocal()
        try:
            script = db.query(Script).filter(Script.id == script_id).first()
            if not script:
                return

            # Delete the script file
            if script.file_path:
                file_path = Path(script.file_path)
                if file_path.exists():
                    file_path.unlink()

            # Delete parse results if they exist
            results_file = Path(settings.UPLOAD_DIR) / "parse_results" / f"script_{script_id}_parsed.json"
            if results_file.exists():
                results_file.unlink()

            # Delete from database
            db.delete(script)
            db.commit()

        finally:
            db.close() 