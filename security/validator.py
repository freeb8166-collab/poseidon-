#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from config import config, logger

class SecurityValidator:
    """Validateur de sécurité"""
    
    def __init__(self):
        self.validation_rules = {
            "password_strength": self._validate_password,
            "file_permissions": self._validate_permissions,
            "network_security": self._validate_network,
            "application_security": self._validate_applications
        }
        
    async def validate(self, target: str, rules: List[str] = None) -> Dict[str, Any]:
        """Valider la sécurité"""
        
        if rules is None:
            rules = list(self.validation_rules.keys())
        
        results = {}
        
        for rule in rules:
            if rule in self.validation_rules:
                results[rule] = await self.validation_rules[rule](target)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "target": target,
            "results": results,
            "overall_status": self._calculate_overall_status(results)
        }
    
    async def _validate_password(self, target: str) -> Dict[str, Any]:
        """Valider la force des mots de passe"""
        
        issues = []
        
        # Vérification basique
        try:
            with open('/etc/passwd', 'r') as f:
                content = f.read()
                if 'root' in content and 'password' in content:
                    issues.append("Mot de passe root faible détecté")
        except:
            pass
        
        return {
            "status": "warning" if issues else "good",
            "issues": issues,
            "score": 70 if issues else 100
        }
    
    async def _validate_permissions(self, target: str) -> Dict[str, Any]:
        """Valider les permissions"""
        
        issues = []
        
        critical_files = [
            "/etc/passwd",
            "/etc/shadow",
            "/system/build.prop"
        ]
        
        for file_path in critical_files:
            try:
                import os
                perms = oct(os.stat(file_path).st_mode)[-3:]
                if perms in ['777', '666']:
                    issues.append(f"Permissions critiques: {file_path} ({perms})")
            except:
                pass
        
        return {
            "status": "warning" if issues else "good",
            "issues": issues,
            "score": 60 if issues else 100
        }
    
    async def _validate_network(self, target: str) -> Dict[str, Any]:
        """Valider la sécurité réseau"""
        
        issues = []
        
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
            
            if len(open_ports) > 5:
                issues.append(f"Trop de ports ouverts: {len(open_ports)}")
                
        except:
            pass
        
        return {
            "status": "warning" if issues else "good",
            "issues": issues,
            "score": 50 if issues else 100
        }
    
    async def _validate_applications(self, target: str) -> Dict[str, Any]:
        """Valider les applications"""
        
        issues = []
        
        try:
            import subprocess
            result = subprocess.run(
                ['pm', 'list', 'packages'],
                capture_output=True,
                text=True
            )
            
            packages = [p.replace('package:', '').strip() 
                       for p in result.stdout.split('\n') if p]
            
            suspicious = []
            for pkg in packages:
                if any(word in pkg.lower() for word in ['hack', 'crack', 'root']):
                    suspicious.append(pkg)
            
            if suspicious:
                issues.append(f"Applications suspectes: {', '.join(suspicious[:5])}")
                
        except:
            pass
        
        return {
            "status": "warning" if issues else "good",
            "issues": issues,
            "score": 60 if issues else 100
        }
    
    def _calculate_overall_status(self, results: Dict) -> str:
        """Calculer le statut global"""
        
        statuses = [r.get('status', 'unknown') for r in results.values()]
        
        if 'error' in statuses:
            return 'error'
        elif 'warning' in statuses:
            return 'warning'
        elif 'good' in statuses:
            return 'good'
        else:
            return 'unknown'
