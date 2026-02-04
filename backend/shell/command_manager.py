"""
Process Manager for shell command execution
Handles command creation and execution with proper subprocess management
"""

import asyncio
import functools
import subprocess
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import Dict, Any
from core.config import settings

async def create_command(shell_command: str, args: Dict[str, Any]) -> str:
    """
    Create a new command entry in MongoDB
    
    Args:
        shell_command: The command name to execute
        args: JSON-serializable arguments for the command
        
    Returns:
        str: The created command ID
    """
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    
    command_doc = {
        "shell_command": shell_command,
        "args": args,
        "exit_state": -1,  # -1 means "not started"
        "stdout": None,
        "stderr": None,
        "created_at": datetime.utcnow(),
        "started_at": None,
        "completed_at": None
    }
    
    result = await db.commands.insert_one(command_doc)
    client.close()
    
    return str(result.inserted_id)

async def process_command(command_id: str) -> Dict[str, Any]:
    """
    Execute a command and wait for completion
    This function MUST wait for command completion to ensure stable final state
    
    Args:
        command_id: The ID of the command to execute
        
    Returns:
        Dict containing execution results
    """
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    
    try:
        # Mark command as started
        await db.commands.update_one(
            {"_id": ObjectId(command_id)},
            {"$set": {"started_at": datetime.utcnow()}}
        )
        
        # Execute the shell command and wait for completion
        print(f"Starting subprocess for command: {command_id}")
        
        def run_subprocess(command_id):
            process = subprocess.Popen(
                ["python", "me_shell.py", command_id],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            return process.returncode, stdout, stderr

        loop = asyncio.get_running_loop()
        exit_state, stdout, stderr = await loop.run_in_executor(
            None, functools.partial(run_subprocess, command_id)
        )
        
        # Update the MongoDB command entry with final results
        update_data = {
            "completed_at": datetime.utcnow()
        }
        
        # If the subprocess completed successfully, the me_shell.py should have
        # already updated stdout/stderr. But we capture the process output too.
        if exit_state == 0:
            print(f"Command {command_id} completed successfully")
            if stdout.strip():
                print(f"Process stdout: {stdout}")
        else:
            print(f"Command {command_id} failed with exit code {exit_state}")
            if stderr.strip():
                print(f"Process stderr: {stderr}")
            
            # Update with subprocess error if me_shell.py didn't handle it
            await db.commands.update_one(
                {"_id": ObjectId(command_id)},
                {
                    "$set": {
                        "exit_state": exit_state,
                        "stderr": stderr if stderr.strip() else "Command failed with no error output",
                        **update_data
                    }
                }
            )
        
        # If exit_state is 0, me_shell.py should have already updated the record
        if exit_state == 0:
            await db.commands.update_one(
                {"_id": ObjectId(command_id)},
                {"$set": update_data}
            )
        
        # Return final command state
        final_command = await db.commands.find_one({"_id": ObjectId(command_id)})
        client.close()
        
        return {
            "command_id": command_id,
            "exit_state": final_command.get("exit_state", exit_state),
            "stdout": final_command.get("stdout"),
            "stderr": final_command.get("stderr"),
            "completed_at": final_command.get("completed_at")
        }
        
    except Exception as e:
        # Handle any errors in process management
        error_msg = f"Process management error: {str(e)}"
        print(f"ERROR: {error_msg}")
        
        await db.commands.update_one(
            {"_id": ObjectId(command_id)},
            {
                "$set": {
                    "exit_state": 2,  # 2 = process management error
                    "stderr": error_msg,
                    "completed_at": datetime.utcnow()
                }
            }
        )
        client.close()
        
        return {
            "command_id": command_id,
            "exit_state": 2,
            "stdout": None,
            "stderr": error_msg,
            "error": str(e)
        }

async def get_command_status(command_id: str) -> Dict[str, Any]:
    """
    Get the current status of a command
    
    Args:
        command_id: The ID of the command to check
        
    Returns:
        Dict containing command status and results
    """
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    
    try:
        command_doc = await db.commands.find_one({"_id": ObjectId(command_id)})
        client.close()
        
        if not command_doc:
            return {
                "error": "Command not found",
                "command_id": command_id
            }
        
        return {
            "command_id": command_id,
            "shell_command": command_doc.get("shell_command"),
            "args": command_doc.get("args"),
            "exit_state": command_doc.get("exit_state"),
            "stdout": command_doc.get("stdout"),
            "stderr": command_doc.get("stderr"),
            "created_at": command_doc.get("created_at"),
            "started_at": command_doc.get("started_at"),
            "completed_at": command_doc.get("completed_at")
        }
        
    except Exception as e:
        client.close()
        return {
            "error": f"Failed to get command status: {str(e)}",
            "command_id": command_id
        }
