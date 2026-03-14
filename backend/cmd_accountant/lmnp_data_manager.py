"""
LMNP Data Manager
Gestion des données de Location Meublée Non Professionnelle par utilisateur et année fiscale.
"""

from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from bson import ObjectId


# ============================================================================
# Pydantic Models - Data Structures
# ============================================================================

class SirenData(BaseModel):
    """Données SIREN de l'entreprise"""
    numero: Optional[str] = None
    denomination: Optional[str] = None
    prenom: Optional[str] = None
    nom: Optional[str] = None
    pays_residence: Optional[str] = None
    adresse: Optional[str] = None
    code_postal: Optional[str] = None
    ville: Optional[str] = None
    date_creation: Optional[str] = None
    updated_at: Optional[datetime] = None


class LogementData(BaseModel):
    """Données d'un logement"""
    id: str
    nom: str
    adresse: str
    code_postal: Optional[str] = None
    ville: Optional[str] = None
    surface: Optional[float] = None
    nb_pieces: Optional[int] = None
    date_acquisition: Optional[str] = None
    prix_acquisition: Optional[float] = None
    updated_at: Optional[datetime] = None


class UsageData(BaseModel):
    """Données d'usage du bien"""
    id: str
    logement_id: str
    type_usage: Optional[str] = None  # 'location', 'location_courte_duree', 'mixte'
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None
    nb_jours_location: Optional[int] = None
    nb_jours_perso: Optional[int] = None
    est_residence_principale: Optional[bool] = False
    updated_at: Optional[datetime] = None


class RecetteData(BaseModel):
    """Données d'une recette"""
    id: str
    date: str
    montant: float
    description: Optional[str] = None
    type_recette: Optional[str] = None  # 'loyer', 'charges', 'autre'
    logement_id: Optional[str] = None
    updated_at: Optional[datetime] = None


class DepenseData(BaseModel):
    """Données d'une dépense"""
    id: str
    date: str
    montant: float
    description: Optional[str] = None
    categorie: Optional[str] = None  # 'travaux', 'entretien', 'charges', 'assurance', etc.
    logement_id: Optional[str] = None
    est_amortissable: Optional[bool] = False
    updated_at: Optional[datetime] = None


class EmpruntData(BaseModel):
    """Données d'un emprunt"""
    id: str
    organisme: str
    montant_initial: float
    taux: float
    date_debut: str
    duree_mois: int
    mensualite: Optional[float] = None
    logement_id: Optional[str] = None
    updated_at: Optional[datetime] = None


class OgaData(BaseModel):
    """Données Organisme de Gestion Agréé"""
    nom: Optional[str] = None
    numero_adhesion: Optional[str] = None
    date_adhesion: Optional[str] = None
    montant_cotisation: Optional[float] = None
    updated_at: Optional[datetime] = None


class StatutFiscalData(BaseModel):
    """Données de statut fiscal"""
    regime_fiscal: Optional[str] = None  # 'reel', 'micro_bic'
    option_amortissement: Optional[bool] = False
    duree_amortissement: Optional[int] = None
    adherent_cga: Optional[bool] = False
    numero_cga: Optional[str] = None
    updated_at: Optional[datetime] = None


class LmnpUserData(BaseModel):
    """Structure complète des données LMNP pour un utilisateur"""
    user_id: str
    fiscal_year: int
    siren: Optional[SirenData] = None
    logements: Optional[List[LogementData]] = []
    usage: Optional[List[UsageData]] = []
    recettes: Optional[List[RecetteData]] = []
    depenses: Optional[List[DepenseData]] = []
    emprunts: Optional[List[EmpruntData]] = []
    oga: Optional[OgaData] = None
    statut_fiscal: Optional[StatutFiscalData] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_complete: bool = False
    version: int = 1


# ============================================================================
# LMNP Data Manager Class
# ============================================================================

