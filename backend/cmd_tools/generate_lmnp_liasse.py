"""
GenerateLmnpLiasse command handler
Generates fiscal liasse from LMNP user data using Caskada flow
"""

import asyncio
import json
import logging
from typing import Dict, Any
from bson import ObjectId

# Import the flow from cmd_accountant
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from cmd_accountant.flow_lmnp_liasse import generate_liasse_json_only

logger = logging.getLogger('GenerateLmnpLiasse')


async def generate_lmnp_liasse(args: Dict[str, Any], db, fs) -> Dict[str, Any]:
    """
    Generate LMNP fiscal liasse from user data
    
    Args:
        args: Dict containing:
            - 'user_id': MongoDB User ID
            - 'fiscal_year': Fiscal year to process
        db: MongoDB database connection
        fs: GridFS instance (not used here but required by command pattern)
        
    Returns:
        Dict containing the generated liasse fiscale summary
    """
    
    user_id = args.get("user_id")
    fiscal_year = args.get("fiscal_year")
    
    if not user_id:
        raise ValueError("No user_id provided for liasse generation")
    
    if not fiscal_year:
        raise ValueError("No fiscal_year provided for liasse generation")
    
    logger.info(f"Starting LMNP liasse generation for user {user_id}, year {fiscal_year}")
    
    try:
        # Execute the Caskada flow to generate liasse
        liasse = await generate_liasse_json_only(user_id, fiscal_year)
        
        logger.info(f"Successfully generated liasse for user {user_id}, year {fiscal_year}")
        
        # Store the liasse in MongoDB for future reference
        liasse_doc = {
            "user_id": user_id,
            "fiscal_year": fiscal_year,
            "liasse": liasse,
            "generated_at": liasse["meta"]["generated_at"]
        }
        
        await db.lmnp_liasses.update_one(
            {"user_id": user_id, "fiscal_year": fiscal_year},
            {"$set": liasse_doc},
            upsert=True
        )
        
        logger.info(f"Liasse stored in database for user {user_id}, year {fiscal_year}")
        
        # Return summary for stdout
        return {
            "user_id": user_id,
            "fiscal_year": fiscal_year,
            "resultat_net": liasse["formulaire_2031"]["compte_resultat"]["resultat_net"],
            "total_actif": liasse["formulaire_2031"]["bilan_actif"]["total_actif"],
            "total_passif": liasse["formulaire_2031"]["bilan_passif"]["total_passif"],
            "bilan_equilibre": liasse["formulaire_2031"]["bilan_passif"]["total_passif"] == liasse["formulaire_2031"]["bilan_actif"]["total_actif"],
            "liasse_id": f"{user_id}_{fiscal_year}"
        }
        
    except Exception as e:
        logger.error(f"Failed to generate liasse for user {user_id}, year {fiscal_year}: {str(e)}")
        raise ValueError(f"Liasse generation failed: {str(e)}")
