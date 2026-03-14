"""
LMNP Routes
Routes FastAPI pour la gestion des données LMNP (Location Meublée Non Professionnelle)
"""

import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from core.auth import User, current_active_user
from core.database import get_database
from cmd_accountant.lmnp_data_manager import LmnpDataManager
from shell.command_manager import create_command, process_command
from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


# ============================================================================
# Request Models
# ============================================================================

class SirenUpdateRequest(BaseModel):
    """Request body pour mise à jour SIREN"""
    numero: str | None = None
    denomination: str | None = None
    prenom: str | None = None
    nom: str | None = None
    pays_residence: str | None = None
    adresse: str | None = None
    code_postal: str | None = None
    ville: str | None = None
    date_creation: str | None = None


class LogementItem(BaseModel):
    """Un logement"""
    id: str
    nom: str
    adresse: str
    code_postal: str | None = None
    ville: str | None = None
    surface: float | None = None
    nb_pieces: int | None = None
    date_acquisition: str | None = None
    prix_acquisition: float | None = None
    valeur_estimee: float | None = None


class LogementsUpdateRequest(BaseModel):
    """Request body pour mise à jour des logements"""
    logements: List[LogementItem]


class UsageItem(BaseModel):
    """Un usage"""
    id: str
    logement_id: str
    type_usage: str | None = None
    date_debut: str | None = None
    date_fin: str | None = None
    nb_jours_location: int | None = None
    nb_jours_perso: int | None = None
    est_residence_principale: bool = False


class UsagesUpdateRequest(BaseModel):
    """Request body pour mise à jour des usages"""
    usages: List[UsageItem]


class RecetteItem(BaseModel):
    """Une recette"""
    id: str
    date: str
    montant: float
    description: str | None = None
    type_recette: str | None = None
    logement_id: str | None = None


class RecettesUpdateRequest(BaseModel):
    """Request body pour mise à jour des recettes"""
    recettes: List[RecetteItem]


class DepenseItem(BaseModel):
    """Une dépense"""
    id: str
    date: str
    montant: float
    description: str | None = None
    categorie: str | None = None
    logement_id: str | None = None
    est_amortissable: bool = False


class DepensesUpdateRequest(BaseModel):
    """Request body pour mise à jour des dépenses"""
    depenses: List[DepenseItem]


class EmpruntItem(BaseModel):
    """Un emprunt"""
    id: str
    organisme: str
    montant_initial: float
    taux: float
    date_debut: str
    duree_mois: int
    mensualite: float | None = None
    logement_id: str | None = None


class EmpruntsUpdateRequest(BaseModel):
    """Request body pour mise à jour des emprunts"""
    emprunts: List[EmpruntItem]


class OgaUpdateRequest(BaseModel):
    """Request body pour mise à jour OGA"""
    nom: str | None = None
    numero_adhesion: str | None = None
    date_adhesion: str | None = None
    montant_cotisation: float | None = None


class StatutFiscalUpdateRequest(BaseModel):
    """Request body pour mise à jour du statut fiscal"""
    regime_fiscal: str | None = None
    assujetti_tva: bool = False
    soumis_cfe: bool = True
    option_amortissement: bool = False
    duree_amortissement: int | None = None
    adherent_cga: bool = False
    numero_cga: str | None = None


# ============================================================================
# Routes
# ============================================================================

@router.get("/lmnp/data/{fiscal_year}")
async def get_lmnp_data(
    fiscal_year: int,
    user: User = Depends(current_active_user),
    db = Depends(get_database)
):
    """
    Récupère toutes les données LMNP d'un utilisateur pour une année fiscale.
    Crée automatiquement un document vide si n'existe pas.
    """
    manager = LmnpDataManager(db)
    data = await manager.get_user_data(str(user.id), fiscal_year)
    
    return {
        "success": True,
        "data": data
    }


@router.patch("/lmnp/data/{fiscal_year}/siren")
async def update_siren(
    fiscal_year: int,
    request: SirenUpdateRequest,
    user: User = Depends(current_active_user),
    db = Depends(get_database)
):
    """Met à jour les données SIREN"""
    manager = LmnpDataManager(db)
    
    # Convertir en dict et filtrer les None
    siren_data = request.model_dump(exclude_none=True)
    
    data = await manager.update_siren(str(user.id), fiscal_year, siren_data)
    
    return {
        "success": True,
        "message": "Données SIREN mises à jour",
        "data": data
    }


