#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, Any, Optional
from ai.llm_client import LLMClient
from ai.memory import MemorySystem
from config import logger

class AdaptationEngine:
    """Moteur d'adaptation automatique"""
    
    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.memory = MemorySystem()
        
    async def adapt(self, failed_step: Dict[str, Any], error_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Adapter une étape qui a échoué"""
        
        memory_result = await self.memory.find_solution(error_result.get('error', ''))
        if memory_result:
            logger.info(f"📚 Solution trouvée en mémoire")
            return memory_result.get('alternative_step')
        
        prompt = f"""
        L'étape suivante a échoué:
        Étape: {failed_step}
        Erreur: {error_result.get('error')}
        
        Propose une alternative pour contourner ce problème.
        Réponds en JSON avec la nouvelle étape.
        """
        
        response = await self.llm.chat(prompt)
        
        try:
            import json
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
            
        return {
            "id": f"alternative_{failed_step.get('id', 'unknown')}",
            "description": f"Version simplifiée de {failed_step.get('description', '')}",
            "type": "generic",
            "priority": "low"
        }
