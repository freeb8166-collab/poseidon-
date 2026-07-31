#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import subprocess
import json
from typing import Dict, Any, List
from tools.terminal import TerminalTool
from tools.network import NetworkTool
from tools.files import FileManager
from tools.app_manager import AppManager
from tools.logger import SecurityLogger
from config import config, logger

class Executor:
    """Exécuteur complet avec toutes les capacités"""
    
    def __init__(self):
        self.logger = SecurityLogger()
        self.terminal = TerminalTool()
        self.network = NetworkTool()
        self.files = FileManager()
        self.apps = AppManager()
        
        # Commandes bloquées
        self.blocked_commands = config.security.blocked_commands
        
    async def execute(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Exécuter une étape avec les outils appropriés"""
        
        step_type = step.get('type', 'generic')
        operation = step.get('operation', '')
        
        logger.info(f"🔧 Exécution: {step_type} - {operation}")
        
        # Vérification de sécurité
        if not self._check_security(step):
            return {
                "status": "blocked",
                "error": "Opération non autorisée",
                "security_alert": True
            }
        
        try:
            if step_type == "file_operation":
                return await self._handle_file_operation(step)
            elif step_type == "app_operation":
                return await self._handle_app_operation(step)
            elif step_type == "network_operation":
                return await self._handle_network_operation(step)
            elif step_type == "system_operation":
                return await self._handle_system_operation(step)
            elif step_type == "terminal_operation":
                return await self._handle_terminal_operation(step)
            else:
                return await self._handle_generic_operation(step)
                
        except Exception as e:
            logger.error(f"❌ Erreur d'exécution: {e}")
            return {
                "status": "error",
                "error": str(e),
                "step": step
            }
    
    async def _handle_file_operation(self, step: Dict) -> Dict:
        """Gérer les opérations sur les fichiers"""
        
        operation = step.get('operation')
        path = step.get('path')
        content = step.get('content', '')
        
        if operation == 'read':
            return await self.files.read_file(path)
        elif operation == 'write':
            return await self.files.write_file(path, content)
        elif operation == 'delete':
            return await self.files.delete_file(path)
        elif operation == 'list':
            recursive = step.get('recursive', False)
            return await self.files.list_directory(path, recursive)
        elif operation == 'modify':
            # Modification avancée
            pattern = step.get('pattern')
            replacement = step.get('replacement')
            return await self._modify_file_content(path, pattern, replacement)
        else:
            return {"status": "error", "error": f"Opération inconnue: {operation}"}
    
    async def _handle_app_operation(self, step: Dict) -> Dict:
        """Gérer les opérations sur les applications"""
        
        operation = step.get('operation')
        package = step.get('package')
        apk_path = step.get('apk_path', '')
        credentials = step.get('credentials', {})
        
        if operation == 'install':
            return await self.apps.install_apk(apk_path)
        elif operation == 'open':
            activity = step.get('activity')
            return await self.apps.open_app(package, activity)
        elif operation == 'create_account':
            return await self.apps.create_account(package, credentials)
        elif operation == 'list':
            return await self._list_apps()
        elif operation == 'uninstall':
            return await self._uninstall_app(package)
        else:
            return {"status": "error", "error": f"Opération inconnue: {operation}"}
    
    async def _handle_network_operation(self, step: Dict) -> Dict:
        """Gérer les opérations réseau"""
        
        operation = step.get('operation')
        target = step.get('target', '')
        
        if operation == 'scan':
            ports = step.get('ports', [21, 22, 80, 443, 3306, 8080])
            return await self.network.scan_ports(target, ports)
        elif operation == 'request':
            method = step.get('method', 'GET')
            data = step.get('data', {})
            return await self.network.request(target, method, data)
        elif operation == 'dns':
            return await self.network.dns_lookup(target)
        else:
            return {"status": "error", "error": f"Opération inconnue: {operation}"}
    
    async def _handle_system_operation(self, step: Dict) -> Dict:
        """Gérer les opérations système"""
        
        operation = step.get('operation')
        
        if operation == 'reboot':
            return await self._system_reboot()
        elif operation == 'shutdown':
            return await self._system_shutdown()
        elif operation == 'info':
            return await self._system_info()
        else:
            return {"status": "error", "error": f"Opération inconnue: {operation}"}
    
    async def _handle_terminal_operation(self, step: Dict) -> Dict:
        """Gérer les commandes terminal"""
        
        command = step.get('command', '')
        timeout = step.get('timeout', 30)
        
        # Vérification des commandes bloquées
        for blocked in self.blocked_commands:
            if blocked in command:
                return {
                    "status": "blocked",
                    "error": f"Commande bloquée: {blocked}"
                }
        
        return await self.terminal.execute(command, timeout)
    
    async def _handle_generic_operation(self, step: Dict) -> Dict:
        """Gérer les opérations génériques"""
        
        # Utiliser l'IA pour déterminer la meilleure approche
        from ai.llm_client import LLMClient
        llm = LLMClient()
        
        prompt = f"""
        Exécute cette tâche de manière générique:
        {json.dumps(step, indent=2)}
        
        Propose une solution et explique les étapes.
        """
        
        response = await llm.chat(prompt)
        
        return {
            "status": "success",
            "message": response,
            "generic_execution": True
        }
    
    async def _modify_file_content(self, path: str, pattern: str, replacement: str) -> Dict:
        """Modifier le contenu d'un fichier (recherche/remplacement)"""
        
        # Lire le fichier
        read_result = await self.files.read_file(path)
        if read_result['status'] != 'success':
            return read_result
        
        content = read_result['content']
        
        # Effectuer le remplacement
        import re
        new_content = re.sub(pattern, replacement, content)
        
        # Écrire le fichier modifié
        return await self.files.write_file(path, new_content)
    
    async def _list_apps(self) -> Dict:
        """Lister les applications installées"""
        
        try:
            result = subprocess.run(
                ['pm', 'list', 'packages'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                packages = [p.replace('package:', '').strip() 
                           for p in result.stdout.split('\n') if p]
                
                return {
                    "status": "success",
                    "count": len(packages),
                    "packages": packages[:50]  # Limite pour performance
                }
            else:
                return {"status": "error", "error": result.stderr}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _uninstall_app(self, package: str) -> Dict:
        """Désinstaller une application"""
        
        if not config.capabilities.system_modification:
            return {"status": "blocked", "error": "Désinstallation désactivée"}
        
        if config.security.require_confirmation:
            print(f"\n⚠️ Désinstaller: {package}")
            print("[1] Oui")
            print("[2] Non")
            choice = input("Choix: ").strip()
            if choice != '1':
                return {"status": "cancelled"}
        
        try:
            result = subprocess.run(
                ['pm', 'uninstall', package],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.success(f"✅ Application désinstallée: {package}")
                return {"status": "success", "output": result.stdout}
            else:
                return {"status": "error", "error": result.stderr}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _system_reboot(self) -> Dict:
        """Redémarrer le système"""
        
        if config.security.require_confirmation:
            print("\n⚠️ Redémarrer le système ?")
            print("[1] Oui")
            print("[2] Non")
            choice = input("Choix: ").strip()
            if choice != '1':
                return {"status": "cancelled"}
        
        try:
            if config.capabilities.root_operations:
                subprocess.run(['su', '-c', 'reboot'], capture_output=True)
            else:
                subprocess.run(['reboot'], capture_output=True)
            return {"status": "success", "message": "Reboot initié"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _system_shutdown(self) -> Dict:
        """Éteindre le système"""
        
        if config.security.require_confirmation:
            print("\n⚠️ Éteindre le système ?")
            print("[1] Oui")
            print("[2] Non")
            choice = input("Choix: ").strip()
            if choice != '1':
                return {"status": "cancelled"}
        
        try:
            if config.capabilities.root_operations:
                subprocess.run(['su', '-c', 'shutdown'], capture_output=True)
            else:
                subprocess.run(['shutdown'], capture_output=True)
            return {"status": "success", "message": "Shutdown initié"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _system_info(self) -> Dict:
        """Obtenir des informations système"""
        
        info = {}
        
        try:
            # Informations CPU
            with open('/proc/cpuinfo', 'r') as f:
                cpu_info = f.read()
                info['cpu'] = cpu_info[:500]
            
            # Informations mémoire
            with open('/proc/meminfo', 'r') as f:
                mem_info = f.read()
                info['memory'] = mem_info[:500]
            
            # Version Android
            result = subprocess.run(['getprop', 'ro.build.version.release'], 
                                   capture_output=True, text=True)
            info['android_version'] = result.stdout.strip()
            
            # Modèle
            result = subprocess.run(['getprop', 'ro.product.model'], 
                                   capture_output=True, text=True)
            info['device_model'] = result.stdout.strip()
            
            return {"status": "success", "system_info": info}
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _check_security(self, step: Dict) -> bool:
        """Vérifier la sécurité de l'opération"""
        
        # Vérification du mode
        if config.mode == 'SAFE':
            return False
        
        # Vérification des opérations autorisées
        operation = step.get('operation', '')
        if operation in ['install', 'uninstall', 'delete', 'modify', 'reboot', 'shutdown']:
            if not config.capabilities.system_modification:
                return False
        
        return True
