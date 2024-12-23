
import re
import ollama

def convert_md_to_string(md_file_path: str) -> str:
    """
    Convert markdown file content to plain text by removing markdown syntax.
    
    Args:
        md_file_path (str): Path to the markdown diary file
        
    Returns:
        str: Plain text content without markdown syntax
    """
    try:
        with open(md_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Extract meaningful content
        sections = []
        
        # Extract timeline content (do this before removing YAML front matter)
        timeline_matches = re.finditer(r'<span[^>]*>([^<]+)</span>', content)
        for match in timeline_matches:
            timeline_text = match.group(1).strip()
            if timeline_text:
                sections.append(timeline_text)
        
        # Remove YAML front matter
        content = re.sub(r'^---[\s\S]*?---\n', '', content)
        
        # Extract content from main sections using more flexible patterns
        section_patterns = [
            (r'#\s*✝\s*praying\s*\n(.*?)(?=\n#|\Z)', 'praying'),
            (r'#\s*😊\s*Daily Summary[：:]\s*\n(.*?)(?=\n#|\Z)', 'summary'),
            (r'#\s*🤩\s*挑战[：:]\s*\n(.*?)(?=\n#|\Z)', 'challenge')
        ]
        
        for pattern, _ in section_patterns:
            matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                section_text = match.group(1).strip()
                if section_text:
                    # Clean up the section text
                    # Remove task lists and bullet points
                    clean_text = re.sub(r'^\s*[-*+]\s+|\s*- \[ \]\s*|\s*- \[x\]\s*', '', section_text, flags=re.MULTILINE)
                    if clean_text.strip():
                        sections.append(clean_text)
        
        # Join all sections with newlines
        content = '\n'.join(sections)
        
        # Keep Chinese text, numbers, basic punctuation, and essential whitespace
        content = re.sub(r'[^\u4e00-\u9fff\d\s.,!?，。！？、：]', ' ', content)
        
        # Clean up whitespace and formatting
        content = re.sub(r'\s+', ' ', content)  # Normalize spaces
        content = re.sub(r'\s+([，。！？、：])', r'\1', content)  # Fix Chinese punctuation
        content = re.sub(r'\n\s*\n', '\n', content)  # Clean up multiple newlines
        content = content.strip()
        
        return content
        
    except Exception as e:
        raise Exception(f"Error converting markdown file: {str(e)}")

def qwen2_summary(text: str) -> str:
    """
    Summarize the given text using Ollama's qwen2.5 model.
    
    Args:
        text (str): Text content to summarize
        max_sentences (int): Maximum number of sentences in the summary (default: 3)
        
    Returns:
        str: Summarized text
    """
    try:
        # Construct the prompt with Chinese context
        prompt = f"""请简单的以第一人称概括日记的内容 50-100字，保持原文的情感和核心信息，：

{text}

总结："""
        
        # Call Ollama API
        response = ollama.chat(
            model="qwen2.5:latest",
            messages=[{
                "role": "user",
                "content": prompt
            }],
            options={
                "temperature": 0.0}
        )
        
        return response['message']['content'].strip()
        
    except Exception as e:
        raise Exception(f"Error generating summary with Ollama: {str(e)}")

def summarize_diary_file(md_file_path: str) -> str:
    """
    Convert markdown file to text and generate a summary.
    
    Args:
        md_file_path (str): Path to the markdown diary file
        
    Returns:
        str: Summarized content
    """
    # Convert MD to text
    plain_text = convert_md_to_string(md_file_path)
    print(f"Plain text: {plain_text}\n")
#     plain_text = """
# 2024-07-06 - Sat Jul: 22:10 ✝️现在我真的不能再否认我的能力，以及耶稣基督的安排了，因为就在30分钟前，我还非常怀疑的觉得自己无法解决这个质量有问题，不是5的mask就会报错的问题，虽然这一次的怀疑比之前要平淡了很多，但是我还是不觉得我能在今天内解决这个cuda的报错问题，可我就是解决了，是靠我的能力没错。也许这一次鉴证并不是关于上帝有多么的神奇，而是告诉我要相信自己的能力，我以及完成过很多次我觉得我无法完成，但是我就是完成了的任务，所以，相信自己的能力，相信上帝创造我，我就有我的价值，不要再自我怀疑而犹豫不前了，听上帝的安排，我能做到的
# 2024-07-03 - Wed Jul: 23:29 做research的时候，以为drop len为什么需要，不加就会cuda error我几天都没搞清楚，当上帝要我今天就把这个知识点搞懂的时候感觉上帝很无理取闹，我只想逃避这些我搞不懂的东西，但是我就是同一天，还是想清楚为什么了，而且并不难，我感觉这并不是因为上帝的指导。我还是无法坚定的相信上帝，我还是经常怀疑，抱怨上帝给我的安排，或者是说我相信上帝，但我不相信自己的力量
# 2024-06-27 - Thu Jun: 21:25 需要压线棒把牙缝里面的东西挑出来
# 2024-06-21 - Fri Jun: 11:30 所以现在，学习数学只是你为了达到某种目的的手段吗？我可以很负责的告诉你数学很有趣，试试在数学里面找到乐趣去指导你愈发深刻，记住你做的一切，都是为了让你的生命更加深刻，更接近神，而这个深刻是没有止境的，
# 2024-06-13 - Thu Jun: 23:49 还是要向上帝祷告，我该如何才能不再看YouTube，b站，这两个东西，只会让我欲火缠身，充满想要对比的胜负欲
# 2024-06-12 - Wed Jun: 23:15 总之现在无论做什么都尽量去与上帝同在，内心要祥和，多阅读，平静一点，要活在自己的节奏里面，看视频容易陷入别人的节奏。今天跑步就跑出了自己的节奏，就跑的很舒服
# 2024-06-12 - Wed Jun: 01:18 上帝和我说，就是因为我现在很狼狈：才破戒，考试因为我看YouTube看手机没考好，一个easy的工作也因为自己的心急而搞得很麻烦，觉得自己毕业典礼的时候要变丑了，然后肚子也不舒服，然后发现其实自己对手机也是有瘾的，是要小心的）就是这么真实的样子，去拍视频，去写文案，才会有共鸣，同时在写视频的过程中我也会更了解我自己
# 2024-06-11 - Tue Jun: 12:54 昨天出去吃饭，吃的很饱，但是感觉肚子不舒服，不仅没睡好，早上起来也不舒服
# 2024-06-08 - Sat Jun: 11:22 所以人生的意义是什么呢？先去跑步你就会明白了
# """
    # Generate summary
    return summarize_diary(plain_text)

if __name__ == "__main__":
    # Use the diary folder from your Documents
    md_file_path = r"diary\diary2.md"
    summary = summarize_diary_file(md_file_path)
    print(f"summary: {summary}")
