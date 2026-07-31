#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from config import config

class ReportGenerator:
    """Générateur de rapports d'audit"""
    
    def __init__(self):
        self.reports_dir = config.reports_dir
        
    async def generate(self, mission: Dict, plan: Dict, results: List, evaluation: Dict) -> Dict[str, Any]:
        """Générer un rapport complet"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_dir / f"audit_report_{timestamp}.html"
        
        report = {
            "header": {
                "title": "Rapport d'Audit de Sécurité",
                "date": datetime.now().isoformat(),
                "mission": mission.get('mission', ''),
                "target": mission.get('target', '')
            },
            "summary": {
                "total_checks": len(results),
                "errors": len([r for r in results if r.get('status') == 'error']),
                "risk_score": evaluation.get('score', 0)
            },
            "findings": self._extract_findings(results),
            "recommendations": evaluation.get('recommendations', []),
            "details": results,
            "evaluation": evaluation
        }
        
        html_content = self._generate_html(report)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        json_path = self.reports_dir / f"audit_report_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return {
            "path": str(report_path),
            "json_path": str(json_path),
            "summary": report["summary"]
        }
    
    def _extract_findings
