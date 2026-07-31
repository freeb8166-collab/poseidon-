#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import asyncio
import aiohttp
from typing import List, Dict, Any
from config import logger

class NetworkTool:
    """Outils réseau pour l'audit"""
    
    async def scan_ports(self, host: str, ports: List[int] = None) -> Dict[str, Any]:
        """Scanner les ports ouverts sur une cible"""
        
        if ports is None:
            ports = [21, 22, 23, 25, 80, 443, 3306, 5432, 8080, 8443]
            
        open_ports = []
        
        for port in ports:
            if await self._check_port(host, port):
                open_ports.append(port)
                
        return {
            "host": host,
            "open_ports": open_ports,
            "count": len(open_ports)
        }
    
    async def _check_port(self, host: str, port: int, timeout: float = 1) -> bool:
        """Vérifier si un port est ouvert"""
        
        try:
            reader, writer = await asyncio.open_connection(
                host, port, loop=asyncio.get_event_loop()
            )
            writer.close()
            await writer.wait_closed()
            return True
        except:
            return False
            
    async def dns_lookup(self, domain: str) -> Dict[str, Any]:
        """Résolution DNS"""
        
        try:
            ip = socket.gethostbyname(domain)
            return {
                "domain": domain,
                "ip": ip,
                "success": True
            }
        except:
            return {
                "domain": domain,
                "error": "DNS lookup failed",
                "success": False
            }
    
    async def request(self, url: str, method: str = 'GET', data: Dict = None) -> Dict[str, Any]:
        """Requête HTTP"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, json=data, timeout=10) as response:
                    return {
                        "status": "success",
                        "code": response.status,
                        "headers": dict(response.headers),
                        "body": await response.text()
                    }
        except Exception as e:
            return {"status": "error", "error": str(e)}
