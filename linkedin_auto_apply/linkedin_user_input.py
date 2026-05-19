import streamlit as st
import yaml
from datetime import datetime
from pathlib import Path
import logging
import subprocess
import os 

# Setup logging
logging.basicConfig(filename="linkedin_input.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Directory to store resumes
RESUME_DIR = Path("resumes")
RESUME_DIR.mkdir(exist_ok=True)

# YAML output path
CONFIG_YAML = "config.yaml"

# Streamlit UI
st.title("🔗 LinkedIn Auto Apply - User Configuration")
st.markdown("Fill out the details to configure your auto-apply preferences.")
logging.info("User started configuration form.")

# 1. LinkedIn credentials
st.header("1. LinkedIn Credentials")
email = st.text_input("Email")
password = st.text_input("Password", type="password")

# 2. Job Preferences
st.header("2. Job Preferences")
job_type = st.selectbox("Job Type", ["Remote", "On-site", "Hybrid"])
years_of_exp = st.number_input("Years of Experience", min_value=0, max_value=50, step=1)
positions = st.text_area("Preferred Positions (comma-separated)")
locations = st.text_area("Preferred Locations (comma-separated)")

# 3. Company Preferences
high_priority_companies = st.text_area("High Priority Companies (comma-separated)")
low_priority_companies = st.text_area("Low Priority / Blacklisted Companies (comma-separated)")

# 4. Languages
st.header("4. Languages and Proficiency")
languages_input = st.text_area("Languages (e.g. English:Fluent, Hindi:Intermediate)")

# 5. Area of Interest
interests = st.text_area("Areas of Interest (comma-separated)")

# 6. Notice Period
notice_period = st.text_input("Notice Period (e.g. Immediate, 1 month)")

# 7. Salary Range
salary_range = st.text_input("Expected Salary Range (e.g. 8-12 LPA)")

# 8. Additional Info
st.header("8. Additional Info")
gender = st.selectbox("Gender", ["Prefer not to say", "Male", "Female", "Other"])
disability = st.text_input("Disability (if any)")
ethnicity = st.text_input("Ethnicity")
authorization = st.text_input("Legal Authorization Info")

# 9. Resume Upload
st.header("📄 Upload Your Resume")
resume_file = st.file_uploader("Upload Resume (.doc or .docx)", type=["doc", "docx"])
resume_filename = None

if resume_file is not None and email:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_email = email.replace("@", "_at_").replace(".", "_dot_")
    resume_filename = f"{safe_email}_{timestamp}.docx"
    resume_path = RESUME_DIR / resume_filename

    with open(resume_path, "wb") as f:
        f.write(resume_file.read())

    st.success(f"Resume uploaded and saved as {resume_filename}")
    logging.info("Resume saved: %s", resume_path)

# 10. Save Configuration
if st.button("Save Configuration"):
    if not email.strip() or not password.strip():
        st.error("Email and password are required.")
    else:
        user_data = {
            "linkedin": {
                "email": email.strip(),
                "password": password.strip()
            },
            "job_preferences": {
                "job_type": job_type,
                "years_of_experience": years_of_exp,
                "positions": [p.strip() for p in positions.split(",") if p.strip()],
                "locations": [l.strip() for l in locations.split(",") if l.strip()]
            },
            "priority_companies": {
                "high": [c.strip() for c in high_priority_companies.split(",") if c.strip()],
                "low": [c.strip() for c in low_priority_companies.split(",") if c.strip()]
            },
            "languages": {
                lang.split(":")[0].strip(): lang.split(":")[1].strip()
                for lang in languages_input.split(",") if ":" in lang
            },
            "interests": [i.strip() for i in interests.split(",") if i.strip()],
            "notice_period": notice_period.strip(),
            "salary_range_inr": salary_range.strip(),
            "additional_info": {
                "gender": gender,
                "disability": disability.strip(),
                "ethnicity": ethnicity.strip(),
                "legal_authorization": authorization.strip()
            },
            "resume_filename": str(RESUME_DIR / resume_filename) if resume_filename else ""
        }

        with open(CONFIG_YAML, "w") as file:
            yaml.dump(user_data, file, sort_keys=False)

        logging.info("Configuration saved to config.yaml")
        st.success("✅ Configuration saved to config.yaml")
        
        venv_python = os.getenv("venv_python")
        scraper_path = os.getenv("job_scrap_extracted")
        try:
            logging.info("Running job_scrap_extracted.py...")
            subprocess.run([venv_python, scraper_path], check=True)
            logging.info("Running job_match.py...")
            matcher_path = os.getenv("job_match")
            subprocess.run(["streamlit","run", matcher_path])
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Command failed: {e.cmd}")
            logging.error(f"Exit code: {e.returncode}")
            logging.error(f"Stdout: {e.stdout}")
            logging.error(f"Stderr: {e.stderr}")
            st.error(f"Script failed: {e}")

        
        