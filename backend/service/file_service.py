"""
File service for handling image uploads/downloads using GridFS
"""
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from gridfs.errors import NoFile
from core.database import get_images_bucket
from typing import List, Dict, Any, Optional
import datetime
from bson import ObjectId
import io

class FileService:
    def __init__(self):
        """Initialize FileService with the images bucket"""
        self._bucket = None
        self._tmp_bucket = None
    
    async def _get_bucket(self) -> AsyncIOMotorGridFSBucket:
        """Get the GridFS bucket (lazy initialization)"""
        if self._bucket is None:
            self._bucket = get_images_bucket()
        return self._bucket
    
    async def _get_tmp_bucket(self) -> AsyncIOMotorGridFSBucket:
        """Get the temporary files GridFS bucket (lazy initialization)"""
        if self._tmp_bucket is None:
            from core.database import get_database
            db = get_database()
            self._tmp_bucket = AsyncIOMotorGridFSBucket(db, bucket_name="tmp_files")
        return self._tmp_bucket

    async def upload_file(self, file_content: bytes, filename: str, content_type: str, 
                         user_email: str, user_id: str) -> Dict[str, Any]:
        """
        Upload a file to GridFS
        
        Args:
            file_content: The file content as bytes
            filename: Original filename
            content_type: MIME type of the file
            user_email: Email of the user uploading
            user_id: ID of the user uploading
            
        Returns:
            Dict with file info and upload result
        """
        try:
            bucket = await self._get_bucket()
            
            # Create metadata
            metadata = {
                "owner_email": user_email,
                "owner_id": user_id,
                "original_filename": filename,
                "display_name": filename,
                "content_type": content_type,
                "upload_date": datetime.datetime.utcnow(),
                "file_size": len(file_content)
            }
            
            # Upload to GridFS should be closed after use
            file_id = await bucket.upload_from_stream(
                filename=filename,
                source=io.BytesIO(file_content),
                metadata=metadata
            )
            
            return {
                "success": True,
                "file_id": str(file_id),
                "filename": filename,
                "size": len(file_content),
                "content_type": content_type,
                "owner": user_email,
                "upload_date": metadata["upload_date"].isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Upload failed: {str(e)}"
            }
    
    async def upload_temp_file(self, file_content: bytes, filename: str, content_type: str, 
                              user_email: str, user_id: str) -> Dict[str, Any]:
        """
        Upload a temporary file to GridFS tmp_files bucket
        
        Args:
            file_content: The file content as bytes
            filename: Original filename
            content_type: MIME type of the file
            user_email: Email of the user uploading
            user_id: ID of the user uploading
            
        Returns:
            Dict with file info and upload result
        """
        try:
            bucket = await self._get_tmp_bucket()
            
            # Create metadata for temporary file
            metadata = {
                "owner_email": user_email,
                "owner_id": user_id,
                "original_filename": filename,
                "content_type": content_type,
                "upload_date": datetime.datetime.utcnow(),
                "file_size": len(file_content),
                "is_temporary": True
            }
            
            # Upload file to tmp_files bucket
            file_stream = io.BytesIO(file_content)
            file_id = await bucket.upload_from_stream(
                filename,
                file_stream,
                metadata=metadata
            )
            
            return {
                "success": True,
                "file_id": str(file_id),
                "filename": filename,
                "size": len(file_content),
                "content_type": content_type,
                "bucket": "tmp_files"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to upload temporary file: {str(e)}"
            }

    async def list_user_files(self, user_email: str, user_id: str) -> List[Dict[str, Any]]:
        """
        List all files for a specific user
        
        Args:
            user_email: User's email
            user_id: User's ID
            
        Returns:
            List of file information dictionaries
        """
        try:
            bucket = await self._get_bucket()
            files = []
            
            # Query files by owner
            cursor = bucket.find({"metadata.owner_email": user_email})
            
            async for file_doc in cursor:
                # Use display_name if available, fallback to original filename
                display_name = file_doc.metadata.get("display_name", file_doc.filename)
                files.append({
                    "id": str(file_doc._id),
                    "name": display_name,  # Always show display name to user
                    "original_name": file_doc.filename,  # Keep original for reference
                    "size": self._format_file_size(file_doc.length),
                    "size_bytes": file_doc.length,
                    "content_type": file_doc.metadata.get("content_type", "unknown"),
                    "uploaded": file_doc.upload_date.strftime("%Y-%m-%d"),
                    "upload_datetime": file_doc.upload_date.isoformat(),
                    "owner": file_doc.metadata.get("owner_email", user_email)
                })
            
            return files
            
        except Exception as e:
            print(f"Error listing files for user {user_email}: {e}")
            return []
    
    async def delete_file(self, file_id: str, user_email: str, user_id: str) -> Dict[str, Any]:
        """
        Delete a file from GridFS (only if owned by user)
        
        Args:
            file_id: GridFS file ID
            user_email: User's email (for ownership verification)
            user_id: User's ID (for ownership verification)
            
        Returns:
            Dict with deletion result
        """
        try:
            bucket = await self._get_bucket()
            
            # First verify the file exists and is owned by the user
            file_info = await self.get_file_info(file_id, user_email, user_id)
            if not file_info:
                return {
                    "success": False,
                    "error": "File not found or access denied"
                }
            
            # Delete the file
            await bucket.delete(ObjectId(file_id))
            
            return {
                "success": True,
                "message": f"File '{file_info['name']}' deleted successfully",
                "deleted_file_id": file_id,
                "deleted_filename": file_info['name']
            }
            
        except NoFile:
            return {
                "success": False,
                "error": "File not found"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Delete failed: {str(e)}"
            }
    
    async def download_file(self, file_id: str, user_email: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Download a file from GridFS (only if owned by user)
        
        Args:
            file_id: GridFS file ID
            user_email: User's email (for ownership verification)
            user_id: User's ID (for ownership verification)
            
        Returns:
            Dict with file content and metadata, or None if not found/no access
        """
        try:
            bucket = await self._get_bucket()
            
            # First get file info to verify ownership
            cursor = bucket.find({"_id": ObjectId(file_id)})
            file_doc = await cursor.next()
            if not file_doc:
                return None
                
            if file_doc.metadata.get("owner_email") != user_email:
                return None  # Access denied
            
            # Download the file content
            content_stream = io.BytesIO()
            await bucket.download_to_stream(ObjectId(file_id), content_stream)
            file_bytes = content_stream.getvalue()
            
            # Use display_name for download filename if available
            download_filename = file_doc.metadata.get("display_name", file_doc.filename)
            
            return {
                "content": file_bytes,
                "filename": download_filename,  # Use display name for download
                "original_filename": file_doc.filename,  # Keep original for reference
                "content_type": file_doc.metadata.get("content_type", "application/octet-stream"),
                "size": file_doc.length
            }
            
        except NoFile:
            return None
        except StopAsyncIteration:
            return None  # No file found
        except Exception as e:
            print(f"Error downloading file {file_id}: {e}")
            return None
    
    async def get_file_info(self, file_id: str, user_email: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get file information (only if owned by user)
        
        Args:
            file_id: GridFS file ID
            user_email: User's email (for ownership verification)
            user_id: User's ID (for ownership verification)
            
        Returns:
            Dict with file info, or None if not found/no access
        """
        try:
            bucket = await self._get_bucket()
            
            cursor = bucket.find({"_id": ObjectId(file_id)})
            file_doc = await cursor.next()
            if not file_doc:
                return None
                
            if file_doc.metadata.get("owner_email") != user_email:
                return None  # Access denied
            
            # Use display_name if available, fallback to original filename
            display_name = file_doc.metadata.get("display_name", file_doc.filename)
            return {
                "id": str(file_doc._id),
                "name": display_name,  # Always show display name to user
                "original_name": file_doc.filename,  # Keep original for reference
                "size": self._format_file_size(file_doc.length),
                "size_bytes": file_doc.length,
                "content_type": file_doc.metadata.get("content_type", "unknown"),
                "uploaded": file_doc.upload_date.strftime("%Y-%m-%d"),
                "upload_datetime": file_doc.upload_date.isoformat(),
                "owner": file_doc.metadata.get("owner_email", user_email)
            }
            
        except StopAsyncIteration:
            return None  # No file found
        except Exception as e:
            print(f"Error getting file info for {file_id}: {e}")
            return None
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    async def rename_file(self, file_id: str, new_display_name: str, user_email: str, user_id: str) -> Dict[str, Any]:
        """
        Rename a file by updating its display name only (PATCH operation)
        
        Args:
            file_id: GridFS file ID
            new_display_name: New display name for the file
            user_email: Email of the user requesting rename
            user_id: ID of the user requesting rename
            
        Returns:
            Dict with success status and message
        """
        try:
            bucket = await self._get_bucket()
            file_id_obj = ObjectId(file_id)
            
            # First verify the file exists and user owns it
            file_info = await self.get_file_info(file_id, user_email, user_id)
            if not file_info:
                return {
                    "success": False,
                    "error": "File not found or access denied"
                }
            
            # Validate new display name
            if not new_display_name.strip():
                return {
                    "success": False,
                    "error": "Display name cannot be empty"
                }
            
            if len(new_display_name.strip()) > 255:
                return {
                    "success": False,
                    "error": "Display name too long (max 255 characters)"
                }
            
            # Update only the display name in GridFS metadata
            # Access the underlying MongoDB database and fs.files collection
            # GridFS stores metadata in fs.files collection
            # Get database from the bucket's underlying client
            from database import database  # Import at runtime to ensure it's initialized
            if database is None:
                return {
                    "success": False,
                    "error": "Database not initialized"
                }
            fs_files_collection = database.fs.files
            
            # Debug: Let's see what we're searching for vs what's in the database
            print(f"🔍 DEBUG - Looking for file:")
            print(f"   file_id: {file_id_obj}")
            print(f"   owner_email: {user_email}")
            print(f"   owner_id: {user_id}")
            
            # First, let's see what's actually in the database
            actual_file = await fs_files_collection.find_one({"_id": file_id_obj})
            if actual_file:
                print(f"🔍 DEBUG - Found file in DB:")
                print(f"   actual owner_email: {actual_file.get('metadata', {}).get('owner_email')}")
                print(f"   actual owner_id: {actual_file.get('metadata', {}).get('owner_id')}")
            else:
                print(f"❌ DEBUG - File not found in database!")
            
            result = await fs_files_collection.update_one(
                {
                    "_id": file_id_obj,
                    "metadata.owner_email": user_email,
                    "metadata.owner_id": user_id
                },
                {
                    "$set": {
                        "metadata.display_name": new_display_name.strip(),
                        "metadata.renamed_at": datetime.datetime.utcnow()
                    }
                }
            )
            
            print(f"🔍 DEBUG - Update result: matched={result.matched_count}, modified={result.modified_count}")
            
            if result.modified_count > 0:
                return {
                    "success": True,
                    "message": f"File display name updated to '{new_display_name.strip()}'",
                    "new_display_name": new_display_name.strip()
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to update display name - file may not exist or access denied"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Rename failed: {str(e)}"
            }
