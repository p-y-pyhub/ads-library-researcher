import os
import base64
import hashlib
from typing import Optional, Dict, Any
from config import logger

def encoder_image_base64(chemin_image: str) -> Optional[str]:
    """
    Lit une image physique sur le disque et la traduit en texte Base64.
    Nécessaire pour envoyer des images locales aux modèles de vision (ex: Ollama).
    """
    if not chemin_image or not os.path.exists(chemin_image):
        logger.warning(f"[Integrity] Fichier introuvable pour encodage Base64 : {chemin_image}")
        return None
        
    try:
        # Lecture en mode binaire ('rb')
        with open(chemin_image, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"[Integrity] Impossible d'encoder l'image {chemin_image} : {e}")
        return None

def calculer_hash_fichier(chemin_fichier: str) -> Optional[str]:
    """
    Calcule l'empreinte SHA-256 d'un fichier sur le disque.
    Lecture par blocs (chunks) pour ne pas saturer la RAM si le fichier est volumineux.
    """
    if not chemin_fichier or not os.path.exists(chemin_fichier):
        return None
        
    sha256_hash = hashlib.sha256()
    try:
        with open(chemin_fichier, "rb") as f:
            # Lecture par blocs de 8 Ko (8192 octets)
            for bloc in iter(lambda: f.read(8192), b""):
                sha256_hash.update(bloc)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"[Integrity] Erreur lors du calcul du hash pour {chemin_fichier} : {e}")
        return None

def generer_integrite_globale(donnees_pub: Dict[str, Any], hash_image: Optional[str], hash_profil: Optional[str]) -> str:
    """
    Crée une empreinte unique (SHA-256) combinant les métadonnées textuelles cruciales 
    et les empreintes des images associées. 
    Cela garantit que le "dossier de preuve" est inviolable et mathématiquement traçable.
    """
    ad_id = donnees_pub.get('ad_id', '')
    advertiser_id = donnees_pub.get('advertiser_id', '')
    ad_text = donnees_pub.get('ad_text', '') or ''
    
    # On gère élégamment les cas où l'image n'a pas pu être téléchargée
    hash_img_str = hash_image or "NO_IMAGE"
    hash_prof_str = hash_profil or "NO_PROFILE"
    
    # Création de la chaîne de preuve stricte
    chaine_preuve = f"{ad_id}|{advertiser_id}|{ad_text}|{hash_img_str}|{hash_prof_str}"
    
    # Encodage en bytes puis hachage
    empreinte = hashlib.sha256(chaine_preuve.encode('utf-8')).hexdigest()
    
    logger.debug(f"[Integrity] Hash global généré pour l'annonce {ad_id} : {empreinte[:8]}...")
    return empreinte