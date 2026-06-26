import os
import hashlib
import aiohttp
import aiofiles
from typing import Tuple, Optional

# Importation de la configuration centralisée
from config import logger, HTTP_HEADERS, DOSSIER_IMAGES

async def telecharger_et_hacher_image(session: aiohttp.ClientSession, url: Optional[str], nom_fichier: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Télécharge une image de manière asynchrone, la sauvegarde localement 
    et calcule son hash SHA-256 à la volée (en streaming).
    
    Retourne un tuple: (chemin_local, hash_sha256)
    """
    if not url:
        return None, None

    chemin_local = os.path.join(DOSSIER_IMAGES, f"{nom_fichier}.jpg")
    sha256_hash = hashlib.sha256()

    try:
        # On utilise la session partagée pour faire la requête HTTP
        # Timeout de 15 secondes pour éviter de bloquer sur une image morte
        async with session.get(url, headers=HTTP_HEADERS, timeout=aiohttp.ClientTimeout(total=15)) as reponse:
            reponse.raise_for_status() # Vérifie que le code HTTP est 200 OK

            # aiofiles permet d'écrire sur le disque sans bloquer la boucle asyncio
            async with aiofiles.open(chemin_local, 'wb') as fichier:
                
                # Lecture en streaming (par blocs de 8 Ko)
                async for bloc in reponse.content.iter_chunked(8192):
                    await fichier.write(bloc)
                    sha256_hash.update(bloc) # On hache pendant qu'on écrit
                    
            hash_image = sha256_hash.hexdigest()
            logger.debug(f"[Réseau] Image téléchargée et hachée avec succès : {chemin_local}")
            return chemin_local, hash_image
            
    except aiohttp.ClientError as e:
        logger.error(f"[Erreur Réseau] Impossible de télécharger l'image {url} : {e}")
        return None, None
    except Exception as e:
        logger.error(f"[Erreur Disque/Système] Problème avec l'image {nom_fichier} : {e}")
        return None, None