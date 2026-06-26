import asyncio
import aiohttp

# Importation de la configuration
from config import logger, TARGET_PERSON

# Importation des services et outils
from services.scraper import MetaAdsScraper
from core.parser import extraire_jsons_multiples, isoler_liste_annonces, analyser_annonce_individuelle
from core.integrity import generer_integrite_globale
from utils.network import telecharger_et_hacher_image
from services.ai_client import enrichir_annonce_visuellement
from services.database import sauvegarder_annonce

async def traiter_une_annonce(annonce_brute: dict, cible: str, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore):
    """
    Fonction asynchrone qui gère le cycle de vie complet d'UNE seule annonce.
    Le sémaphore évite de surcharger la RAM et la carte graphique (Ollama).
    """
    async with semaphore:
        # 1. PARSING: Extraction textuelle sans appels réseau
        donnee_extraite = analyser_annonce_individuelle(annonce_brute)
        if not donnee_extraite:
            return None
        
        ad_id = donnee_extraite.get("ad_id")
        advertiser_id = donnee_extraite.get("advertiser_id", "inconnu")

        logger.info(f"Traitement de l'annonce {ad_id}...")

        # 2. RÉSEAU: Téléchargements parallèles (Image pub + Image profil)
        tache_dl_pub = telecharger_et_hacher_image(session, donnee_extraite.get("image_url"), f"pub_{ad_id}")
        tache_dl_profil = telecharger_et_hacher_image(session, donnee_extraite.get("profile_picture_url"), f"profil_{advertiser_id}_{ad_id}")
        
        # On attend que les deux images soient téléchargées
        (chemin_img, hash_img), (chemin_profil, hash_profil) = await asyncio.gather(tache_dl_pub, tache_dl_profil)

        # 3. INTÉGRITÉ: Construction des preuves
        donnee_extraite["chemin_image_local"] = chemin_img
        donnee_extraite["hash_image_sha256"] = hash_img
        donnee_extraite["chemin_profil_local"] = chemin_profil
        donnee_extraite["hash_profil_sha256"] = hash_profil
        donnee_extraite["hash_integrite_global"] = generer_integrite_globale(donnee_extraite, hash_img, hash_profil)

        # 4. IA VISION: Enrichissement sémantique des images téléchargées
        annonce_enrichie = await enrichir_annonce_visuellement(donnee_extraite, chemin_img, chemin_profil)

        # 5. BASE DE DONNÉES: Sauvegarde finale asynchrone
        await sauvegarder_annonce(annonce_enrichie, cible)

        return annonce_enrichie


async def main():
    logger.info("="*60)
    logger.info(f"DÉMARRAGE DU ROBOT D'INVESTIGATION META ADS")
    logger.info(f"Cible de recherche : {TARGET_PERSON}")
    logger.info("="*60)
    
    # ÉTAPE 1 : SCRAPING ET INTERCEPTION
    scraper = MetaAdsScraper()
    raw_data_list = await scraper.run_search(TARGET_PERSON)
    
    if not raw_data_list:
        logger.warning("Aucune donnée interceptée. Fin du programme.")
        return

    # ÉTAPE 2 : EXTRACTION DU TEXTE BRUT
    logger.info("Analyse des requêtes GraphQL interceptées...")
    annonces_brutes = []
    
    for raw_text in raw_data_list:
        blocs_json = extraire_jsons_multiples(raw_text)
        for bloc in blocs_json:
            annonces_brutes.extend(isoler_liste_annonces(bloc))
            
    total_annonces = len(annonces_brutes)
    if total_annonces == 0:
        logger.warning("Aucune annonce trouvée dans l'arborescence des JSON.")
        return
        
    logger.info(f"🟢 {total_annonces} annonces brutes détectées. Démarrage du pipeline IA...")

    # ÉTAPE 3 : TRAITEMENT DE MASSE ASYNCHRONE
    # On autorise un maximum de 3 annonces traitées en même temps pour protéger Ollama
    semaphore = asyncio.Semaphore(3) 
    
    # On crée une seule session HTTP pour tous les téléchargements (gain de vitesse énorme)
    async with aiohttp.ClientSession() as session:
        # On prépare la liste de nos tâches
        taches = [
            traiter_une_annonce(annonce, TARGET_PERSON, session, semaphore)
            for annonce in annonces_brutes
        ]
        
        # On lance toutes les tâches en parallèle !
        resultats = await asyncio.gather(*taches)
        
    # On compte les succès (les annonces qui n'ont pas retourné None)
    annonces_succes = [r for r in resultats if r is not None]
    
    logger.info("="*60)
    logger.info(f"EXTRACTION TERMINÉE : {len(annonces_succes)}/{total_annonces} annonces sauvegardées.")
    logger.info("="*60)

if __name__ == "__main__":
    # Pour éviter certaines erreurs sur Windows avec Asyncio
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(main())