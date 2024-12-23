"""
given a md template like this:
---
tags:
  - timeline
meditation: 0
vocab: 0
joggling: 0
workSession: 0
---
<span 
	  class='ob-timelines' 
	  data-date=' {{date:YYYY-MM-DD}} ' 
	  data-title=' 日记' 
	  data-class='blue' 
	  data-img = 'diary/timeline-image/b.png' 
	  data-type='range' 
	  data-end=' {{date:YYYY-MM-DD}} '> 
		
</span>
# ✝ praying


---
# 💪 records of self-control： 
注意力要在呼吸，呼吸轻柔
每天静坐 10 分钟，写个reflection就行了



---
# 😊Daily Summary：


---
# 🤩挑战：


---
# Day planner
need do research, always, it is fun 😍
- [ ] exercise 
- [ ] ai code


return a dictionary that return a dictionary that content:
1. content of each header 1 
2. dictionary of tags
3. dictionary of content inside span
ignore ---


"""

import re
import yaml

def clean_content(content):
    """Remove extra newlines and separator lines (---), preserving YAML frontmatter."""
    # First extract the frontmatter if it exists
    frontmatter_pattern = r"^(---\n.*?\n---\n)"
    frontmatter_match = re.match(frontmatter_pattern, content, re.DOTALL)
    
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        rest_content = content[len(frontmatter):]
    else:
        frontmatter = ""
        rest_content = content
    
    # Clean the rest of the content
    rest_content = re.sub(r'\n{3,}', '\n\n', rest_content)
    rest_content = re.sub(r'\n---\n', '\n', rest_content)
    rest_content = rest_content.strip()
    
    # Combine frontmatter and cleaned content
    return frontmatter + rest_content if frontmatter else rest_content

def extract_yaml_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    yaml_pattern = r"^---\n(.*?)\n---"
    match = re.search(yaml_pattern, content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return {}
    return {}

def extract_span_content(content):
    """Extract content inside span tag and parse its data attributes."""
    span_pattern = r"<span[^>]*>(.*?)</span>"
    data_pattern = r'data-(\w+)\s*=\s*[\'"]([^\'"]*)[\'"]'
    
    span_match = re.search(span_pattern, content, re.DOTALL)
    if span_match:
        span_text = span_match.group(0)
        data_attrs = dict(re.findall(data_pattern, span_text))
        return data_attrs
    return {}

def extract_header_content(content):
    """Extract content under each header 1 (#)."""
    # Split content by headers
    header_pattern = r"#\s+([^#\n]+)([^#]*?)(?=\n#|\Z)"
    headers = {}
    
    for match in re.finditer(header_pattern, content):
        header_title = match.group(1).strip()
        header_content = match.group(2).strip()
        headers[header_title] = header_content
    
    return headers

def parse_markdown_template(md_content):
    """
    Parse markdown template and return a dictionary containing:
    1. Content of each header 1
    2. Dictionary of tags
    3. Dictionary of content inside span
    """
    # Remove any Windows line endings and clean content
    md_content = md_content.replace('\r\n', '\n')
    md_content = clean_content(md_content)
    
    result = {
        'frontmatter': extract_yaml_frontmatter(md_content),
        'span_data': extract_span_content(md_content),
        'headers': extract_header_content(md_content)
    }
    
    return result

def extract_template_content(template_content):
    """Extract predefined content from a template file."""
    result = parse_markdown_template(template_content)
    template_predefined = {}
    
    # Store non-empty predefined content for each header
    for header, content in result['headers'].items():
        if content.strip():
            template_predefined[header] = content.strip()
    
    return template_predefined

def remove_template_content(content, template_content):
    """Remove predefined template content from a file."""
    # Get predefined content from template
    template_predefined = extract_template_content(template_content)
    
    # Parse the actual content
    parsed_content = parse_markdown_template(content)
    
    # Remove predefined content from each header
    for header, header_content in parsed_content['headers'].items():
        if header in template_predefined:
            # Remove the predefined content
            cleaned_content = header_content.replace(template_predefined[header], '').strip()
            parsed_content['headers'][header] = cleaned_content
    
    # Reconstruct the markdown content
    result = []
    
    # Add frontmatter
    if parsed_content['frontmatter']:
        result.append('---')
        result.append(yaml.dump(parsed_content['frontmatter'], allow_unicode=True).strip())
        result.append('---\n')
    
    # Add span if exists
    if parsed_content['span_data']:
        span_text = "<span"
        for key, value in parsed_content['span_data'].items():
            span_text += f' data-{key}="{value}"'
        span_text += ">\n\n</span>\n"
        result.append(span_text)
    
    # Add headers and their content
    for header, content in parsed_content['headers'].items():
        result.append(f"# {header}\n")
        if content.strip():
            result.append(f"{content.strip()}\n")
        result.append("\n")
    
    return '\n'.join(result)

def get_non_empty_headers_content(content, template_content=None):
    """
    Return non-empty header content as a string, with symbols removed from headers.
    Format: header: content; header2: content2
    If template_content is provided, removes template content first.
    """
    if template_content:
        content = remove_template_content(content, template_content)
    
    parsed_content = parse_markdown_template(content)
    
    # Remove emojis and symbols from headers and get non-empty content
    result_pairs = []
    for header, content in parsed_content['headers'].items():
        cleaned_content = content.strip()
        if cleaned_content:
            # Remove emojis and symbols from header
            clean_header = re.sub(r'[^\w\s]', '', header).strip()
            # Replace newlines with spaces and remove multiple spaces
            cleaned_content = re.sub(r'\s+', ' ', cleaned_content.replace('\n', ' '))
            result_pairs.append(f"{clean_header}: {cleaned_content}")
    
    return "; ".join(result_pairs)

if __name__ == "__main__":
    # Use the diary folder from your Documents
    md_file_path = r"diary_summarization\diary\diary2.md"
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    result = parse_markdown_template(md_content)
    print(result)

    # Test the template content removal
    template_path = r"diary_summarization\diary\td.md"
    diary_path = r"diary_summarization\diary\diary2.md"
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    with open(diary_path, 'r', encoding='utf-8') as f:
        diary_content = f.read()
    
    # Remove template content
    cleaned_content = remove_template_content(diary_content, template_content)
    result = parse_markdown_template(cleaned_content)
    print(result)

    # Get formatted content
    formatted_content = get_non_empty_headers_content(diary_content, template_content)
    print("\nFormatted content:")
    print(formatted_content)