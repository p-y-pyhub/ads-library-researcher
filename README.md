# [FR] Ads Library Researcher 🕵️‍♂️🔍

## Objectif du Projet
**Meta Ads Library Researcher** est un robot d'investigation automatisé conçu pour intercepter, extraire, sécuriser et analyser les publicités diffusées sur la bibliothèque publicitaire de Meta (Facebook). Ce système capture les requêtes réseau, extrait les métadonnées complexes, génère des preuves cryptographiques d'intégrité et enrichit les données via une intelligence artificielle locale (Ollama) avant de les stocker.

## Architecture et Flux de Traitement

Le pipeline de traitement est entièrement asynchrone pour maximiser les performances.

* **1. Interception Réseau (Scraping) :** Un navigateur piloté par Playwright effectue une recherche ciblée et écoute passivement le trafic réseau pour isoler les réponses GraphQL de Meta.
* **2. Extraction Tolérante aux Fautes (Parsing) :** Les données textuelles brutes sont traitées par un décodeur JSON capable d'isoler des blocs multiples.
* **3. Téléchargements Parallèles :** Les images des publicités et des profils annonceurs sont téléchargées de manière concurrente avec `aiohttp`.
* **4. Scellement Cryptographique (Integrity) :** Le système calcule une empreinte globale combinant les textes et les images pour garantir que la preuve publicitaire est mathématiquement traçable.
* **5. Analyse Sémantique (IA Vision) :** Les images téléchargées sont envoyées à un modèle de vision local (Ollama) pour extraire factuellement le texte incrusté, la description des personnes, les logos et la cohérence des profils.
* **6. Stockage (Database) :** Les annonces enrichies sont sauvegardées dans MongoDB avec une logique d'Upsert (mise à jour ou insertion) basée sur l'identifiant unique de la publicité.

## Structure des Fichiers

| Dossier / Fichier | Responsabilité Technique |
| :--- | :--- |
| **`main.py`** | Point d'entrée asynchrone orchestrant le pipeline, gérant un sémaphore de concurrence (limité à 3) pour protéger les ressources de l'IA locale. |
| **`config.py`** | Centralisation des variables d'environnement, configuration du logging (console et fichier) et des constantes HTTP. |
| **`core/parser.py`** | Mécanisme de *Self-Healing* pour naviguer récursivement dans les structures JSON changeantes de Facebook et extraire les nœuds publicitaires. |
| **`core/integrity.py`** | Encodage Base64 et hachage SHA-256 en flux (chunks) pour les fichiers volumineux sans saturer la RAM. |
| **`core/prompts.py`** | Stockage strict des instructions JSON fournies au modèle de vision pour l'analyse factuelle. |
| **`services/scraper.py`** | Agent Playwright (Chromium) qui simule le comportement humain et intercepte les flux `search_results`. |
| **`services/ai_client.py`** | Client HTTP asynchrone pour interroger l'API locale d'Ollama avec les images encodées. |
| **`services/database.py`** | Connexion asynchrone via Motor, gestion des timestamps en UTC et requêtes d'Upsert MongoDB. |
| **`utils/network.py`** | Sauvegarde locale des flux binaires d'images via `aiofiles` avec calcul de hash à la volée. |

## Intégrité des Preuves (Cryptographie)

Pour assurer que le "dossier de preuve" est inviolable, le module `integrity.py` génère une empreinte stricte. La formule utilisée pour ce scellement global est la suivante :

Empreinte = SHA-256(ID_ad + ID_adv + Texte_ad + Hash_img + Hash_prof)

Cette méthode garantit que toute modification ultérieure d'un seul pixel de l'image ou d'une seule lettre du texte publicitaire invalidera le hash global.

## Configuration Environnementale (`.env`)

Le projet repose sur plusieurs variables d'environnement gérées par `dotenv`.

| Variable | Description | Valeur par défaut |
| :--- | :--- | :--- |
| `TARGET_PERSON` | La personnalité ou l'entité ciblée par l'investigation | `Kevin O'leary` |
| `OLLAMA_HOST` | Adresse locale ou distante du serveur Ollama | `http://localhost:11434` |
| `OLLAMA_MODEL` | Modèle linguistique standard utilisé | `gemma4:e2b` |
| `OLLAMA_VISION_MODEL`| Modèle multimodal utilisé pour l'analyse d'images | `gemma4:e2b` |
| `MONGO_URI` | Chaîne de connexion à la base de données MongoDB | `mongodb://localhost:27017/` |
| `DB_NAME` | Nom de la base de données principale | `registre_publicites` |
| `COLLECTION_PUBS_NAME`| Nom de la collection stockant les documents finaux | `preuves_meta` |
| `DOSSIER_IMAGES` | Chemin du dossier local pour le stockage des preuves visuelles | `preuves_images` |

## Prérequis et Installation

* **Python 3.9+** : Requis pour les fonctionnalités avancées d'`asyncio`.
* **MongoDB** : Doit être actif localement ou via un cluster distant.
* **Ollama** : Doit être


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
