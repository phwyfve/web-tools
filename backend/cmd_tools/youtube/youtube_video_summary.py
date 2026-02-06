from typing import List, Dict, Any, Tuple
import yaml
import logging
from caskada import Node, Flow
from .utils.call_llm import call_llm
from .utils.youtube_processor import get_video_info
from .utils.html_generator import html_generator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define the specific nodes for the YouTube Content Processor

class ProcessYouTubeURL(Node):
    """Process YouTube URL to extract video information"""
    async def prep(self, shared):
        """Get URL from shared"""
        return shared["url"]
    
    async def exec(self, url):
        """Extract video information"""
        if not url:
            raise ValueError("No YouTube URL provided")
        
        logger.info(f"Processing YouTube URL: {url}")
        video_info = get_video_info(url)
        
        if "error" in video_info:
            raise ValueError(f"Error processing video: {video_info['error']}")
        
        return video_info
    
    async def post(self, shared, prep_res, exec_res):
        """Store video information in shared"""
        shared["video_info"] = exec_res
        logger.info(f"Video title: {exec_res.get('title')}")
        logger.info(f"Transcript length: {len(exec_res.get('transcript', ''))}")
        return "default"

class ExtractTopicsAndQuestions(Node):
    
    chunk_size = 20

    """Extract interesting topics and generate questions from the video transcript"""
    async def prep(self, shared):
        """Get transcript and title from video_info"""
        video_info = shared["video_info"]
        transcript = video_info.get("transcript", "")
        title = video_info.get("title", "")
        return {"transcript": transcript, "title": title}
    
    async def exec(self, data):
        """Extract topics and generate questions using LLM"""
        transcript = data["transcript"]
        title = data["title"]
        
        # Single prompt to extract topics and questions together
        prompt = f"""
You are an expert content analyzer. Given a YouTube video transcript, identify at most 5 most interesting topics discussed and generate at most 3 most thought-provoking questions for each topic.
These questions don't need to be directly asked in the video. It's good to have clarification questions.

VIDEO TITLE: {title}

TRANSCRIPT:
{transcript}

Format your response in YAML:

```yaml
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
        
        return result_topics
    
    async def post(self, shared, prep_res, exec_res):
        """Store topics with questions in shared"""
        shared["topics"] = exec_res
        shared.remaining_chunks = 0
        
        # Count and log total questions
        total_questions = sum(len(topic.get("questions", [])) for topic in exec_res)
        logger.info(f"Extracted {len(exec_res)} topics with {total_questions} questions")

        for index, topic in enumerate(exec_res):
            shared.remaining_chunks += 1
            self.trigger("default", {"index": index, "chunk": {"topic": topic, "transcript": shared["video_info"].get("transcript", "")}})

class ProcessContent(Node):
    """Process each topic for rephrasing and answering"""
    async def prep(self, memory):

        return memory.index, memory.chunk
    
    async def exec(self, data_tuple):
        """Process a topic using LLM"""
        index, chunk = data_tuple
        
        topic = chunk["topic"]
        transcript = chunk["transcript"]
        topic_title = topic["title"]
        questions = [q["original"] for q in topic["questions"]]
        
        topic_title = topic["title"]
        questions = [q["original"] for q in topic["questions"]]
        
        prompt = f"""You are a content simplifier for children. Given a topic and questions from a YouTube video, rephrase the topic title and questions to be clearer, and provide simple ELI5 (Explain Like I'm 5) answers.

TOPIC: {topic_title}

QUESTIONS:
{chr(10).join([f"- {q}" for q in questions])}

TRANSCRIPT EXCERPT:
{transcript}

For topic title and questions:
1. Keep them catchy and interesting, but short

For your answers:
1. Format them using HTML with <b> and <i> tags for highlighting. 
2. Prefer lists with <ol> and <li> tags. Ideally, <li> followed by <b> for the key points.
3. Quote important keywords but explain them in easy-to-understand language (e.g., "<b>Quantum computing</b> is like having a super-fast magical calculator")
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

    
    async def post(self, shared, prep_res, processed):
        """Update topics with processed content in shared"""
        topics = shared["topics"]
        
        # Update the topic with processed content
        for topic in topics:
            topic_title = topic["title"]
            if topic_title == processed["title"]:
                
                # Update topic with rephrased title
                topic["rephrased_title"] = processed["rephrased_title"]
                
                # Map of original question to processed question
                orig_to_processed = {
                    q["original"]: q
                    for q in processed["questions"]
                }
                
                # Update each question
                for q in topic["questions"]:
                    original = q["original"]
                    if original in orig_to_processed:
                        processed_q = orig_to_processed[original]
                        q["rephrased"] = processed_q.get("rephrased", original)
                        q["answer"] = processed_q.get("answer", "")
        
        # Update shared with modified topics
        shared["topics"] = topics
        
        logger.info(f"Processed content for {processed["title"]} topic")
        return "default"

class GenerateHTML(Node):
    """Generate HTML output from processed content"""
    async def prep(self, shared):
        """Get video info and topics from shared"""
        video_info = shared["video_info"]
        topics = shared["topics"]
        
        return {
            "video_info": video_info,
            "topics": topics
        }
    
    async def exec(self, data):
        """Generate HTML using html_generator"""
        video_info = data["video_info"]
        topics = data["topics"]
        
        title = video_info.get("title", "YouTube Video Summary")
        thumbnail_url = video_info.get("thumbnail_url", "")
        
        # Prepare sections for HTML
        sections = []
        for topic in topics:
            # Skip topics without questions
            if not topic.get("questions"):
                continue
                
            # Use rephrased_title if available, otherwise use original title
            section_title = topic.get("rephrased_title", topic.get("title", ""))
            
            # Prepare bullets for this section
            bullets = []
            for question in topic.get("questions", []):
                # Use rephrased question if available, otherwise use original
                q = question.get("rephrased", question.get("original", ""))
                a = question.get("answer", "")
                
                # Only add bullets if both question and answer have content
                if q.strip() and a.strip():
                    bullets.append((q, a))
            
            # Only include section if it has bullets
            if bullets:
                sections.append({
                    "title": section_title,
                    "bullets": bullets
                })
        
        # Generate HTML
        html_content = html_generator(title, thumbnail_url, sections)
        return html_content
    
    async def post(self, shared, prep_res, exec_res):
        """Store HTML output in shared"""
        shared["html_output"] = exec_res
        
        # Write HTML to file
        output_path = shared.output_path if hasattr(shared, "output_path") else shared.output_filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(exec_res)
        
        logger.info(f"Generated HTML output and saved to {output_path}")
        return "default"

# Create the flow
def create_youtube_processor_flow():
    """Create and connect the nodes for the YouTube processor flow"""
    process_url = ProcessYouTubeURL(max_retries=2, wait=10)
    extract_topics_and_questions = ExtractTopicsAndQuestions(max_retries=2, wait=10)
    process_content = ProcessContent(max_retries=2, wait=10)
    generate_html = GenerateHTML(max_retries=2, wait=10)
    
    process_url >> extract_topics_and_questions >> process_content >> generate_html
    
    return  Flow(start=process_url)
