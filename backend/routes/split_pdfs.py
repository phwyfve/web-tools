"""
SplitPdfs API route
Handles PDF file upload and split command creation
"""

import asyncio
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from core.auth import User
from core.auth import current_active_user
from service.file_service import FileService
from shell.command_manager import create_command, process_command

# Set up logger for this module
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/splitPdf")
async def split_pdf_endpoint(
    file: UploadFile = File(...),
    user: User = Depends(current_active_user)
):
    """
    Upload a PDF file and create a split command
    
    Steps:
    1. Validate uploaded file is a PDF
    2. Store file in GridFS tmp_files bucket
    3. Create split command with file ID
    4. Start command processing asynchronously
    5. Return command ID for polling
    """
    
    logger.info(f"✂️ Starting PDF split for user {user.email} with file {file.filename}")
    
    # Validate file is a PDF
    logger.info(f"📁 File: {file.filename} ({file.content_type})")
    if not file.content_type or not file.content_type.startswith('application/pdf'):
        logger.error(f"❌ Invalid file type: {file.content_type}")
        raise HTTPException(
            status_code=400,
            detail=f"File '{file.filename}' is not a PDF. Only PDF files are allowed."
        )
    
    try:
        logger.info("🔧 Creating FileService instance...")
        file_service = FileService()
        
        # Read file content
        logger.info(f"📖 Reading file content...")
        content = await file.read()
        logger.info(f"📊 File size: {len(content)} bytes")
        
        if len(content) == 0:
            logger.error(f"❌ Empty file: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' is empty"
            )
        
        # Upload to tmp_files bucket
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
        
        file_id = result["file_id"]
        logger.info(f"✅ File uploaded with ID: {file_id}")
        
        # Create split command
        logger.info(f"🚀 Creating split command with file ID: {file_id}")
        command_id = await create_command(
            shell_command="SplitPdfs",
            args={"file_id": file_id}
        )
        
        logger.info(f"📝 Command created with ID: {command_id}")
        
        # Start command processing in background
        logger.info("⚡ Starting command processing in background...")
        asyncio.create_task(process_command(command_id))
        
        # Return command ID for client polling
        logger.info(f"✅ Split command initiated successfully: {command_id}")
        return {
            "success": True,
            "command_id": command_id,
            "file_id": file_id,
            "filename": file.filename,
            "message": "PDF split command created. Use command_id to check status."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in split_pdf_endpoint: {str(e)}")
        logger.exception("Full exception details:")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
