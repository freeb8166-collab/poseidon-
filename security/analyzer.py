#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from config import config, logger

class SecurityAnalyzer:
    """Analyseur de sécurité"""
    
    def __init__(self):
        self.vulnerabilities = []
        self.findings = []
        
    async def analyze_system(self) -> Dict[str, Any]:
        """Analyser la sécurité du système"""
        
        logger.info("🔍 Analyse de sécurité du système...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities": [],
            "risks": [],
            "recommendations": []
        }
        
        # 1. Vérifier les permissions
        perm_check = await self._check_permissions()
        results["permissions"] = perm_check
        
        # 2. Vérifier les applications
        app_check = await self._check_applications()
        results["applications"] = app_check
        
        # 3. Vérifier les fichiers sensibles
        file_check = await self._check_sensitive_files()
        results["sensitive_files"] = file_check
        
        # 4. Vérifier les connexions réseau
        network_check = await self._check_network()
        results["network"] = network_check
        
        # 5. Générer les recommandations
        results["recommendations"] = await self._generate_recommendations(results)
        
        return results
    
    async def _check_permissions(self) -> Dict[str, Any]:
        """Vérifier les permissions système"""
        
        issues = []
        
        # Vérifier les permissions des fichiers critiques
        critical_files = [
            "/etc/passwd",
            "/etc/shadow",
            "/system/build.prop",
            "/data/data/com.termux/files/home/.bashrc"
        ]
        
        for file_path in critical_files:
            try:
                path = Path(file_path)
                if path.exists():
                    perms = oct(path.stat().st_mode)[-3:]
                    if perms in ['777', '666']:
                        issues.append({
                            "file": file_path,
                            "permissions": perms,
                            "risk": "high",
                            "message": f"Permissions trop permissives: {perms}"
                        })
            except:
                pass
        
        return {
            "issues": issues,
            "count": len(issues),
            "status": "warning" if issues else "good"
        }
    
    async def _check_applications(self) -> Dict[str, Any]:
        """Vérifier les applications installées"""
        
        try:
            import subprocess
            result = subprocess.run(
                ['pm', 'list', 'packages'],
                capture_output=True,
                text=True
            )
            
            packages = [p.replace('package:', '').strip() 
                       for p in result.stdout.split('\n') if p]
            
            # Vérifier les applications suspectes
            suspicious = []
            for pkg in packages:
                if any(word in pkg.lower() for word in ['hack', 'crack', 'root', 'exploit']):
                    suspicious.append(pkg)
            
            return {
                "total": len(packages),
                "suspicious": suspicious,
                "status": "warning" if suspicious else "good"
            }
            
        except:
            return {"error": "Impossible de lister les applications"}
    
    async def _check_sensitive_files(self) -> Dict[str, Any]:
        """Vérifier les fichiers sensibles"""
        
        sensitive_files = []
        
        # Vérifier les fichiers de configuration
        config_files = [
            ".env", "config.json", "settings.py",
            "secrets.txt", "passwords.txt", "credentials.txt"
        ]
        
        for file in config_files:
            try:
                path = Path.home() / file
                if path.exists():
                    sensitive_files.append({
                        "file": str(path),
                        "risk": "high",
                        "message": "Fichier sensible trouvé"
                    })
            except:
                pass
        
        return {
            "sensitive_files": sensitive_files,
            "count": len(sensitive_files),
            "status": "warning" if sensitive_files else "good"
        }
    
    async def _check_network(self) -> Dict[str, Any]:
        """Vérifier la sécurité réseau"""
        
        try:
            import subprocess
            result = subprocess.run(
                ['netstat', '-tuln'],
                capture_output=True,
                text=True
            )
            
            open_ports = []
            for line in result.stdout.split('\n'):
                if 'LISTEN' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        port = parts[3].split(':')[-1]
                        open_ports.append(port)
            
            return {
                "open_ports": open_ports,
                "count": len(open_ports),
                "status": "warning" if len(open_ports) > 10 else "good"
            }
            
        except:
            return {"error": "Impossible de vérifier le réseau"}
    
    async def _generate_recommendations(self, results: Dict) -> List[str]:
        """Générer des recommandations"""
        
        recommendations = []
        
        if results.get("permissions", {}).get("issues"):
            recommendations.append("🔐 Corriger les permissions des fichiers critiques")
        
        if results.get("applications", {}).get("suspicious"):
            recommendations.append("⚠️ Examiner les applications suspectes")
        
        if results.get("sensitive_files", {}).get("sensitive_files"):
            recommendations.append("📄 Protéger les fichiers sensibles avec des permissions restrictives")
        
        if not recommendations:
            recommendations.append("✅ Système sécurisé - Aucune recommandation majeure")
        
        return recommendations
