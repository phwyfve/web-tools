"""
Flow LMNP - Génération de la liasse fiscale

Architecture simple:
1. LoadUserData: Charge les données LMNP de l'utilisateur en mémoire
2. GenerateCerfa2031: Génère le PDF Cerfa 2031 rempli
"""

import asyncio
from caskada import Node, Flow, Memory
from pathlib import Path
import logging
from typing import Dict, Any

from core.database import get_database
from cmd_accountant.lmnp_data_manager import LmnpDataManager
from cmd_accountant.cerfa_processing.cerfa_pdf_filler import fill_cerfa_from_user_data

logger = logging.getLogger(__name__)


# ============================================================================
# NODE 1: Load User Data
# ============================================================================
class LoadUserData(Node):
    """Charge les données LMNP de l'utilisateur pour l'année fiscale"""
    
    async def prep(self, memory):
        return memory
    
    async def exec(self, memory):
        """Charge toutes les données utilisateur depuis MongoDB"""
        try:
            db = get_database()
            manager = LmnpDataManager(db)
            
            user_id = memory.user_id
            fiscal_year = memory.fiscal_year
            
            logger.info(f"Loading LMNP data for user {user_id}, fiscal year {fiscal_year}")
            
            # Charger les données complètes
            user_data = await manager.get_user_data(user_id, fiscal_year)
            
            if not user_data:
                raise ValueError(f"No LMNP data found for user {user_id}, year {fiscal_year}")
            
            # Stocker dans le contexte partagé (Memory)
            memory.user_data = user_data
            
            logger.info(f"✓ Loaded user data: {len(user_data.get('logements', []))} logements, "
                       f"{len(user_data.get('recettes', []))} recettes, "
                       f"{len(user_data.get('depenses', []))} dépenses")
            
            return memory
        except Exception as e:
            logger.error(f"❌ LoadUserData failed: {e}", exc_info=True)
            raise
    
    async def post(self, memory, prep_res, exec_res):
        return memory


# ============================================================================
# NODE 2: Generate Cerfa 2031
# ============================================================================
class GenerateCerfa2031(Node):
    """Génère le PDF Cerfa 2031 (Bilan simplifié) rempli"""
    
    async def prep(self, memory):
        return memory
    
    async def exec(self, memory):
        """Génère le PDF Cerfa 2031 avec les données utilisateur"""
        try:
            logger.info("Generating Cerfa 2031 PDF")
            
            # Récupérer les données utilisateur depuis la mémoire
            user_data = memory.user_data
            
            # Chemins
            script_dir = Path(__file__).parent
            yaml_config_path = script_dir / "cerfa_processing" / "cerfa_fields_template.yaml"
            
            # Chemin de sortie
            output_dir = getattr(memory, "output_dir", script_dir / "output")
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
            
            user_id = memory.user_id
            fiscal_year = memory.fiscal_year
            output_path = output_dir / f"cerfa_2031_{user_id}_{fiscal_year}.pdf"
            
            logger.info(f"Output path: {output_path}")
            logger.info(f"YAML config: {yaml_config_path}")
            
            # Générer le PDF
            success = fill_cerfa_from_user_data(
                yaml_config_path=str(yaml_config_path),
                cerfa_code="2031",
                user_data=user_data,
                output_path=str(output_path)
            )
            
            if not success:
                raise RuntimeError("Failed to generate Cerfa 2031 PDF")
            
            # Stocker le chemin du PDF généré
            memory.cerfa_2031_path = str(output_path)
            
            logger.info(f"✓ Cerfa 2031 generated successfully: {output_path}")
            
            return memory
        except Exception as e:
            logger.error(f"❌ GenerateCerfa2031 failed: {e}", exc_info=True)
            raise
    
    async def post(self, memory, prep_res, exec_res):
        return memory


# ============================================================================
# Flow Creation
# ============================================================================
def create_liasse_flow():
    """Crée le flow complet de génération de liasse fiscale"""
    
    logger.info("Creating LMNP liasse flow")
    
    # Instancier les nodes
    load_data = LoadUserData()
    generate_cerfa = GenerateCerfa2031()
    
    # Construire le pipeline: charger données → générer Cerfa
    load_data >> generate_cerfa
    
    # Créer le flow
    flow = Flow(
        start=load_data,
        options={
            "max_visits": 10,
            "name": "lmnp_liasse_generation"
        }
    )
    
    logger.info("Flow created successfully")
    return flow


async def generate_liasse_for_user(user_id: str, fiscal_year: int, output_dir: str = None) -> Dict[str, Any]:
    """
    Génère la liasse fiscale pour un utilisateur
    
    Args:
        user_id: ID de l'utilisateur
        fiscal_year: Année fiscale
        output_dir: Dossier de sortie (optionnel)
        
    Returns:
        Dict avec les chemins des PDFs générés
    """
    logger.info(f"Starting liasse generation for user {user_id}, year {fiscal_year}")
    
    # Créer le flow
    flow = create_liasse_flow()
    
    # Préparer le contexte
    memory = Memory({
        "user_id": user_id,
        "fiscal_year": fiscal_year
    })
    
    if output_dir:
        memory.output_dir = output_dir
    
    # Exécuter le flow
    try:
        logger.info("Starting flow execution...")
        result = await flow.run(memory)
        logger.info("Flow execution completed successfully")
        
        # Récupérer cerfa_2031_path du Memory
        cerfa_path = getattr(result, 'cerfa_2031_path', None)
        
        return {
            "success": True,
            "user_id": user_id,
            "fiscal_year": fiscal_year,
            "cerfa_2031": cerfa_path
        }
        
    except Exception as e:
        logger.error(f"❌ Flow execution failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "user_id": user_id,
            "fiscal_year": fiscal_year
        }
