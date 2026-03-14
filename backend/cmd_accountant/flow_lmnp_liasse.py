"""
Caskada flow for LMNP fiscal accounting and liasse generation.

Architecture en nodes pour transformer les données utilisateur LMNP en liasse fiscale.
Chaque node enrichit le contexte global (Memory) avec ses calculs.
"""
import asyncio
from caskada import Node, Flow, Memory
from datetime import datetime
from typing import Dict, List
import logging

from core.database import get_database
from cmd_accountant.lmnp_data_manager import LmnpDataManager

logger = logging.getLogger(__name__)


# ============================================================================
# NODE 1: Load User Data
# ============================================================================
class LoadLmnpUserData(Node):
    """Charge les données LMNP de l'utilisateur pour l'année fiscale"""
    
    async def prep(self, memory):
        return memory
    
    async def exec(self, memory):
        db = get_database()
        manager = LmnpDataManager(db)
        
        user_id = memory.user_id
        fiscal_year = memory.fiscal_year
        
        logger.info(f"Loading LMNP data for user {user_id}, fiscal year {fiscal_year}")
        
        # Charger les données complètes
        user_data = await manager.get_user_data(user_id, fiscal_year)
        
        if not user_data:
            raise ValueError(f"No LMNP data found for user {user_id}, year {fiscal_year}")
        
        # Stocker dans le contexte
        memory.user_data = user_data
        memory.logements = user_data.get("logements", [])
        memory.recettes = user_data.get("recettes", [])
        memory.depenses = user_data.get("depenses", [])
        memory.emprunts = user_data.get("emprunts", [])
        memory.statut_fiscal = user_data.get("statut_fiscal", {})
        memory.siren = user_data.get("siren", {})
        
        logger.info(f"Loaded: {len(memory.logements)} logements, {len(memory.recettes)} recettes, "
                   f"{len(memory.depenses)} dépenses, {len(memory.emprunts)} emprunts")
        
        return memory
    
    async def post(self, memory, prep_res, exec_res):
        return memory


# ============================================================================
# NODE 2: Compute Immobilisations (Amortissements par composants)
# ============================================================================
class ComputeImmobilisations(Node):
    """Calcule les immobilisations et amortissements par composants"""
    
    async def prep(self, memory):
        return memory
    
    async def exec(self, memory):
        logger.info("Computing immobilisations with component-based depreciation")
        
        immobilisations = []
        total_dotations_exercice = 0
        
        for logement in memory.logements:
            prix_acquisition = logement.get("prix_acquisition", 0)
            date_acquisition = logement.get("date_acquisition", "")
            logement_id = logement.get("id", "")
            nom = logement.get("nom", logement.get("adresse", ""))
            
            if not prix_acquisition or not date_acquisition:
                logger.warning(f"Skipping logement {nom}: missing prix_acquisition or date_acquisition")
                continue
            
            # Calcul années depuis acquisition
            annee_acquisition = int(date_acquisition[:4])
            annees_depuis_acquisition = memory.fiscal_year - annee_acquisition
            
            # Décomposition par composants (méthode fiscale recommandée)
            composants = [
                {
                    "nature": f"{nom} - Terrain",
                    "valeur": prix_acquisition * 0.20,
                    "duree": 0,  # Non amortissable
                    "taux": 0
                },
                {
                    "nature": f"{nom} - Gros œuvre",
                    "valeur": prix_acquisition * 0.40,
                    "duree": 50,
                    "taux": 2.0
                },
                {
                    "nature": f"{nom} - Toiture et étanchéité",
                    "valeur": prix_acquisition * 0.10,
                    "duree": 15,
                    "taux": 6.67
                },
                {
                    "nature": f"{nom} - Installations techniques",
                    "valeur": prix_acquisition * 0.10,
                    "duree": 15,
                    "taux": 6.67
                },
                {
                    "nature": f"{nom} - Agencements",
                    "valeur": prix_acquisition * 0.10,
                    "duree": 10,
                    "taux": 10.0
                },
                {
                    "nature": f"{nom} - Menuiseries extérieures",
                    "valeur": prix_acquisition * 0.10,
                    "duree": 25,
                    "taux": 4.0
                }
            ]
            
            for composant in composants:
                if composant["duree"] == 0:
                    # Terrain non amortissable
                    immobilisations.append({
                        "logement_id": logement_id,
                        "nature": composant["nature"],
                        "categorie": "terrain",
                        "date_acquisition": date_acquisition,
                        "valeur_origine": composant["valeur"],
                        "amortissements_anterieurs": 0,
                        "dotations_exercice": 0,
                        "amortissements_cumules": 0,
                        "valeur_nette_comptable": composant["valeur"],
                        "duree_amortissement": 0,
                        "taux_amortissement": 0,
                        "mode_amortissement": "non_amortissable"
                    })
                else:
                    # Calcul amortissement linéaire
                    dotation_annuelle = composant["valeur"] * composant["taux"] / 100
                    
                    # Dotation de l'exercice (prorata temporis première année)
                    if annees_depuis_acquisition == 0:
                        # Première année : prorata temporis
                        # Simplification : on suppose acquisition en milieu d'année = 6/12
                        dotation_exercice = dotation_annuelle * 0.5
                    elif annees_depuis_acquisition <= composant["duree"]:
                        dotation_exercice = dotation_annuelle
                    else:
                        # Complètement amorti
                        dotation_exercice = 0
                    
                    # Amortissements antérieurs
                    amortissements_anterieurs = dotation_annuelle * max(0, annees_depuis_acquisition - 1)
                    if annees_depuis_acquisition == 1:
                        # Ajout du prorata de la première année
                        amortissements_anterieurs = dotation_annuelle * 0.5
                    
                    # Plafond : ne pas dépasser la valeur d'origine
                    amortissements_cumules = min(
                        amortissements_anterieurs + dotation_exercice,
                        composant["valeur"]
                    )
                    valeur_nette = composant["valeur"] - amortissements_cumules
                    
                    immobilisations.append({
                        "logement_id": logement_id,
                        "nature": composant["nature"],
                        "categorie": "constructions",
                        "date_acquisition": date_acquisition,
                        "valeur_origine": composant["valeur"],
                        "amortissements_anterieurs": amortissements_anterieurs,
                        "dotations_exercice": dotation_exercice,
                        "amortissements_cumules": amortissements_cumules,
                        "valeur_nette_comptable": valeur_nette,
                        "duree_amortissement": composant["duree"],
                        "taux_amortissement": composant["taux"],
                        "mode_amortissement": "lineaire"
                    })
                    
                    total_dotations_exercice += dotation_exercice
        
        # Stocker dans le contexte
        memory.immobilisations = immobilisations
        memory.total_dotations_amortissements = total_dotations_exercice
        
        logger.info(f"Computed {len(immobilisations)} immobilisation components, "
                   f"total dotations exercice: {total_dotations_exercice:.2f} €")
        
        return memory
    
    async def post(self, memory, prep_res, exec_res):
        return memory


