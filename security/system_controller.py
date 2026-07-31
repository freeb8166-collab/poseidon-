#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os
import json
from typing import Dict, Any, List
from datetime import datetime
from config import config, logger

class SystemController:
    """Contrôleur système"""
    
    def __init__(self):
        self.allow_root = config.capabilities.root_operations
        
    async def execute_system_command(self, command: str, use_root: bool = False) -> Dict[str, Any]:
        """Exécuter une commande système"""
        
        if use_root and not self.allow_root:
            return {"status": "blocked", "error": "Opérations root désactivées"}
        
        try:
            if use_root:
                cmd = ['su', '-c', command]
            else:
                cmd = command.split()
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"status": "error", "error": "Timeout"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Obtenir des informations système"""
        
        info = {}
        
        try:
            # Android version
            result = subprocess.run(
                ['getprop', 'ro.build.version.release'],
                capture_output=True,
                text=True
            )
            info['android_version'] = result.stdout.strip()
            
            # Device model
            result = subprocess.run(
                ['getprop', 'ro.product.model'],
                capture_output=True,
                text=True
            )
            info['device_model'] = result.stdout.strip()
            
            # CPU info
            with open('/proc/cpuinfo', 'r') as f:
                cpu_info = f.read()
                info['cpu'] = cpu_info[:200]
            
            # Memory info
            with open('/proc/meminfo', 'r') as f:
                mem_info = f.read()
                info['memory'] = mem_info[:200]
            
            # Storage
            try:
                result = subprocess.run(
                    ['df', '-h'],
                    capture_output=True,
                    text=True
                )
                info['storage'] = result.stdout[:500]
            except:
                pass
            
            return {
                "status": "success",
                "system_info": info,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def restart_service(self, service_name: str) -> Dict[str, Any]:
        """Redémarrer un service"""
        
        if config.security.require_confirmation:
            print(f"\n⚠️ Redémarrer le service: {service_name}")
            print("[1] Oui")
            print("[2] Non")
            choice = input("Choix: ").strip()
            if choice != '1':
                return {"status": "cancelled"}
        
        return await self.execute_system_command(f'systemctl restart {service_name}', self.allow_root)
    
    async def check_service_status(self, service_name: str) -> Dict[str, Any]:
        """Vérifier le statut d'un service"""
        
        return await self.execute_system_command(f'systemctl status {service_name}', self.allow_root) me 
