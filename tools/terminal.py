#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import asyncio
from typing import Dict, Any

class TerminalTool:
    """Outils pour l'exécution de commandes terminal"""
    
    async def execute(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Exécuter une commande shell de manière sécurisée"""
        
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            return {
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore'),
                "returncode": process.returncode,
                "success": process.returncode == 0
            }
            
        except asyncio.TimeoutError:
            process.kill()
            return {
                "error": "Timeout",
                "success": False
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
