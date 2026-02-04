"""
SplitPdfs command handler
Splits a PDF file into individual pages and creates a ZIP archive
"""

import io
import json
import logging
import zipfile
from typing import Dict, Any
from bson import ObjectId
import gridfs
from PyPDF2 import PdfWriter, PdfReader

# Set up logging for this module
logger = logging.getLogger('SplitPdfs')

def split_pdfs(args: Dict[str, Any], db, fs: gridfs.GridFS) -> Dict[str, Any]:
    """
    Split a PDF file into individual pages and create a ZIP archive
    
    Args:
        args: Dict containing 'file_id' - GridFS file ID of the PDF to split
        db: MongoDB database connection
        fs: GridFS instance for tmp_files bucket
        
    Returns:
        Dict containing 'output_file_id' of the resulting ZIP archive
    """
    
    file_id_str = args.get("file_id")
    if not file_id_str:
        raise ValueError("No file_id provided for PDF split")
    
    logger.info(f"Starting PDF split for file: {file_id_str}")
    
    # Convert string ID to ObjectId
    try:
        file_id = ObjectId(file_id_str)
    except Exception as e:
        raise ValueError(f"Invalid file ID '{file_id_str}': {str(e)}")
    
    # Download PDF from GridFS
    try:
        grid_file = fs.get(file_id)
        file_content = grid_file.read()
        original_filename = grid_file.filename or "document.pdf"
        logger.info(f"Downloaded {original_filename} ({len(file_content)} bytes)")
    except gridfs.NoFile:
        raise ValueError(f"File with ID '{file_id_str}' not found in GridFS")
    except Exception as e:
        raise ValueError(f"Failed to download file '{file_id_str}': {str(e)}")
    
    # Read PDF content
    try:
        pdf_buffer = io.BytesIO(file_content)
        pdf_reader = PdfReader(pdf_buffer)
        total_pages = len(pdf_reader.pages)
        
        logger.info(f"PDF has {total_pages} pages to split")
        
        if total_pages == 0:
            raise ValueError("PDF has no pages to split")
        
    except Exception as e:
        raise ValueError(f"Failed to read PDF file: {str(e)}")
    
    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    split_files_info = []
    
    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Split each page into a separate PDF
            for page_num in range(total_pages):
                logger.info(f"Processing page {page_num + 1}/{total_pages}")
                
                # Create a new PDF with just this page
                pdf_writer = PdfWriter()
                pdf_writer.add_page(pdf_reader.pages[page_num])
                
                # Write page PDF to buffer
                page_buffer = io.BytesIO()
                pdf_writer.write(page_buffer)
                page_content = page_buffer.getvalue()
                
                # Generate filename for this page
                base_name = original_filename.rsplit('.', 1)[0]  # Remove .pdf extension
                page_filename = f"{base_name}_page_{page_num + 1:03d}.pdf"
                
                # Add to ZIP
                zip_file.writestr(page_filename, page_content)
                
                split_files_info.append({
                    "page_number": page_num + 1,
                    "filename": page_filename,
                    "size_bytes": len(page_content)
                })
                
                logger.info(f"Added {page_filename} ({len(page_content)} bytes) to ZIP")
        
        # Get ZIP content
        zip_content = zip_buffer.getvalue()
        logger.info(f"ZIP archive created successfully ({len(zip_content)} bytes, {total_pages} files)")
        
        # Generate filename for ZIP
        base_name = original_filename.rsplit('.', 1)[0]
        zip_filename = f"{base_name}_split_{total_pages}_pages.zip"
        
        # Upload ZIP to GridFS
        zip_file_id = fs.put(
            zip_content,
            filename=zip_filename,
            content_type="application/zip",
            metadata={
                "original_file": {
                    "id": file_id_str,
                    "filename": original_filename,
                    "size": len(file_content)
                },
                "split_type": "pdf_split",
                "total_pages": total_pages,
                "split_files": split_files_info
            }
        )
        
        logger.info(f"ZIP archive uploaded to GridFS with ID: {zip_file_id}")
        
        # Return success result with standardized field names
        return {
            "success": True,
            "output_file_id": str(zip_file_id),
            "output_filename": zip_filename,
            "total_pages": total_pages,
            "original_file": {
                "id": file_id_str,
                "filename": original_filename,
                "size_bytes": len(file_content)
            },
            "split_files": split_files_info,
            "zip_size_bytes": len(zip_content)
        }
        
    except Exception as e:
        # Ensure proper error handling
        logger.error(f"PDF split failed: {str(e)}")
        logger.exception("Full exception details:")
        raise  # Re-raise to be caught by myshell.py
