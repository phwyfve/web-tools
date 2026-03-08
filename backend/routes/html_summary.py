"""
HtmlSummary API route
Handles text/HTML content submission and summary command creation
"""

import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from typing import Optional
from core.auth import User
from core.auth import current_active_user
from shell.command_manager import create_command, process_command

# Set up logger for this module
logger = logging.getLogger(__name__)

router = APIRouter()

class HtmlSummaryRequest(BaseModel):
    content: str = Body(..., description="Text content to summarize")
    title: Optional[str] = None

@router.post("/htmlSummary")
async def html_summary_endpoint(
    request: HtmlSummaryRequest,
    user: User = Depends(current_active_user)
):
    """
    Submit text content and create an HTML summary command
    
    Steps:
    1. Validate content
    2. Create html_summary command with content
    3. Start command processing asynchronously
    4. Return command ID for polling
    """
    
    logger.info(f"📄 Starting HTML summary for user {user.email}")
    
    if not request.content or not request.content.strip():
        logger.error(f"❌ No content provided")
        raise HTTPException(
            status_code=400,
            detail="Content cannot be empty"
        )
    
    try:
        # Create html_summary command
        logger.info(f"🚀 Creating HTML summary command")
        command_id = await create_command(
            shell_command="HtmlSummary",
            args={
                "content": request.content,
                "title": request.title or "Content Summary",
                "user_id": str(user.id)
            }
        )
        
        logger.info(f"📝 Command created with ID: {command_id}")
        
        # Start command processing in background
        logger.info("⚡ Starting command processing in background...")
        asyncio.create_task(process_command(command_id))
        
        # Return command ID for client polling
        logger.info(f"✅ HTML summary command initiated successfully: {command_id}")
        return {
            "success": True,
            "command_id": command_id,
            "message": "HTML summary started. Use command_id to check status."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in html_summary_endpoint: {str(e)}")
        logger.exception("Full exception details:")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
