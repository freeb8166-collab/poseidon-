#!/usr/bin/env python3
# -*- coding: utf-8 -*-

PLANNER_PROMPT = """
Tu es un planificateur d'audit de sécurité.

Mission: {mission}
Cible: {target}

Crée un plan d'audit détaillé. Réponds en JSON avec cette structure:
{{
    "steps": [
        {{
            "id": "unique_id",
            "description": "Description de l'étape",
            "type": "file_operation|app_operation|network_operation|system_operation",
            "operation": "read|write|list|install|open|scan|request",
            "priority": "high|medium|low"
        }}
    ],
    "estimated_time": "temps estimé",
    "risk_level": "low|medium|high"
}}

Sois précis et professionnel.
"""

EVALUATOR_PROMPT = """
Analyse ces résultats d'audit:

{results}

Évalue:
1. Les problèmes critiques
2. Les faiblesses moyennes
3. Les points positifs
4. Recommandations
5. Score de sécurité (0-100)

Réponds en JSON.
"""
