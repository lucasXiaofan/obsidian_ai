from diary_summarization.ollama_functions import qwen2_summary
from diary_summarization.md_helper_functions import get_non_empty_headers_content
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
    
    # Check if has_summary: true in front matter
    if has_summary(diary_content):
        print("Diary already has summary. no changes made.")
        return diary_content
    
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

def has_summary(diary_content: str) -> bool:
    """
    Check if the diary content has has_summary: true in its front matter.
    
    Args:
        diary_content (str): Content of the diary file
        
    Returns:
        bool: True if diary has has_summary: true in front matter, False otherwise
    """
    # Look for front matter between --- markers
    front_matter_pattern = r'^---\n(.*?)\n---'
    front_matter_match = re.search(front_matter_pattern, diary_content, re.DOTALL)
    
    if front_matter_match:
        front_matter = front_matter_match.group(1)
        # Look for has_summary: true in front matter
        has_summary_match = re.search(r'has_summary:\s*true', front_matter, re.IGNORECASE)
        return bool(has_summary_match)
    
    return False

def update_diary_summaries(diary_folder: str) -> tuple[bool, str]:
    """
    Update summaries for all diary entries in the specified folder using the diary template.
    
    Args:
        diary_folder (str): Path to the folder containing diary entries
        
    Returns:
        tuple[bool, str]: Success status and message
    """
    import os
    import glob
    
    try:
        # Verify folder exists
        if not os.path.exists(diary_folder):
            return False, "Diary folder does not exist"
        
        # Get all markdown files in the folder
        diary_files = glob.glob(os.path.join(diary_folder, "*.md"))
        
        if not diary_files:
            return False, "No diary files found in the specified folder"
        
        # Process each diary file using the existing function
        processed_count = 0
        for diary_path in diary_files:
            try:
                process_diary_file(diary_path, diary_template_path)
                processed_count += 1
            except Exception as e:
                print(f"Error processing {diary_path}: {str(e)}")
                continue
        
        return True, f"Successfully updated summaries for {processed_count} diary entries"
        
    except Exception as e:
        return False, f"Error updating diary summaries: {str(e)}"

if __name__ == "__main__":
    # Example usage
    diary_path = r"C:\Users\lucas\Documents\road\diary\2024-12-20.md"
    template_path = r"diary_summarization\diary\td.md"
    
    updated_content = process_diary_file(diary_path, template_path)
    print("Diary has been updated with summary.")