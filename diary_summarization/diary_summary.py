from ollama_functions import qwen2_summary
from md_helper_functions import get_non_empty_headers_content
from dotenv import load_dotenv
import re

diary_template_path = r"diary_summarization\diary\td.md"

def get_diary_summary(diary_path):
    with open(diary_path, 'r', encoding='utf-8') as f:
        diary_content = f.read()
    
    with open(diary_template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Remove template content
    cleaned_content = get_non_empty_headers_content(diary_content, template_content)

    # Summarize the cleaned content
    summary = qwen2_summary(cleaned_content)
    
    return summary

def add_summary_to_diary(diary_content, template_content=None):
    """
    Add a summary of the diary content to the span tag.
    The summary will be generated based on the non-empty headers content.
    """
    # Get the diary content without template content
    diary_text = get_non_empty_headers_content(diary_content, template_content)
    
    if not diary_text:
        return diary_content  # Return original content if no content to summarize
    
    # Generate summary using ollama
    
    summary = qwen2_summary(diary_text)
    
    # Replace empty span content with summary
    span_pattern = r'(<span[^>]*>)\s*(\n*)\s*(</span>)'
    replacement = r'\1\n\t\t' + summary + r'\n\3'
    
    updated_content = re.sub(span_pattern, replacement, diary_content)
    
    return updated_content

def process_diary_file(diary_path, template_path=None):
    """
    Process a diary file and add summary to it.
    Updates the original file with the summary added to the span tag.
    """
    # Read diary content
    with open(diary_path, 'r', encoding='utf-8') as f:
        diary_content = f.read()
    
    # Read template content if provided
    template_content = None
    if template_path:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    
    # Add summary to diary
    updated_content = add_summary_to_diary(diary_content, template_content)
    
    # Write the updated content back to the file
    with open(diary_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    return updated_content

if __name__ == "__main__":
    # Example usage
    diary_path = r"C:\Users\lucas\Documents\road\diary\2024-12-20.md"
    template_path = r"diary_summarization\diary\td.md"
    
    updated_content = process_diary_file(diary_path, template_path)
    print("Diary has been updated with summary.")