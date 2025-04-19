import os
from openai import AzureOpenAI
from typing import Dict, Any, Optional
import json
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai.types.error import APIError, APIConnectionError, RateLimitError

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAnalysisError(Exception):
    """AI分析过程中的自定义错误"""
    pass

class AIAnalysisService:
    def __init__(self, max_retries: int = 3, initial_wait: float = 1):
        self.client = AzureOpenAI(
            api_key = "f317dfd5256942ad873d3e13a1eb1dc7",
            api_version = "2024-08-01-preview",
            azure_endpoint = "https://exbq.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-08-01-preview"
        )
        self.max_retries = max_retries
        self.initial_wait = initial_wait

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((APIError, APIConnectionError, RateLimitError)),
        before_sleep=lambda retry_state: logger.info(f"Retrying after {retry_state.next_action.sleep} seconds...")
    )
    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """
        调用OpenAI API的方法，包含重试逻辑
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content
        except RateLimitError as e:
            logger.warning(f"Rate limit hit: {str(e)}")
            raise
        except APIConnectionError as e:
            logger.warning(f"Connection error: {str(e)}")
            raise
        except APIError as e:
            logger.warning(f"API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI call: {str(e)}")
            raise AIAnalysisError(f"Failed to get AI response: {str(e)}")

    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """
        解析AI响应，确保返回有效的JSON
        """
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
            logger.error(f"Raw response: {response}")
            raise AIAnalysisError("AI response was not valid JSON")

    def analyze_characters(self, parsed_script: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析角色信息，包含错误处理和重试
        """
        try:
            system_prompt = """你是一个专业的剧本分析助手。请分析提供的剧本中的角色信息，包括：
            1. 每个角色的出场次数
            2. 每个角色的对话数量
            3. 每个角色首次出现的场景
            请以JSON格式返回分析结果。"""
            
            user_prompt = json.dumps(parsed_script, ensure_ascii=False)
            
            result = self._call_openai(system_prompt, user_prompt)
            return self._parse_ai_response(result)
        except Exception as e:
            logger.error(f"Character analysis failed: {str(e)}")
            raise AIAnalysisError(f"Failed to analyze characters: {str(e)}")

    def analyze_resources(self, parsed_script: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析资源信息，包含错误处理和重试
        """
        try:
            system_prompt = """你是一个专业的剧本分析助手。请分析提供的剧本中的资源信息，包括：
            1. 各类资源的统计数量
            2. 每种资源类型的详细列表
            3. 资源在不同场景中的分布
            请以JSON格式返回分析结果。"""
            
            user_prompt = json.dumps(parsed_script, ensure_ascii=False)
            
            result = self._call_openai(system_prompt, user_prompt)
            return self._parse_ai_response(result)
        except Exception as e:
            logger.error(f"Resource analysis failed: {str(e)}")
            raise AIAnalysisError(f"Failed to analyze resources: {str(e)}")

    def analyze_scenes(self, parsed_script: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析场景信息，包含错误处理和重试
        """
        try:
            system_prompt = """你是一个专业的剧本分析助手。请分析提供的剧本中的场景信息，包括：
            1. 场景数量统计
            2. 每个场景的主要内容概述
            3. 场景转换的频率和规律
            请以JSON格式返回分析结果。"""
            
            user_prompt = json.dumps(parsed_script, ensure_ascii=False)
            
            result = self._call_openai(system_prompt, user_prompt)
            return self._parse_ai_response(result)
        except Exception as e:
            logger.error(f"Scene analysis failed: {str(e)}")
            raise AIAnalysisError(f"Failed to analyze scenes: {str(e)}")

    def generate_complete_analysis(self, parsed_script: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成完整分析，包含错误处理
        """
        try:
            return {
                "character_analysis": self.analyze_characters(parsed_script),
                "resource_analysis": self.analyze_resources(parsed_script),
                "scene_analysis": self.analyze_scenes(parsed_script)
            }
        except Exception as e:
            logger.error(f"Complete analysis failed: {str(e)}")
            raise AIAnalysisError(f"Failed to generate complete analysis: {str(e)}") 