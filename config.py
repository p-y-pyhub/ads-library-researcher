import os
import logging
from dotenv import load_dotenv

# Charge les variables d'environnement depuis un fichier .env (s'il existe)
load_dotenv()

# ==========================================
# 1. CONFIGURATION DU LOGGING
# ==========================================
# On crée un dossier pour les logs si nécessaire
DOSSIER_LOGS = "logs"
os.makedirs(DOSSIER_LOGS, exist_ok=True)

# Format des messages de log (Ex: "2023-10-27 14:30:00 - IA_VISION - INFO - Analyse réussie")
FORMAT_LOG = "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"

logging.basicConfig(
    level=logging.INFO, # Passer à logging.DEBUG pour voir absolument tout
    format=FORMAT_LOG,
    handlers=[
        logging.FileHandler(os.path.join(DOSSIER_LOGS, "app.log"), encoding='utf-8'), # Sauvegarde dans un fichier
        logging.StreamHandler() # Affiche aussi dans la console
    ]
)

# On expose une instance de logger par défaut, même si chaque fichier peut créer le sien
logger = logging.getLogger("MetaAdsScraper")

# ==========================================
# 2. VARIABLES MÉTIER ET CHEMINS
# ==========================================
# Utilisation de os.getenv pour récupérer les infos sécurisées, avec une valeur par défaut en 2ème argument
TARGET_PERSON = os.getenv("TARGET_PERSON", "Kevin O'leary")

# ==========================================
# 3. CONFIGURATION OLLAMA (IA Locale)
# ==========================================
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_URL = f"{OLLAMA_HOST}/api/generate"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e2b")
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "gemma4:e2b")

# ==========================================
# 4. CONFIGURATION SCRAPING ET RÉSEAU
# ==========================================
FB_AD_LIBRARY_URL = "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=CA&media_type=all"

# En-têtes HTTP pour se faire passer pour un vrai navigateur lors des téléchargements
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-CA,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.facebook.com/"
}

# ==========================================
# 5. CONFIGURATION BASE DE DONNÉES (MongoDB)
# ==========================================
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "registre_publicites")
COLLECTION_PUBS_NAME = os.getenv("COLLECTION_PUBS_NAME", "preuves_meta")

# ==========================================
# 6. GESTION DES FICHIERS LOCAUX
# ==========================================
DOSSIER_IMAGES = os.getenv("DOSSIER_IMAGES", "preuves_images")

# S'assurer que le dossier des images existe dès le lancement
os.makedirs(DOSSIER_IMAGES, exist_ok=True)

logger.info("Configuration chargée avec succès.")