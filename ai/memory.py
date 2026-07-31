#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from config import config, logger

class MemorySystem:
    """Système de mémoire persistante"""
    
    def __init__(self):
        self.db_path = config.database_path
        self._init_db()
        
    def _init_db(self):
        """Initialiser la base de données"""
        
        self.db_path.parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                mission TEXT,
                target TEXT,
                status TEXT,
                results TEXT,
                evaluation TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                error TEXT,
                context TEXT,
                solution TEXT,
                success BOOLEAN
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS solutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_pattern TEXT,
                alternative_step TEXT,
                success_count INTEGER DEFAULT 0,
                last_used TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    async def store_experience(self, data: Dict[str, Any]):
        """Stocker une expérience"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO missions (timestamp, mission, target, status, results, evaluation)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            data.get('mission', {}).get('mission', ''),
            data.get('mission', {}).get('target', ''),
            data.get('evaluation', {}).get('status', 'completed'),
            json.dumps(data.get('results', [])),
            json.dumps(data.get('evaluation', {}))
        ))
        
        for error in data.get('errors', []):
            cursor.execute('''
                INSERT INTO errors (timestamp, error, context, solution)
                VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                error.get('error', ''),
                json.dumps(error.get('step', {})),
                json.dumps({})
            ))
        
        conn.commit()
        conn.close()
        
    async def find_solution(self, error: str) -> Optional[Dict[str, Any]]:
        """Trouver une solution existante pour une erreur"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT error_pattern, alternative_step FROM solutions
            WHERE ? LIKE '%' || error_pattern || '%'
            ORDER BY success_count DESC
            LIMIT 1
        ''', (error,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "error_pattern": result[0],
                "alternative_step": json.loads(result[1])
            }
        return None
        
    async def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtenir l'historique des missions"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, mission, target, status
            FROM missions
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {"timestamp": r[0], "mission": r[1], "target": r[2], "status": r[3]}
            for r in results
        ]
