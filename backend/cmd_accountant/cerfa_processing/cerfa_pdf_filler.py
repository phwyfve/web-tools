"""
Moteur de remplissage des PDF Cerfa

Ce moteur:
1. Lit la config des champs depuis cerfa_fields_config.py
2. Copie le PDF template
3. Parcourt les labels définis
4. Pour chaque label trouvé, appelle le hook approprié
5. Écrit les valeurs calculées dans le PDF

Flow naturel: comme si on remplissait le formulaire à la main
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import shutil

try:
    from .cerfa_fields_config import CERFA_FIELDS, get_all_labels_for_cerfa, get_field_config, get_template_file
except ImportError:
    # Import absolu si exécuté comme script standalone
    from cerfa_fields_config import CERFA_FIELDS, get_all_labels_for_cerfa, get_field_config, get_template_file

logger = logging.getLogger(__name__)


class CerfaPdfFiller:
    """Moteur de remplissage des PDF Cerfa"""
    
    def __init__(self, template_dir: str):
        """
        Initialise le moteur
        
        Args:
            template_dir: Répertoire contenant les templates PDF
        """
        self.template_dir = Path(template_dir)
        
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
            # Vérifier que le Cerfa existe dans la config
            if cerfa_code not in CERFA_FIELDS:
                logger.error(f"Cerfa {cerfa_code} not found in CERFA_FIELDS config")
                return False
            
            # Récupérer le nom du template
            template_filename = get_template_file(cerfa_code)
            if not template_filename:
                logger.error(f"No template file defined for Cerfa {cerfa_code}")
                return False
                
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
            
            # Récupérer la config du Cerfa
            cerfa_config = CERFA_FIELDS[cerfa_code]
            
            # Parcourir toutes les pages définies
            fields_written = 0
            for page_num, page_config in cerfa_config["pages"].items():
                page_idx = page_num - 1  # 0-indexed
                
                if page_idx >= len(doc):
                    logger.warning(f"Page {page_num} not found in PDF")
                    continue
                
                page = doc[page_idx]
                section = page_config.get("section", "")
                
                logger.info(f"Processing page {page_num}, section: {section}")
                
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
            field_config: Configuration du champ depuis cerfa_fields_config.py
            user_data: Données utilisateur
            
        Returns:
            True si le champ a été rempli, False sinon
        """
        label = field_config.get("label", "")
        hook_func = field_config.get("hook")
        
        if not label:
            logger.warning("Field has no label, skipping")
            return False
        
        if not hook_func:
            logger.warning(f"Field '{label}' has no hook, skipping")
            return False
        
        # Rechercher le label dans la page
        text_instances = page.search_for(label)
        
        if not text_instances:
            logger.debug(f"Label not found: '{label}'")
            return False
        
        # Prendre la première occurrence
        label_rect = text_instances[0]
        text_position = (label_rect.x0, label_rect.y0, label_rect.x1, label_rect.y1)
        
        logger.debug(f"Found label: '{label}' at {text_position}")
        
        # Appeler le hook (lambda) pour calculer ce qu'il faut écrire
        write_instruction = hook_func(label, text_position, user_data)
        
        if not write_instruction:
            logger.debug(f"Hook returned None for: '{label}'")
            return False
        
        # Écrire le texte dans le PDF
        self._write_text_to_pdf(page, write_instruction)
        
        logger.debug(f"✓ Written: '{write_instruction['text']}' for label '{label}'")
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
    template_dir: str,
    cerfa_code: str,
    user_data: Dict[str, Any],
    output_path: str
) -> bool:
    """
    Fonction helper pour remplir un Cerfa
    
    Args:
        template_dir: Répertoire contenant les templates PDF
        cerfa_code: Code du Cerfa (ex: "2031")
        user_data: Données LMNP de l'utilisateur
        output_path: Chemin du PDF de sortie
        
    Returns:
        True si succès
    """
    filler = CerfaPdfFiller(template_dir)
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
    }
    
    # Chemins
    script_dir = Path(__file__).parent
    template_dir = script_dir / "_templace_cerfa_2026"
    output_path = script_dir / "test_output_2031.pdf"
    
    print("="*80)
    print("TESTING CERFA PDF FILLER")
    print("="*80)
    print(f"Template dir: {template_dir}")
    print(f"Output: {output_path}")
    print("="*80)
    
    # Remplir le Cerfa
    success = fill_cerfa_from_user_data(
        str(template_dir),
        "2031",
        test_user_data,
        str(output_path)
    )
    
    if success:
        print("\n✓ Cerfa filled successfully!")
        print(f"Check the output: {output_path}")
    else:
        print("\n✗ Failed to fill Cerfa")
