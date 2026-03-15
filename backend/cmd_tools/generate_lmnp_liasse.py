"""
GenerateLmnpLiasse command handler
Generates fiscal liasse PDF from LMNP user data using Caskada flow
"""

import asyncio
import json
import logging
from typing import Dict, Any
from bson import ObjectId
from pathlib import Path

# Import the flow from cmd_accountant
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from cmd_accountant.flow_lmnp_liasse import generate_liasse_for_user

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
        # Define output directory in /tmp (writable in Docker)
        output_dir = Path("/tmp") / "liasse_output" / f"liasse_{fiscal_year}_{user_id}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Execute the Caskada flow to generate liasse PDFs
        result = await generate_liasse_for_user(user_id, fiscal_year, str(output_dir))
        
        logger.info(f"Successfully generated liasse for user {user_id}, year {fiscal_year}")
        
        # Store the result in MongoDB for future reference
        liasse_doc = {
            "user_id": user_id,
            "fiscal_year": fiscal_year,
            "cerfa_2031_path": result.get("cerfa_2031"),
            "success": result.get("success"),
            "generated_at": None  # Could add timestamp if needed
        }
        
        await db.lmnp_liasses.update_one(
            {"user_id": user_id, "fiscal_year": fiscal_year},
            {"$set": liasse_doc},
            upsert=True
        )
        
        logger.info(f"Liasse metadata stored in database for user {user_id}, year {fiscal_year}")
        
        # Return summary for stdout
        return {
            "user_id": user_id,
            "fiscal_year": fiscal_year,
            "success": result.get("success"),
            "cerfa_2031": result.get("cerfa_2031"),
            "output_dir": str(output_dir)
        }
        
    except Exception as e:
        logger.error(f"Failed to generate liasse for user {user_id}, year {fiscal_year}: {str(e)}")
        raise ValueError(f"Liasse generation failed: {str(e)}")
