# AI-Powered Job Application Automation System


## 🚀 Project Overview

This project leverages **Large Language Models (LLMs)** and **agentic AI** to automate and optimize the job application pipeline. It supports users through two major components:

1. **ATS-Friendly Resume Generation**
2. **Automated LinkedIn Job Application Engine**

By intelligently integrating user data, LLMs, and real-time job scraping, this system aims to **minimize manual effort**, **enhance resume targeting**, and **maximize job match accuracy**— all while increasing the likelihood of securing interviews.

---

## ✨ Features

### Intelligent Resume Generation
Generates ATS-friendly resumes tailored to specific job roles
Uses LLMs via Ollama for smart content generation
Optimizes resumes with:
Role-specific keywords
Industry-relevant skills
Professional formatting
Enhances ATS matching scores automatically
Supports resume customization based on:
Skills
Experience
Preferred domain
Target job role

##🔍 **Smart Job Scraping System**
Scrapes job postings from online job portals
Filters jobs based on:
Job title
Location
Experience level
User preferences
Collects real-time job data for analysis and application

##🤖 **Automated Job Application Engine**
Automates browser actions using Selenium
Automatically:
Opens job portals
Fills application forms
Uploads resumes
Submits applications
Reduces manual job application effort by over 80%
Supports bulk job application workflows

##📊 **AI-Based Job Matching**
Analyzes job descriptions using LLMs
Matches user resumes with job requirements
Identifies relevant opportunities with higher compatibility
Improves application targeting accuracy

---

## 🛠 Tech Stack

| Component        | Technology                 |
|------------------|----------------------------|
| Resume Generation | Qwen-32B Instruct (LLM)    |
| Job Matching     | Fine-tuned Mistral Model   |
| Scraping         | BeautifulSoup, Requests    |
| Automation       | Selenium                   |
| Backend          | Python (FastAPI/Flask)     |
| Frontend (Optional) | React / Streamlit       |
| Resume Export    | WeasyPrint / PDFKit        |

---

## 📦 Installation
```bash
# 1. Clone the repository
git clone git@github.com:sweha19032004/AI-Powered-Job-Application-Automation-System.git

# 2. Create virtual environment
python -m venv venv

# 3. Install dependencies
py -m pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Fill in your LinkedIn credentials, API keys, etc.

# 5. Run the app
venv\Scripts\python.exe -m streamlit run main.py
```






