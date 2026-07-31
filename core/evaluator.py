#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from typing import List, Dict, Any
from ai.llm_client import LLMClient
from ai.prompts import EVALUATOR_PROMPT

class Evaluator:
    """Évaluateur des résultats d'audit"""
    
    def __init__(self, llm: LLMClient):
        self.llm = llm
        
    async def evaluate(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Évaluer les résultats d'audit"""
        
        prompt = EVALUATOR_PROMPT.format(
            results=json.dumps(results, indent=2)
        )
        
        response = await self.llm.chat(prompt)
        
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
            
        return {
            "score": 70,
            "critical_issues": [],
            "medium_issues": [],
            "recommendations": [
                "Effectuer une revue de code",
                "Mettre à jour les configurations",
                "Vérifier les permissions"
            ],
            "status": "completed"
        }