# ============================================================================
# NODE 3: Compute Charges (Répartition par poste comptable)
# ============================================================================
class ComputeCharges(Node):
    """Répartit les dépenses par poste comptable"""
    
    async def prep(self, memory):
        return memory
    
    async def exec(self, memory):
        logger.info("Computing charges by accounting category")
        
        # Mapping catégories utilisateur → postes comptables
        mapping_categories = {
            "Taxes": "impots_taxes",
            "Assurance": "assurances",
            "Comptabilité": "honoraires",
            "Energie": "charges_locatives_energie",
            "Tech": "services_exterieurs",
            "Co Propriété": "charges_copropriete",
            "Electroménager": "entretien_reparations"
        }
        
        charges = {
            "impots_taxes": 0,
            "assurances": 0,
            "honoraires": 0,
            "charges_locatives_energie": 0,
            "services_exterieurs": 0,
            "charges_copropriete": 0,
            "entretien_reparations": 0,
            "charges_financieres": 0
        }
        
        # Répartition des dépenses
        for depense in memory.depenses:
            categorie = depense.get("categorie", "")
            montant = depense.get("montant", 0)
            poste = mapping_categories.get(categorie, "services_exterieurs")
            charges[poste] += montant
        
        # Calcul des charges financières (intérêts d'emprunts)
        for emprunt in memory.emprunts:
            capital_restant = emprunt.get("capital_restant_du", 0)
            taux_interet = emprunt.get("taux_interet", 0)
            
            if capital_restant and taux_interet:
                # Calcul simplifié : intérêts annuels
                # TODO: affiner avec échéancier réel
                interets_annuels = capital_restant * taux_interet / 100
                charges["charges_financieres"] += interets_annuels
        
        # Calcul totaux
        total_charges_exploitation = sum(
            v for k, v in charges.items() if k != "charges_financieres"
        )
        total_charges_financieres = charges["charges_financieres"]
        
        # Stocker dans le contexte
        memory.charges_detail = charges
        memory.total_charges_exploitation = total_charges_exploitation
        memory.total_charges_financieres = total_charges_financieres
        
        logger.info(f"Charges exploitation: {total_charges_exploitation:.2f} €, "
                   f"Charges financières: {total_charges_financieres:.2f} €")
        
        return memory
    
    async def post(self, memory, prep_res, exec_res):
        return memory


# ============================================================================
# NODE 4: Compute Produits (Recettes)
# ============================================================================
class ComputeProduits(Node):
    """Calcule les produits d'exploitation (recettes locatives)"""
    
    async def prep(self, memory):
        return memory
    
    async def exec(self, memory):
        logger.info("Computing produits (recettes)")
        
        total_recettes = sum(r.get("montant", 0) for r in memory.recettes)
        
        # Si TVA applicable, distinguer HT et TTC
        assujetti_tva = memory.statut_fiscal.get("assujetti_tva", False)
        
        if assujetti_tva:
            # Recettes TTC, calculer HT et TVA collectée
            taux_tva = 0.10  # 10% pour locations meublées
            recettes_ht = total_recettes / (1 + taux_tva)
            tva_collectee = total_recettes - recettes_ht
        else:
            recettes_ht = total_recettes
            tva_collectee = 0
        
        memory.total_recettes_ttc = total_recettes
        memory.total_recettes_ht = recettes_ht
        memory.tva_collectee = tva_collectee
        
        logger.info(f"Recettes: {total_recettes:.2f} € (HT: {recettes_ht:.2f} €, "
                   f"TVA collectée: {tva_collectee:.2f} €)")
        
        return memory
    
    async def post(self, memory, prep_res, exec_res):
        return memory


