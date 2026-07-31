#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from typing import Dict, Any, List
from ai.llm_client import LLMClient
from ai.prompts import PLANNER_PROMPT

class Planner:
    """Planificateur d'audits"""
    
    def __init__(self, llm: LLMClient):
        self.llm = llm
        
    async def create_plan(self, mission: str, target: str) -> Dict[str, Any]:
        """Créer un plan d'audit"""
        
        prompt = PLANNER_PROMPT.format(mission=mission, target=target)
        response = await self.llm.chat(prompt)
        
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
                return plan
        except Exception as e:
            print(f"Erreur parsing plan: {e}")
        
        return self._default_plan(mission, target)
    
    def _default_plan(self, mission: str, target: str) -> Dict[str, Any]:
        """Plan par défaut"""
        
        return {
            "steps": [
                {
                    "id": "reconnaissance",
                    "description": "Collecte d'informations sur la cible",
                    "type": "network_operation",
                    "operation": "scan",
                    "target": target
                },
                {
                    "id": "file_analysis",
                    "description": "Analyse des fichiers système",
                    "type": "file_operation",
                    "operation": "list",
                    "path": "/"
                },
                {
                    "id": "app_analysis",
                    "description": "Analyse des applications installées",
                    "type": "app_operation",
                    "operation": "list"
                },
                {
                    "id": "reporting",
                    "description": "Génération du rapport",
                    "type": "reporting"
                }
            ],
            "estimated_time": "5-10 minutes",
            "risk_level": "medium"
        }
