import json
from typing import List, Dict, Any, Optional
from config import logger

def extraire_jsons_multiples(texte_brut: str) -> List[Dict[str, Any]]:
    """
    Méthode robuste utilisant JSONDecoder().raw_decode() pour extraire 
    plusieurs objets JSON valides concaténés dans une seule chaîne de texte.
    """
    decoder = json.JSONDecoder()
    texte_brut = texte_brut.strip()
    resultats = []
    
    while texte_brut:
        try:
            # On extrait le premier objet JSON et l'index de la fin de cet objet
            objet, index = decoder.raw_decode(texte_brut)
            resultats.append(objet)
            
            # On coupe le texte lu, et on nettoie les espaces avant la prochaine boucle
            texte_brut = texte_brut[index:].strip()
        except json.JSONDecodeError:
            # Si on rencontre du texte illisible à la fin, on arrête la boucle doucement
            break
            
    logger.debug(f"[Parser] {len(resultats)} blocs JSON extraits du texte brut.")
    return resultats

def isoler_liste_annonces(donnees: Any) -> List[Dict[str, Any]]:
    """
    Mécanisme Self-Healing : Cherche récursivement la liste des annonces 
    (les 'edges') peu importe la profondeur ou les changements de structure de Facebook.
    """
    if isinstance(donnees, dict):
        # On cherche la signature classique de la liste d'annonces
        if "search_results_connection" in donnees and "edges" in donnees["search_results_connection"]:
            return donnees["search_results_connection"]["edges"]
        
        # Si Facebook a changé l'arborescence, on fouille plus loin
        for cle, valeur in donnees.items():
            resultat = isoler_liste_annonces(valeur)
            if resultat:
                return resultat
                
    elif isinstance(donnees, list):
        for element in donnees:
            resultat = isoler_liste_annonces(element)
            if resultat:
                return resultat
    
    return [] # Retourne une liste vide si rien n'est trouvé

def analyser_annonce_individuelle(annonce_brute: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Approche Déterministe : Extrait les champs de l'annonce via une navigation 
    stricte dans le dictionnaire JSON, avec gestion des cas particuliers (Vidéos, Carrousels).
    """
    try:
        # 1. Sécuriser l'accès à la racine des données de l'annonce
        node = annonce_brute.get("node", {})
        collated_results = node.get("collated_results", [])
        
        if not collated_results:
            return None
            
        ad_data = collated_results[0]
        snapshot = ad_data.get("snapshot", {})

        # 2. Logique de repli pour le TEXTE
        ad_text = None
        if "body" in snapshot and isinstance(snapshot["body"], dict):
            ad_text = snapshot["body"].get("text")
            
        # Parfois Meta utilise des variables (ex: {{product.brand}}), le vrai texte est dans les 'cards'
        if (not ad_text or "{{" in ad_text) and snapshot.get("cards"):
            ad_text = snapshot["cards"][0].get("body")

        # 3. Logique de repli pour l'IMAGE
        image_url = None
        if snapshot.get("images"):
            image_url = snapshot["images"][0].get("original_image_url")
        elif snapshot.get("videos"):
            # Si c'est une vidéo, on prend la miniature
            image_url = snapshot["videos"][0].get("video_preview_image_url")
        elif snapshot.get("cards"):
            # Si c'est un carrousel, on prend la première carte
            image_url = snapshot["cards"][0].get("original_image_url")
            
        # 4. Logique de repli pour le LIEN sortant
        learn_more_url = snapshot.get("link_url")
        if (not learn_more_url or "{{" in learn_more_url) and snapshot.get("cards"):
            learn_more_url = snapshot["cards"][0].get("link_url")

        # 5. Construction du dictionnaire final standardisé
        resultat = {
            "ad_id": ad_data.get("ad_archive_id"),
            "start_date": ad_data.get("start_date"),
            "platforms": ad_data.get("publisher_platform", []),
            "ad_text": ad_text,
            "image_url": image_url,
            "versions_count": ad_data.get("collation_count"),
            "advertiser_name": snapshot.get("page_name"),
            "advertiser_id": snapshot.get("page_id"),
            "followers_count": snapshot.get("page_like_count"),
            "profile_picture_url": snapshot.get("page_profile_picture_url"),
            "learn_more_url": learn_more_url
        }

        # Sécurité supplémentaire : s'assurer qu'on a au moins un ID de publicité
        if not resultat["ad_id"]:
            return None

        return resultat

    except Exception as e:
        logger.error(f"[Parser] Impossible d'extraire les données de l'annonce : {e}")
        return None