# ============================================================================
# NODE 5: Compute Compte de Résultat
# ============================================================================
class ComputeCompteResultat(Node):
    """Calcule le compte de résultat complet"""
    
    async def prep(self, memory):
        return memory
    
    async def exec(self, memory):
        logger.info("Computing compte de résultat")
        
        # Produits d'exploitation
        produits_exploitation = memory.total_recettes_ht
        
        # Charges d'exploitation (hors amortissements et financières)
        charges_exploitation_hors_amort = memory.total_charges_exploitation
        
        # Dotations aux amortissements
        dotations_amortissements = memory.total_dotations_amortissements
        
        # Total charges d'exploitation
        total_charges_exploitation = charges_exploitation_hors_amort + dotations_amortissements
        
        # Résultat d'exploitation
        resultat_exploitation = produits_exploitation - total_charges_exploitation
        
        # Résultat financier
        produits_financiers = 0  # TODO: si placements
        charges_financieres = memory.total_charges_financieres
        resultat_financier = produits_financiers - charges_financieres
        
        # Résultat courant avant impôt
        resultat_courant = resultat_exploitation + resultat_financier
        
        # Résultat exceptionnel
        produits_exceptionnels = 0  # TODO: si cessions d'actifs, etc.
        charges_exceptionnelles = 0
        resultat_exceptionnel = produits_exceptionnels - charges_exceptionnelles
        
        # Résultat net comptable
        resultat_net = resultat_courant + resultat_exceptionnel
        
        # Stocker dans le contexte
        memory.compte_resultat = {
            "produits_exploitation": {
                "locations_meublees": produits_exploitation,
                "autres_produits": 0,
                "total_produits_exploitation": produits_exploitation
            },
            "charges_exploitation": {
                "impots_taxes": memory.charges_detail["impots_taxes"],
                "assurances": memory.charges_detail["assurances"],
                "honoraires": memory.charges_detail["honoraires"],
                "charges_locatives_energie": memory.charges_detail["charges_locatives_energie"],
                "services_exterieurs": memory.charges_detail["services_exterieurs"],
                "charges_copropriete": memory.charges_detail["charges_copropriete"],
                "entretien_reparations": memory.charges_detail["entretien_reparations"],
                "dotations_amortissements": dotations_amortissements,
                "total_charges_exploitation": total_charges_exploitation
            },
            "resultat_exploitation": resultat_exploitation,
            "resultat_financier": {
                "produits_financiers": produits_financiers,
                "charges_financieres": charges_financieres,
                "resultat_financier": resultat_financier
            },
            "resultat_courant": resultat_courant,
            "resultat_exceptionnel": {
                "produits_exceptionnels": produits_exceptionnels,
                "charges_exceptionnelles": charges_exceptionnelles,
                "resultat_exceptionnel": resultat_exceptionnel
            },
            "resultat_net": resultat_net
        }
        
        logger.info(f"Résultat exploitation: {resultat_exploitation:.2f} €, "
                   f"Résultat courant: {resultat_courant:.2f} €, "
                   f"Résultat net: {resultat_net:.2f} €")
        
        return memory
    
    async def post(self, memory, prep_res, exec_res):
        return memory


# ============================================================================
# NODE 6: Compute Bilan
# ============================================================================
class ComputeBilan(Node):
    """Calcule le bilan actif et passif"""
    
    async def prep(self, memory):
        return memory
    
    async def exec(self, memory):
        logger.info("Computing bilan actif and passif")
        
        # ACTIF
        # -----------
        
        # Immobilisations
        total_immobilisations_brutes = sum(i["valeur_origine"] for i in memory.immobilisations)
        total_amortissements = sum(i["amortissements_cumules"] for i in memory.immobilisations)
        total_immobilisations_nettes = total_immobilisations_brutes - total_amortissements
        
        # Actif circulant (simplifié)
        # TODO: calculer créances réelles (loyers impayés, etc.)
        creances = 0
        disponibilites = 0  # TODO: solde bancaire si dispo
        total_actif_circulant = creances + disponibilites
        
        # Comptes de régularisation
        charges_constatees_avance = 0  # TODO
        
        # Total actif
        total_actif = total_immobilisations_nettes + total_actif_circulant + charges_constatees_avance
        
        # PASSIF
        # -----------
        
        # Capitaux propres
        resultat_exercice = memory.compte_resultat["resultat_net"]
        report_a_nouveau = 0  # TODO: récupérer depuis exercice N-1
        total_capitaux_propres = report_a_nouveau + resultat_exercice
        
        # Provisions
        provisions_risques_charges = 0  # TODO
        
        # Dettes
        emprunts_etablissements_credit = sum(e.get("capital_restant_du", 0) for e in memory.emprunts)
        fournisseurs = 0  # TODO: factures impayées
        dettes_fiscales_sociales = 0  # TODO: impôts et taxes à payer
        autres_dettes = 0
        total_dettes = (emprunts_etablissements_credit + fournisseurs + 
                       dettes_fiscales_sociales + autres_dettes)
        
        # Comptes de régularisation
        produits_constates_avance = 0  # TODO: loyers perçus d'avance
        
        # Total passif
        total_passif = (total_capitaux_propres + provisions_risques_charges + 
                       total_dettes + produits_constates_avance)
        
        # Équilibrage bilan (différence = erreur ou élément manquant)
        ecart_bilan = total_actif - total_passif
        
        if abs(ecart_bilan) > 0.01:
            logger.warning(f"Bilan non équilibré ! Écart: {ecart_bilan:.2f} €")
            # Ajustement temporaire dans "autres dettes" ou report à nouveau
            if ecart_bilan > 0:
                # Actif > Passif : augmenter capitaux propres
                report_a_nouveau += ecart_bilan
                total_capitaux_propres += ecart_bilan
            else:
                # Passif > Actif : augmenter autres dettes
                autres_dettes += abs(ecart_bilan)
                total_dettes += abs(ecart_bilan)
            
            total_passif = total_actif  # Force équilibrage
        
        # Stocker dans le contexte
        memory.bilan = {
            "actif": {
                "immobilisations": {
                    "immobilisations_brutes": total_immobilisations_brutes,
                    "amortissements": total_amortissements,
                    "immobilisations_nettes": total_immobilisations_nettes
                },
                "actif_circulant": {
                    "creances": creances,
                    "disponibilites": disponibilites,
                    "total_actif_circulant": total_actif_circulant
                },
                "comptes_regularisation": {
                    "charges_constatees_avance": charges_constatees_avance
                },
                "total_actif": total_actif
            },
            "passif": {
                "capitaux_propres": {
                    "report_a_nouveau": report_a_nouveau,
                    "resultat_exercice": resultat_exercice,
                    "total_capitaux_propres": total_capitaux_propres
                },
                "provisions": {
                    "provisions_risques_charges": provisions_risques_charges
                },
                "dettes": {
                    "emprunts_etablissements_credit": emprunts_etablissements_credit,
                    "fournisseurs": fournisseurs,
                    "dettes_fiscales_sociales": dettes_fiscales_sociales,
                    "autres_dettes": autres_dettes,
                    "total_dettes": total_dettes
                },
                "comptes_regularisation": {
                    "produits_constates_avance": produits_constates_avance
                },
                "total_passif": total_passif
            },
            "equilibre": abs(ecart_bilan) < 0.01
        }
        
        logger.info(f"Bilan: Total actif = {total_actif:.2f} €, Total passif = {total_passif:.2f} €, "
                   f"Équilibré: {memory.bilan['equilibre']}")
        
        return memory
    
    async def post(self, memory, prep_res, exec_res):
        return memory


