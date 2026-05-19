# AI-Powered Job Application Automation System


## 🚀 Project Overview

This project leverages **Large Language Models (LLMs)** and **agentic AI** to automate and optimize the job application pipeline. It supports users through two major components:

1. **ATS-Friendly Resume Generation**
2. **Automated LinkedIn Job Application Engine**

By intelligently integrating user data, LLMs, and real-time job scraping, this system aims to **minimize manual effort**, **enhance resume targeting**, and **maximize job match accuracy**—all while increasing the likelihood of securing interviews.
`
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
###🔍 **Smart Job Scraping System**
Scrapes job postings from online job portals
Filters jobs based on:
Job title
Location
Experience level
User preferences
Collects real-time job data for analysis and application
🤖 **Automated Job Application Engine**
Automates browser actions using Selenium
Automatically:
Opens job portals
Fills application forms
Uploads resumes
Submits applications
Reduces manual job application effort by over 80%
Supports bulk job application workflows
📊** AI-Based Job Matching**
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

![image](https://github.com/user-attachments/assets/8cd4d9f2-f1b8-415a-a1b1-da03a1a6348e)
![image](https://github.com/user-attachments/assets/a1732060-2640-4b0f-a631-c2a19e33b9cc)
![image](https://github.com/user-attachments/assets/d5be5244-32b0-4c27-bcf7-f4ea1d26881d)
![image](https://github.com/user-attachments/assets/20e3297e-1b6d-4d7b-9698-a20e347c5d60)
![image](https://github.com/user-attachments/assets/a65aecbc-088c-4ddc-a448-77d2f9ba93f3)