@router.patch("/lmnp/data/{fiscal_year}/logements")
async def update_logements(
    fiscal_year: int,
    request: LogementsUpdateRequest,
    user: User = Depends(current_active_user),
    db = Depends(get_database)
):
    """Met à jour la liste des logements"""
    manager = LmnpDataManager(db)
    
    # Convertir en list de dicts
    logements_data = [logement.model_dump(exclude_none=True) for logement in request.logements]
    
    data = await manager.update_logements(str(user.id), fiscal_year, logements_data)
    
    return {
        "success": True,
        "message": "Logements mis à jour",
        "data": data
    }


@router.patch("/lmnp/data/{fiscal_year}/usage")
async def update_usage(
    fiscal_year: int,
    request: UsagesUpdateRequest,
    user: User = Depends(current_active_user),
    db = Depends(get_database)
):
    """Met à jour la liste des usages"""
    manager = LmnpDataManager(db)
    
    usages = [usage.model_dump(exclude_none=True) for usage in request.usages]
    
    data = await manager.update_usage(str(user.id), fiscal_year, usages)
    
    return {
        "success": True,
        "message": "Usages mis à jour",
        "data": data
    }


@router.patch("/lmnp/data/{fiscal_year}/recettes")
async def update_recettes(
    fiscal_year: int,
    request: RecettesUpdateRequest,
    user: User = Depends(current_active_user),
    db = Depends(get_database)
):
    """Met à jour la liste des recettes"""
    manager = LmnpDataManager(db)
    
    recettes_data = [recette.model_dump(exclude_none=True) for recette in request.recettes]
    
    data = await manager.update_recettes(str(user.id), fiscal_year, recettes_data)
    
    return {
        "success": True,
        "message": "Recettes mises à jour",
        "data": data
    }


@router.patch("/lmnp/data/{fiscal_year}/depenses")
async def update_depenses(
    fiscal_year: int,
    request: DepensesUpdateRequest,
    user: User = Depends(current_active_user),
    db = Depends(get_database)
):
    """Met à jour la liste des dépenses"""
    manager = LmnpDataManager(db)
    
    depenses_data = [depense.model_dump(exclude_none=True) for depense in request.depenses]
    
    data = await manager.update_depenses(str(user.id), fiscal_year, depenses_data)
    
    return {
        "success": True,
        "message": "Dépenses mises à jour",
        "data": data
    }


@router.patch("/lmnp/data/{fiscal_year}/emprunts")
async def update_emprunts(
    fiscal_year: int,
    request: EmpruntsUpdateRequest,
    user: User = Depends(current_active_user),
    db = Depends(get_database)
):
    """Met à jour la liste des emprunts"""
    manager = LmnpDataManager(db)
    
    emprunts_data = [emprunt.model_dump(exclude_none=True) for emprunt in request.emprunts]
    
    data = await manager.update_emprunts(str(user.id), fiscal_year, emprunts_data)
    
    return {
        "success": True,
        "message": "Emprunts mis à jour",
        "data": data
    }


@router.patch("/lmnp/data/{fiscal_year}/oga")
async def update_oga(
    fiscal_year: int,
    request: OgaUpdateRequest,
    user: User = Depends(current_active_user),
    db = Depends(get_database)
):
    """Met à jour les données OGA"""
    manager = LmnpDataManager(db)
    
    oga_data = request.model_dump(exclude_none=True)
    
    data = await manager.update_oga(str(user.id), fiscal_year, oga_data)
    
    return {
        "success": True,
        "message": "Données OGA mises à jour",
        "data": data
    }


@router.patch("/lmnp/data/{fiscal_year}/statut-fiscal")
async def update_statut_fiscal(
    fiscal_year: int,
    request: StatutFiscalUpdateRequest,
    user: User = Depends(current_active_user),
    db = Depends(get_database)
):
    """Met à jour le statut fiscal"""
    manager = LmnpDataManager(db)
    
    statut_data = request.model_dump(exclude_none=True)
    
    data = await manager.update_statut_fiscal(str(user.id), fiscal_year, statut_data)
    
    return {
        "success": True,
        "message": "Statut fiscal mis à jour",
        "data": data
    }


