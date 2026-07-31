#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm

from config import config, logger
from core.planner import Planner
from core.executor import Executor
from core.evaluator import Evaluator
from core.adaptation import AdaptationEngine
from core.reporting import ReportGenerator
from ai.llm_client import LLMClient
from ai.memory import MemorySystem
from tools.logger import SecurityLogger

console = Console()

class SecurityAgent:
    """Agent IA principal d'audit de sécurité"""
    
    def __init__(self):
        self.llm = LLMClient()
        self.planner = Planner(self.llm)
        self.executor = Executor()
        self.evaluator = Evaluator(self.llm)
        self.adaptation = AdaptationEngine(self.llm)
        self.report_generator = ReportGenerator()
        self.memory = MemorySystem()
        self.logger = SecurityLogger()
        
        self.current_mission = None
        self.mission_plan = None
        self.results = []
        self.errors = []
        self.is_running = False
        
    async def start_mission(self, mission: str, target: str) -> Dict[str, Any]:
        """Démarrer une mission d'audit"""
        
        if self.is_running:
            return {"error": "Une mission est déjà en cours", "status": "busy"}
        
        self.is_running = True
        
        console.print(Panel.fit(
            f"[bold cyan]🛡️  MISSION D'AUDIT DE SÉCURITÉ[/bold cyan]\n"
            f"🔍 {mission}\n"
            f"🎯 Cible: {target}",
            border_style="cyan"
        ))
        
        # Vérification de la cible
        if not self._validate_target(target):
            self.is_running = False
            return {"error": "Cible non autorisée", "status": "rejected"}
        
        self.current_mission = {
            "mission": mission,
            "target": target,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Phase 1: Analyse et planification
            self.logger.info("🧠 Analyse de la mission en cours...")
            plan = await self.planner.create_plan(mission, target)
            
            if not plan:
                self.is_running = False
                return {"error": "Impossible de créer un plan", "status": "failed"}
            
            self.mission_plan = plan
            self.logger.success(f"📋 Plan créé: {len(plan['steps'])} étapes")
            
            # Phase 2: Exécution
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("[cyan]Exécution de l'audit...", total=len(plan['steps']))
                
                for step in plan['steps']:
                    progress.update(task, description=f"[cyan]{step['description']}")
                    
                    try:
                        result = await self._execute_step(step)
                        self.results.append(result)
                        
                        if result.get('status') == 'error':
                            self.logger.warning(f"⚠️ Erreur détectée: {result.get('error')}")
                            adapted_step = await self.adaptation.adapt(step, result)
                            
                            if adapted_step:
                                self.logger.info("🔄 Stratégie adaptée, nouvelle tentative...")
                                new_result = await self._execute_step(adapted_step)
                                self.results.append(new_result)
                        
                        progress.advance(task)
                        
                    except Exception as e:
                        self.logger.error(f"❌ Erreur critique: {str(e)}")
                        self.errors.append({"step": step, "error": str(e)})
            
            # Phase 3: Évaluation
            self.logger.info("📊 Évaluation des résultats...")
            evaluation = await self.evaluator.evaluate(self.results)
            
            # Phase 4: Rapport
            self.logger.info("📝 Génération du rapport...")
            report = await self.report_generator.generate(
                mission=self.current_mission,
                plan=self.mission_plan,
                results=self.results,
                evaluation=evaluation
            )
            
            # Phase 5: Apprentissage
            self.logger.info("🧠 Mise à jour de la mémoire...")
            await self.memory.store_experience({
                "mission": self.current_mission,
                "plan": self.mission_plan,
                "results": self.results,
                "errors": self.errors,
                "evaluation": evaluation
            })
            
            console.print(Panel(
                f"[bold green]✅ AUDIT TERMINÉ[/bold green]\n"
                f"📊 {len(self.results)} vérifications effectuées\n"
                f"⚠️ {len(self.errors)} erreurs rencontrées\n"
                f"📄 Rapport: {report['path']}",
                border_style="green"
            ))
            
            self.is_running = False
            
            return {
                "status": "completed",
                "results": self.results,
                "report": report
            }
            
        except Exception as e:
            self.is_running = False
            self.logger.error(f"❌ Erreur mission: {e}")
            return {"error": str(e), "status": "failed"}
    
    def _validate_target(self, target: str) -> bool:
        """Valider la cible par rapport aux règles de sécurité"""
        
        for allowed in config.security.allowed_targets:
            if '*' in allowed:
                import re
                pattern = allowed.replace('*', '.*')
                if re.match(pattern, target):
                    return True
            elif target == allowed:
                return True
        
        self.logger.error(f"🚫 Cible non autorisée: {target}")
        return False
    
    async def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Exécuter une étape du plan"""
        
        try:
            self.logger.debug(f"🔧 Exécution: {step['description']}")
            result = await self.executor.execute(step)
            
            result['timestamp'] = datetime.now().isoformat()
            result['step'] = step.get('id')
            
            if result.get('status') == 'success':
                self.logger.info(f"✅ Étape réussie: {step.get('id', 'inconnue')}")
            else:
                self.logger.warning(f"⚠️ Étape: {step.get('id', 'inconnue')} - {result.get('error', 'Erreur inconnue')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Étape échouée: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "step": step.get('id'),
                "timestamp": datetime.now().isoformat()
            }

    async def interactive_mode(self):
        """Mode interactif pour discussions avec l'agent"""
        
        console.print("[bold cyan]🛡️  Mode Interactif - Agent IA[/bold cyan]")
        console.print("Tapez 'mission' pour démarrer un audit")
        console.print("Tapez 'historique' pour voir les missions passées")
        console.print("Tapez 'install' pour installer un APK")
        console.print("Tapez 'open' pour ouvrir une application")
        console.print("Tapez 'read' pour lire un fichier")
        console.print("Tapez 'modify' pour modifier un fichier")
        console.print("Tapez 'quit' pour quitter\n")
        
        while True:
            try:
                cmd = input("🧑> ").strip()
                
                if cmd.lower() in ['quit', 'exit']:
                    break
                elif cmd.lower() == 'historique':
                    await self._show_history()
                elif cmd.lower().startswith('mission'):
                    if self.is_running:
                        print("⏳ Une mission est déjà en cours...")
                        continue
                    target = input("🎯 Cible à analyser: ").strip()
                    if target:
                        await self.start_mission(cmd[7:].strip(), target)
                elif cmd.lower().startswith('install'):
                    apk_path = input("📦 Chemin de l'APK: ").strip()
                    if apk_path:
                        from tools.app_manager import AppManager
                        app = AppManager()
                        result = await app.install_apk(apk_path)
                        console.print(f"[green]{result}[/green]")
                elif cmd.lower().startswith('open'):
                    package = input("📱 Nom du package: ").strip()
                    if package:
                        from tools.app_manager import AppManager
                        app = AppManager()
                        result = await app.open_app(package)
                        console.print(f"[green]{result}[/green]")
                elif cmd.lower().startswith('read'):
                    path = input("📄 Chemin du fichier: ").strip()
                    if path:
                        from tools.files import FileManager
                        files = FileManager()
                        result = await files.read_file(path)
                        if result['status'] == 'success':
                            console.print(f"[cyan]{result['content'][:500]}...[/cyan]")
                        else:
                            console.print(f"[red]{result}[/red]")
                elif cmd.lower().startswith('modify'):
                    path = input("📄 Chemin du fichier: ").strip()
                    content = input("📝 Nouveau contenu: ").strip()
                    if path and content:
                        from tools.files import FileManager
                        files = FileManager()
                        result = await files.write_file(path, content)
                        console.print(f"[green]{result}[/green]")
                else:
                    # Chat avec l'agent
                    response = await self.llm.chat(cmd)
                    console.print(f"🤖 {response}")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                console.print(f"[red]Erreur: {str(e)}[/red]")
    
    async def _show_history(self):
        """Afficher l'historique des missions"""
        
        history = await self.memory.get_history()
        
        table = Table(title="Historique des Missions")
        table.add_column("Date", style="cyan")
        table.add_column("Mission", style="white")
        table.add_column("Cible", style="yellow")
        table.add_column("Statut", style="green")
        
        for entry in history[-10:]:
            table.add_row(
                entry.get('timestamp', '')[:19],
                entry.get('mission', '')[:30],
                entry.get('target', '')[:20],
                entry.get('status', '')
            )
        
        console.print(table) et 
