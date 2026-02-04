from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from core.auth import User
from core.auth import current_active_user
from service.user_service import UserService
from service.file_service import FileService
from typing import Dict, Any
import io

router = APIRouter()

@router.get("/protected-route")
async def protected_route(user: User = Depends(current_active_user)):
    """Example protected route that requires authentication"""
    return {
        "message": f"Hello {user.email}! This is a protected route.",
        "user_id": str(user.id),
        "user_data": {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_verified": user.is_verified
        }
    }


@router.get("/user-profile")
async def get_user_profile(user: User = Depends(current_active_user)):
    """Get current user's profile"""
    return {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_verified": user.is_verified,
        "is_active": user.is_active,
    }


# Request/Response models for authentication endpoints
class AuthenticateRequest(BaseModel):
    email: str
    password: str
    first_name: str = "User"
    last_name: str = "Name"
    create: bool = True

class RegisterRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str

class AuthResponse(BaseModel):
    success: bool
    action: str = None
    token: str = None
    token_type: str = None
    user_profile: Dict[str, Any] = None
    error: str = None
    details: Dict[str, Any] = None

class RenameFileRequest(BaseModel):
    new_name: str


@router.post("/authenticate", response_model=AuthResponse)
async def authenticate_user(request: AuthenticateRequest):
    """
    Authenticate user by email. Creates user if doesn't exist and create=True.
    This is a direct route wrapper for the authenticate_email_async function.
    """
    print(f"🔍 /api/authenticate called with email: {request.email}, create: {request.create}")
    try:
        service = UserService()
        result = await service.authenticate_email_async(
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            create=request.create
        )
        
        print(f"✅ Authentication result: success={result.get('success')}, action={result.get('action')}")
        return AuthResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/register", response_model=AuthResponse)
async def register_user(request: RegisterRequest):
    """
    Register a new user (or authenticate if already exists).
    This is a direct route wrapper for the register_async function.
    Always attempts to create the user, falls back to authentication if exists.
    """
    print(f"🔍 /api/register called with email: {request.email}")
    try:
        service = UserService()
        result = await service.authenticate_email_async(
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            create=True  # Always try to create
        )
        
        print(f"✅ Registration result: success={result.get('success')}, action={result.get('action')}")
        return AuthResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}"
        )


# File Management Routes (Protected) - Using GridFS
@router.get("/files")
async def list_files(user: User = Depends(current_active_user)):
    """List user's files using GridFS"""
    try:
        file_service = FileService()
        files = await file_service.list_user_files(user.email, str(user.id))
        
        return {
            "files": files,
            "total": len(files),
            "user": user.email
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@router.post("/files/upload")
async def upload_file(file: UploadFile = File(), user: User = Depends(current_active_user)):
    """Upload a file using GridFS"""
    try:
        file_service = FileService()
        
        # Read file content
        content = await file.read()
        
        result = await file_service.upload_file(
            file_content=content,
            filename=file.filename,
            content_type=file.content_type,
            user_email=user.email,
            user_id=str(user.id)
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Upload failed"))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@router.delete("/files/{file_id}")
async def delete_file(file_id: str, user: User = Depends(current_active_user)):
    """Delete a file using GridFS"""
    try:
        file_service = FileService()
        
        result = await file_service.delete_file(file_id, user.email, str(user.id))
        
        if result.get("success"):
            return result
        else:
            if "not found" in result.get("error", "").lower():
                raise HTTPException(status_code=404, detail=result.get("error"))
            else:
                raise HTTPException(status_code=500, detail=result.get("error"))
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@router.get("/files/{file_id}")
async def download_file(file_id: str, user: User = Depends(current_active_user)):
    """Download a file using GridFS"""
    try:
        file_service = FileService()
        
        # Download file content with user verification
        file_data = await file_service.download_file(file_id, user.email, str(user.id))
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found or access denied")
        
        # Create streaming response
        return StreamingResponse(
            io.BytesIO(file_data["content"]),
            media_type=file_data["content_type"],
            headers={"Content-Disposition": f"attachment; filename={file_data['filename']}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")

@router.get("/files/{file_id}/info")
async def get_file_info(file_id: str, user: User = Depends(current_active_user)):
    """Get file information using GridFS"""
    try:
        file_service = FileService()
        file_info = await file_service.get_file_info(file_id, user.email, str(user.id))
        
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found or access denied")
        
        return {
            "success": True,
            "file_info": file_info,
            "owner": user.email
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get file info: {str(e)}")

@router.post("/files/{file_id}/rename")
async def rename_file_post(
    file_id: str, 
    request: RenameFileRequest,
    user: User = Depends(current_active_user)
):
    """Rename a file (update display name only) - POST operation"""
    try:
        file_service = FileService()
        
        result = await file_service.rename_file(
            file_id=file_id,
            new_display_name=request.new_name,
            user_email=user.email,
            user_id=str(user.id)
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "new_display_name": result["new_display_name"],
                "file_id": file_id
            }
        else:
            # Determine appropriate HTTP status code
            if "not found" in result["error"].lower() or "access denied" in result["error"].lower():
                raise HTTPException(status_code=404, detail=result["error"])
            elif "empty" in result["error"].lower() or "too long" in result["error"].lower():
                raise HTTPException(status_code=400, detail=result["error"])
            else:
                raise HTTPException(status_code=500, detail=result["error"])
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rename failed: {str(e)}")


@router.delete("/account")
async def delete_account(user: User = Depends(current_active_user)):
    """
    Delete current user's account and all associated data
     WARNING: This is a destructive operation that cannot be undone!
    """
    try:
        print(f" Account deletion request for User: {user.email}, ID: {user.id}")

        user_service = UserService()
        result = await user_service.delete_account_async(
            user_email=user.email,
            user_id=str(user.id)
        )
        
        if result["success"]:
            print(f" Account deletion successful: {user.email}")
            print(f"   Files deleted: {result.get('files_deleted', 0)}")
            return {
                "success": True,
                "message": result["message"],
                "files_deleted": result.get("files_deleted", 0),
                "account_deleted": user.email
            }
        else:
            # Determine appropriate HTTP status code
            if "not found" in result["error"].lower():
                raise HTTPException(status_code=404, detail=result["error"])
            elif "access denied" in result["error"].lower():
                raise HTTPException(status_code=403, detail=result["error"])
            else:
                raise HTTPException(status_code=500, detail=result["error"])
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"Account deletion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Account deletion failed: {str(e)}")
