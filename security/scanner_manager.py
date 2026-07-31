#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from config import config, logger

class ScannerManager:
    """Gestionnaire de scanners"""
    
    def __init__(self):
        self.scanners = {
            "port_scan": self._port_scan,
            "vulnerability_scan": self._vulnerability_scan,
            "file_scan": self._file_scan,
            "network_scan": self._network_scan
        }
        
    async def scan(self, scan_type: str, target: str = None, params: Dict = None) -> Dict[str, Any]:
        """Lancer un scan"""
        
        if scan_type not in self.scanners:
            return {"error": f"Type de scan inconnu: {scan_type}"}
        
        logger.info(f"🔍 Scan {scan_type} lancé sur {target}")
        
        try:
            result = await self.scanners[scan_type](target, params)
            return {
                "status": "success",
                "type": scan_type,
                "target": target,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
        except Exception as e:
            logger.error(f"❌ Erreur scan {scan_type}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _port_scan(self, target: str, params: Dict = None) -> Dict[str, Any]:
        """Scanner les ports"""
        
        ports = params.get('ports', [22, 80, 443, 3306, 5432, 8080, 8443])
        open_ports = []
        
        for port in ports:
            try:
                reader, writer = await asyncio.open_connection(
                    target, port, loop=asyncio.get_event_loop()
                )
                writer.close()
                await writer.wait_closed()
                open_ports.append(port)
            except:
                pass
        
        return {
            "open_ports": open_ports,
            "count": len(open_ports),
            "ports_scanned": len(ports)
        }
    
    async def _vulnerability_scan(self, target: str, params: Dict = None) -> Dict[str, Any]:
        """Scanner les vulnérabilités"""
        
        vulnerabilities = []
        
        # Vérification basique des vulnérabilités
        checks = [
            {"name": "default_credentials", "risk": "high"},
            {"name": "open_ports", "risk": "medium"},
            {"name": "missing_headers", "risk": "low"}
        ]
        
        # Simulation de détection
        for check in checks:
            if await self._check_vulnerability(target, check['name']):
                vulnerabilities.append({
                    "name": check['name'],
                    "risk": check['risk'],
                    "description": f"{check['name']} détecté sur {target}"
                })
        
        return {
            "vulnerabilities": vulnerabilities,
            "count": len(vulnerabilities),
            "risk_level": "high" if any(v['risk'] == 'high' for v in vulnerabilities) else "medium"
        }
    
    async def _check_vulnerability(self, target: str, check_name: str) -> bool:
        """Vérifier une vulnérabilité spécifique"""
        
        # Simulation - retourner True ou False
        import random
        return random.choice([True, False]) if target else False
    
    async def _file_scan(self, target: str, params: Dict = None) -> Dict[str, Any]:
        """Scanner les fichiers"""
        
        path = params.get('path', '/')
        pattern = params.get('pattern', '.*')
        
        try:
            import subprocess
            result = subprocess.run(
                ['find', path, '-name', pattern],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            files = result.stdout.split('\n') if result.stdout else []
            
            return {
                "files_found": len(files),
                "files": files[:50],  # Limite
                "path": path,
                "pattern": pattern
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _network_scan(self, target: str, params: Dict = None) -> Dict[str, Any]:
        """Scanner le réseau"""
        
        try:
            import subprocess
            result = subprocess.run(
                ['nmap', '-sn', target],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "output": result.stdout[:500],
                "status": "success"
            }
            
        except Exception as e:
            return {"error": str(e)}
