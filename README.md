# [FR] Ads Library Researcher 🕵️‍♂️🔍

> **Objectif :** Un outil d'indexation (crawler) de bibliothèques publicitaires conçu pour extraire des informations clés sur les publicités, dans le but d'identifier et de remédier aux campagnes frauduleuses (arnaques, scams).

## 📖 À propos du projet

`ads-library-researcher` est un script Python conçu pour automatiser la collecte de données issues des bibliothèques de publicités (comme Facebook Ads Library, Google Ads Transparency Center, etc.). En extrayant les métadonnées pertinentes, cet outil permet aux chercheurs en cybersécurité, aux analystes de la fraude et aux équipes de modération de détecter et de signaler plus efficacement les annonces trompeuses.

## 📂 Architecture du projet

Le projet est structuré de manière modulaire pour faciliter l'ajout de nouvelles fonctionnalités et le support de nouvelles plateformes publicitaires :

- `main.py` : Point d'entrée principal de l'application.
- `config.py` : Gestion de la configuration (clés d'API, variables d'environnement, paramètres de recherche).
- `core/` : Logique métier principale (moteurs de recherche, logique d'indexation).
- `services/` : Intégrations avec les services tiers (API des réseaux sociaux, bases de données, etc.).
- `utils/` : Fonctions utilitaires partagées (formatage des données, gestion des requêtes, logs).

### 🇬🇧 English Version (`README.md`)

# Ads Library Researcher 🕵️‍♂️🔍

> **Objective:** An ads library crawler designed to extract ad information for scam identification, analysis, and remediation.

## 📖 About the Project

`ads-library-researcher` is a Python-based tool built to automate the extraction of data from various advertisement libraries (e.g., Facebook Ads Library, Google Ads Transparency Center). By fetching and structuring relevant metadata, this tool empowers cybersecurity researchers, fraud analysts, and moderation teams to efficiently detect, track, and report deceptive ad campaigns.

## 📂 Project Structure

The repository follows a modular architecture to easily accommodate new ad platforms and feature sets:

- `main.py`: The main entry point of the application.
- `config.py`: Configuration management (API keys, environment variables, search parameters).
- `core/`: Core business logic (crawling engines, parsing logic).
- `services/`: Third-party service integrations (social media APIs, database connectors).
- `utils/`: Shared helper functions (data formatting, request handling, logging).
