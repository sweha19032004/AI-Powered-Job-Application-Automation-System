import requests
import os
import logging
from dotenv import load_dotenv
# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Resume:
    """
    Class to generate ATS-friendly resume using Hugging Face model inference.
    """

    def __init__(self, name, contact, education, skills, experience, projects, job, api_key=None):
        
        self.api_key = os.getenv("TOKEN")
        self.model = os.getenv("resume_model")

        self.name = name
        self.contact = contact
        self.education = education 
        self.skills = skills 
        self.experience = experience 
        self.projects = projects 
        self.job = job 

        if not self.api_key:
            raise ValueError("❌ API key is missing! Set it as an environment variable or pass it explicitly.")

    def construct_prompt(self):
        """
        Constructs a clean prompt for the LLM with job description and candidate details.
        """
        return f"""
You are an expert in writing ATS-friendly resumes.

**Instructions:**
- Optimize the resume content to match the provided job description.
- Ensure ATS-compliance by using industry-relevant keywords.
- Format the resume in a structured way as professional resume used in market
-Do NOT fabricate or assume any missing data.
- Use ONLY the information provided below.
- Format with sections and bullet points.
- Match the resume to the given job description using industry keywords.
- Keep it professional and clear.
 

**Job Description:**
{self.job}

**Candidate Information:**
- Name: {self.name}
- Contact: {self.contact}
- Education: {self.education}
- Skills: {self.skills}
- Experience: {self.experience}
- Projects: {self.projects}

**Expected Output:**  
Generate a professional, structured, and ATS-friendly resume that aligns with the job description.
"""

    def run(self):
        """
        Sends a prompt to Hugging Face inference API and returns the generated resume.
        """
        url = f"https://api-inference.huggingface.co/models/{self.model}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": self.construct_prompt(),
            "parameters": {
                "max_new_tokens": 800,
                "temperature": 0.7  # Slightly lower for consistency
            }
        }

        logging.info("📤 Sending request to Hugging Face API...")

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)

            if response.status_code == 200:
                response_json = response.json()

                # Handle standard HF inference response format
                if isinstance(response_json, list) and response_json:
                    return response_json[0].get("generated_text", "⚠ No response generated.")
                elif isinstance(response_json, dict) and "generated_text" in response_json:
                    return response_json["generated_text"]
                else:
                    logging.warning("⚠ Unexpected format from Hugging Face API.")
                    return str(response_json)

            else:
                logging.error(f"❌ API Error {response.status_code}: {response.text}")
                return f"⚠ API Error {response.status_code}: {response.text}"

        except requests.exceptions.Timeout:
            logging.error("❌ API Request Timeout!")
            return "⚠ The request timed out. Try again later."

        except requests.exceptions.ConnectionError:
            logging.error("❌ Network Error!")
            return "⚠ Network error! Please check your internet connection."

        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Request Failed: {e}")
            return f"⚠ Request failed: {e}"








