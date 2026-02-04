"""
MergeImages API route
Handles image file upload and merge command creation
"""

import asyncio
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import List
from core.auth import User
from core.auth import current_active_user
from service.file_service import FileService
from shell.command_manager import create_command, process_command

# Set up logger for this module
logger = logging.getLogger(__name__)

router = APIRouter()

# Supported image MIME types
SUPPORTED_IMAGE_TYPES = [
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/bmp',
    'image/gif',
    'image/tiff'
]

@router.post("/mergeImages")
async def merge_images_endpoint(
    files: List[UploadFile] = File(...),
    user: User = Depends(current_active_user)
):
    """
    Upload image files and create a merge command to convert them to PDF
    
    Steps:
    1. Validate uploaded files are supported image formats
    2. Store files in GridFS tmp_files bucket
    3. Create merge command with file IDs
    4. Start command processing asynchronously
    5. Return command ID for polling
    """
    
    logger.info(f"🔥 Starting image to PDF merge for user {user.email} with {len(files)} files")
    
    if len(files) < 1:
        logger.warning(f"❌ No files provided")
        raise HTTPException(
            status_code=400,
            detail="At least 1 image file is required"
        )
    
    # Validate all files are supported images
    for i, file in enumerate(files):
        logger.info(f"📁 File {i+1}: {file.filename} ({file.content_type})")
        if not file.content_type or file.content_type not in SUPPORTED_IMAGE_TYPES:
            logger.error(f"❌ Invalid file type: {file.content_type}")
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' is not a supported image format. Supported formats: JPG, JPEG, PNG, BMP, GIF, TIFF."
            )
    
    try:
        logger.info("🔧 Creating FileService instance...")
        file_service = FileService()
        uploaded_file_ids = []
        
        # Upload each file to GridFS tmp_files bucket
        for i, file in enumerate(files):
            logger.info(f"📤 Uploading file {i+1}: {file.filename}")
            
            # Read file content
            content = await file.read()
            logger.info(f"📊 File size: {len(content)} bytes")
            
            if len(content) == 0:
                logger.error(f"❌ Empty file: {file.filename}")
                raise HTTPException(
                    status_code=400,
                    detail=f"File '{file.filename}' is empty"
                )
            
            # Upload to tmp_files bucket (different from user files)
            logger.info(f"🗃️ Calling upload_temp_file for {file.filename}")
            result = await file_service.upload_temp_file(
                file_content=content,
                filename=file.filename,
                content_type=file.content_type,
                user_email=user.email,
                user_id=str(user.id)
            )
            
            logger.info(f"📋 Upload result: {result}")
            
            if not result.get("success"):
                logger.error(f"❌ Upload failed: {result}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to upload file '{file.filename}': {result.get('error')}"
                )
            
            uploaded_file_ids.append(result["file_id"])
            logger.info(f"✅ File uploaded with ID: {result['file_id']}")
        
        # Create merge command
        logger.info(f"🚀 Creating merge images command with file IDs: {uploaded_file_ids}")
        command_id = await create_command(
            shell_command="MergeImages",
            args={
                "file_ids": uploaded_file_ids,
                "user_id": str(user.id),
                "user_email": user.email
            }
        )
        
        logger.info(f"✅ Command created with ID: {command_id}")
        
        # Start command processing asynchronously
        logger.info("🔄 Starting async command processing...")
        asyncio.create_task(process_command(command_id))
        
        logger.info("🎉 Image merge request completed successfully")
        return {
            "success": True,
            "command_id": command_id,
            "message": f"Image to PDF merge started for {len(files)} files",
            "uploaded_files": [
                {"filename": f.filename, "file_id": fid} 
                for f, fid in zip(files, uploaded_file_ids)
            ]
        }
        
    except HTTPException:
        logger.error("❌ HTTP Exception occurred (re-raising)")
        raise
    except Exception as e:
        logger.error(f"💥 Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process image merge request: {str(e)}"
        )
