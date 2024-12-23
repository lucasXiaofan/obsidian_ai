from crewai import LLM, Agent, Task, Crew
from dotenv import load_dotenv
from typing import Dict, Any
import re
from datetime import datetime
import os
from pathlib import Path

# Load environment variables
load_dotenv()
print(os.getenv("OPENAI_API_KEY"))
# Configure OpenAI API
os.environ['OPENAI_MODEL_NAME'] = 'gpt-4o-mini'
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

class DiaryProcessor:
    def __init__(self, diary_folder: str):
        self.diary_folder = Path(diary_folder)
        
        # Create OpenAI LLM configuration

        
        # Create agents with specific roles
        self.analyzer_agent = Agent(
            role='Diary Analyzer',
            goal='Analyze diary entries and extract key information',
            backstory='Expert in analyzing personal diary entries and extracting emotional patterns and key events. You understand both English and Chinese content.',
            verbose=True,
            allow_delegation=False,
      
        )
        
        self.summarizer_agent = Agent(
            role='Content Summarizer',
            goal='Create concise summaries of diary content',
            backstory='Specialist in condensing diary entries while preserving important emotional and factual content. You can work with both English and Chinese content.',
            verbose=True,
            allow_delegation=False,
        )
        
        self.template_agent = Agent(
            role='Template Formatter',
            goal='Format analyzed content into the specified template',
            backstory='Expert in organizing and formatting content according to predefined templates. You can handle both English and Chinese content.',
            verbose=True,
            allow_delegation=False,
        )

    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from diary content"""
        metadata = {
            'meditation': 0,
            'vocab': 0,
            'joggling': 0,
            'workSession': 0
        }
        
        # Extract metadata using regex
        meta_pattern = r'meditation:\s*(\d+)|vocab:\s*(\d+)|joggling:\s*(\d+)|workSession:\s*(\d+)'
        matches = re.finditer(meta_pattern, content, re.IGNORECASE)
        for match in matches:
            for key, value in zip(metadata.keys(), match.groups()):
                if value is not None:
                    metadata[key] = int(value)
        
        return metadata

    def load_diary_content(self, file_path: str) -> str:
        """Load diary content from a markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def process_diary(self, content: str) -> str:
        # Create tasks for the agents
        analysis_task = Task(
            description="Analyze the diary entry and identify key themes, emotions, and events",
            agent=self.analyzer_agent,
            expected_output="A detailed analysis of the diary entry's themes, emotions, and key events"
        )

        summary_task = Task(
            description="Create a concise summary of the diary entry focusing on main points and emotional state",
            agent=self.summarizer_agent,
            expected_output="A concise summary of the diary entry highlighting main points and emotional state"
        )

        template_task = Task(
            description="Format the analyzed content into the specified template structure",
            agent=self.template_agent,
            expected_output="The diary content formatted according to the template structure"
        )

        # Create and run the crew
        crew = Crew(
            agents=[self.analyzer_agent, self.summarizer_agent, self.template_agent],
            tasks=[analysis_task, summary_task, template_task],
            verbose=True
        )

        # Get metadata
        metadata = self.extract_metadata(content)
        
        # Get current date
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Create template with extracted information
        template = f"""---
tags:
  - timeline
meditation: {metadata['meditation']}
vocab: {metadata['vocab']}
joggling: {metadata['joggling']}
workSession: {metadata['workSession']}
---
<span 
      class='ob-timelines' 
      data-date='{current_date}' 
      data-title='日记' 
      data-class='blue' 
      data-img='diary/timeline-image/b.png' 
      data-type='range' 
      data-end='{current_date}'> 
    {crew.kickoff()}
</span>
"""
        return template

    def process_diary_files(self) -> Dict[str, str]:
        """Process all markdown files in the diary folder"""
        processed_entries = {}
        
        # Ensure diary folder exists
        if not self.diary_folder.exists():
            raise FileNotFoundError(f"Diary folder not found: {self.diary_folder}")
        
        # Process each markdown file
        for file_path in self.diary_folder.glob('*.md'):
            try:
                content = self.load_diary_content(str(file_path))
                processed_content = self.process_diary(content)
                processed_entries[file_path.name] = processed_content
            except Exception as e:
                print(f"Error processing {file_path.name}: {str(e)}")
        
        return processed_entries

# Example usage
if __name__ == "__main__":
    # Use the diary folder from your Documents
    diary_folder = r"diary_summarization\diary"
    processor = DiaryProcessor(diary_folder)
    
    # Process all diary entries
    processed_entries = processor.process_diary_files()
    
    # Print results
    for filename, processed_content in processed_entries.items():
        print(f"\nProcessing {filename}:")
        print(processed_content)
        print("-" * 80)
