"""
Admin routes for manual cleanup operations
Provides endpoints for administrators to manage temporary file cleanup
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from core.auth import User, current_active_user
from service.cleanup_service import TmpFilesCleanupService
from typing import Optional

router = APIRouter()

# Request models
class CleanupRequest(BaseModel):
    max_age_hours: Optional[int] = 24
    cleanup_type: Optional[str] = "full"  # "time_based", "command_based", or "full"

# Response models are handled by the cleanup service directly

@router.get("/admin/cleanup/stats")
async def get_cleanup_stats(user: User = Depends(current_active_user)):
    """
    Get statistics about temporary files
    
    Returns information about tmp_files without deleting anything.
    Useful for monitoring and deciding when to run cleanup.
    """
    try:
        cleanup_service = TmpFilesCleanupService()
        stats = await cleanup_service.get_cleanup_stats()
        
        return {
            "success": True,
            "user": user.email,
            "action": "get_stats",
            **stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cleanup stats: {str(e)}"
        )

@router.post("/admin/cleanup/manual")
async def manual_cleanup(
    request: CleanupRequest,
    user: User = Depends(current_active_user)
):
    """
    Manually trigger cleanup of temporary files
    
    Args:
        request: Cleanup parameters (max_age_hours, cleanup_type)
        user: Authenticated user (must be logged in)
        
    Returns:
        Cleanup results and statistics
    """
    try:
        cleanup_service = TmpFilesCleanupService()
        
        # Choose cleanup method based on request
        if request.cleanup_type == "time_based":
            result = await cleanup_service.cleanup_old_files(request.max_age_hours)
            result["cleanup_type"] = "time_based"
            
        elif request.cleanup_type == "command_based":
            result = await cleanup_service.cleanup_by_command_status()
            result["cleanup_type"] = "command_based"
            
        else:  # "full" or any other value
            result = await cleanup_service.full_cleanup(request.max_age_hours)
            result["cleanup_type"] = "full"
        
        # Add metadata
        result["triggered_by"] = user.email
        result["manual_cleanup"] = True
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Manual cleanup failed: {str(e)}"
        )

@router.post("/admin/cleanup/emergency")
async def emergency_cleanup(user: User = Depends(current_active_user)):
    """
    Emergency cleanup - deletes ALL temporary files regardless of age
    
    Use with caution! This will delete all files in tmp_files bucket.
    Should only be used when storage is critically low.
    """
    try:
        cleanup_service = TmpFilesCleanupService()
        
        # Emergency cleanup: delete all files (max_age_hours = 0)
        result = await cleanup_service.cleanup_old_files(max_age_hours=0)
        
        # Add emergency metadata
        result["cleanup_type"] = "emergency"
        result["triggered_by"] = user.email
        result["emergency_cleanup"] = True
        result["warning"] = "All temporary files were deleted regardless of age"
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Emergency cleanup failed: {str(e)}"
        )

@router.delete("/admin/cleanup/file/{file_id}")
async def delete_specific_file(
    file_id: str,
    user: User = Depends(current_active_user)
):
    """
    Delete a specific temporary file by ID
    
    Args:
        file_id: GridFS ObjectId of the file to delete
        user: Authenticated user
        
    Returns:
        Deletion result
    """
    try:
        from bson import ObjectId
        cleanup_service = TmpFilesCleanupService()
        
        # Validate ObjectId format
        try:
            obj_id = ObjectId(file_id)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file ID format: {file_id}"
            )
        
        # Get file info before deletion
        cursor = cleanup_service.tmp_bucket.find({"_id": obj_id})
        try:
            file_doc = await cursor.next()
            file_info = {
                "id": str(file_doc._id),
                "filename": file_doc.filename,
                "size": file_doc.length,
                "upload_date": file_doc.upload_date.isoformat()
            }
        except StopAsyncIteration:
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {file_id}"
            )
        
        # Delete the file
        await cleanup_service.tmp_bucket.delete(obj_id)
        
        return {
            "success": True,
            "action": "delete_specific_file",
            "deleted_file": file_info,
            "triggered_by": user.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )
    

