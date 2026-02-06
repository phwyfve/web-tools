from typing import List, Dict, Any, Tuple
from datetime import datetime
from urllib.parse import quote_plus
import logging
import yaml
import zipfile
import asyncio
import os
import tempfile
from .utils.call_llm import call_llm
from .utils.youtube_processor import extract_video_id
from .youtube_video_summary import create_youtube_processor_flow
from youtube_search import YoutubeSearch
from caskada import Node, Flow, Memory

logger = logging.getLogger(__name__)

class YoutubeSearchNode(Node):
    """Search YouTube for videos based on a query and return videos published today"""

    async def prep(self, memory):
        logger.info(f"YoutubeSearch : Searching YouTube for today's videos about: {memory.subject}")
        return quote_plus(memory.subject.strip())

    async def exec(self, subject):

        logger.info(f"YoutubeSearch : Searching YouTube for today's videos about: {subject}")
        try:
            results = YoutubeSearch(
                subject, 
                max_results=20).to_dict()
        except Exception as e:
            logger.error(f"Search failed for subject '{subject}': {e}")
            return []

        video_urls = []

        for video in results:
            
            published_time = video.get("publish_time", "").lower()
            video_url = "https://www.youtube.com" + video.get("url_suffix", "")

            # Heuristic: published today
            if any(k in published_time for k in ["hour", "minute", "just now", "heures", "minutes"]):
                video_urls.append(video_url)
            else:
                logger.info(f"Skipping video not published today: ({published_time})")

        logger.info(f"Found {len(video_urls)} videos published today.")
        return video_urls
    
    async def post(self, memory: Memory, prep_res, exec_res):
        memory.video_list = exec_res
        self.trigger("default") 

class YoutubeVideoSelection(Node):
    async def prep(self, memory: Memory):
        return memory

    async def exec(self, memory):
        video_list = memory.video_list
        if( not video_list or len(video_list) <= 3):
            logger.info("Less than or equal to 3 videos found, selecting all.")
            return video_list
        
        logger.info("Selecting top 3 relevant videos using LLM...")
        prompt = f"""Given the following list of YouTube video URLs, select the 
3 most relevant to the subject "{memory.subject}". Return the result as YAML with the key `videos`.

video_list:
{memory.video_list}
"""
        response = await call_llm(prompt)
        yaml_content = response.split("```yaml")[1].split("```")[0].strip() if "```yaml" in response else response
        parsed = yaml.safe_load(yaml_content)
        raw_videos = parsed.get("videos", [])[:3]
        return raw_videos

    async def post(self, memory: Memory, prep_res, exec_res):
        memory.selected_videos = exec_res
        memory.remaining_chunks = 0
        for index, video in enumerate(exec_res):
            logger.info(f"Selected video {index + 1}: {video}")
            memory.remaining_chunks += 1
            self.trigger("default", {"index": index, "url": video})


class YoutubeVideoSummary(Node):
    async def prep(self, memory):
        return {
            "index": memory.index,
            "url": memory.url
        }

    async def exec(self, data_tuple):
        index = data_tuple["index"]
        url = data_tuple["url"]

        # Create flow
        flow = create_youtube_processor_flow()

        # Initialize shared memory for the subprocess
        output_dir = os.path.join(tempfile.gettempdir(), "webtools", "youtube")
        os.makedirs(output_dir, exist_ok=True)
        output_filename = f"youtube_summary_{index}_{extract_video_id(url)}.html"
        output_path = os.path.join(output_dir, output_filename)

        sub_shared = {
            "url": url,
            "output_filename": output_filename,
            "output_path": output_path
        }

        # Run the sub-flow
        logger.info(f"Starting YouTube processing flow for URL: {url}")
        await flow.run(sub_shared)

        return sub_shared["output_filename"]

    async def post(self, memory: Memory, prep_res, exec_res):
        if not hasattr(memory, "summaries"):
            memory.summaries = []

        memory.summaries.append(exec_res)
        memory.remaining_chunks -= 1
        if memory.remaining_chunks == 0:
            logger.info(f"All video summaries completed. {memory.summaries}")
            self.trigger("default", {})  # Trigger next node


class FinalReportGenerator(Node):
    async def prep(self, memory: Memory):
        return memory.summaries

    async def exec(self, summaries: List[str]):
        # Generate index HTML with links to the 3 summaries
        output_dir = os.path.join(tempfile.gettempdir(), "webtools", "youtube")
        os.makedirs(output_dir, exist_ok=True)
        index_filename = "index.html"
        index_path = os.path.join(output_dir, index_filename)
        links_html = "<h1>Robotics Stock - Video Summaries</h1>\n<ul>"
        for summary_file in summaries:
            links_html += f'<li><a href="{summary_file}">{summary_file}</a></li>\n'
        links_html += "</ul>"

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(links_html)

        # Create zip with all files
        zip_filename = "youtube_report.zip"
        zip_path = os.path.join(output_dir, zip_filename)
        with zipfile.ZipFile(zip_path, "w") as zipf:
            zipf.write(index_path, arcname=index_filename)
            for file in summaries:
                file_path = os.path.join(output_dir, file)
                zipf.write(file_path, arcname=file)

        return zip_filename

    async def post(self, shared, prep_res, exec_res):
        logger.info(f"Report generated and zipped: {exec_res}")


def create_main_flow():
    search = YoutubeSearchNode()
    select = YoutubeVideoSelection()
    summarize = YoutubeVideoSummary()
    finalize = FinalReportGenerator()

    search >> select >> summarize >> finalize

    # Créer le flow à partir du premier nœud
    return Flow(start=search)


async def main():

    memory = Memory({"subject": "Robotics Stock"})
    
    flow = create_main_flow()
    await flow.run(memory)

if __name__ == "__main__":
    asyncio.run(main())
