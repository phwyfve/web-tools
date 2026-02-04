import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException, Body
from core.auth import User
from core.auth import current_active_user
from shell.command_manager import create_command, process_command

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/youtubeSummary")
async def youtube_summary_endpoint(
    url: str = Body(..., embed=True),
    user: User = Depends(current_active_user)
):
    """
    Submit a YouTube video URL and create a summary command
    Steps:
    1. Validate URL
    2. Create youtube_summary command with URL
    3. Start command processing asynchronously
    4. Return command ID for polling
    """
    logger.info(f"\U0001F4FA Starting YouTube summary for user {user.email} with url {url}")
    if not url or not url.startswith("http"):
        logger.error(f"\u274c Invalid URL: {url}")
        raise HTTPException(
            status_code=400,
            detail=f"URL '{url}' is not valid."
        )
    try:
        # create_command est async, donc il faut await
        command_id = await create_command(
            shell_command="youtube_summary",
            args={"url": url, "user_id": str(user.id)}
        )
        # Start processing asynchronously
        asyncio.create_task(process_command(command_id))
        return {"command_id": command_id}
    except Exception as e:
        logger.error(f"\u274c Failed to create/process command: {e}")
        raise HTTPException(status_code=500, detail="Failed to process YouTube summary command.")