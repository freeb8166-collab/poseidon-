#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os
import shutil
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests
from config import config, logger

class AppManager:
    """Gestionnaire d'applications Android"""
    
    def __init__(self):
        self.installed_apps = []
        self.apk_cache = config.termux_home / ".apk_cache"
        self.apk_cache.mkdir(exist_ok=True)
        self.allow_install = config.capabilities.apk_install
        
    async def install_apk(self, apk_path: str, source: str = "file") -> Dict[str, Any]:
        """Installer un APK"""
        
        if not self.allow_install:
            return {"status": "blocked", "error": "Installation APK désactivée"}
        
        if not os.path.exists(apk_path) and source != "url":
            return {"status": "error", "error": f"APK non trouvé: {apk_path}"}
        
        if source == "url":
            downloaded = await self._download_apk(apk_path)
            if not downloaded['success']:
                return downloaded
            apk_path = downloaded['path']
        
        analysis = await self._analyze_apk(apk_path)
        logger.info(f"📊 Analyse APK: {analysis}")
        
        if config.security.require_confirmation:
            confirmed = await self._request_confirmation(analysis)
            if not confirmed:
                return {"status": "cancelled", "message": "Installation annulée"}
        
        try:
            result = subprocess.run(
                ['pm', 'install', '-r', apk_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.success(f"✅ APK installé: {apk_path}")
                await self._backup_apk(apk_path)
                
                return {
                    "status": "success",
                    "output": result.stdout,
                    "package": self._extract_package_name(apk_path),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                if config.capabilities.root_operations:
                    logger.info("🔑 Tentative avec privilèges root...")
                    root_result = subprocess.run(
                        ['su', '-c', f'pm install -r {apk_path}'],
                        capture_output=True,
                        text=True
                    )
                    if root_result.returncode == 0:
                        return {"status": "success", "output": root_result.stdout}
                
                return {
                    "status": "error",
                    "error": result.stderr,
                    "code": result.returncode
                }
                
        except subprocess.TimeoutExpired:
            return {"status": "error", "error": "Timeout lors de l'installation"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def open_app(self, package_name: str, activity: str = None) -> Dict[str, Any]:
        """Ouvrir une application"""
        
        if not config.capabilities.app_control:
            return {"status": "blocked", "error": "Contrôle des apps désactivé"}
        
        try:
            if activity:
                cmd = ['am', 'start', '-n', f'{package_name}/{activity}']
            else:
                cmd = ['am', 'start', '-n', package_name]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.success(f"✅ Application ouverte: {package_name}")
                return {"status": "success", "package": package_name}
            else:
                return {"status": "error", "error": result.stderr}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def create_account(self, app_package: str, credentials: Dict) -> Dict[str, Any]:
        """Créer un compte pour une application"""
        
        if not config.capabilities.account_creation:
            return {"status": "blocked", "error": "Création de compte désactivée"}
        
        logger.info(f"🔐 Création de compte pour: {app_package}")
        
        try:
            uri = f"content://{app_package}/accounts"
            
            result = subprocess.run([
                'content', 'insert',
                '--uri', uri,
                '--bind', f'name:s:{credentials.get("username", "")}',
                '--bind', f'password:s:{credentials.get("password", "")}',
                '--bind', f'email:s:{credentials.get("email", "")}'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.success(f"✅ Compte créé pour: {app_package}")
                return {"status": "success", "package": app_package}
            else:
                return {"status": "error", "error": result.stderr}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _download_apk(self, url: str) -> Dict[str, Any]:
        try:
            filename = url.split('/')[-1]
            if not filename.endswith('.apk'):
                filename += '.apk'
            
            download_path = self.apk_cache / filename
            
            logger.info(f"⬇️ Téléchargement de: {url}")
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.success(f"✅ APK téléchargé: {download_path}")
            
            return {
                "success": True,
                "path": str(download_path),
                "size": download_path.stat().st_size
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur téléchargement: {e}")
            return {"success": False, "error": str(e)}
    
    async def _analyze_apk(self, apk_path: str) -> Dict[str, Any]:
        analysis = {
            "path": apk_path,
            "size": os.path.getsize(apk_path),
            "permissions": [],
            "risk_level": "unknown"
        }
        
        try:
            result = subprocess.run(
                ['aapt', 'dump', 'badging', apk_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                import re
                permissions = re.findall(r"uses-permission: name='(.*?)'", result.stdout)
                analysis['permissions'] = permissions
                
                dangerous_perms = [
                    'READ_CONTACTS', 'WRITE_CONTACTS',
                    'READ_SMS', 'WRITE_SMS',
                    'CAMERA', 'RECORD_AUDIO',
                    'READ_PHONE_STATE', 'ACCESS_FINE_LOCATION'
                ]
                
                risk_count = sum(1 for p in permissions if any(dp in p for dp in dangerous_perms))
                
                if risk_count > 5:
                    analysis['risk_level'] = 'HIGH'
                elif risk_count > 2:
                    analysis['risk_level'] = 'MEDIUM'
                else:
                    analysis['risk_level'] = 'LOW'
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur analyse APK: {e}")
        
        return analysis
    
    async def _request_confirmation(self, analysis: Dict) -> bool:
        print("\n" + "="*50)
        print("⚠️ CONFIRMATION D'INSTALLATION REQUISE")
        print("="*50)
        print(f"📦 Fichier: {analysis.get('path', '')}")
        print(f"📊 Taille: {analysis.get('size', 0) / 1024 / 1024:.2f} MB")
        print(f"🔐 Permissions: {len(analysis.get('permissions', []))}")
        print(f"⚠️ Risque: {analysis.get('risk_level', 'UNKNOWN')}")
        print("="*50)
        print("[1] ✅ Installer")
        print("[2] ❌ Refuser")
        print("="*50)
        
        choice = input("Votre choix: ").strip()
        return choice == '1'
    
    async def _backup_apk(self, apk_path: str):
        backup_dir = config.backups_dir / "apks"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"backup_{timestamp}_{Path(apk_path).name}"
        
        shutil.copy2(apk_path, backup_path)
        logger.debug(f"💾 Backup APK: {backup_path}")
    
    def _extract_package_name(self, apk_path: str) -> str:
        try:
            result = subprocess.run(
                ['aapt', 'dump', 'badging', apk_path],
                capture_output=True,
                text=True
            )
            import re
            match = re.search(r"package: name='(.*?)'", result.stdout)
            if match:
                return match.group(1)
        except:
            pass
        return "unknown"
