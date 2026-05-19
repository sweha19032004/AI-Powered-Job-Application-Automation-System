import streamlit as st
import pandas as pd
import yaml 
import threading
import requests
import logging
from docx import Document
import os
import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage
import os

# -----------------------------------
# Logging setup
logging.basicConfig(
    filename="job_match_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -----------------------------------
st.set_page_config("Job Match Assistant", layout="wide")

# --- Load config and resume ---
def load_config_and_resume():
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    resume_path = config["resume_filename"].replace("\\", "/")

    if not os.path.exists(resume_path):
        logging.error(f"Resume file not found: {resume_path}")
        st.error(f"❌ Resume file not found: {resume_path}")
        st.stop()

    doc = Document(resume_path)
    resume_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    logging.info("Loaded config and resume successfully.")
    return config, resume_text

config, resume_text = load_config_and_resume()

# --- Load job data ---
@st.cache_data
def load_jobs():
    try:
        df = pd.read_csv("linkedin_scraped_jobs.csv")
        logging.info("✅ Job data loaded from 'linkedin_scrapejobs.csv'.")
    except Exception as e:
        logging.error(f"❌ Failed to load job CSV: {e}")
        st.error(f"❌ Failed to load job CSV: {e}")
        st.stop()

    if 'Status' not in df.columns:
        df['Status'] = 'Not Selected'
    return df

df = load_jobs()

# --- Build job description for AI ---
def build_job_description(row):
    return row.get("About", "").strip()

# --- LangChain + Ollama match scoring ---
def get_match_percentage(job_description, resume_text):
    prompt = f"""
You are an AI assistant that evaluates how well a resume matches a job description.
Only compare the job description and resume.

Give a match percentage (0-100), explain reasoning, list strengths and weaknesses.

Job Description:
{job_description}

Resume:
{resume_text}

Respond in JSON format like:
{{ "match_percentage": 80 (give match percentage here), "reason": "Your resume matches well because... (donot include match percentage give reasons for why the resume is match for the job )" }}
"""
    result = {}
    logging.info("🔍 Calling LangChain + Ollama for match scoring...")

    def call_ollama():
        try:
            chat = ChatOllama(model="mistral") 
            messages = [HumanMessage(content=prompt)]
            response = chat(messages)
            result["response"] = response
            logging.info("✅ Ollama response received.")
        except Exception as e:
            result["error"] = str(e)
            logging.error(f"❌ Ollama failed: {e}")

    thread = threading.Thread(target=call_ollama)
    thread.start()
    thread.join(timeout=300)  

    if not thread.is_alive() and "response" in result:
        try:
            reply_content = result["response"].content.strip()
            parsed = json.loads(reply_content)
            return parsed.get("match_percentage", 0), parsed.get("reason", reply_content)
        except Exception as e:
            logging.warning(f"⚠️ Ollama response parsing failed: {e}")
            return 0, result["response"].content.strip()

    logging.warning("⚠️ Ollama timeout/failure. Falling back to HuggingFace.")

    
    headers = {
    "Authorization": f"Bearer {os.getenv('Token')}"
}
    api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"

    try:
        response = requests.post(api_url, headers=headers, json={"inputs": prompt}, timeout=60)
        response.raise_for_status()
        json_response = response.json()

        if isinstance(json_response, list) and "generated_text" in json_response[0]:
            generated = json_response[0]["generated_text"]
        else:
            generated = str(json_response)

        match_percentage = 0
        reason = generated.strip()

        if generated.strip().startswith("{"):
            try:
                parsed = json.loads(generated)
                match_percentage = parsed.get("match_percentage", 0)
                reason = parsed.get("reason", generated)
            except:
                pass
        if match_percentage == 0:
            match = re.search(r'match_percentage[":\s]*([0-9]+)', generated)
            if match:
                match_percentage = int(match.group(1))

        return match_percentage, reason

    except Exception as e:
        logging.error(f"❌ HuggingFace fallback failed: {e}")
        logging.info("🔁 Falling back to basic text similarity model.")

        # --- Basic fallback using cosine similarity ---
        try:
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            match_score = int(similarity * 100)

            reason = (
                "⚠️ Both LangChain + Ollama and HuggingFace failed. "
                f"Used fallback TF-IDF cosine similarity which gave a match score of {match_score}%."
            )
            return match_score, reason
        except Exception as e:
            logging.error(f"❌ TF-IDF fallback also failed: {e}")
            return 0, "⚠️ All methods failed (LangChain + Ollama, HuggingFace, and text similarity)."

# --- Streamlit UI ---
st.title("🧠 Smart LLM-Powered Job Matcher")

applied_indices = []

for idx, row in df.iterrows():
    with st.expander(f"📄 {row['Job Title']} at {row['Company and Location']}"):
        job_desc = build_job_description(row)
        match_pct, reason = get_match_percentage(job_desc, resume_text)

        st.markdown(f"**🔢 Match Score:** {match_pct}%")
        st.markdown(f"**📝 Reason:** _{reason}_")
        st.markdown(f"**🔗 Job Link:** [Open Posting]({row['Apply Link']})")

        if match_pct >= 40:
            if st.button(f"✅ Apply Now", key=f"apply_{idx}"):
                df.at[idx, "Status"] = "Applied"
                applied_indices.append(idx)
                logging.info(f"📌 Marked as Applied: {row['Job Title']} at {row['Company and Location']}")
                st.success("✅ Marked as Applied")
        else:
            df.at[idx, "Status"] = "Rejected"
            logging.info(f"🚫 Rejected job due to low score: {row['Job Title']} at {row['Company and Location']}")
            st.warning("❌ Job Rejected due to low match score.")

# --- Save Updates ---
if applied_indices:
    df.to_csv("linkedin_scrapejobs_updated.csv", index=False)
    st.success("📁 Job statuses saved to 'linkedin_scrapejobs_updated.csv'")
    logging.info("📁 Job statuses updated and saved to CSV.")