# ============================================================================
# NODE 7: Apply Fiscal Rules (Réintégrations/Déductions)
# ============================================================================
class ApplyFiscalRules(Node):
    """Applique les règles fiscales pour calculer le résultat fiscal"""
    
    async def prep(self, memory):
        return memory
    
    async def exec(self, memory):
        logger.info("Applying fiscal rules (réintégrations/déductions)")
        
        resultat_comptable = memory.compte_resultat["resultat_net"]
        
        # Réintégrations fiscales
        reintegrations = {
            "charges_non_deductibles": 0,  # TODO: identifier charges non déductibles
            "amortissements_excedentaires": 0,  # TODO: si dépassement limites
            "autres_reintegrations": 0
        }
        total_reintegrations = sum(reintegrations.values())
        
        # Déductions fiscales
        deductions = {
            "deficits_reportables": 0,  # TODO: récupérer déficits N-1 à N-10
            "plus_values_long_terme": 0,
            "autres_deductions": 0
        }
        total_deductions = sum(deductions.values())
        
        # Résultat fiscal
        resultat_fiscal = resultat_comptable + total_reintegrations - total_deductions
        
        # Stocker dans le contexte
        memory.resultat_fiscal_detail = {
            "resultat_comptable": resultat_comptable,
            "reintegrations": reintegrations,
            "total_reintegrations": total_reintegrations,
            "deductions": deductions,
            "total_deductions": total_deductions,
            "resultat_fiscal": resultat_fiscal
        }
        
        logger.info(f"Résultat comptable: {resultat_comptable:.2f} €, "
                   f"Résultat fiscal: {resultat_fiscal:.2f} €")
        
        return memory
    
    async def post(self, memory, prep_res, exec_res):
        return memory


# ============================================================================
# NODE 8: Build Liasse Fiscale JSON
# ============================================================================
class BuildLiasseFiscale(Node):
    """Construit le JSON final de la liasse fiscale"""
    
    async def prep(self, memory):
        return memory
    
    async def exec(self, memory):
        logger.info("Building final liasse fiscale JSON")
        
        liasse = {
            "meta": {
                "fiscal_year": memory.fiscal_year,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "user_id": memory.user_id,
                "siren": memory.siren.get("numero", None),
                "denomination": memory.siren.get("denomination", None),
                "regime_fiscal": memory.statut_fiscal.get("regime_fiscal", "reel_simplifie")
            },
            "formulaire_2031": {
                "bilan_actif": memory.bilan["actif"],
                "bilan_passif": memory.bilan["passif"],
                "compte_resultat": memory.compte_resultat
            },
            "formulaire_2033A": {
                "immobilisations": memory.immobilisations,
                "total_immobilisations_brutes": sum(i["valeur_origine"] for i in memory.immobilisations),
                "total_amortissements": sum(i["amortissements_cumules"] for i in memory.immobilisations),
                "total_valeur_nette": sum(i["valeur_nette_comptable"] for i in memory.immobilisations)
            },
            "formulaire_2033B": {
                "amortissements": self._build_tableau_amortissements(memory.immobilisations),
                "total_debut": sum(i["amortissements_anterieurs"] for i in memory.immobilisations),
                "total_dotations": sum(i["dotations_exercice"] for i in memory.immobilisations),
                "total_fin": sum(i["amortissements_cumules"] for i in memory.immobilisations)
            },
            "formulaire_2033E": {
                "determination_resultat": memory.resultat_fiscal_detail
            }
        }
        
        memory.liasse_fiscale = liasse
        
        logger.info("Liasse fiscale JSON built successfully")
        
        return memory
    
    def _build_tableau_amortissements(self, immobilisations):
        """Regroupe les amortissements par catégorie"""
        categories = {}
        
        for immo in immobilisations:
            cat = immo["categorie"]
            if cat not in categories:
                categories[cat] = {
                    "nature": cat.capitalize(),
                    "montant_debut_exercice": 0,
                    "dotations_exercice": 0,
                    "montant_fin_exercice": 0
                }
            
            categories[cat]["montant_debut_exercice"] += immo["amortissements_anterieurs"]
            categories[cat]["dotations_exercice"] += immo["dotations_exercice"]
            categories[cat]["montant_fin_exercice"] += immo["amortissements_cumules"]
        
        return list(categories.values())
    
    async def post(self, memory, prep_res, exec_res):
        return memory


