#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from config import config, logger

class EvidenceCollector:
    """Collecteur de preuves"""
    
    def __init__(self):
        self.evidence_dir = config.reports_dir / "evidence"
        self.evidence_dir.mkdir(exist_ok=True)
        self.evidence = []
        
    async def collect(self, data_type: str, data: Any, source: str = None) -> Dict[str, Any]:
        """Collecter une preuve"""
        
        evidence = {
            "id": hashlib.md5(f"{datetime.now().isoformat()}{data_type}".encode()).hexdigest()[:8],
            "type": data_type,
            "data": data,
            "source": source or "unknown",
            "timestamp": datetime.now().isoformat(),
            "hash": hashlib.sha256(json.dumps(data, default=str).encode()).hexdigest()
        }
        
        self.evidence.append(evidence)
        
        # Sauvegarder
        await self._save_evidence(evidence)
        
        logger.debug(f"🔍 Preuve collectée: {evidence['id']}")
        
        return evidence
    
    async def _save_evidence(self, evidence: Dict):
        """Sauvegarder une preuve"""
        
        evidence_file = self.evidence_dir / f"evidence_{evidence['id']}.json"
        with open(evidence_file, 'w', encoding='utf-8') as f:
            json.dump(evidence, f, indent=2, default=str)
    
    async def get_all(self) -> List[Dict]:
        """Obtenir toutes les preuves"""
        
        return self.evidence
    
    async def get_by_type(self, data_type: str) -> List[Dict]:
        """Obtenir les preuves par type"""
        
        return [e for e in self.evidence if e['type'] == data_type]
    
    async def verify_hash(self, evidence_id: str) -> bool:
        """Vérifier l'intégrité d'une preuve"""
        
        evidence_file = self.evidence_dir / f"evidence_{evidence_id}.json"
        
        if not evidence_file.exists():
            return False
        
        try:
            with open(evidence_file, 'r') as f:
                evidence = json.load(f)
            
            # Recalculer le hash
            data_hash = hashlib.sha256(json.dumps(evidence['data'], default=str).encode()).hexdigest()
            
            return data_hash == evidence['hash']
            
        except:
            return False
