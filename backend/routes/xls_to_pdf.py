"""
XlsToPdf API route
Handles Excel file upload and conversion command creation
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

# Supported Excel MIME types
SUPPORTED_EXCEL_TYPES = [
    'application/vnd.ms-excel',  # .xls
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
    'application/vnd.ms-excel.sheet.macroEnabled.12',  # .xlsm
]

@router.post("/xlsToPdf")
async def xls_to_pdf_endpoint(
    files: List[UploadFile] = File(...),
    user: User = Depends(current_active_user)
):
    """
    Upload Excel files and create a conversion command to PDF
    
    Steps:
    1. Validate uploaded files are supported Excel formats
    2. Store files in GridFS tmp_files bucket
    3. Create conversion command with file IDs
    4. Start command processing asynchronously
    5. Return command ID for polling
    """
    
    logger.info(f"🔥 Starting Excel to PDF conversion for user {user.email} with {len(files)} files")
    
    if len(files) < 1:
        logger.warning(f"❌ No files provided")
        raise HTTPException(
            status_code=400,
            detail="At least 1 Excel file is required"
        )
    
    # Validate all files are supported Excel formats
    for i, file in enumerate(files):
        logger.info(f"📁 File {i+1}: {file.filename} ({file.content_type})")
        
        # Check MIME type or file extension
        is_valid = False
        if file.content_type and file.content_type in SUPPORTED_EXCEL_TYPES:
            is_valid = True
        elif file.filename:
            # Fallback to file extension check
            ext = file.filename.lower().rsplit('.', 1)[-1] if '.' in file.filename else ''
            if ext in ['xls', 'xlsx', 'xlsm']:
                is_valid = True
        
        if not is_valid:
            logger.error(f"❌ Invalid file type: {file.content_type}")
            raise HTTPException(
                status_code=400,
                detail=f"File '{file.filename}' is not a supported Excel format. Supported formats: XLS, XLSX, XLSM."
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
                content_type=file.content_type or 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
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
        
        # Create conversion command
        logger.info(f"🚀 Creating Excel to PDF conversion command with file IDs: {uploaded_file_ids}")
        command_id = await create_command(
            shell_command="XlsToPdf",
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
        
        logger.info("🎉 Excel to PDF conversion request completed successfully")
        return {
            "success": True,
            "command_id": command_id,
            "message": f"Excel to PDF conversion started for {len(files)} files",
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
            detail=f"Failed to process Excel to PDF conversion request: {str(e)}"
        )
