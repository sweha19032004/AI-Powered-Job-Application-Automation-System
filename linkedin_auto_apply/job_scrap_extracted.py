import pandas as pd
import re
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tabulate import tabulate
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

EMAIL = os.getenv("LINKEDIN_EMAIL")
PASSWORD = os.getenv("LINKEDIN_PASSWORD")

service = Service(ChromeDriverManager().install())
browser = webdriver.Chrome(service=service)

browser.get("https://www.linkedin.com")

# Sign in
signinwithemail = browser.find_element(By.CSS_SELECTOR, "a[data-test-id='home-hero-sign-in-cta']")
signinwithemail.click()

wait = WebDriverWait(browser, 10)
username = wait.until(EC.presence_of_element_located((By.ID, "username")))
username.send_keys(EMAIL)

password = wait.until(EC.presence_of_element_located((By.ID, "password")))
password.send_keys(PASSWORD)

login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
login_button.click()

browser.get("https://www.linkedin.com/jobs/")

# Scroll and expand job list
browser.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
time.sleep(2)

clicked = False
try:
    show_all_link = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[.//span[text()='Show all']]"))
    )
    browser.execute_script("arguments[0].scrollIntoView(true);", show_all_link)
    time.sleep(1)
    show_all_link.click()
    clicked = True
except:
    try:
        show_all_button = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Show all']]"))
        )
        browser.execute_script("arguments[0].scrollIntoView(true);", show_all_button)
        time.sleep(1)
        show_all_button.click()
        clicked = True
    except:
        pass

# Scroll to load job cards
try:
    first_card = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "job-card-container"))
    )
    first_card.click()
except:
    print("Could not click first job.")

for _ in range(15):
    browser.execute_script("window.scrollBy(0, 600);")
    time.sleep(1)

# Extract job titles
job_elements = WebDriverWait(browser, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "flex-grow-1"))
)
job_data_blocks = [el.text.strip() for el in job_elements if el.text.strip()]
job_titles = [block.split("\\n")[0] for block in job_data_blocks]

# Extract company names and locations
company_elements = browser.find_elements(By.CLASS_NAME, "artdeco-entity-lockup__subtitle")
comp_name = [el.text.strip() for el in company_elements if el.text.strip()]

# Loop to extract about and apply links
about_details = []
apply_links = []
job_cards = browser.find_elements(By.CLASS_NAME, "job-card-container")

for index in range(len(job_cards)):
    try:
        job_cards = browser.find_elements(By.CLASS_NAME, "job-card-container")
        browser.execute_script("arguments[0].scrollIntoView();", job_cards[index])
        time.sleep(0.5)
        job_cards[index].click()

        about_element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "jobs-description__content"))
        )
        about_text = about_element.text.strip().replace("\\n", " ")
        about_details.append(about_text)

        try:
            apply_button = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-apply-button"))
            )
            original_tab = browser.current_window_handle
            apply_button.click()
            time.sleep(2)

            all_tabs = browser.window_handles
            if len(all_tabs) > 1:
                browser.switch_to.window(all_tabs[1])
                apply_url = browser.current_url
                browser.close()
                browser.switch_to.window(original_tab)
            else:
                apply_url = browser.current_url
                try:
                    close_button = WebDriverWait(browser, 5).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "artdeco-modal__dismiss"))
                    )
                    close_button.click()
                except:
                    pass
            apply_links.append(apply_url)
        except:
            apply_links.append("Not found")
    except:
        about_details.append("N/A")
        apply_links.append("N/A")

# Ensure lengths match
min_len = min(len(job_titles), len(comp_name), len(about_details), len(apply_links))

df = pd.DataFrame({
    "Job Title": job_titles[:min_len],
    "Company and Location": comp_name[:min_len],
    "About": about_details[:min_len],
    "Apply Link": apply_links[:min_len]
})

print(tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=True))
df.to_csv("linkedin_scraped_jobs.csv", index=False)
print("✅ Saved to 'linkedin_scraped_jobs.csv'")