@router.get("/lmnp/export/{fiscal_year}")
async def export_lmnp_data(
    fiscal_year: int,
    user: User = Depends(current_active_user),
    db = Depends(get_database)
):
    """
    Exporte toutes les données LMNP au format JSON pour génération de la liasse fiscale.
    """
    manager = LmnpDataManager(db)
    data = await manager.export_data(str(user.id), fiscal_year)
    
    return {
        "success": True,
        "fiscal_year": fiscal_year,
        "exported_at": datetime.utcnow().isoformat(),
        "data": data
    }


@router.get("/lmnp/data/{fiscal_year}/validation")
async def get_validation_recap(
    fiscal_year: int,
    user: User = Depends(current_active_user),
    db = Depends(get_database)
):
    """Récupère le récapitulatif avec validations et calculs"""
    manager = LmnpDataManager(db)
    recap = await manager.get_validation_recap(str(user.id), fiscal_year)
    
    # Log de la structure complète pour développement du moteur comptable
    import json
    print("\n" + "="*80)
    print(f"STRUCTURE DONNÉES LMNP - Année {fiscal_year} - User {user.id}")
    print("="*80)
    print(json.dumps(recap, indent=2, default=str, ensure_ascii=False))
    print("="*80 + "\n")
    
    return {
        "success": True,
        "data": recap
    }


@router.post("/lmnp/data/{fiscal_year}/transmettre")
async def transmettre_declaration(
    fiscal_year: int,
    user: User = Depends(current_active_user),
    db = Depends(get_database)
):
    """Transmet la déclaration (change le statut)"""
    manager = LmnpDataManager(db)
    
    # Vérifier que tout est valide avant de transmettre
    recap = await manager.get_validation_recap(str(user.id), fiscal_year)
    
    if not recap.get("is_valid"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La déclaration ne peut pas être transmise. Certaines informations sont manquantes."
        )
    
    data = await manager.transmettre_declaration(str(user.id), fiscal_year)
    
    return {
        "success": True,
        "message": "Déclaration transmise avec succès",
        "data": data
    }


@router.delete("/lmnp/data/{fiscal_year}")
async def delete_lmnp_data(
    fiscal_year: int,
    user: User = Depends(current_active_user),
    db = Depends(get_database)
):
    """Supprime les données d'une année fiscale"""
    manager = LmnpDataManager(db)
    deleted = await manager.delete_user_data(str(user.id), fiscal_year)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aucune donnée trouvée pour l'année {fiscal_year}"
        )
    
    return {
        "success": True,
        "message": f"Données de l'année {fiscal_year} supprimées"
    }


@router.get("/lmnp/years")
async def list_user_years(
    user: User = Depends(current_active_user),
    db = Depends(get_database)
):
    """Liste toutes les années fiscales disponibles pour l'utilisateur connecté"""
    manager = LmnpDataManager(db)
    years = await manager.list_user_years(str(user.id))
    
    return {
        "success": True,
        "years": years
    }


@router.post("/lmnp/data/{fiscal_year}/generate-liasse")
async def generate_liasse_endpoint(
    fiscal_year: int,
    user: User = Depends(current_active_user)
):
    """
    Lance la génération de la liasse fiscale LMNP pour l'année donnée
    
    Steps:
    1. Créer la commande GenerateLmnpLiasse avec user_id et fiscal_year
    2. Démarrer le traitement asynchrone
    3. Retourner command_id pour polling
    """
    try:
        command_id = await create_command(
            shell_command="GenerateLmnpLiasse",
            args={
                "user_id": str(user.id),
                "fiscal_year": fiscal_year
            }
        )
        
        # Start processing asynchronously
        asyncio.create_task(process_command(command_id))
        
        return {
            "success": True,
            "command_id": command_id,
            "message": f"Génération de la liasse fiscale {fiscal_year} démarrée"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de la commande: {str(e)}"
        )


@router.get("/lmnp/data/{fiscal_year}/liasse")
async def get_generated_liasse(
    fiscal_year: int,
    user: User = Depends(current_active_user),
    db = Depends(get_database)
):
    """Récupère la dernière liasse fiscale générée pour l'année donnée"""
    liasse_doc = await db.lmnp_liasses.find_one({
        "user_id": str(user.id),
        "fiscal_year": fiscal_year
    })
    
    if not liasse_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aucune liasse fiscale trouvée pour l'année {fiscal_year}"
        )
    
    return {
        "success": True,
        "data": liasse_doc["liasse"],
        "generated_at": liasse_doc.get("generated_at")
    }
    
    return {
        "success": True,
        "years": years
    }
