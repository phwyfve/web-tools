"""
HtmlSummary command handler
Creates a simple one-question, five-subquestions HTML summary from content
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

# Set up logging for this module
logger = logging.getLogger('HtmlSummary')

# Import LLM utilities
from cmd_tools.youtube.utils.call_llm import call_llm
from cmd_tools.youtube.utils.html_generator import html_generator


async def html_summary(args: Dict[str, Any], db, fs: gridfs.GridFS) -> Dict[str, Any]:
    """
    Create a simple HTML summary with one main question and 5 subquestions
    
    Args:
        args: Dict containing 'content' (text content) or 'file_id' (PDF file ID)
        db: MongoDB database connection
        fs: GridFS instance for tmp_files bucket
        
    Returns:
        Dict containing 'html_file_id' and 'html_filename' of the resulting HTML
    """
    
    # Get content either from direct text or from file
    content = args.get("content", "")
    file_id_str = args.get("file_id", "")
    source_name = "Direct Content"
    
    if file_id_str:
        # Download from GridFS if file_id provided
        try:
            file_id = ObjectId(file_id_str)
        except Exception as e:
            raise ValueError(f"Invalid file ID '{file_id_str}': {str(e)}")
        
        try:
            grid_file = fs.get(file_id)
            content = grid_file.read().decode('utf-8')
            source_name = grid_file.filename
            logger.info(f"Downloaded {source_name} ({len(content)} bytes)")
        except gridfs.NoFile:
            raise ValueError(f"File with ID '{file_id_str}' not found in GridFS")
        except Exception as e:
            raise ValueError(f"Failed to download file '{file_id_str}': {str(e)}")
    
    if not content.strip():
        raise ValueError("No content provided for HTML summary")
    
    logger.info(f"Starting HTML summary creation from {source_name}")
    logger.info(f"Content length: {len(content)} characters")
    
    # Limit content to avoid too long prompts
    content_excerpt = content[:3000]
    
    # Step 1: Generate one main question and 5 subquestions
    logger.info("Generating main question and subquestions...")
    main_question, subquestions = await generate_main_and_subquestions(content_excerpt, source_name)
    
    # Step 2: Generate answers for all questions
    logger.info("Generating answers...")
    processed_q_and_a = await generate_answers(main_question, subquestions, content_excerpt)
    
    # Step 3: Generate HTML from questions and answers
    logger.info("Generating HTML output...")
    title = f"Summary of {source_name}"
    
    # Create section with main question and subquestions
    bullets = []
    
    # Add main question
    main_q = processed_q_and_a.get("main_question", {})
    if main_q.get("rephrased") and main_q.get("answer"):
        bullets.append((main_q["rephrased"], main_q["answer"]))
    
    # Add subquestions
    for sub_q in processed_q_and_a.get("subquestions", []):
        if sub_q.get("rephrased") and sub_q.get("answer"):
            bullets.append((sub_q["rephrased"], sub_q["answer"]))
    
    sections = []
    if bullets:
        sections.append({
            "title": "Key Points",
            "bullets": bullets
        })
    
    html_content = html_generator(title, "", sections)
    
    # Save HTML to file
    output_dir = os.path.join(tempfile.gettempdir(), "webtools", "html")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename
    base_filename = os.path.splitext(source_name)[0]
    html_filename = f"html_summary_{base_filename}.html"
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
                "source": source_name,
                "process_type": "html_summary",
                "questions_count": 6
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
        "source": source_name
    }


async def generate_main_and_subquestions(content: str, source_name: str) -> tuple:
    """Generate one main question and 5 subquestions from content"""
    
    prompt = f"""
You are a content analyst. Given content from a document, generate ONE main overarching question and exactly 5 focused subquestions that explore different aspects of the content.

SOURCE: {source_name}

CONTENT:
{content}

The main question should be broad and overarching.
The 5 subquestions should be specific and complementary.

Format your response in YAML:

```yaml
main_question: |
    What is the core theme or central idea discussed in this content?
subquestions:
  - |
    First specific aspect or detail about the content?
  - |
    Second specific aspect or detail about the content?
  - |
    Third specific aspect or detail about the content?
  - |
    Fourth specific aspect or detail about the content?
  - |
    Fifth specific aspect or detail about the content?
```
    """
    
    response = await call_llm(prompt)
    
    # Extract YAML content
    yaml_content = response.split("```yaml")[1].split("```")[0].strip() if "```yaml" in response else response
    
    parsed = yaml.safe_load(yaml_content)
    main_question = parsed.get("main_question", "What is the main topic of this content?")
    subquestions = parsed.get("subquestions", [])
    
    # Ensure exactly 5 subquestions
    subquestions = subquestions[:5]
    while len(subquestions) < 5:
        subquestions.append(f"Additional detail question {len(subquestions) + 1}?")
    
    logger.info(f"Generated 1 main question and {len(subquestions)} subquestions")
    
    return main_question, subquestions


async def generate_answers(main_question: str, subquestions: List[str], content: str) -> Dict[str, Any]:
    """Generate answers for main question and subquestions"""
    
    all_questions = [main_question] + subquestions
    questions_yaml = "\n".join([f"  - original: |\n        {q}" for q in all_questions])
    
    prompt = f"""You are a content expert. Given a main question, 5 subquestions, and document content, provide clear and concise answers.

MAIN QUESTION: {main_question}

SUBQUESTIONS:
{chr(10).join([f"{i+1}. {q}" for i, q in enumerate(subquestions)])}

CONTENT:
{content}

For each question:
1. Rephrase it to be clearer and more specific
2. Provide a simple but informative answer in HTML with <b> and <i> tags
3. Use lists with <ol> and <li> tags when appropriate
4. Keep answers concise but complete (max 150 words each)

Format your response in YAML:

```yaml
main_question:
  original: |
    {main_question}
  rephrased: |
    Clearer version of the main question
  answer: |
    Comprehensive but concise answer in HTML
subquestions:
  - original: |
      {subquestions[0] if len(subquestions) > 0 else 'Question 1?'}
    rephrased: |
      Clearer version
    answer: |
      Answer in HTML
  - original: |
      {subquestions[1] if len(subquestions) > 1 else 'Question 2?'}
    ...
```
    """
    
    response = await call_llm(prompt)
    
    # Extract YAML content
    yaml_content = response.split("```yaml")[1].split("```")[0].strip() if "```yaml" in response else response
    
    parsed = yaml.safe_load(yaml_content)
    
    result = {
        "main_question": parsed.get("main_question", {}),
        "subquestions": parsed.get("subquestions", [])
    }
    
    return result
