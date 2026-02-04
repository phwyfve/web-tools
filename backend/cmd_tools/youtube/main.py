import argparse
import asyncio
import logging
import sys
import os
from flow import create_youtube_processor_flow

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("youtube_processor.log")
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the YouTube content processor."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Process a YouTube video to extract topics, questions, and generate ELI5 answers."
    )
    parser.add_argument(
        "--url", 
        type=str, 
        help="YouTube video URL to process",
        required=False
    )
    args = parser.parse_args()
    
    # Get YouTube URL from arguments or prompt user
    url = args.url
    if not url:
        url = input("Enter YouTube URL to process: ")
    
    logger.info(f"Starting YouTube content processor for URL: {url}")

    # Create flow
    flow = create_youtube_processor_flow()
    
    # Initialize shared memory
    shared = {
        "url": url
    }
    
    # Run the flow
    asyncio.run( flow.run(shared))
    
    # Report success and output file location
    print("\n" + "=" * 50)
    print("Processing completed successfully!")
    print(f"Output HTML file: {os.path.abspath('output.html')}")
    print("=" * 50 + "\n")

    return 0

if __name__ == "__main__":
    sys.exit(main())
