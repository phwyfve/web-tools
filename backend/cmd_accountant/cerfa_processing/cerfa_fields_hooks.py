"""
Cerfa Fields Hooks - Logique de remplissage des champs Cerfa

Ce fichier contient la fonction principale `on_hook_reached` qui est appelée
pour chaque label trouvé dans le PDF.

Flow:
1. Le moteur trouve un label dans le PDF (ex: "Exercice ouvert le")
2. Il appelle on_hook_reached() avec:
   - field_config: Config du champ depuis le YAML
   - text_position: Position (x, y, width, height) du label trouvé
   - user_data: Données LMNP de l'utilisateur pour l'année fiscale
3. Le hook calcule:
   - La valeur à écrire
   - La position où écrire (relative au label)
4. Le hook retourne les instructions d'écriture
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def on_hook_reached(
    field_config: Dict[str, Any],
    text_position: Tuple[float, float, float, float],
    user_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Fonction appelée quand un label est trouvé dans le PDF.
    
    Args:
        field_config: Configuration du champ depuis le YAML
            {
                "label_search": "Exercice ouvert le",
                "field_path": "...",
                "field_direction": "right",
                "field_type": "text",
                "required": true,
                "default_value": "01/01/2025"
            }
        
        text_position: Position du label trouvé (x0, y0, x1, y1)
        
        user_data: Données LMNP de l'utilisateur
            {
                "fiscal_year": 2025,
                "siren": {...},
                "logements": [...],
                "recettes": [...],
                "depenses": [...],
                ...
            }
    
    Returns:
        Instructions d'écriture ou None si rien à écrire:
        {
            "text": "Valeur à écrire",
            "x": 150.5,
            "y": 700.2,
            "font_size": 10,
            "font_name": "Helvetica",
            "color": (0, 0, 0)  # RGB
        }
    """
    
    label = field_config.get("label_search", "")
    field_type = field_config.get("field_type", "text")
    field_direction = field_config.get("field_direction", "right")
    
    # Position du label
    label_x0, label_y0, label_x1, label_y1 = text_position
    
    # Calcul de la position de la zone de saisie selon la direction
    if field_direction == "right":
        write_x = label_x1 + 5  # 5 points de marge à droite du label
        write_y = label_y0
    elif field_direction == "below":
        write_x = label_x0
        write_y = label_y0 - 15  # 15 points en dessous
    elif field_direction == "right_aligned":
        # Pour les montants alignés à droite (colonnes de chiffres)
        write_x = label_x1 + 150  # Position fixe pour alignement
        write_y = label_y0
    else:
        write_x = label_x1 + 5
        write_y = label_y0
    
    # ========================================================================
    # LOGIQUE DE REMPLISSAGE PAR LABEL
    # ========================================================================
    
    # ------------------------------------------------------------------------
    # Dates d'exercice
    # ------------------------------------------------------------------------
    if label == "Exercice ouvert le":
        fiscal_year = user_data.get("fiscal_year", 2025)
        value = f"01/01/{fiscal_year}"
        
        return {
            "text": value,
            "x": 125,
            "y": write_y + 7,   # Centrage vertical ajusté
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
            "y": write_y + 7,   # Centrage vertical ajusté
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
                "x": write_x + 13,
                "y": write_y + 8,   # Centrage vertical ajusté
                "font_size": 10,    # Taille réduite
                "font_name": "Helvetica-Bold",
                "color": (0, 0, 0)
            }
        return None  # Ne rien écrire si pas coché
    
    if label == "Option pour la comptabilité super-simplifiée":
        # Par défaut coché pour LMNP
        default_checked = field_config.get("default_value") == "true"
        
        if default_checked:
            return {
                "text": "X",
                "x": write_x + 10.4,
                "y": write_y + 8,   # Centrage vertical ajusté
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
        
        if denomination:
            return {
                "text": denomination,
                "x": write_x,
                "y": write_y,
                "font_size": 10,
                "font_name": "Helvetica",
                "color": (0, 0, 0)
            }
        return None
    
    if label == "Adresse de l'entreprise l'entreprise :":
        siren = user_data.get("siren", {})
        adresse = siren.get("adresse", "")
        code_postal = siren.get("code_postal", "")
        ville = siren.get("ville", "")
        
        adresse_complete = f"{adresse} {code_postal} {ville}".strip()
        
        if adresse_complete:
            return {
                "text": adresse_complete,
                "x": write_x,
                "y": write_y,
                "font_size": 10,
                "font_name": "Helvetica",
                "color": (0, 0, 0)
            }
        return None
    
    # ------------------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------------------
    if label == "IDENTIFICATION":
        # Récupérer les données SIREN
        siren = user_data.get("siren", {})
        
        # Construire la ligne d'identification
        # Format: "Nom Prénom / Dénomination - N° SIREN"
        nom = siren.get("nom", "")
        prenom = siren.get("prenom", "")
        denomination = siren.get("denomination", "")
        numero_siren = siren.get("numero", "")
        
        if denomination:
            identity = denomination
        elif nom and prenom:
            identity = f"{nom} {prenom}"
        else:
            identity = ""
        
        if numero_siren:
            identity += f" - SIREN: {numero_siren}"
        
        return {
            "text": identity,
            "x": write_x,
            "y": write_y,
            "font_size": 10,
            "font_name": "Helvetica",
            "color": (0, 0, 0)
        }
    
    # ------------------------------------------------------------------------
    # Activité
    # ------------------------------------------------------------------------
    if label == "Activités exercées (souligner l'activité principale) :":
        default_activity = field_config.get("default_value", "Location meublée non professionnelle")
        
        return {
            "text": default_activity,
            "x": write_x,
            "y": write_y,
            "font_size": 10,
            "font_name": "Helvetica",
            "color": (0, 0, 0)
        }
    
    # ------------------------------------------------------------------------
    # Champs calculés - Actif
    # ------------------------------------------------------------------------
    if label == "Immobilisations corporelles":
        # Calculer la somme des valeurs d'origine des immobilisations
        immobilisations = user_data.get("immobilisations", [])
        total_brut = sum(immo.get("valeur_origine", 0) for immo in immobilisations)
        
        return {
            "text": f"{total_brut:,.2f}".replace(",", " "),  # Format français
            "x": write_x,
            "y": write_y,
            "font_size": 10,
            "font_name": "Helvetica",
            "color": (0, 0, 0)
        }
    
    if label == "Amortissements":
        # Calculer la somme des amortissements cumulés
        immobilisations = user_data.get("immobilisations", [])
        total_amort = sum(immo.get("amortissements_cumules", 0) for immo in immobilisations)
        
        return {
            "text": f"{total_amort:,.2f}".replace(",", " "),
            "x": write_x,
            "y": write_y,
            "font_size": 10,
            "font_name": "Helvetica",
            "color": (0, 0, 0)
        }
    
    # ------------------------------------------------------------------------
    # Champs calculés - Passif
    # ------------------------------------------------------------------------
    if label == "Résultat de l'exercice":
        # Récupérer le résultat net du compte de résultat
        # (doit être calculé avant par le flow_lmnp_liasse)
        compte_resultat = user_data.get("compte_resultat", {})
        resultat_net = compte_resultat.get("resultat_net", 0)
        
        return {
            "text": f"{resultat_net:,.2f}".replace(",", " "),
            "x": write_x,
            "y": write_y,
            "font_size": 10,
            "font_name": "Helvetica",
            "color": (0, 0, 0)
        }
    
    if label == "Dettes financières":
        # Calculer la somme des capitaux restants dus
        emprunts = user_data.get("emprunts", [])
        total_dettes = sum(emp.get("capital_restant", 0) for emp in emprunts)
        
        return {
            "text": f"{total_dettes:,.2f}".replace(",", " "),
            "x": write_x,
            "y": write_y,
            "font_size": 10,
            "font_name": "Helvetica",
            "color": (0, 0, 0)
        }
    
    # ------------------------------------------------------------------------
    # Champs calculés - Produits
    # ------------------------------------------------------------------------
    if label == "Prestations de services":
        # Somme des recettes
        recettes = user_data.get("recettes", [])
        total_recettes = sum(r.get("montant", 0) for r in recettes)
        
        return {
            "text": f"{total_recettes:,.2f}".replace(",", " "),
            "x": write_x,
            "y": write_y,
            "font_size": 10,
            "font_name": "Helvetica",
            "color": (0, 0, 0)
        }
    
    # ------------------------------------------------------------------------
    # Champs calculés - Charges
    # ------------------------------------------------------------------------
    if label == "Impôts et taxes":
        # Depuis les charges détaillées calculées par le flow
        charges_detail = user_data.get("charges_detail", {})
        impots_taxes = charges_detail.get("impots_taxes", 0)
        
        return {
            "text": f"{impots_taxes:,.2f}".replace(",", " "),
            "x": write_x,
            "y": write_y,
            "font_size": 10,
            "font_name": "Helvetica",
            "color": (0, 0, 0)
        }
    
    if label == "Dotations aux amortissements":
        # Total des dotations de l'exercice
        total_dotations = user_data.get("total_dotations_amortissements", 0)
        
        return {
            "text": f"{total_dotations:,.2f}".replace(",", " "),
            "x": write_x,
            "y": write_y,
            "font_size": 10,
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
            "x": write_x,
            "y": write_y,
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
