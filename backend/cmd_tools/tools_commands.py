"""
Command registry for shell tools
Maps command names to their handler functions
"""

from .youtube_summary import youtube_summary
from .MergePdfs import merge_pdfs
from .SplitPdfs import split_pdfs
from .MergeImages import merge_images
from .XlsToPdf import xls_to_pdf

COMMAND_REGISTRY = {
    "MergePdfs": merge_pdfs,
    "SplitPdfs": split_pdfs,
    "MergeImages": merge_images,
    "XlsToPdf": xls_to_pdf,
    "youtube_summary": youtube_summary
}
