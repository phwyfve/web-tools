"""
YouTubeSummary command handler
Summarizes a YouTube video using a processing flow
"""

import asyncio
from typing import Dict, Any

from .youtube.utils.youtube_processor import extract_video_id
from .youtube.youtube_video_summary import create_youtube_processor_flow
import logging
import gridfs

logger = logging.getLogger('youtube_summary')

async def youtube_summary(args: Dict[str, Any], db, fs: gridfs.GridFS) -> Dict[str, Any]:
    """
    Summarize a YouTube video using a processing flow
    Args:
        args: Dict containing 'url' - the YouTube video URL
        db: MongoDB database connection (unused)
        fs: GridFS instance (unused)
    Returns:
        Dict containing 'output_file' (the path to output.html)
    """
    url = args.get("url")
    if not url:
        raise ValueError("No URL provided for YouTube summary")

    # Create flow
    flow = create_youtube_processor_flow()

    # Initialize shared memory
    shared = {
        "url": url,
        "output_filename": f"youtube_summary{extract_video_id(url)}.html"
    }

    # Run the flow
    logger.info(f"Starting YouTube processing flow for URL: {url}")
    await flow.run(shared)

    # Upload summary to GridFS with proper file handling and error logging
    try:
        with open(f"{shared['output_filename']}", "rb") as f:
            summary_file_id = fs.put(
                f.read(),
                filename=shared["output_filename"],
                content_type="application/html",
                metadata={
                    "original_video": url,
                    "merge_type": "html_summary"
                }
            )
        logger.info(f"Summary HTML uploaded to GridFS with ID: {summary_file_id}")
    except Exception as e:
        logger.error(f"Failed to upload summary to GridFS: {e}")
        raise

    # Return success result
    return {
        "success": True,
        "summary_file_id": str(summary_file_id),
        "summary_filename": shared["output_filename"]
    }
