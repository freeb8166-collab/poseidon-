#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import chromadb
from chromadb.utils import embedding_functions
from typing import Dict, List, Any
from datetime import datetime
from config import config, logger

class VectorMemory:
    """Mémoire vectorielle pour recherche sémantique"""
    
    def __init__(self):
        try:
            self.client = chromadb.PersistentClient(
                path=str(config.base_dir / "database" / "vector_store")
            )
            
            self.collection = self.client.get_or_create_collection(
                name="security_knowledge",
                embedding_function=embedding_functions.DefaultEmbeddingFunction()
            )
            logger.info("🧠 Mémoire vectorielle initialisée")
        except Exception as e:
            logger.warning(f"⚠️ Erreur vector memory: {e}")
            self.collection = None
    
    def store_knowledge(self, text: str, metadata: Dict):
        """Stocker une connaissance avec embedding"""
        
        if not self.collection:
            return
        
        doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )
        logger.debug(f"💾 Connaissance stockée: {text[:50]}...")
    
    def search_similar(self, query: str, n_results: int = 5) -> List[Dict]:
        """Rechercher des connaissances similaires"""
        
        if not self.collection:
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            return [
                {
                    "content": doc,
                    "metadata": meta
                }
                for doc, meta in zip(
                    results['documents'][0] if results['documents'] else [],
                    results['metadatas'][0] if results['metadatas'] else []
                )
            ]
        except Exception as e:
            logger.error(f"Erreur recherche vectorielle: {e}")
            return []
