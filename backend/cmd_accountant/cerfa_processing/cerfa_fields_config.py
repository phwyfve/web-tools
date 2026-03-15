"""
Configuration des champs Cerfa - SOURCE UNIQUE DE VÉRITÉ
=========================================================

Ce fichier définit tous les champs des formulaires Cerfa.
C'est la seule source de vérité pour les labels et positions.

Structure:
- CERFA_FIELDS: dictionnaire principal indexé par cerfa_code et page_number
- Chaque champ contient:
  * label: Texte exact à rechercher dans le PDF
  * hook: Fonction qui calcule la valeur et la position
"""

from typing import Dict, Any, Callable, Optional, Tuple


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
                        "hook": "exercice_ouvert",
                    },
                    {
                        "label": "et clos le",
                        "hook": "exercice_clos",
                    },
                    {
                        "label": "Régime \"simplifié d'imposition\"",
                        "hook": "regime_simplifie",
                    },
                    {
                        "label": "Option pour la comptabilité super-simplifiée",
                        "hook": "option_super_simplifie",
                    },
                    {
                        "label": "Dénomination de l'entreprise :",
                        "hook": "denomination",
                    },
                    {
                        "label": "Adresse de l'entreprise :",
                        "hook": "adresse",
                    },
                    {
                        "label": "Mél :",
                        "hook": "email",
                    },
                    {
                        "label": "Téléphone :",
                        "hook": "telephone",
                    },
                    {
                        "label": "SIREN",
                        "hook": "siren",
                    },
                    {
                        "label": "Préciser l'ancienne adresse en cas de changement :",
                        "hook": "ancienne_adresse",
                    },
                    {
                        "label": "Activités exercées (souligner l'activité principale) :",
                        "hook": "activites",
                    },
                    {
                        "label": "3 Total",
                        "hook": "total_3",
                    },
                    {
                        "label": "4 Bénéfice imposable",
                        "hook": "benefice_imposable",
                    },
                    {
                        "label": "7 BIC non professionnels",
                        "hook": "bic_non_pro",
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
