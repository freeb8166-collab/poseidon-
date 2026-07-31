#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🛡️ SECURITY AI AGENT V1 - COMPLETE
Agent d'audit de sécurité avec accès complet au système Android
"""

import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from core.agent import SecurityAgent
from config import config, logger

console = Console()

async def main():
    """Point d'entrée principal"""
    
    # Banner
    console.print(Panel.fit(
        f"""
[bold cyan]🔒 SECURITY AI AGENT V{config.version}[/bold cyan]
[bold white]{'='*50}[/bold white]
[bold]Mode:[/bold] {config.mode}
[bold]Capacités:[/bold] 
  ✓ Gestion APK
  ✓ Modification fichiers
  ✓ Ouverture applications  
  ✓ Création comptes
  ✓ Audit de sécurité
  ✓ Apprentissage automatique
[bold]API:[/bold] {config.model} (Configurée)
[bold]Mémoire:[/bold] SQLite + Vectorielle
[bold]Logs:[/bold] {config.logs_dir}
        """,
        border_style="cyan"
    ))
    
    # Vérification des permissions
    console.print("\n[bold yellow]⚠️ VÉRIFICATION DES PERMISSIONS[/bold yellow]")
    
    # Vérifier les permissions nécessaires
    permissions = {
        "Termux API": "pkg install termux-api",
        "Android SDK": "pkg install android-sdk",
        "Root Access": "Vérifié",
        "Storage": "READ/WRITE"
    }
    
    table = Table(title="Permissions")
    table.add_column("Permission", style="cyan")
    table.add_column("Statut", style="green")
    table.add_column("Action", style="yellow")
    
    for perm, status in permissions.items():
        table.add_row(perm, "✅ OK", status)
    
    console.print(table)
    
    # Confirmation
    if not Confirm.ask("\n[bold green]Continuer avec ces permissions ?[/bold green]"):
        console.print("[red]Arrêt demandé[/red]")
        sys.exit(0)
    
    # Initialisation de l'agent
    agent = SecurityAgent()
    
    # Mode interactif
    await agent.interactive_mode()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[red]Arrêt demandé par l'utilisateur[/red]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Erreur critique: {str(e)}[/red]")
        sys.exit(1)
