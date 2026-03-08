"""
PdfToHtml command handler
Extracts text from PDF, generates questions, and creates an HTML summary
"""

import asyncio
import io
import json
import logging
import os
import tempfile
from typing import Dict, Any, List
from bson import ObjectId
import gridfs
import yaml
import PyPDF2

# Set up logging for this module
logger = logging.getLogger('PdfToHtml')

# Import LLM utilities
from cmd_tools.youtube.utils.call_llm import call_llm
from cmd_tools.youtube.utils.html_generator import html_generator


async def pdf_to_html(args: Dict[str, Any], db, fs: gridfs.GridFS) -> Dict[str, Any]:
    """
    Extract text from PDF, generate questions, and create HTML summary
    
    Args:
        args: Dict containing 'file_id' - the GridFS file ID of the PDF
        db: MongoDB database connection
        fs: GridFS instance for tmp_files bucket
        
    Returns:
        Dict containing 'html_file_id' and 'html_filename' of the resulting HTML
    """
    
    file_id_str = args.get("file_id")
    if not file_id_str:
        raise ValueError("No file_id provided for PDF to HTML conversion")
    
    logger.info(f"Starting PDF to HTML conversion for file: {file_id_str}")
    
    # Convert string ID to ObjectId
    try:
        file_id = ObjectId(file_id_str)
    except Exception as e:
        raise ValueError(f"Invalid file ID '{file_id_str}': {str(e)}")
    
    # Download PDF from GridFS
    try:
        grid_file = fs.get(file_id)
        pdf_content = grid_file.read()
        original_filename = grid_file.filename
        logger.info(f"Downloaded {original_filename} ({len(pdf_content)} bytes)")
    except gridfs.NoFile:
        raise ValueError(f"File with ID '{file_id_str}' not found in GridFS")
    except Exception as e:
        raise ValueError(f"Failed to download file '{file_id_str}': {str(e)}")
    
    # Extract text from PDF
    logger.info("Extracting text from PDF...")
    pdf_text = await extract_pdf_text(pdf_content)
    
    if not pdf_text.strip():
        raise ValueError("Could not extract any text from the PDF")
    
    logger.info(f"Extracted {len(pdf_text)} characters from PDF")
    
    # Step 1: Guess title and generate questions from PDF text
    logger.info("Generating questions from PDF content...")
    title, topics = await generate_questions_from_text(pdf_text, original_filename)
    
    # Step 2: Process each topic to rephrase and answer
    logger.info(f"Processing {len(topics)} topics...")
    processed_topics = []
    for index, topic in enumerate(topics):
        logger.info(f"Processing topic {index + 1}/{len(topics)}: {topic['title']}")
        processed_topic = await process_topic(topic, pdf_text)
        processed_topics.append(processed_topic)
    
    # Step 3: Generate HTML from processed topics
    logger.info("Generating HTML output...")
    sections = []
    for topic in processed_topics:
        section_title = topic.get("rephrased_title", topic.get("title", ""))
        bullets = []
        for question in topic.get("questions", []):
            q = question.get("rephrased", question.get("original", ""))
            a = question.get("answer", "")
            if q.strip() and a.strip():
                bullets.append((q, a))
        
        if bullets:
            sections.append({
                "title": section_title,
                "bullets": bullets
            })
    
    html_content = html_generator(title, "", sections)
    
    # Save HTML to file
    output_dir = os.path.join(tempfile.gettempdir(), "webtools", "pdf")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename
    base_filename = os.path.splitext(original_filename)[0]
    html_filename = f"pdf_summary_{base_filename}.html"
    output_path = os.path.join(output_dir, html_filename)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    logger.info(f"HTML saved to {output_path}")
    
    # Upload HTML to GridFS
    try:
        html_file_id = fs.put(
            html_content.encode('utf-8'),
            filename=html_filename,
            content_type="text/html",
            metadata={
                "original_pdf": original_filename,
                "pdf_file_id": file_id_str,
                "process_type": "pdf_to_html"
            }
        )
        logger.info(f"HTML uploaded to GridFS with ID: {html_file_id}")
    except Exception as e:
        logger.error(f"Failed to upload HTML to GridFS: {e}")
        raise
    
    # Return success result
    return {
        "success": True,
        "html_file_id": str(html_file_id),
        "html_filename": html_filename,
        "title": title,
        "topics_count": len(processed_topics)
    }


