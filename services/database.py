import traceback
from datetime import datetime, timezone
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient

# Importation de la configuration centralisée
from config import logger, MONGO_URI, DB_NAME, COLLECTION_PUBS_NAME

# ==========================================
# INITIALISATION DE LA CONNEXION
# ==========================================
# On crée le client MongoDB au chargement du module.
# serverSelectionTimeoutMS=5000 évite que le script tourne dans le vide pendant 30s 
# si ton serveur MongoDB local n'est pas allumé.
try:
    client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    collection_pubs = db[COLLECTION_PUBS_NAME]
except Exception as e:
    logger.critical(f"[Base de données] Impossible d'initialiser la connexion MongoDB : {e}")

async def sauvegarder_annonce(annonce_extraite: Dict[str, Any], cible_recherche: str) -> bool:
    """
    Insère ou met à jour une annonce dans MongoDB de manière asynchrone.
    Utilise le mécanisme 'Upsert' (Update + Insert).
    """
    ad_id = annonce_extraite.get("ad_id")
    if not ad_id:
        logger.warning("[Base de données] Tentative de sauvegarde d'une annonce sans ad_id. Ignoré.")
        return False

    # 1. Ajout du contexte métier
    annonce_extraite["cible_recherche"] = cible_recherche

    # 2. Gestion stricte du temps (Toujours stocker en UTC en base de données)
    maintenant_utc = datetime.now(timezone.utc).isoformat()
    
    # 3. Préparation de l'opération MongoDB
    # $set met à jour les données fraîchement scrapées et la date de dernière vue
    # $setOnInsert n'ajoute la date de découverte QUE si c'est la toute première fois qu'on voit cette pub
    operation_mise_a_jour = {
        "$set": {
            **annonce_extraite,
            "date_derniere_vue_utc": maintenant_utc
        },
        "$setOnInsert": {
            "date_decouverte_utc": maintenant_utc
        }
    }

    # 4. Exécution asynchrone de la requête
    try:
        # await rend l'appel non-bloquant pour le reste du programme
        resultat = await collection_pubs.update_one(
            {"ad_id": ad_id}, 
            operation_mise_a_jour, 
            upsert=True
        )
        
        # On log le résultat pour savoir si on a découvert une nouvelle fraude ou mis à jour une existante
        if resultat.upserted_id:
            logger.info(f"[Base de données] 🟢 NOUVELLE annonce découverte et sauvegardée : {ad_id}")
        else:
            logger.debug(f"[Base de données] 🔵 Annonce déjà connue, mise à jour effectuée : {ad_id}")
            
        return True
        
    except Exception as e:
        logger.error(f"[Erreur Base de données] Échec de la sauvegarde pour l'annonce {ad_id} : {e}")
        # En mode debug, on peut afficher la trace complète de l'erreur pour comprendre ce qui a planté
        logger.debug(traceback.format_exc())
        return False