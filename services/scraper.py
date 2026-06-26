import asyncio
import re
from playwright.async_api import async_playwright, Response
from config import logger, FB_AD_LIBRARY_URL

class MetaAdsScraper:
    def __init__(self):
        # On remplace la variable globale par un attribut d'instance
        self.intercepted_data = []

    async def _intercept_response(self, response: Response):
        """
        Méthode interne qui écoute le trafic réseau et isole les appels GraphQL.
        Lit la réponse en texte brut pour éviter de planter sur le format multi-JSON de Meta.
        """
        if "graphql" in response.url and response.request.method == "POST":
            try:
                # On lit la réponse comme du texte brut
                raw_text = await response.text()
                
                # 1. FILTRE D'EXCLUSION : On rejette les suggestions au clavier
                if "typeahead_suggestions" in raw_text:
                    return 
                
                # 2. FILTRE D'INCLUSION : On cherche le contenu de la vraie recherche
                if "search_results" in raw_text or "ad_library_main" in raw_text:
                    logger.info(f"[Réseau] Vrai résultat GraphQL intercepté ! ({len(raw_text)} caractères)")
                    self.intercepted_data.append(raw_text)
                    
            except Exception as e:
                # On log l'erreur proprement au lieu d'utiliser print()
                logger.debug(f"[Réseau] Erreur mineure lors de l'interception : {e}")

    async def run_search(self, target_person: str) -> list[str]:
        """
        Lance le navigateur, effectue la recherche sur Meta Ads et retourne les données interceptées.
        """
        logger.info(f"Démarrage de l'agent navigateur pour : {target_person}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(locale="fr-CA") 
            page = await context.new_page()

            # On attache notre écouteur réseau
            page.on("response", self._intercept_response)

            logger.info("Navigation vers la librairie de publicités...")
            await page.goto(FB_AD_LIBRARY_URL)
            await page.wait_for_timeout(3000)

            # --- SÉLECTION DE LA CATÉGORIE ---
            logger.info("Ouverture du menu des catégories...")
            bouton_categorie = page.locator('div[role="button"]:has-text("Catégorie publicitaire"), div[role="combobox"]:has-text("Catégorie publicitaire")').first
            
            if not await bouton_categorie.is_visible():
                bouton_categorie = page.get_by_text("Catégorie publicitaire", exact=True).first

            await bouton_categorie.click()
            await page.wait_for_timeout(1500)

            logger.info("Sélection de 'Toutes les publicités'...")
            option_toutes = page.get_by_text("Toutes les publicités", exact=True).first
            await option_toutes.click()
            
            # Délai pour laisser React activer la boîte de recherche
            await page.wait_for_timeout(2500) 

            # --- RECHERCHE DE LA CIBLE ---
            logger.info(f"Recherche de la personnalité : {target_person}")
            
            # Cibler exactement le texte avec une regex (insensible à la casse)
            search_box = page.get_by_placeholder(re.compile(r"annonceur", re.IGNORECASE)).first
            
            if not await search_box.is_visible():
                logger.warning("Plan B activé pour cibler la boîte de recherche...")
                search_box = page.locator('input[type="text"]:not([disabled])').first
            
            await search_box.wait_for(state="visible")
            await search_box.click()
            await page.wait_for_timeout(500) 
            
            logger.info("Frappe au clavier en cours...")
            await page.keyboard.type(target_person, delay=150) # Simulation humaine
            
            # Attendre le menu de suggestions
            await page.wait_for_timeout(1500) 
            
            logger.info("Lancement de la recherche (Touche Entrée)...")
            await page.keyboard.press("Enter")

            # Attente cruciale pour laisser le temps à GraphQL de répondre
            logger.info("Attente des requêtes réseau (8 secondes)...")
            await page.wait_for_timeout(8000)

            await browser.close()
            logger.info("Navigateur fermé.")

        return self.intercepted_data