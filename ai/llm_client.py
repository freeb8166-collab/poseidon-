#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import aiohttp
import asyncio
from typing import Optional, Dict, Any, List
from config import config, logger

class LLMClient:
    """Client pour les modèles de langage"""
    
    def __init__(self):
        self.api_key = config.api_key
        self.api_url = config.api_url
        self.model = config.model
        
    async def chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """Chat avec le modèle LLM"""
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://termux.local",
            "X-Title": "SecurityAgent"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('choices'):
                            return data['choices'][0]['message']['content']
                    else:
                        error_text = await response.text()
                        logger.error(f"Erreur API {response.status}: {error_text}")
                        return f"Erreur API: {response.status}"
                        
        except Exception as e:
            logger.error(f"Erreur LLM: {str(e)}")
            return f"Erreur: {str(e)}"
