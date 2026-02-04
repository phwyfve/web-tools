"""
MergePdfs command handler
Merges multiple PDF files into a single PDF
"""

import io
import json
import logging
from typing import Dict, Any, List
from bson import ObjectId
import gridfs
from PyPDF2 import PdfWriter, PdfReader

# Set up logging for this module
logger = logging.getLogger('MergePdfs')

def merge_pdfs(args: Dict[str, Any], db, fs: gridfs.GridFS) -> Dict[str, Any]:
    """
    Merge multiple PDF files from GridFS into a single PDF
    
    Args:
        args: Dict containing 'file_ids' - list of GridFS file IDs
        db: MongoDB database connection
        fs: GridFS instance for tmp_files bucket
        
    Returns:
        Dict containing 'merged_file_id' of the resulting merged PDF
    """
    
    file_ids = args.get("file_ids", [])
    if not file_ids:
        raise ValueError("No file_ids provided for PDF merge")
    
    if len(file_ids) < 2:
        raise ValueError("At least 2 PDF files are required for merging")
    
    logger.info(f"Starting PDF merge of {len(file_ids)} files: {file_ids}")
    
    # Create PDF writer for merged output
    pdf_writer = PdfWriter()
    processed_files = []
    
    try:
        # Process each PDF file
        for i, file_id_str in enumerate(file_ids):
            logger.info(f"Processing file {i+1}/{len(file_ids)}: {file_id_str}")
            
            # Convert string ID to ObjectId
            try:
                file_id = ObjectId(file_id_str)
            except Exception as e:
                raise ValueError(f"Invalid file ID '{file_id_str}': {str(e)}")
            
            # Download file from GridFS
            try:
                grid_file = fs.get(file_id)
                file_content = grid_file.read()
                processed_files.append({
                    "id": file_id_str,
                    "filename": grid_file.filename,
                    "size": len(file_content)
                })
                logger.info(f"Downloaded {grid_file.filename} ({len(file_content)} bytes)")
            except gridfs.NoFile:
                raise ValueError(f"File with ID '{file_id_str}' not found in GridFS")
            except Exception as e:
                raise ValueError(f"Failed to download file '{file_id_str}': {str(e)}")
            
            # Read PDF content
            try:
                pdf_buffer = io.BytesIO(file_content)
                pdf_reader = PdfReader(pdf_buffer)
                
                # Add all pages from this PDF to the writer
                page_count = len(pdf_reader.pages)
                logger.info(f"Adding {page_count} pages from {grid_file.filename}")
                
                for page_num in range(page_count):
                    pdf_writer.add_page(pdf_reader.pages[page_num])
                    
            except Exception as e:
                raise ValueError(f"Failed to read PDF file '{grid_file.filename}': {str(e)}")
        
        # Create merged PDF in memory
        merged_buffer = io.BytesIO()
        pdf_writer.write(merged_buffer)
        merged_content = merged_buffer.getvalue()
        
        logger.info(f"Merged PDF created successfully ({len(merged_content)} bytes)")
        
        # Generate filename for merged PDF
        merged_filename = f"merged_pdf_{len(file_ids)}_files.pdf"
        
        # Upload merged PDF to GridFS
        merged_file_id = fs.put(
            merged_content,
            filename=merged_filename,
            content_type="application/pdf",
            metadata={
                "original_files": processed_files,
                "merge_type": "pdf_merge",
                "total_pages": len(pdf_writer.pages)
            }
        )
        
        logger.info(f"Merged PDF uploaded to GridFS with ID: {merged_file_id}")
        
        # Return success result
        return {
            "success": True,
            "merged_file_id": str(merged_file_id),
            "merged_filename": merged_filename,
            "total_pages": len(pdf_writer.pages),
            "original_files": processed_files,
            "merged_size_bytes": len(merged_content)
        }
        
    except Exception as e:
        # Ensure proper error handling
        logger.error(f"PDF merge failed: {str(e)}")
        logger.exception("Full exception details:")
        raise  # Re-raise to be caught by myshell.py
