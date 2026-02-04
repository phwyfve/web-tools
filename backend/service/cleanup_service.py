"""
Cleanup service for temporary files in GridFS tmp_files bucket
Handles both automatic batch cleanup and manual cleanup operations
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from bson import ObjectId
from core.config import settings

# Set up logging
logger = logging.getLogger('cleanup_service')

class TmpFilesCleanupService:
    """Service for cleaning up temporary files from GridFS"""
    
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.mongodb_url)
        self.db = self.client[settings.database_name]
        self.tmp_bucket = AsyncIOMotorGridFSBucket(self.db, bucket_name="tmp_files")
    
    async def cleanup_old_files(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """
        Remove temporary files older than max_age_hours
        
        Args:
            max_age_hours: Files older than this will be deleted (default: 24 hours)
            
        Returns:
            Dict with cleanup statistics
        """
        cutoff_date = datetime.utcnow() - timedelta(hours=max_age_hours)
        logger.info(f"🧹 Starting cleanup of tmp files older than {max_age_hours} hours (before {cutoff_date})")
        
        deleted_count = 0
        total_size_freed = 0
        deleted_files = []
        errors = []
        
        try:
            # Find old files
            cursor = self.tmp_bucket.find({"uploadDate": {"$lt": cutoff_date}})
            
            async for file_doc in cursor:
                try:
                    file_info = {
                        "id": str(file_doc._id),
                        "filename": file_doc.filename,
                        "size": file_doc.length,
                        "upload_date": file_doc.upload_date.isoformat()
                    }
                    
                    # Delete the file
                    await self.tmp_bucket.delete(file_doc._id)
                    
                    deleted_count += 1
                    total_size_freed += file_doc.length
                    deleted_files.append(file_info)
                    
                    logger.info(f"🗑️ Deleted tmp file: {file_doc.filename} (ID: {file_doc._id}, Size: {file_doc.length} bytes)")
                    
                except Exception as e:
                    error_info = {
                        "file_id": str(file_doc._id),
                        "filename": getattr(file_doc, 'filename', 'unknown'),
                        "error": str(e)
                    }
                    errors.append(error_info)
                    logger.error(f"❌ Failed to delete {file_doc._id}: {e}")
            
            # Log summary
            size_mb = total_size_freed / (1024 * 1024)
            logger.info(f"✅ Cleanup completed: {deleted_count} files removed, {size_mb:.2f} MB freed")
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "total_size_freed_bytes": total_size_freed,
                "total_size_freed_mb": round(size_mb, 2),
                "cutoff_date": cutoff_date.isoformat(),
                "deleted_files": deleted_files,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"❌ Critical error during cleanup: {e}")
            return {
                "success": False,
                "error": str(e),
                "deleted_count": deleted_count,
                "total_size_freed_bytes": total_size_freed
            }
    
    async def cleanup_by_command_status(self) -> Dict[str, Any]:
        """
        Remove temporary files for completed/failed commands older than 1 hour
        
        This is more intelligent cleanup that looks at command status rather than just file age.
        Files are only deleted if their associated command is completed and old enough.
        
        Returns:
            Dict with cleanup statistics
        """
        cutoff_date = datetime.utcnow() - timedelta(hours=1)
        logger.info(f"🎯 Starting command-based cleanup for commands completed before {cutoff_date}")
        
        deleted_count = 0
        total_size_freed = 0
        processed_commands = []
        errors = []
        
        try:
            # Find completed commands older than 1 hour
            command_cursor = self.db.commands.find({
                "exit_state": {"$ne": -1},  # Not running (-1 = not started)
                "completed_at": {"$lt": cutoff_date}
            })
            
            async for command in command_cursor:
                command_id = str(command["_id"])
                try:
                    # Get input files from command args
                    file_ids = command.get("args", {}).get("file_ids", [])
                    
                    if not file_ids:
                        continue  # No files to clean up
                    
                    command_info = {
                        "command_id": command_id,
                        "shell_command": command.get("shell_command"),
                        "exit_state": command.get("exit_state"),
                        "completed_at": command.get("completed_at"),
                        "file_ids": file_ids,
                        "deleted_files": []
                    }
                    
                    # Delete each input file
                    for file_id_str in file_ids:
                        try:
                            file_obj_id = ObjectId(file_id_str)
                            
                            # Get file info before deleting
                            file_cursor = self.tmp_bucket.find({"_id": file_obj_id})
                            try:
                                file_doc = await file_cursor.next()
                                file_size = file_doc.length
                                filename = file_doc.filename
                                
                                # Delete the file
                                await self.tmp_bucket.delete(file_obj_id)
                                
                                deleted_count += 1
                                total_size_freed += file_size
                                command_info["deleted_files"].append({
                                    "file_id": file_id_str,
                                    "filename": filename,
                                    "size": file_size
                                })
                                
                                logger.info(f"🗑️ Deleted input file {filename} for command {command_id}")
                                
                            except StopAsyncIteration:
                                # File already deleted or doesn't exist
                                logger.warning(f"File {file_id_str} not found (already deleted?)")
                                
                        except Exception as e:
                            error_info = {
                                "command_id": command_id,
                                "file_id": file_id_str,
                                "error": str(e)
                            }
                            errors.append(error_info)
                            logger.error(f"❌ Failed to delete file {file_id_str} for command {command_id}: {e}")
                    
                    if command_info["deleted_files"]:
                        processed_commands.append(command_info)
                        
                except Exception as e:
                    error_info = {
                        "command_id": command_id,
                        "error": str(e)
                    }
                    errors.append(error_info)
                    logger.error(f"❌ Failed to process command {command_id}: {e}")
            
            # Log summary
            size_mb = total_size_freed / (1024 * 1024)
            logger.info(f"✅ Command-based cleanup completed: {deleted_count} files removed from {len(processed_commands)} commands, {size_mb:.2f} MB freed")
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "processed_commands_count": len(processed_commands),
                "total_size_freed_bytes": total_size_freed,
                "total_size_freed_mb": round(size_mb, 2),
                "cutoff_date": cutoff_date.isoformat(),
                "processed_commands": processed_commands,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"❌ Critical error during command-based cleanup: {e}")
            return {
                "success": False,
                "error": str(e),
                "deleted_count": deleted_count,
                "processed_commands_count": len(processed_commands),
                "total_size_freed_bytes": total_size_freed
            }
    
    async def get_cleanup_stats(self) -> Dict[str, Any]:
        """
        Get statistics about temporary files without deleting them
        
        Returns:
            Dict with tmp_files statistics
        """
        try:
            # Count all files
            total_files = 0
            total_size = 0
            files_by_age = {
                "last_hour": 0,
                "last_day": 0,
                "last_week": 0,
                "older": 0
            }
            
            now = datetime.utcnow()
            one_hour_ago = now - timedelta(hours=1)
            one_day_ago = now - timedelta(days=1)
            one_week_ago = now - timedelta(weeks=1)
            
            cursor = self.tmp_bucket.find({})
            
            async for file_doc in cursor:
                total_files += 1
                total_size += file_doc.length
                
                upload_date = file_doc.upload_date
                if upload_date > one_hour_ago:
                    files_by_age["last_hour"] += 1
                elif upload_date > one_day_ago:
                    files_by_age["last_day"] += 1
                elif upload_date > one_week_ago:
                    files_by_age["last_week"] += 1
                else:
                    files_by_age["older"] += 1
            
            return {
                "success": True,
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "files_by_age": files_by_age,
                "timestamp": now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get cleanup stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def full_cleanup(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """
        Run both time-based and command-based cleanup
        
        Args:
            max_age_hours: Maximum age for files in hours
            
        Returns:
            Combined cleanup results
        """
        logger.info(f"🚀 Starting full cleanup process...")
        
        # Run both cleanup methods
        time_based_result = await self.cleanup_old_files(max_age_hours)
        command_based_result = await self.cleanup_by_command_status()
        
        # Combine results
        total_deleted = time_based_result.get("deleted_count", 0) + command_based_result.get("deleted_count", 0)
        total_size_freed = time_based_result.get("total_size_freed_bytes", 0) + command_based_result.get("total_size_freed_bytes", 0)
        
        return {
            "success": True,
            "cleanup_type": "full",
            "total_deleted_files": total_deleted,
            "total_size_freed_bytes": total_size_freed,
            "total_size_freed_mb": round(total_size_freed / (1024 * 1024), 2),
            "time_based_cleanup": time_based_result,
            "command_based_cleanup": command_based_result,
            "timestamp": datetime.utcnow().isoformat()
        }


async def run_single_cleanup():
    """
    Run cleanup once and return
    """
    cleanup_service = TmpFilesCleanupService()
    max_age_hours = getattr(settings, 'tmp_files_max_age_hours', 24)
    
    try:
        logger.info("⏰ Running scheduled cleanup...")
        result = await cleanup_service.full_cleanup(max_age_hours=max_age_hours)
        
        if result["success"]:
            logger.info(f"✅ Scheduled cleanup completed: {result['total_deleted_files']} files, {result['total_size_freed_mb']} MB freed")
        else:
            logger.error(f"❌ Scheduled cleanup failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"❌ Critical error in cleanup: {e}")

def start_cleanup_scheduler():
    """
    Create and return a background task for cleanup scheduling
    This returns a task that can be managed by FastAPI's lifespan
    """
    cleanup_interval_minutes = getattr(settings, 'cleanup_interval_minutes', 60)
    
    logger.info(f"🕐 Creating cleanup scheduler: will run every {cleanup_interval_minutes} minutes")
    
    async def cleanup_loop():
        """Internal cleanup loop that runs in the background"""
        
        # Wait a bit before starting (let the app fully initialize)
        await asyncio.sleep(60)  # Wait 1 minute after startup
        
        while True:
            try:
                # Run a single cleanup
                await run_single_cleanup()
                
                # Wait for next cleanup
                await asyncio.sleep(cleanup_interval_minutes * 60)  # Convert minutes to seconds
                
            except asyncio.CancelledError:
                logger.info("🛑 Cleanup scheduler cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Critical error in cleanup scheduler: {e}")
                # Continue running even if there's an error
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    return asyncio.create_task(cleanup_loop())
