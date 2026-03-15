from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# HOOKS - Logique de remplissage par champ
# ============================================================================
# Chaque fonction hook reçoit:
#   - label: le label tel que défini dans cerfa_fields_config.py
#   - text_position: (x0, y0, x1, y1) position du label trouvé dans le PDF
#   - user_data: données utilisateur LMNP
#
# Et retourne un dictionnaire avec:
#   - text: le texte à écrire
#   - x, y: position absolue où écrire
#   - font_size, font_name, color: style du texte
#
# Retourne None si le champ ne doit pas être rempli.
# ============================================================================

def hook_exercice_ouvert(label: str, text_position: Tuple[float, float, float, float], user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        fiscal_year = user_data.get("fiscal_year", 2025)
        value = f"01/01/{fiscal_year}"
        
        return {
            "text": value,
            "x": 125,
            "y": 123.76,   # Centrage vertical ajusté
            "font_size": 8,     # Taille réduite pour correspondre au Cerfa
            "font_name": "Helvetica",
            "color": (0, 0, 0)
        }
    
    if label == "et clos le":
        fiscal_year = user_data.get("fiscal_year", 2025)
        value = f"31/12/{fiscal_year}"
        
        return {
            "text": value,
            "x": 125,
            "y": 134.07,   # Centrage vertical ajusté
            "font_size": 8,     # Taille réduite pour correspondre au Cerfa
            "font_name": "Helvetica",
            "color": (0, 0, 0)
        }
    
    # ------------------------------------------------------------------------
    # Régime fiscal
    # ------------------------------------------------------------------------
    if label == "Régime \"simplifié d'imposition\"":
        # Vérifier le statut fiscal
        statut_fiscal = user_data.get("statut_fiscal", {})
        regime = statut_fiscal.get("regime_fiscal", "")
        
        # Cocher si régime réel simplifié
        if regime == "reel_simplifie":
            
            return {
                "text": "X",
                "x": 449.52,
                "y": 124.76,
                "font_size": 10,    # Taille réduite
                "font_name": "Helvetica-Bold",
                "color": (0, 0, 0)
            }
        return None  # Ne rien écrire si pas coché
    
    if label == "Option pour la comptabilité super-simplifiée":
        # Par défaut coché pour LMNP
        default_checked = field_config.get("default_value") == "true"
        
        if default_checked:
            final_x = 478.7 
            final_y = 135.07
            logger.info(f"[HOOK] Option super-simplifiée: label_position={text_position}, final_x={final_x}, final_y={final_y}")
            
            return {
                "text": "X",
                "x": final_x,
                "y": final_y,   # Centrage vertical ajusté
                "font_size": 10,    # Taille réduite
                "font_name": "Helvetica-Bold",
                "color": (0, 0, 0)
            }
        return None
    
    # ------------------------------------------------------------------------
    # Dénomination et Adresse
    # ------------------------------------------------------------------------
    if label == "Dénomination de l'entreprise :":
        siren = user_data.get("siren", {})
        denomination = siren.get("denomination", "")
        logger.info(f"[HOOK] Dénomination: '{denomination}' for label_position={text_position}")
        if denomination:
            return {
                "text": denomination,
                "x": 135.06764221191406,
                "y": 135.06764221191406,
                "font_size": 10,
                "font_name": "Helvetica",
                "color": (0, 0, 0)
            }
        return None
    
    if label == "Adresse de l'entreprise :":
        siren = user_data.get("siren", {})
        adresse = siren.get("adresse", "")
        code_postal = siren.get("code_postal", "")
        ville = siren.get("ville", "")
        logger.info(f"[HOOK] Adresse: '{adresse} {code_postal} {ville}' for label_position={text_position}")
        adresse_complete = f"{adresse} {code_postal} {ville}".strip()
        
        if adresse_complete:
            return {
                "text": adresse_complete,
                "x": 125,
                "y": 200,
                "font_size": 10,
                "font_name": "Helvetica",
                "color": (0, 0, 0)
            }
        return None
    
    # ------------------------------------------------------------------------
    # Activité
    # ------------------------------------------------------------------------
    if label == "Activités exercées (souligner l'activité principale) :":
        default_activity = field_config.get("default_value", "Location meublée non professionnelle")
        
        return {
            "text": default_activity,
            "x": 125,
            "y": 215,  # En dessous du label
            "font_size": 8,
            "font_name": "Helvetica",
            "color": (0, 0, 0)
        }
    
    # ------------------------------------------------------------------------
    # Par défaut: utiliser default_value si présent
    # ------------------------------------------------------------------------
    if "default_value" in field_config:
        default_value = field_config["default_value"]
        
        return {
            "text": str(default_value),
            "x": 125,
            "y": 250,
            "font_size": 10,
            "font_name": "Helvetica",
            "color": (0, 0, 0)
        }
    
    # Si aucune règle ne correspond, logger un warning
    logger.warning(f"No hook logic defined for label: {label}")
    return None


def format_currency(amount: float) -> str:
    """
    Formate un montant en format français
    Ex: 1234.56 -> "1 234,56"
    """
    formatted = f"{amount:,.2f}"
    # Remplacer le séparateur de milliers et décimal pour format français
    formatted = formatted.replace(",", " ").replace(".", ",")
    return formatted


def format_date(date_str: str) -> str:
    """
    Formate une date au format JJ/MM/AAAA
    """
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d/%m/%Y")
    except:
        return date_str
