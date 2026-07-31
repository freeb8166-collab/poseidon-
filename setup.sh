#!/bin/bash

echo "🛡️ Security AI Agent V1 - Installation"
echo "========================================"

# Mise à jour Termux
echo "📦 Mise à jour de Termux..."
pkg update && pkg upgrade -y

# Installation des dépendances
echo "📦 Installation des dépendances..."
pkg install -y python python-pip git
pkg install -y openssl curl wget
pkg install -y termux-api
pkg install -y android-sdk

# Installation des dépendances Python
echo "📦 Installation des dépendances Python..."
pip install -r requirements.txt

# Configuration
echo "⚙️ Configuration..."
cp .env.example .env
echo "🔑 Veuillez configurer votre clé API dans .env"

# Création des dossiers
echo "📁 Création des dossiers..."
mkdir -p database reports backups logs

# Permissions
echo "🔐 Configuration des permissions..."
termux-setup-storage
chmod +x main.py

echo "✅ Installation terminée !"
echo "📝 Lancez: python main.py"on 
