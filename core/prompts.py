PROMPT_ANALYSE_PUB = """
            Retourne UNIQUEMENT un objet JSON valide contenant l'analyse factuelle de cette image publicitaire Facebook.
            Ne fais AUCUNE phrase d'introduction ni de conclusion. Réponds directement en JSON avec ces clés exactes :
            {
            "texte_incruste": "La transcription mot à mot de tout texte visible sur l'image (ou null si aucun)",
            "description_personnes": "S'il y a des humains, décris leur nombre, genre apparent, tranche d'âge, couleur de cheveux, vêtements (ex: Homme, environ 50 ans, complet veston, cheveux gris)",
            "description_logos_et_insignes": "Décris les formes, couleurs et textes des logos ou symboles visibles (ex: Carré bleu avec un symbole blanc, texte 'Nouvelles')",
            "elements_decor": "Liste des éléments visuels clés (ex: Graphique boursier en arrière-plan, flèche rouge pointant vers le bas, studio de télévision, liasse d'argent)"            }
        """
    
PROMPT_ANALYSE_PROFIL = """
            Retourne UNIQUEMENT un objet JSON valide contenant l'analyse factuelle de cette image de profil d'annonceur.
            Ne fais AUCUNE phrase d'introduction ni de conclusion. Réponds directement en JSON avec ces clés exactes :
            {
            "nature_avatar": "Choix parmi: logo_entreprise, visage_humain, illustration_generique, image_de_stock",
            "texte_visible": "Texte ou initiales visibles sur l'avatar (ou null)",
            "coherence_sémantique": "Évaluation courte sur la légitimité visuelle de l'avatar par rapport à un annonceur réel"
            }
        """
