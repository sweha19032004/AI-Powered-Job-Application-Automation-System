import streamlit as st
import subprocess
import os

# Set the title of the page
st.title("Job Resume and Match AI")

# Set a short description
st.write("Welcome! Choose one of the options below:")

# Create two buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("Resume Maker"):
        # Path to the Resume Maker script
        resume_maker_path = os.getenv("resume_maker_input")
        
        # Run the Resume Maker script using subprocess
        subprocess.Popen(["streamlit", "run", resume_maker_path], shell=True)

with col2:
    if st.button("Job Matcher"):
        # Path to the Job Matcher script
        job_matcher_path = os.getenv("linkedin_auto_apply")
        
        # Run the Job Matcher script using subprocess
        subprocess.Popen(["streamlit", "run", job_matcher_path], shell=True)
