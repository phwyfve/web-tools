#!/usr/bin/env python3
"""
Python shell dispatcher for JSON-driven commands
Usage: python me_shell.py <command_id>
"""

import sys
import asyncio
import json
import logging
import traceback
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
from gridfs import GridFS
from bson import ObjectId
from cmd_tools.tools_commands import COMMAND_REGISTRY
from core.config import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/me_shell.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('me_shell')

async def main():
    """Main entry point for command execution"""
    if len(sys.argv) < 2:
        logger.error("Error: command_id is required")
        print("Error: command_id is required", file=sys.stderr)
        sys.exit(1)
    
    command_id = sys.argv[1]
    logger.info(f"Me_shell dispatcher started for command: {command_id}")
    
    try:
        # Connect to MongoDB
        logger.info(f"Connecting to MongoDB: {settings.mongodb_url}")
        client = AsyncIOMotorClient(settings.mongodb_url)
        db = client[settings.database_name]
        logger.info(f"Connected to database: {settings.database_name}")
        
        # Load command from database
        logger.info(f"Fetching command document for ID: {command_id}")
        command_doc = await db.commands.find_one({"_id": ObjectId(command_id)})
        if not command_doc:
            logger.error(f"Command {command_id} not found in database")
            print(f"Error: Command {command_id} not found", file=sys.stderr)
            sys.exit(1)
        
        shell_command = command_doc.get("shell_command")
        args = command_doc.get("args", {})
        logger.info(f"Found command: {shell_command} with args: {args}")
        
        # Look up handler
        logger.info(f"Available commands: {list(COMMAND_REGISTRY.keys())}")
        if shell_command not in COMMAND_REGISTRY:
            error_msg = f"Unknown command '{shell_command}'. Available: {list(COMMAND_REGISTRY.keys())}"
            logger.error(error_msg)
            print(f"Error: {error_msg}", file=sys.stderr)
            sys.exit(1)
        
        handler = COMMAND_REGISTRY[shell_command]
        
        # Setup GridFS - use pymongo for GridFS since it needs sync client
        logger.info("Setting up GridFS connection")
        sync_client = pymongo.MongoClient(settings.mongodb_url)
        sync_db = sync_client[settings.database_name]
        fs = GridFS(sync_db, collection="tmp_files")
        logger.info("GridFS connection established")
        
        # Execute handler
        logger.info(f"Executing command: {shell_command}")
        logger.info(f"Args: {json.dumps(args, indent=2)}")
        
        # Since we changed merge_pdfs to be sync, check if handler is async
        if asyncio.iscoroutinefunction(handler):
            logger.info("Handler is async - using await")
            result = await handler(args, db, fs)
        else:
            logger.info("Handler is sync - calling directly")
            result = handler(args, sync_db, fs)
        
        # Update command with success
        logger.info("Updating command status with success result")
        await db.commands.update_one(
            {"_id": ObjectId(command_id)},
            {
                "$set": {
                    "exit_state": 0,
                    "stdout": json.dumps(result, indent=2),
                    "stderr": None
                }
            }
        )
        
        logger.info("Command completed successfully")
        logger.info(f"Result: {json.dumps(result, indent=2)}")
        print("Command completed successfully")
        print(f"Result: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        # Update command with error
        error_msg = f"Command failed: {str(e)}"
        stderr_output = f"{error_msg}\n\nTraceback:\n{traceback.format_exc()}"
        
        logger.error(f"Command execution error: {error_msg}")
        logger.exception("Full exception details:")
        
        try:
            client = AsyncIOMotorClient(settings.mongodb_url)
            db = client[settings.database_name]
            await db.commands.update_one(
                {"_id": ObjectId(command_id)},
                {
                    "$set": {
                        "exit_state": 1,
                        "stdout": None,
                        "stderr": stderr_output
                    }
                }
            )
            logger.info("Updated command status with error result")
        except Exception as update_error:
            logger.error(f"Failed to update command status: {update_error}")
            print(f"Failed to update command status: {update_error}", file=sys.stderr)
        
        print(error_msg, file=sys.stderr)
        print(f"Full traceback:\n{traceback.format_exc()}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
