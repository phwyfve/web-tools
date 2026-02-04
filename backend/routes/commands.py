"""
Commands API route
Provides long-polling endpoint for command status checking
"""

from fastapi import APIRouter, HTTPException, Path
from shell.command_manager import get_command_status

router = APIRouter()

@router.get("/command/{command_id}")
async def get_command_endpoint(
    command_id: str = Path(..., description="The ID of the command to check")
):
    """
    Get command status and results
    
    Long-polling logic for client:
    - If exit_state == -1: command is still running
    - If exit_state != -1: command finished (success or error)
    
    Returns:
        Command details including execution status and results
    """
    
    try:
        result = await get_command_status(command_id)
        
        if "error" in result:
            raise HTTPException(
                status_code=404,
                detail=result["error"]
            )
        
        return {
            "success": True,
            "command": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get command status: {str(e)}"
        )
