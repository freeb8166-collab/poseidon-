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
    
    def _extract_findings(self, results: List) -> List[Dict]:
        findings = []
        for result in results:
            if result.get('status') == 'success':
                data = result.get('data', {})
                if data.get('vulnerabilities'):
                    for vuln in data['vulnerabilities']:
                        findings.append({
                            "type": "vulnerability",
                            "description": vuln,
                            "severity": "high"
                        })
        return findings
    
    def _generate_html(self, report: Dict) -> str:
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{report['header']['title']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ background: #ecf0f1; padding: 20px; margin: 20px 0; border-radius: 5px; }}
        .finding {{ background: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 4px solid #e74c3c; }}
        .recommendation {{ background: #e8f5e9; padding: 15px; margin: 10px 0; border-left: 4px solid #4caf50; }}
        .score {{ font-size: 48px; font-weight: bold; color: #2c3e50; }}
        .high {{ color: #e74c3c; }}
        .medium {{ color: #f39c12; }}
        .low {{ color: #27ae60; }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>{report['header']['title']}</h1>
        <p><strong>Mission:</strong> {report['header']['mission']}</p>
        <p><strong>Cible:</strong> {report['header']['target']}</p>
        <p><strong>Date:</strong> {report['header']['date']}</p>
    </div>
    
    <div class="summary">
        <h2>Résumé</h2>
        <div class="score">{report['summary']['risk_score']}/100</div>
        <p>Vérifications: {report['summary']['total_checks']}</p>
        <p>Erreurs: {report['summary']['errors']}</p>
    </div>
    
    <h2>Découvertes</h2>
    {''.join([f'<div class="finding"><strong>{f["type"]}</strong> - {f["description"]} (Sévérité: {f["severity"]})</div>' for f in report.get('findings', [])])}
    
    <h2>Recommandations</h2>
    {''.join([f'<div class="recommendation">✓ {r}</div>' for r in report.get('recommendations', [])])}
</div>
</body>
</html>
        """
