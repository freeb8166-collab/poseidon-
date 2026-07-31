#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import magic
import subprocess
from config import config, logger

class FileManager:
    """Gestionnaire de fichiers avec accès complet au système"""
    
    def __init__(self):
        self.allow_modify = config.capabilities.file_modification
        self.allow_root = config.capabilities.root_operations
        self.base_path = config.root_path
        
    async def read_file(self, file_path: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """Lire un fichier avec détection automatique"""
        
        full_path = self._resolve_path(file_path)
        
        if not full_path.exists():
            return {"status": "error", "error": "Fichier non trouvé"}
        
        try:
            # Détection du type de fichier
            file_type = magic.from_file(str(full_path))
            
            if 'text' in file_type or 'empty' in file_type:
                with open(full_path, 'r', encoding=encoding) as f:
                    content = f.read()
            else:
                # Fichier binaire
                with open(full_path, 'rb') as f:
                    content = f.read().hex()
                content = f"BINAIRE: {content[:200]}..."
            
            return {
                "status": "success",
                "path": str(full_path),
                "size": full_path.stat().st_size,
                "type": file_type,
                "content": content,
                "permissions": oct(full_path.stat().st_mode)[-3:],
                "modified": datetime.fromtimestamp(full_path.stat().st_mtime).isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def write_file(self, file_path: str, content: str, mode: str = 'w') -> Dict[str, Any]:
        """Écrire dans un fichier"""
        
        if not self.allow_modify:
            return {"status": "blocked", "error": "Modification de fichier désactivée"}
        
        full_path = self._resolve_path(file_path)
        
        # Vérification des permissions
        if not self._check_permissions(full_path):
            if self.allow_root:
                # Tentative avec root
                return await self._write_file_root(full_path, content)
            else:
                return {"status": "error", "error": "Permissions insuffisantes"}
        
        try:
            # Backup avant modification
            await self._backup_file(full_path)
            
            # Écriture
            with open(full_path, mode, encoding='utf-8') as f:
                f.write(content)
            
            logger.success(f"✅ Fichier modifié: {full_path}")
            
            return {
                "status": "success",
                "path": str(full_path),
                "size": full_path.stat().st_size,
                "modified": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def delete_file(self, file_path: str, force: bool = False) -> Dict[str, Any]:
        """Supprimer un fichier"""
        
        if not self.allow_modify:
            return {"status": "blocked", "error": "Suppression désactivée"}
        
        full_path = self._resolve_path(file_path)
        
        if not full_path.exists():
            return {"status": "error", "error": "Fichier non trouvé"}
        
        # Confirmation
        if config.security.require_confirmation:
            print(f"\n⚠️ Supprimer: {full_path}")
            print("[1] Oui")
            print("[2] Non")
            choice = input("Choix: ").strip()
            if choice != '1':
                return {"status": "cancelled"}
        
        # Backup avant suppression
        await self._backup_file(full_path)
        
        try:
            if full_path.is_file():
                full_path.unlink()
            else:
                shutil.rmtree(full_path)
            
            logger.success(f"✅ Supprimé: {full_path}")
            
            return {
                "status": "success",
                "path": str(full_path),
                "deleted": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def list_directory(self, path: str, recursive: bool = False) -> Dict[str, Any]:
        """Lister le contenu d'un répertoire"""
        
        full_path = self._resolve_path(path)
        
        if not full_path.exists() or not full_path.is_dir():
            return {"status": "error", "error": "Répertoire non trouvé"}
        
        files = []
        
        try:
            for item in full_path.iterdir():
                file_info = {
                    "name": item.name,
                    "path": str(item),
                    "is_dir": item.is_dir(),
                    "size": item.stat().st_size if item.is_file() else 0,
                    "permissions": oct(item.stat().st_mode)[-3:],
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                }
                
                if item.is_file():
                    file_info['type'] = magic.from_file(str(item))
                
                files.append(file_info)
                
                if recursive and item.is_dir():
                    sub_files = await self.list_directory(str(item), True)
                    if sub_files['status'] == 'success':
                        files.extend(sub_files['files'])
            
            return {
                "status": "success",
                "path": str(full_path),
                "files": files,
                "count": len(files)
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _backup_file(self, file_path: Path):
        """Créer un backup d'un fichier"""
        
        backup_dir = config.backups_dir / "files"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{file_path.name}_{timestamp}.backup"
        
        if file_path.exists():
            shutil.copy2(file_path, backup_path)
            logger.debug(f"💾 Backup: {backup_path}")
    
    async def _write_file_root(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Écrire un fichier avec privilèges root"""
        
        try:
            # Écrire dans un fichier temporaire
            temp_path = config.temp_dir / f"temp_{datetime.now().timestamp()}.txt"
            with open(temp_path, 'w') as f:
                f.write(content)
            
            # Copier avec root
            result = subprocess.run(
                ['su', '-c', f'cp {temp_path} {file_path}'],
                capture_output=True,
                text=True
            )
            
            temp_path.unlink()
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "path": str(file_path),
                    "root": True
                }
            else:
                return {"status": "error", "error": result.stderr}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _resolve_path(self, path: str) -> Path:
        """Résoudre le chemin complet"""
        
        if path.startswith('/'):
            return Path(path)
        elif path.startswith('~'):
            return Path(config.termux_home / path[1:])
        else:
            return Path.cwd() / path
    
    def _check_permissions(self, path: Path) -> bool:
        """Vérifier les permissions d'écriture"""
        
        if not path.exists():
            # Vérifier le parent
            return os.access(str(path.parent), os.W_OK)
        
        return os.access(str(path), os.W_OK)
