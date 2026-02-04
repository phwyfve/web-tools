"""
File download routes for processed files
Handles downloading of temporary/processed files without requiring user authentication
"""

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import StreamingResponse
from service.file_service import FileService
import io
from bson import ObjectId

router = APIRouter()

@router.get("/processed-files/{file_id}")
async def download_processed_file(
    file_id: str = Path(..., description="The GridFS file ID to download")
):
    """
    Download a processed file from GridFS tmp_files collection
    
    This endpoint is designed for downloading temporary files created by processing
    commands (like merged PDFs). It doesn't require user authentication since
    the file_id itself serves as the access token.
    
    Args:
        file_id: The GridFS ObjectId of the file to download
        
    Returns:
        StreamingResponse with the file content
    """
    
    try:
        # Validate file ID format
        try:
            ObjectId(file_id)
        except Exception:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file ID format: {file_id}"
            )
        
        # Use FileService to download from tmp_files bucket
        file_service = FileService()
        
        # Get the tmp_files bucket
        bucket = await file_service._get_tmp_bucket()
        
        # Download the file content using the same pattern as FileService
        content_stream = io.BytesIO()
        await bucket.download_to_stream(ObjectId(file_id), content_stream)
        file_bytes = content_stream.getvalue()
        
        # Get file metadata
        cursor = bucket.find({"_id": ObjectId(file_id)})
        file_doc = await cursor.next()
        
        if not file_doc:
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {file_id}"
            )
        
        # Extract filename and content type
        filename = file_doc.filename or f"processed_file_{file_id}.pdf"
        content_type = file_doc.metadata.get("content_type", "application/pdf")
        
        # Create streaming response
        return StreamingResponse(
            io.BytesIO(file_bytes),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (400, 404, etc.)
        raise
    except StopAsyncIteration:
        # No file found in cursor
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {file_id}"
        )
    except Exception as e:
        # Handle any other unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download file: {str(e)}"
        )