class LmnpDataManager:
    """Manager pour les opérations CRUD sur les données LMNP"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.lmnp_user_data
    
    async def get_user_data(self, user_id: str, fiscal_year: int) -> Optional[Dict[str, Any]]:
        """
        Récupère toutes les données LMNP d'un utilisateur pour une année fiscale.
        Crée un document vide si n'existe pas.
        """
        data = await self.collection.find_one({
            "user_id": user_id,
            "fiscal_year": fiscal_year
        })
        
        if not data:
            # Créer un document vide pour cette année
            new_data = {
                "user_id": user_id,
                "fiscal_year": fiscal_year,
                "siren": None,
                "logements": [],
                "usage": None,
                "recettes": [],
                "depenses": [],
                "emprunts": [],
                "oga": None,
                "statut_fiscal": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_complete": False,
                "version": 1
            }
            result = await self.collection.insert_one(new_data)
            new_data["_id"] = result.inserted_id
            return self._serialize_doc(new_data)
        
        return self._serialize_doc(data)
    
    async def update_siren(self, user_id: str, fiscal_year: int, siren_data: Dict[str, Any]) -> Dict[str, Any]:
        """Met à jour les données SIREN"""
        siren_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"user_id": user_id, "fiscal_year": fiscal_year},
            {
                "$set": {
                    "siren": siren_data,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return await self.get_user_data(user_id, fiscal_year)
    
    async def update_logements(self, user_id: str, fiscal_year: int, logements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Met à jour la liste des logements"""
        # Ajouter updated_at à chaque logement
        for logement in logements:
            logement["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"user_id": user_id, "fiscal_year": fiscal_year},
            {
                "$set": {
                    "logements": logements,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return await self.get_user_data(user_id, fiscal_year)
    
    async def update_usage(self, user_id: str, fiscal_year: int, usages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Met à jour la liste des usages"""
        for usage in usages:
            usage["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"user_id": user_id, "fiscal_year": fiscal_year},
            {
                "$set": {
                    "usage": usages,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return await self.get_user_data(user_id, fiscal_year)
    
    async def update_recettes(self, user_id: str, fiscal_year: int, recettes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Met à jour la liste des recettes"""
        for recette in recettes:
            recette["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"user_id": user_id, "fiscal_year": fiscal_year},
            {
                "$set": {
                    "recettes": recettes,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return await self.get_user_data(user_id, fiscal_year)
    
    async def update_depenses(self, user_id: str, fiscal_year: int, depenses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Met à jour la liste des dépenses"""
        for depense in depenses:
            depense["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"user_id": user_id, "fiscal_year": fiscal_year},
            {
                "$set": {
                    "depenses": depenses,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return await self.get_user_data(user_id, fiscal_year)
    
    async def update_emprunts(self, user_id: str, fiscal_year: int, emprunts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Met à jour la liste des emprunts"""
        for emprunt in emprunts:
            emprunt["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"user_id": user_id, "fiscal_year": fiscal_year},
            {
                "$set": {
                    "emprunts": emprunts,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return await self.get_user_data(user_id, fiscal_year)
    
    async def update_oga(self, user_id: str, fiscal_year: int, oga_data: Dict[str, Any]) -> Dict[str, Any]:
        """Met à jour les données OGA"""
        oga_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"user_id": user_id, "fiscal_year": fiscal_year},
            {
                "$set": {
                    "oga": oga_data,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return await self.get_user_data(user_id, fiscal_year)
    
    async def update_statut_fiscal(self, user_id: str, fiscal_year: int, statut_data: Dict[str, Any]) -> Dict[str, Any]:
        """Met à jour le statut fiscal"""
        statut_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"user_id": user_id, "fiscal_year": fiscal_year},
            {
                "$set": {
                    "statut_fiscal": statut_data,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return await self.get_user_data(user_id, fiscal_year)
    
    async def export_data(self, user_id: str, fiscal_year: int) -> Dict[str, Any]:
        """
        Exporte toutes les données au format JSON pour génération de la liasse fiscale.
        Identique à get_user_data mais indique l'intention d'export.
        """
        return await self.get_user_data(user_id, fiscal_year)
    
    async def delete_user_data(self, user_id: str, fiscal_year: int) -> bool:
        """Supprime les données d'une année fiscale"""
        result = await self.collection.delete_one({
            "user_id": user_id,
            "fiscal_year": fiscal_year
        })
        return result.deleted_count > 0
    
    async def list_user_years(self, user_id: str) -> List[int]:
        """Liste toutes les années fiscales disponibles pour un utilisateur"""
        cursor = self.collection.find(
            {"user_id": user_id},
            {"fiscal_year": 1}
        ).sort("fiscal_year", -1)
        
        years = []
        async for doc in cursor:
            years.append(doc["fiscal_year"])
        
        return years
    
    def _serialize_doc(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convertit ObjectId en string pour la sérialisation JSON"""
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc
