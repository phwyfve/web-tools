"""
MergeImages command handler
Converts multiple image files to PDF and merges them into a single PDF
"""

import io
import logging
from typing import Dict, Any, List
from bson import ObjectId
import gridfs
from PIL import Image
from PyPDF2 import PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader

# Set up logging for this module
logger = logging.getLogger('MergeImages')

# Supported image formats
SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}

def merge_images(args: Dict[str, Any], db, fs: gridfs.GridFS) -> Dict[str, Any]:
    """
    Convert multiple image files from GridFS to PDF pages and merge into a single PDF
    
    Args:
        args: Dict containing 'file_ids' - list of GridFS file IDs
        db: MongoDB database connection
        fs: GridFS instance for tmp_files bucket
        
    Returns:
        Dict containing 'merged_file_id' of the resulting merged PDF
    """
    
    file_ids = args.get("file_ids", [])
    if not file_ids:
        raise ValueError("No file_ids provided for image merge")
    
    if len(file_ids) < 1:
        raise ValueError("At least 1 image file is required for merging")
    
    logger.info(f"Starting image to PDF conversion and merge of {len(file_ids)} files: {file_ids}")
    
    # Create PDF writer for merged output
    pdf_writer = PdfWriter()
    processed_files = []
    
    try:
        # Process each image file
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
            
            # Convert image to PDF page
            try:
                # Load image using PIL
                image = Image.open(io.BytesIO(file_content))
                
                # Convert to RGB if necessary (for PDF compatibility)
                if image.mode not in ('RGB', 'L'):
                    logger.info(f"Converting image from {image.mode} to RGB")
                    image = image.convert('RGB')
                
                # Get image dimensions
                img_width, img_height = image.size
                logger.info(f"Image dimensions: {img_width}x{img_height}")
                
                # Determine page orientation based on image aspect ratio
                if img_width > img_height:
                    # Landscape
                    page_width, page_height = A4[1], A4[0]  # Swap dimensions for landscape
                    orientation = "landscape"
                else:
                    # Portrait
                    page_width, page_height = A4
                    orientation = "portrait"
                
                logger.info(f"Using {orientation} orientation ({page_width}x{page_height})")
                
                # Calculate scaling to fit image on page while preserving aspect ratio
                # Leave some margin (20 points on each side)
                margin = 20
                available_width = page_width - (2 * margin)
                available_height = page_height - (2 * margin)
                
                # Calculate scale factors
                width_scale = available_width / img_width
                height_scale = available_height / img_height
                
                # Use the smaller scale to ensure image fits within page
                scale = min(width_scale, height_scale)
                
                # Calculate final image dimensions
                final_width = img_width * scale
                final_height = img_height * scale
                
                # Center image on page
                x_offset = (page_width - final_width) / 2
                y_offset = (page_height - final_height) / 2
                
                logger.info(f"Scaled image to {final_width}x{final_height}, centered at ({x_offset}, {y_offset})")
                
                # Create PDF page with image
                pdf_buffer = io.BytesIO()
                c = canvas.Canvas(pdf_buffer, pagesize=(page_width, page_height))
                
                # Draw image on canvas
                img_reader = ImageReader(image)
                c.drawImage(img_reader, x_offset, y_offset, 
                           width=final_width, height=final_height,
                           preserveAspectRatio=True)
                
                c.save()
                
                # Read the created PDF page
                pdf_buffer.seek(0)
                from PyPDF2 import PdfReader
                page_reader = PdfReader(pdf_buffer)
                
                # Add page to the merged PDF
                pdf_writer.add_page(page_reader.pages[0])
                logger.info(f"Successfully added page for {grid_file.filename}")
                
            except Exception as e:
                raise ValueError(f"Failed to convert image '{grid_file.filename}' to PDF: {str(e)}")
        
        # Create merged PDF in memory
        merged_buffer = io.BytesIO()
        pdf_writer.write(merged_buffer)
        merged_content = merged_buffer.getvalue()
        
        logger.info(f"Merged PDF created successfully ({len(merged_content)} bytes)")
        
        # Generate filename for merged PDF
        merged_filename = f"merged_images_{len(file_ids)}_files.pdf"
        
        # Upload merged PDF to GridFS
        merged_file_id = fs.put(
            merged_content,
            filename=merged_filename,
            content_type="application/pdf",
            metadata={
                "original_files": processed_files,
                "merge_type": "image_to_pdf_merge",
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
        logger.error(f"Image to PDF merge failed: {str(e)}")
        logger.exception("Full exception details:")
        raise  # Re-raise to be caught by myshell.py
