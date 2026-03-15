"""
Configuration des champs Cerfa - SOURCE UNIQUE DE VÉRITÉ
=========================================================

Ce fichier définit tous les champs des formulaires Cerfa.
C'est la seule source de vérité pour les labels et la logique de remplissage.

Structure:
- CERFA_FIELDS: dictionnaire principal indexé par cerfa_code et page_number
- Chaque champ contient:
  * label: Texte exact à rechercher dans le PDF
  * hook: Fonction lambda qui calcule la valeur et la position
          Signature: (label, text_position, user_data) -> Dict ou None
"""

from typing import Dict, Any, Optional, Tuple


# ============================================================================
# DÉFINITIONS DES CHAMPS
# ============================================================================

CERFA_FIELDS = {
    "2031": {  # Cerfa code
        "template_file": "2031-sd_5396.pdf",
        "description": "Bilan simplifié (régime réel simplifié)",
        
        "pages": {
            1: {  # Page number
                "section": "identification",
                "fields": [
                    {
                        "label": "Exercice ouvert le",
                        "hook": lambda label, text_position, user_data: {
                            "text": f"01/01/{user_data.get('fiscal_year', 2025)}",
                            "x": 125,
                            "y": 123.76,
                            "font_size": 8,
                            "font_name": "Helvetica",
                            "color": (0, 0, 0)
                        },
                    },
                    {
                        "label": "et clos le",
                        "hook": lambda label, text_position, user_data: {
                            "text": f"31/12/{user_data.get('fiscal_year', 2025)}",
                            "x": 125,
                            "y": 134.07,
                            "font_size": 8,
                            "font_name": "Helvetica",
                            "color": (0, 0, 0)
                        },
                    },
                    {
                        "label": "Régime \"simplifié d'imposition\"",
                        "hook": lambda label, text_position, user_data: {
                            "text": "X",
                            "x": 449.52,
                            "y": 124.76,
                            "font_size": 10,
                            "font_name": "Helvetica-Bold",
                            "color": (0, 0, 0)
                        } if user_data.get("statut_fiscal", {}).get("regime_fiscal") == "reel_simplifie" else None,
                    },
                    {
                        "label": "Option pour la comptabilité super-simplifiée",
                        "hook": lambda label, text_position, user_data: {
                            "text": "X",
                            "x": 478.7,
                            "y": 135.07,
                            "font_size": 10,
                            "font_name": "Helvetica-Bold",
                            "color": (0, 0, 0)
                        },
                    },
                    {
                        "label": "Dénomination de l'entreprise :",
                        "hook": lambda label, text_position, user_data: {
                            "text": user_data.get("siren", {}).get("denomination", ""),
                            "x": 135.07,
                            "y": 135.07,
                            "font_size": 10,
                            "font_name": "Helvetica",
                            "color": (0, 0, 0)
                        } if user_data.get("siren", {}).get("denomination") else None,
                    },
                    {
                        "label": "Adresse de l'entreprise :",
                        "hook": lambda label, text_position, user_data: (
                            lambda adresse_complete: {
                                "text": adresse_complete,
                                "x": 125,
                                "y": 200,
                                "font_size": 10,
                                "font_name": "Helvetica",
                                "color": (0, 0, 0)
                            } if adresse_complete else None
                        )(f"{user_data.get('siren', {}).get('adresse', '')} {user_data.get('siren', {}).get('code_postal', '')} {user_data.get('siren', {}).get('ville', '')}".strip()),
                    },
                    {
                        "label": "Mél :",
                        "hook": lambda label, text_position, user_data: None,  # TODO: Ajouter email
                    },
                    {
                        "label": "Téléphone :",
                        "hook": lambda label, text_position, user_data: None,  # TODO: Ajouter téléphone
                    },
                    {
                        "label": "SIREN",
                        "hook": lambda label, text_position, user_data: {
                            "text": user_data.get("siren", {}).get("numero", ""),
                            "x": 125,
                            "y": 250,
                            "font_size": 10,
                            "font_name": "Helvetica",
                            "color": (0, 0, 0)
                        } if user_data.get("siren", {}).get("numero") else None,
                    },
                    {
                        "label": "Préciser l'ancienne adresse en cas de changement :",
                        "hook": lambda label, text_position, user_data: {
                            "text": user_data.get("siren", {}).get("ancienne_adresse", ""),
                            "x": 125,
                            "y": 260,
                            "font_size": 10,
                            "font_name": "Helvetica",
                            "color": (0, 0, 0)
                        } if user_data.get("siren", {}).get("ancienne_adresse") else None,
                    },
                    {
                        "label": "Activités exercées (souligner l'activité principale) :",
                        "hook": lambda label, text_position, user_data: {
                            "text": "Location meublée non professionnelle",
                            "x": 125,
                            "y": 215,
                            "font_size": 8,
                            "font_name": "Helvetica",
                            "color": (0, 0, 0)
                        },
                    },
                    {
                        "label": "3 Total",
                        "hook": lambda label, text_position, user_data: None,  # TODO: Calculer
                    },
                    {
                        "label": "4 Bénéfice imposable",
                        "hook": lambda label, text_position, user_data: None,  # TODO: Calculer
                    },
                    {
                        "label": "7 BIC non professionnels",
                        "hook": lambda label, text_position, user_data: None,  # TODO: Calculer
                    },
                ]
            }
        }
    }
}


def get_all_labels_for_cerfa(cerfa_code: str, page_number: int) -> list[str]:
    """
    Retourne la liste de tous les labels à rechercher pour un Cerfa et une page donnés.
    """
    cerfa = CERFA_FIELDS.get(cerfa_code)
    if not cerfa:
        return []
    
    pages = cerfa.get("pages", {})
    page = pages.get(page_number)
    if not page:
        return []
    
    return [field["label"] for field in page.get("fields", [])]


def get_field_config(cerfa_code: str, page_number: int, label: str) -> Optional[Dict[str, Any]]:
    """
    Retourne la config d'un champ spécifique.
    """
    cerfa = CERFA_FIELDS.get(cerfa_code)
    if not cerfa:
        return None
    
    pages = cerfa.get("pages", {})
    page = pages.get(page_number)
    if not page:
        return None
    
    for field in page.get("fields", []):
        if field["label"] == label:
            return field
    
    return None


def get_template_file(cerfa_code: str) -> Optional[str]:
    """
    Retourne le nom du fichier template pour un Cerfa donné.
    """
    cerfa = CERFA_FIELDS.get(cerfa_code)
    if not cerfa:
        return None
    return cerfa.get("template_file")
