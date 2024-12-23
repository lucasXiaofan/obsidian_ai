import streamlit as st
import os
from datetime import datetime
from pathlib import Path
import glob
from diary_summarization.diary_summary import update_diary_summaries

def get_recent_diaries(diary_folder, limit=10):
    """Get the most recent diary files from the specified folder."""
    diary_files = glob.glob(os.path.join(diary_folder, "*.md"))
    # Sort files by modification time, most recent first
    diary_files.sort(key=os.path.getmtime, reverse=True)
    return diary_files[:limit]

st.title("Obsidian Diary Manager")

# Input for diary folder path
diary_folder = st.text_input("Enter your Obsidian diary folder path:", 
                            help="Enter the full path to your diary folder")

if diary_folder:
    if not os.path.exists(diary_folder):
        st.error("The specified folder does not exist!")
    else:
        # Display recent diaries
        st.subheader("10 Most Recent Diaries")
        recent_diaries = get_recent_diaries(diary_folder)
        
        if recent_diaries:
            for diary in recent_diaries:
                diary_name = os.path.basename(diary)
                modified_time = datetime.fromtimestamp(os.path.getmtime(diary))
                st.write(f" {diary_name} (Last modified: {modified_time.strftime('%Y-%m-%d %H:%M:%S')})")
        else:
            st.info("No diary files found in the specified folder.")
        
        # Update summaries button
        if st.button("Update Diary Summaries"):
            with st.spinner("Updating summaries..."):
                try:
                    update_diary_summaries(diary_folder)
                    st.success("Successfully updated diary summaries!")
                except Exception as e:
                    st.error(f"Error updating summaries: {str(e)}")