async def extract_pdf_text(pdf_content: bytes) -> str:
    """Extract text from PDF content"""
    try:
        pdf_buffer = io.BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_buffer)
        
        text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            text += page_text + "\n"
            logger.debug(f"Extracted text from page {page_num + 1}")
        
        return text
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


async def generate_questions_from_text(text: str, filename: str) -> tuple:
    """Generate title guess and questions from text"""
    
    # Limit text to first 5000 characters to avoid too long prompts
    text_excerpt = text[:5000]
    
    prompt = f"""
You are an expert content analyzer. Given PDF content, guess the document title, identify at most 5 most interesting topics discussed, and generate at most 3 thought-provoking questions for each topic.

DOCUMENT: {filename}

CONTENT EXCERPT:
{text_excerpt}

Format your response in YAML:

```yaml
guessed_title: |
    Document Title Based on Content
topics:
  - title: |
        First Topic Title
    questions:
      - |
        Question 1 about first topic?
      - |
        Question 2 ...
  - title: |
        Second Topic Title
    questions:
        ...
```
    """
    
    response = await call_llm(prompt)
    
    # Extract YAML content
    yaml_content = response.split("```yaml")[1].split("```")[0].strip() if "```yaml" in response else response
    
    parsed = yaml.safe_load(yaml_content)
    guessed_title = parsed.get("guessed_title", f"Summary of {filename}")
    raw_topics = parsed.get("topics", [])
    
    # Ensure we have at most 5 topics
    raw_topics = raw_topics[:5]
    
    # Format the topics and questions for our data structure
    result_topics = []
    for topic in raw_topics:
        topic_title = topic.get("title", "")
        raw_questions = topic.get("questions", [])
        
        # Create a complete topic with questions
        result_topics.append({
            "title": topic_title,
            "questions": [
                {
                    "original": q,
                    "rephrased": "",
                    "answer": ""
                }
                for q in raw_questions
            ]
        })
    
    logger.info(f"Guessed title: {guessed_title}")
    logger.info(f"Generated {len(result_topics)} topics with {sum(len(t.get('questions', [])) for t in result_topics)} questions")
    
    return guessed_title, result_topics


async def process_topic(topic: Dict[str, Any], text: str) -> Dict[str, Any]:
    """Process a topic to rephrase and answer questions"""
    
    topic_title = topic["title"]
    questions = [q["original"] for q in topic["questions"]]
    
    # Limit text to relevant excerpt
    text_excerpt = text[:5000]
    
    prompt = f"""You are a content simplifier for children. Given a topic and questions from a document, rephrase the topic title and questions to be clearer, and provide simple ELI5 (Explain Like I'm 5) answers.

TOPIC: {topic_title}

QUESTIONS:
{chr(10).join([f"- {q}" for q in questions])}

DOCUMENT EXCERPT:
{text_excerpt}

For topic title and questions:
1. Keep them catchy and interesting, but short

For your answers:
1. Format them using HTML with <b> and <i> tags for highlighting. 
2. Prefer lists with <ol> and <li> tags. Ideally, <li> followed by <b> for the key points.
3. Quote important keywords but explain them in easy-to-understand language
4. Keep answers interesting but short

Format your response in YAML:

```yaml
rephrased_title: |
    Interesting topic title in 10 words
questions:
  - original: |
        {questions[0] if len(questions) > 0 else ''}
    rephrased: |
        Interesting question in 15 words
    answer: |
        Simple answer that a 5-year-old could understand in 100 words
  - original: |
        {questions[1] if len(questions) > 1 else ''}
    ...
```
    """
    
    response = await call_llm(prompt)
    
    # Extract YAML content
    yaml_content = response.split("```yaml")[1].split("```")[0].strip() if "```yaml" in response else response
    
    parsed = yaml.safe_load(yaml_content)
    rephrased_title = parsed.get("rephrased_title", topic_title)
    processed_questions = parsed.get("questions", [])
    
    result = {
        "title": topic_title,
        "rephrased_title": rephrased_title,
        "questions": processed_questions
    }
    
    return result
