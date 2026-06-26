import os
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from config import logger, OLLAMA_URL, OLLAMA_VISION_MODEL
from core.integrity import encoder_image_base64

from core.prompts import PROMPT_ANALYSE_PUB, PROMPT_ANALYSE_PROFIL

async def analyser_image_avec_ollama_vision(session: aiohttp.ClientSession, chemin_image: Optional[str], prompt_specifique: str) -> str:
    """
    Envoie l'image encodée et le prompt d'enquête à Ollama de manière asynchrone.
    Prend une session aiohttp en paramètre pour optimiser les connexions réseau.
    """
    if not chemin_image or not os.path.exists(chemin_image):
        return "Aucune image disponible pour analyse."

    image_base64 = encoder_image_base64(chemin_image)
    if not image_base64:
        return "Échec de l'encodage de l'image."

    payload = {
        "model": OLLAMA_VISION_MODEL,
        "prompt": prompt_specifique,
        "images": [image_base64],
        "stream": False,
        "keep_alive": 0, # Libère la VRAM immédiatement après (bon pour les petites configs)
        "options": {
            "temperature": 0.1,
            "top_p": 0.1,
            "top_k": 15
        }
    }

    try:
        logger.debug(f"[IA-Vision] Début de l'analyse pour {os.path.basename(chemin_image)}...")
        # Timeout généreux (60s) car l'inférence vision peut être gourmande
        async with session.post(OLLAMA_URL, json=payload, timeout=aiohttp.ClientTimeout(total=210)) as reponse:
            reponse.raise_for_status()
            data = await reponse.json()
            return data.get("response", "Aucune description générée.").strip()
            
    except asyncio.TimeoutError:
        logger.error(f"[Erreur IA-Vision] Délai d'attente dépassé pour {chemin_image}.")
        return "Échec : Le modèle a mis trop de temps à répondre."
    except Exception as e:
        logger.error(f"[Erreur IA-Vision] Échec de l'analyse d'image : {e}")
        return f"Échec de l'analyse visuelle automatique : {e}"

async def enrichir_annonce_visuellement(annonce: Dict[str, Any], chemin_img_pub: Optional[str], chemin_img_profil: Optional[str]) -> Dict[str, Any]:
    """
    Fonction orchestratrice qui lance les deux analyses visuelles (Pub + Profil) 
    EN PARALLÈLE pour gagner un maximum de temps.
    """
    logger.info(f"[IA] Démarrage de l'enrichissement visuel pour l'annonce {annonce.get('ad_id')}")
    
    # prompt_pub = """
    #         Retourne UNIQUEMENT un objet JSON valide contenant l'analyse factuelle de cette image publicitaire Facebook.
    #         Ne fais AUCUNE phrase d'introduction ni de conclusion. Réponds directement en JSON avec ces clés exactes :
    #         {
    #         "texte_incruste": "La transcription mot à mot de tout texte visible sur l'image (ou null si aucun)",
    #         "description_personnes": "S'il y a des humains, décris leur nombre, genre apparent, tranche d'âge, couleur de cheveux, vêtements (ex: Homme, environ 50 ans, complet veston, cheveux gris)",
    #         "description_logos_et_insignes": "Décris les formes, couleurs et textes des logos ou symboles visibles (ex: Carré bleu avec un symbole blanc, texte 'Nouvelles')",
    #         "elements_decor": "Liste des éléments visuels clés (ex: Graphique boursier en arrière-plan, flèche rouge pointant vers le bas, studio de télévision, liasse d'argent)"            }
    #     """
    
    # prompt_profil = """
    #         Retourne UNIQUEMENT un objet JSON valide contenant l'analyse factuelle de cette image de profil d'annonceur.
    #         Ne fais AUCUNE phrase d'introduction ni de conclusion. Réponds directement en JSON avec ces clés exactes :
    #         {
    #         "nature_avatar": "Choix parmi: logo_entreprise, visage_humain, illustration_generique, image_de_stock",
    #         "texte_visible": "Texte ou initiales visibles sur l'avatar (ou null)",
    #         "coherence_sémantique": "Évaluation courte sur la légitimité visuelle de l'avatar par rapport à un annonceur réel"
    #         }
    #     """

    # On utilise une seule session HTTP pour les deux requêtes (plus performant)
    async with aiohttp.ClientSession() as session:
        # asyncio.gather lance les fonctions en même temps et attend que toutes soient terminées
        tache_pub = analyser_image_avec_ollama_vision(session, chemin_img_pub, PROMPT_ANALYSE_PUB)
        tache_profil = analyser_image_avec_ollama_vision(session, chemin_img_profil, PROMPT_ANALYSE_PROFIL)
        
        # On récupère les résultats dans l'ordre où on a lancé les tâches
        desc_pub, desc_profil = await asyncio.gather(tache_pub, tache_profil)

    # On injecte les résultats dans le dictionnaire de l'annonce
    annonce["description_visuelle_pub"] = desc_pub
    annonce["description_visuelle_profil"] = desc_profil
    
    return annonce