# ============================================================================
# NODE 9: Generate Simple PDF (Visualization)
# ============================================================================
class GenerateSimplePDF(Node):
    """Génère un PDF simple pour visualisation (pas les formulaires Cerfa)"""
    
    async def prep(self, memory):
        return memory
    
    async def exec(self, memory):
        logger.info("Generating liasse fiscale HTML visualization")
        
        liasse = memory.liasse_fiscale
        meta = liasse['meta']
        f2031 = liasse['formulaire_2031']
        f2033a = liasse['formulaire_2033A']
        f2033b = liasse['formulaire_2033B']
        
        bilan_actif = f2031['bilan_actif']
        bilan_passif = f2031['bilan_passif']
        compte_resultat = f2031['compte_resultat']
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Liasse Fiscale LMNP {memory.fiscal_year}</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        body {{
            font-family: Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.4;
            color: #000;
        }}
        .page-break {{
            page-break-after: always;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 2px solid #000;
        }}
        .header h1 {{
            font-size: 18pt;
            margin: 0 0 10px 0;
            font-weight: bold;
        }}
        .header .info {{
            font-size: 10pt;
            margin: 5px 0;
        }}
        .section-title {{
            background-color: #0066cc;
            color: white;
            padding: 8px 15px;
            font-size: 14pt;
            font-weight: bold;
            margin-top: 25px;
            margin-bottom: 15px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        table.fiscal-table {{
            border: 1px solid #000;
        }}
        table.fiscal-table th {{
            background-color: #e6f2ff;
            padding: 8px;
            text-align: left;
            border: 1px solid #000;
            font-weight: bold;
            font-size: 9pt;
        }}
        table.fiscal-table td {{
            padding: 6px 8px;
            border: 1px solid #000;
            font-size: 9pt;
        }}
        table.fiscal-table td.label {{
            font-weight: normal;
            width: 60%;
        }}
        table.fiscal-table td.amount {{
            text-align: right;
            font-family: "Courier New", monospace;
            width: 40%;
        }}
        table.fiscal-table tr.total {{
            background-color: #ffffcc;
            font-weight: bold;
        }}
        table.fiscal-table tr.subtotal {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        .formula-note {{
            font-size: 8pt;
            color: #666;
            font-style: italic;
            margin: 5px 0;
        }}
        .positive {{
            color: #006600;
        }}
        .negative {{
            color: #cc0000;
        }}
    </style>
</head>
<body>

    <!-- PAGE 1: PAGE DE GARDE -->
    <div class="header">
        <h1>LIASSE FISCALE LMNP</h1>
        <div class="info">Exercice clos le 31/12/{memory.fiscal_year}</div>
        <div class="info">Régime: {meta.get('regime_fiscal', 'Réel simplifié').upper()}</div>
    </div>
    
    <table style="margin-top: 30px;">
        <tr>
            <td style="width: 40%; font-weight: bold;">SIREN</td>
            <td style="width: 60%;">{meta.get('siren', 'N/A')}</td>
        </tr>
        <tr>
            <td style="font-weight: bold;">Dénomination</td>
            <td>{meta.get('denomination', 'N/A')}</td>
        </tr>
        <tr>
            <td style="font-weight: bold;">Exercice</td>
            <td>Du 01/01/{memory.fiscal_year} au 31/12/{memory.fiscal_year}</td>
        </tr>
        <tr>
            <td style="font-weight: bold;">Date de génération</td>
            <td>{meta.get('generated_at', '')[:10]}</td>
        </tr>
    </table>

    <div class="page-break"></div>

    <!-- PAGE 2: FORMULAIRE 2031 - BILAN ACTIF -->
    <div class="section-title">FORMULAIRE 2031 - BILAN ACTIF</div>
    
    <table class="fiscal-table">
        <thead>
            <tr>
                <th>ACTIF</th>
                <th style="text-align: right;">Montant (€)</th>
            </tr>
        </thead>
        <tbody>
            <tr class="subtotal">
                <td class="label">ACTIF IMMOBILISÉ</td>
                <td class="amount"></td>
            </tr>
            <tr>
                <td class="label">&nbsp;&nbsp;Immobilisations brutes</td>
                <td class="amount">{bilan_actif['immobilisations']['immobilisations_brutes']:,.2f}</td>
            </tr>
            <tr>
                <td class="label">&nbsp;&nbsp;Amortissements</td>
                <td class="amount">({bilan_actif['immobilisations']['amortissements']:,.2f})</td>
            </tr>
            <tr class="subtotal">
                <td class="label">Total Immobilisations nettes</td>
                <td class="amount">{bilan_actif['immobilisations']['immobilisations_nettes']:,.2f}</td>
            </tr>
            
            <tr class="subtotal">
                <td class="label">ACTIF CIRCULANT</td>
                <td class="amount"></td>
            </tr>
            <tr>
                <td class="label">&nbsp;&nbsp;Créances</td>
                <td class="amount">{bilan_actif['actif_circulant']['creances']:,.2f}</td>
            </tr>
            <tr>
                <td class="label">&nbsp;&nbsp;Disponibilités</td>
                <td class="amount">{bilan_actif['actif_circulant']['disponibilites']:,.2f}</td>
            </tr>
            <tr class="subtotal">
                <td class="label">Total Actif circulant</td>
                <td class="amount">{bilan_actif['actif_circulant']['total_actif_circulant']:,.2f}</td>
            </tr>
            
            <tr>
                <td class="label">Charges constatées d'avance</td>
                <td class="amount">{bilan_actif['comptes_regularisation']['charges_constatees_avance']:,.2f}</td>
            </tr>
            
            <tr class="total">
                <td class="label">TOTAL ACTIF</td>
                <td class="amount">{bilan_actif['total_actif']:,.2f}</td>
            </tr>
        </tbody>
    </table>

    <!-- BILAN PASSIF -->
    <div class="section-title">FORMULAIRE 2031 - BILAN PASSIF</div>
    
    <table class="fiscal-table">
        <thead>
            <tr>
                <th>PASSIF</th>
                <th style="text-align: right;">Montant (€)</th>
            </tr>
        </thead>
        <tbody>
            <tr class="subtotal">
                <td class="label">CAPITAUX PROPRES</td>
                <td class="amount"></td>
            </tr>
            <tr>
                <td class="label">&nbsp;&nbsp;Report à nouveau</td>
                <td class="amount">{bilan_passif['capitaux_propres']['report_a_nouveau']:,.2f}</td>
            </tr>
            <tr>
                <td class="label">&nbsp;&nbsp;Résultat de l'exercice</td>
                <td class="amount {'positive' if bilan_passif['capitaux_propres']['resultat_exercice'] >= 0 else 'negative'}">{bilan_passif['capitaux_propres']['resultat_exercice']:,.2f}</td>
            </tr>
            <tr class="subtotal">
                <td class="label">Total Capitaux propres</td>
                <td class="amount">{bilan_passif['capitaux_propres']['total_capitaux_propres']:,.2f}</td>
            </tr>
            
            <tr>
                <td class="label">Provisions pour risques et charges</td>
                <td class="amount">{bilan_passif['provisions']['provisions_risques_charges']:,.2f}</td>
            </tr>
            
            <tr class="subtotal">
                <td class="label">DETTES</td>
                <td class="amount"></td>
            </tr>
            <tr>
                <td class="label">&nbsp;&nbsp;Emprunts auprès des établissements de crédit</td>
                <td class="amount">{bilan_passif['dettes']['emprunts_etablissements_credit']:,.2f}</td>
            </tr>
            <tr>
                <td class="label">&nbsp;&nbsp;Fournisseurs</td>
                <td class="amount">{bilan_passif['dettes']['fournisseurs']:,.2f}</td>
            </tr>
            <tr>
                <td class="label">&nbsp;&nbsp;Dettes fiscales et sociales</td>
                <td class="amount">{bilan_passif['dettes']['dettes_fiscales_sociales']:,.2f}</td>
            </tr>
            <tr>
                <td class="label">&nbsp;&nbsp;Autres dettes</td>
                <td class="amount">{bilan_passif['dettes']['autres_dettes']:,.2f}</td>
            </tr>
            <tr class="subtotal">
                <td class="label">Total Dettes</td>
                <td class="amount">{bilan_passif['dettes']['total_dettes']:,.2f}</td>
            </tr>
            
            <tr>
                <td class="label">Produits constatés d'avance</td>
                <td class="amount">{bilan_passif['comptes_regularisation']['produits_constates_avance']:,.2f}</td>
            </tr>
            
            <tr class="total">
                <td class="label">TOTAL PASSIF</td>
                <td class="amount">{bilan_passif['total_passif']:,.2f}</td>
            </tr>
        </tbody>
    </table>

    <div class="page-break"></div>

    <!-- PAGE 3: COMPTE DE RÉSULTAT -->
    <div class="section-title">FORMULAIRE 2031 - COMPTE DE RÉSULTAT</div>
    
    <table class="fiscal-table">
        <thead>
            <tr>
                <th>PRODUITS D'EXPLOITATION</th>
                <th style="text-align: right;">Montant (€)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class="label">Locations meublées</td>
                <td class="amount">{compte_resultat['produits_exploitation']['locations_meublees']:,.2f}</td>
            </tr>
            <tr>
                <td class="label">Autres produits</td>
                <td class="amount">{compte_resultat['produits_exploitation'].get('autres_produits', 0):,.2f}</td>
            </tr>
            <tr class="total">
                <td class="label">TOTAL PRODUITS D'EXPLOITATION</td>
                <td class="amount">{compte_resultat['produits_exploitation']['total_produits_exploitation']:,.2f}</td>
            </tr>
        </tbody>
    </table>
    
    <table class="fiscal-table">
        <thead>
            <tr>
                <th>CHARGES D'EXPLOITATION</th>
                <th style="text-align: right;">Montant (€)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class="label">Impôts et taxes</td>
                <td class="amount">{compte_resultat['charges_exploitation']['impots_taxes']:,.2f}</td>
            </tr>
            <tr>
                <td class="label">Assurances</td>
                <td class="amount">{compte_resultat['charges_exploitation']['assurances']:,.2f}</td>
            </tr>
            <tr>
                <td class="label">Honoraires (comptabilité, CGA)</td>
                <td class="amount">{compte_resultat['charges_exploitation']['honoraires']:,.2f}</td>
            </tr>
            <tr>
                <td class="label">Charges locatives et énergie</td>
                <td class="amount">{compte_resultat['charges_exploitation']['charges_locatives_energie']:,.2f}</td>
            </tr>
            <tr>
                <td class="label">Services extérieurs</td>
                <td class="amount">{compte_resultat['charges_exploitation']['services_exterieurs']:,.2f}</td>
            </tr>
            <tr>
                <td class="label">Charges de copropriété</td>
                <td class="amount">{compte_resultat['charges_exploitation']['charges_copropriete']:,.2f}</td>
            </tr>
            <tr>
                <td class="label">Entretien et réparations</td>
                <td class="amount">{compte_resultat['charges_exploitation']['entretien_reparations']:,.2f}</td>
            </tr>
            <tr>
                <td class="label">Dotations aux amortissements</td>
                <td class="amount">{compte_resultat['charges_exploitation']['dotations_amortissements']:,.2f}</td>
            </tr>
            <tr class="total">
                <td class="label">TOTAL CHARGES D'EXPLOITATION</td>
                <td class="amount">{compte_resultat['charges_exploitation']['total_charges_exploitation']:,.2f}</td>
            </tr>
        </tbody>
    </table>
    
    <table class="fiscal-table">
        <tbody>
            <tr class="total {'positive' if compte_resultat['resultat_exploitation'] >= 0 else 'negative'}">
                <td class="label">RÉSULTAT D'EXPLOITATION</td>
                <td class="amount">{compte_resultat['resultat_exploitation']:,.2f}</td>
            </tr>
        </tbody>
    </table>
    
    <table class="fiscal-table">
        <thead>
            <tr>
                <th>RÉSULTAT FINANCIER</th>
                <th style="text-align: right;">Montant (€)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class="label">Produits financiers</td>
                <td class="amount">{compte_resultat['resultat_financier']['produits_financiers']:,.2f}</td>
            </tr>
            <tr>
                <td class="label">Charges financières (intérêts d'emprunts)</td>
                <td class="amount">{compte_resultat['resultat_financier']['charges_financieres']:,.2f}</td>
            </tr>
            <tr class="subtotal">
                <td class="label">Résultat financier</td>
                <td class="amount">{compte_resultat['resultat_financier']['resultat_financier']:,.2f}</td>
            </tr>
        </tbody>
    </table>
    
    <table class="fiscal-table">
        <tbody>
            <tr class="subtotal">
                <td class="label">RÉSULTAT COURANT AVANT IMPÔT</td>
                <td class="amount">{compte_resultat['resultat_courant']:,.2f}</td>
            </tr>
        </tbody>
    </table>
    
    <table class="fiscal-table">
        <thead>
            <tr>
                <th>RÉSULTAT EXCEPTIONNEL</th>
                <th style="text-align: right;">Montant (€)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class="label">Produits exceptionnels</td>
                <td class="amount">{compte_resultat['resultat_exceptionnel']['produits_exceptionnels']:,.2f}</td>
            </tr>
            <tr>
                <td class="label">Charges exceptionnelles</td>
                <td class="amount">{compte_resultat['resultat_exceptionnel']['charges_exceptionnelles']:,.2f}</td>
            </tr>
            <tr class="subtotal">
                <td class="label">Résultat exceptionnel</td>
                <td class="amount">{compte_resultat['resultat_exceptionnel']['resultat_exceptionnel']:,.2f}</td>
            </tr>
        </tbody>
    </table>
    
    <table class="fiscal-table">
        <tbody>
            <tr class="total {'positive' if compte_resultat['resultat_net'] >= 0 else 'negative'}">
                <td class="label">RÉSULTAT NET (Bénéfice ou Perte)</td>
                <td class="amount" style="font-size: 12pt;">{compte_resultat['resultat_net']:,.2f}</td>
            </tr>
        </tbody>
    </table>

    <div class="page-break"></div>

    <!-- PAGE 4: FORMULAIRE 2033-A - IMMOBILISATIONS -->
    <div class="section-title">FORMULAIRE 2033-A - IMMOBILISATIONS</div>
    
    <table class="fiscal-table">
        <thead>
            <tr>
                <th style="width: 30%;">Nature</th>
                <th style="text-align: right;">Valeur origine</th>
                <th style="text-align: right;">Amort. antérieurs</th>
                <th style="text-align: right;">Dotations exercice</th>
                <th style="text-align: right;">Amort. cumulés</th>
                <th style="text-align: right;">Valeur nette</th>
            </tr>
        </thead>
        <tbody>
"""

        # Immobilisations détaillées
        for immo in f2033a['immobilisations'][:10]:  # Limite à 10 pour lisibilité
            html_content += f"""
            <tr>
                <td class="label">{immo['nature'][:40]}</td>
                <td class="amount">{immo['valeur_origine']:,.2f}</td>
                <td class="amount">{immo['amortissements_anterieurs']:,.2f}</td>
                <td class="amount">{immo['dotations_exercice']:,.2f}</td>
                <td class="amount">{immo['amortissements_cumules']:,.2f}</td>
                <td class="amount">{immo['valeur_nette_comptable']:,.2f}</td>
            </tr>
"""

        html_content += f"""
            <tr class="total">
                <td class="label">TOTAL</td>
                <td class="amount">{f2033a['total_immobilisations_brutes']:,.2f}</td>
                <td class="amount"></td>
                <td class="amount">{f2033b['total_dotations']:,.2f}</td>
                <td class="amount">{f2033a['total_amortissements']:,.2f}</td>
                <td class="amount">{f2033a['total_valeur_nette']:,.2f}</td>
            </tr>
        </tbody>
    </table>

    <div class="page-break"></div>

    <!-- PAGE 5: FORMULAIRE 2033-B - TABLEAU DES AMORTISSEMENTS -->
    <div class="section-title">FORMULAIRE 2033-B - TABLEAU DES AMORTISSEMENTS</div>
    
    <table class="fiscal-table">
        <thead>
            <tr>
                <th style="width: 40%;">Nature</th>
                <th style="text-align: right;">Montant début exercice</th>
                <th style="text-align: right;">Dotations exercice</th>
                <th style="text-align: right;">Montant fin exercice</th>
            </tr>
        </thead>
        <tbody>
"""

        for amort in f2033b['amortissements']:
            html_content += f"""
            <tr>
                <td class="label">{amort['nature']}</td>
                <td class="amount">{amort['montant_debut_exercice']:,.2f}</td>
                <td class="amount">{amort['dotations_exercice']:,.2f}</td>
                <td class="amount">{amort['montant_fin_exercice']:,.2f}</td>
            </tr>
"""

        html_content += f"""
            <tr class="total">
                <td class="label">TOTAL AMORTISSEMENTS</td>
                <td class="amount">{f2033b['total_debut']:,.2f}</td>
                <td class="amount">{f2033b['total_dotations']:,.2f}</td>
                <td class="amount">{f2033b['total_fin']:,.2f}</td>
            </tr>
        </tbody>
    </table>
    
    <div style="margin-top: 40px; padding: 15px; background-color: #f9f9f9; border: 1px solid #ccc;">
        <p style="margin: 0; font-size: 9pt; color: #666;">
            <strong>Document généré automatiquement</strong> - Ce document est une représentation simplifiée de la liasse fiscale.
            Pour une déclaration officielle, veuillez compléter les formulaires Cerfa 2031 et 2033.
        </p>
    </div>

</body>
</html>
        """
        
        memory.pdf_html = html_content
        # Ajouter le HTML dans la liasse fiscale pour le stockage en DB
        memory.liasse_fiscale["html_output"] = html_content
        
        logger.info("Liasse fiscale HTML generated with professional formatting")
        
        return memory
    
    async def post(self, memory, prep_res, exec_res):
        return memory


# ============================================================================
# FLOW DEFINITION
# ============================================================================
def create_liasse_flow():
    """Crée le flow complet de génération de liasse fiscale"""
    
    load = LoadLmnpUserData()
    immobilisations = ComputeImmobilisations()
    charges = ComputeCharges()
    produits = ComputeProduits()
    compte_resultat = ComputeCompteResultat()
    bilan = ComputeBilan()
    fiscal_rules = ApplyFiscalRules()
    build_liasse = BuildLiasseFiscale()
    generate_pdf = GenerateSimplePDF()
    
    # Pipeline linéaire
    load >> immobilisations >> charges >> produits >> compte_resultat >> bilan >> fiscal_rules >> build_liasse >> generate_pdf
    
    return Flow(start=load, options={"max_visits": 100})


# ============================================================================
# ENTRYPOINTS
# ============================================================================
async def generate_liasse_for_user(user_id: str, fiscal_year: int):
    """Génère la liasse fiscale pour un utilisateur et une année donnée"""
    
    memory = Memory({
        "user_id": user_id,
        "fiscal_year": fiscal_year
    })
    
    flow = create_liasse_flow()
    await flow.run(memory)
    
    return memory.liasse_fiscale


async def generate_liasse_json_only(user_id: str, fiscal_year: int):
    """Génère le JSON de la liasse avec HTML (mais sans conversion PDF finale)"""
    
    memory = Memory({
        "user_id": user_id,
        "fiscal_year": fiscal_year
    })
    
    # Flow avec génération HTML
    load = LoadLmnpUserData()
    immobilisations = ComputeImmobilisations()
    charges = ComputeCharges()
    produits = ComputeProduits()
    compte_resultat = ComputeCompteResultat()
    bilan = ComputeBilan()
    fiscal_rules = ApplyFiscalRules()
    build_liasse = BuildLiasseFiscale()
    generate_pdf = GenerateSimplePDF()
    
    load >> immobilisations >> charges >> produits >> compte_resultat >> bilan >> fiscal_rules >> build_liasse >> generate_pdf
    
    flow = Flow(start=load)
    await flow.run(memory)
    
    return memory.liasse_fiscale


if __name__ == "__main__":
    # Test avec un user_id et année fiscale
    import sys
    user_id = sys.argv[1] if len(sys.argv) > 1 else "test_user_id"
    fiscal_year = int(sys.argv[2]) if len(sys.argv) > 2 else 2026
    
    liasse = asyncio.run(generate_liasse_for_user(user_id, fiscal_year))
    
    import json
    print(json.dumps(liasse, indent=2, ensure_ascii=False))
