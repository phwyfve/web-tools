"""
Command registry for shell tools
Maps command names to their handler functions
"""

from .youtube_summary import youtube_summary
from .MergePdfs import merge_pdfs
from .SplitPdfs import split_pdfs
from .MergeImages import merge_images
from .XlsToPdf import xls_to_pdf
from .pdf_to_html import pdf_to_html
from .html_summary import html_summary
from .call_llm_handler import call_llm_handler
from .generate_lmnp_liasse import generate_lmnp_liasse

COMMAND_REGISTRY = {
    "MergePdfs": merge_pdfs,
    "SplitPdfs": split_pdfs,
    "MergeImages": merge_images,
    "XlsToPdf": xls_to_pdf,
    "youtube_summary": youtube_summary,
    "PdfToHtml": pdf_to_html,
    "HtmlSummary": html_summary,
    "call_llm": call_llm_handler,
    "GenerateLmnpLiasse": generate_lmnp_liasse
}
