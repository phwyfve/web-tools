"""
Moteur de remplissage des PDF Cerfa

Ce moteur:
1. Lit le YAML de configuration des champs
2. Copie le PDF template
3. Parcourt les labels définis dans le YAML
4. Pour chaque label trouvé, appelle le hook approprié
5. Écrit les valeurs calculées dans le PDF

Flow naturel: comme si on remplissait le formulaire à la main
"""

import fitz  # PyMuPDF
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import shutil

try:
    from .cerfa_fields_hooks import on_hook_reached
except ImportError:
    # Import absolu si exécuté comme script standalone
    from cerfa_fields_hooks import on_hook_reached

logger = logging.getLogger(__name__)


class CerfaPdfFiller:
    """Moteur de remplissage des PDF Cerfa"""
    
    def __init__(self, yaml_config_path: str):
        """
        Initialise le moteur
        
        Args:
            yaml_config_path: Chemin vers le fichier YAML de configuration
        """
        self.yaml_config_path = Path(yaml_config_path)
        self.config = self._load_yaml_config()
        
        # Résoudre template_directory en chemin relatif au YAML
        template_dir_str = self.config.get("template_directory", "")
        if template_dir_str:
            # Si chemin relatif, le résoudre par rapport au fichier YAML
            template_dir = Path(template_dir_str)
            if not template_dir.is_absolute():
                template_dir = self.yaml_config_path.parent / template_dir
            self.template_dir = template_dir
        else:
            self.template_dir = self.yaml_config_path.parent
        
    def _load_yaml_config(self) -> Dict:
        """Charge la configuration YAML"""
        try:
            with open(self.yaml_config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded YAML config: {self.yaml_config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load YAML config: {e}")
            raise
    
    def fill_cerfa(
        self,
        cerfa_code: str,
        user_data: Dict[str, Any],
        output_path: str
    ) -> bool:
        """
        Remplit un formulaire Cerfa avec les données utilisateur
        
        Args:
            cerfa_code: Code du Cerfa à remplir (ex: "2031", "2033A")
            user_data: Données LMNP de l'utilisateur
            output_path: Chemin du PDF de sortie
            
        Returns:
            True si succès, False sinon
        """
        try:
            # Trouver la config du Cerfa
            cerfa_config = self._find_cerfa_config(cerfa_code)
            if not cerfa_config:
                logger.error(f"Cerfa {cerfa_code} not found in config")
                return False
            
            # Chemin du template
            template_filename = cerfa_config["cerfa_filename"]
            template_path = self.template_dir / template_filename
            
            if not template_path.exists():
                logger.error(f"Template not found: {template_path}")
                return False
            
            logger.info(f"Filling Cerfa {cerfa_code}: {template_filename}")
            logger.info(f"Output: {output_path}")
            
            # Copier le template vers le fichier de sortie
            shutil.copy2(template_path, output_path)
            logger.info("Template copied")
            
            # Ouvrir le PDF copié pour édition
            doc = fitz.open(output_path)
            
            # Parcourir toutes les pages définies
            fields_written = 0
            for page_config in cerfa_config.get("pages", []):
                page_num = page_config["page_number"] - 1  # 0-indexed
                
                if page_num >= len(doc):
                    logger.warning(f"Page {page_num + 1} not found in PDF")
                    continue
                
                page = doc[page_num]
                section = page_config.get("section", "")
                
                logger.info(f"Processing page {page_num + 1}, section: {section}")
                
                # Parcourir tous les champs de cette page
                for field_config in page_config.get("fields", []):
                    result = self._process_field(page, field_config, user_data)
                    if result:
                        fields_written += 1
            
            # Sauvegarder le PDF modifié (incremental=True car on sauvegarde sur le fichier ouvert)
            doc.save(output_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
            doc.close()
            
            logger.info(f"✓ Cerfa filled successfully: {fields_written} fields written")
            return True
            
        except Exception as e:
            logger.error(f"Error filling Cerfa: {e}", exc_info=True)
            return False
    
    def _find_cerfa_config(self, cerfa_code: str) -> Optional[Dict]:
        """Trouve la configuration d'un Cerfa par son code"""
        for cerfa in self.config.get("cerfas", []):
            if cerfa.get("cerfa_code") == cerfa_code:
                return cerfa
        return None
    
    def _process_field(
        self,
        page: fitz.Page,
        field_config: Dict[str, Any],
        user_data: Dict[str, Any]
    ) -> bool:
        """
        Traite un champ: recherche le label et appelle le hook
        
        Args:
            page: Page PDF PyMuPDF
            field_config: Configuration du champ depuis le YAML
            user_data: Données utilisateur
            
        Returns:
            True si le champ a été rempli, False sinon
        """
        label_search = field_config.get("label_search", "")
        
        if not label_search:
            logger.warning("Field has no label_search, skipping")
            return False
        
        # Rechercher le label dans la page
        text_instances = page.search_for(label_search)
        
        if not text_instances:
            logger.debug(f"Label not found: '{label_search}'")
            return False
        
        # Prendre la première occurrence
        label_rect = text_instances[0]
        text_position = (label_rect.x0, label_rect.y0, label_rect.x1, label_rect.y1)
        
        logger.debug(f"Found label: '{label_search}' at {text_position}")
        
        # Appeler le hook pour calculer ce qu'il faut écrire
        write_instruction = on_hook_reached(field_config, text_position, user_data)
        
        if not write_instruction:
            logger.debug(f"Hook returned None for: '{label_search}'")
            return False
        
        # Écrire le texte dans le PDF
        self._write_text_to_pdf(page, write_instruction)
        
        logger.debug(f"✓ Written: '{write_instruction['text']}' for label '{label_search}'")
        return True
    
    def _write_text_to_pdf(self, page: fitz.Page, instruction: Dict[str, Any]):
        """
        Écrit du texte dans le PDF
        
        Args:
            page: Page PDF
            instruction: Instructions d'écriture
                {
                    "text": "Texte à écrire",
                    "x": 150.5,
                    "y": 700.2,
                    "font_size": 10,
                    "font_name": "Helvetica",
                    "color": (0, 0, 0)
                }
        """
        text = instruction.get("text", "")
        x = instruction.get("x", 0)
        y = instruction.get("y", 0)
        font_size = instruction.get("font_size", 10)
        font_name = instruction.get("font_name", "helv")  # helv = Helvetica dans PyMuPDF
        color = instruction.get("color", (0, 0, 0))
        
        # Convertir le nom de police si nécessaire
        fontname_map = {
            "Helvetica": "helv",
            "Helvetica-Bold": "hebo",
            "Times-Roman": "tiro",
            "Courier": "cour"
        }
        fontname = fontname_map.get(font_name, "helv")
        
        # Point d'insertion (bas-gauche du texte)
        point = fitz.Point(x, y)
        
        # Écrire le texte
        page.insert_text(
            point,
            text,
            fontsize=font_size,
            fontname=fontname,
            color=color
        )


def fill_cerfa_from_user_data(
    yaml_config_path: str,
    cerfa_code: str,
    user_data: Dict[str, Any],
    output_path: str
) -> bool:
    """
    Fonction helper pour remplir un Cerfa
    
    Args:
        yaml_config_path: Chemin vers cerfa_fields_template.yaml
        cerfa_code: Code du Cerfa (ex: "2031")
        user_data: Données LMNP de l'utilisateur
        output_path: Chemin du PDF de sortie
        
    Returns:
        True si succès
    """
    filler = CerfaPdfFiller(yaml_config_path)
    return filler.fill_cerfa(cerfa_code, user_data, output_path)


# ============================================================================
# Exemple d'utilisation
# ============================================================================

if __name__ == "__main__":
    """Test du moteur de remplissage"""
    import asyncio
    from pathlib import Path
    
    # Configuration du logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Données de test
    test_user_data = {
        "fiscal_year": 2025,
        "siren": {
            "numero": "123456789",
            "denomination": "SCI Test LMNP",
            "nom": "Dupont",
            "prenom": "Jean",
            "adresse": "123 Rue de la Location",
            "code_postal": "75001",
            "ville": "Paris"
        },
        "statut_fiscal": {
            "regime_fiscal": "reel_simplifie"
        },
        "immobilisations": [
            {
                "valeur_origine": 200000,
                "amortissements_cumules": 10000,
                "valeur_nette_comptable": 190000
            }
        ],
        "recettes": [
            {"montant": 12000},
            {"montant": 8000}
        ],
        "depenses": [],
        "emprunts": [
            {"capital_restant": 150000}
        ],
        "charges_detail": {
            "impots_taxes": 2000
        },
        "total_dotations_amortissements": 4000,
        "compte_resultat": {
            "resultat_net": 6000
        }
    }
    
    # Chemins
    script_dir = Path(__file__).parent
    yaml_path = script_dir / "cerfa_fields_template.yaml"
    output_path = script_dir / "test_output_2031.pdf"
    
    print("="*80)
    print("TESTING CERFA PDF FILLER")
    print("="*80)
    print(f"YAML config: {yaml_path}")
    print(f"Output: {output_path}")
    print("="*80)
    
    # Remplir le Cerfa
    success = fill_cerfa_from_user_data(
        str(yaml_path),
        "2031",
        test_user_data,
        str(output_path)
    )
    
    if success:
        print("\n✓ Cerfa filled successfully!")
        print(f"Check the output: {output_path}")
    else:
        print("\n✗ Failed to fill Cerfa")
