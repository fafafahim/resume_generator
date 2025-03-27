import os
import sys
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import json   # Added json import

def extract_job_info(url):
    # Get Brave Search API key from environment variable
    api_key = os.getenv("BRAVE_SEARCH_API_KEY")
    if not api_key:
        print("Error: BRAVE_SEARCH_API_KEY is not set.")
        sys.exit(1)

    # Use the API key in headers if applicable
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve URL. Status code: {response.status_code}")
        sys.exit(1)

    soup = BeautifulSoup(response.content, "html.parser")

    # Attempt to extract the job title and company.
    # Adjust selectors based on the specific job posting page structure.
    title_tag = soup.find("h1")
    job_title = title_tag.get_text(strip=True) if title_tag else "Not found"

    # Updated company extraction: check for tags with "company" in class or anchor tags containing 'linkedin.com/company' in href
    company_tag = soup.find(lambda tag: (tag.name in ["div", "span"] and "company" in tag.get("class", [])) or (tag.name == "a" and "linkedin.com/company" in tag.get("href", "")))
    company = company_tag.get_text(strip=True) if company_tag else ""
    # Fallback if extraction failed or value is unexpected
    if not company or company.lower() in ["not found", "ot found"]:
        fallback = soup.find(text=lambda t: "Company:" in t)
        if fallback:
            company = fallback.split("Company:")[-1].strip()
    if not company:
         company = "Not found"

    return job_title, company

# Renamed and updated function to append job info to JSON
def append_to_json(job_title, company, url, job_description, filename="/Users/coding/Desktop/localRepos/resume-generator/_submitted/_applied.json"):
    # Ensure the directory exists
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    
    # Load existing JSON data if file exists; otherwise, create new list
    if os.path.isfile(filename):
        with open(filename, "r", encoding="utf-8") as jsonfile:
            try:
                data = json.load(jsonfile)
                if not isinstance(data, list):
                    data = []
            except json.JSONDecodeError:
                data = []
    else:
        data = []
    
    # Prepare the job entry with a timestamp
    job_entry = {
        "job_title": job_title,
        "company": company,
        "url": url,
        "job_description": job_description,
        "timestamp": datetime.now().isoformat(),
        "llm_processed": False,
        "resume": "",
        "cover_letter": "",
        "applied": False,
        "skip": False  
    }
    data.append(job_entry)
    
    with open(filename, "w", encoding="utf-8") as jsonfile:
        json.dump(data, jsonfile, indent=4)
    print(f"Appended job info to {filename}")

def main():
    if len(sys.argv) < 2:
        url = input("Enter the job posting URL: ")
        job_description = input("Enter the Job Description: ")
    else:
        url = sys.argv[1]
        if len(sys.argv) < 3:
            job_description = input("Enter the Job Description: ")
        else:
            job_description = sys.argv[2]
    job_title, company = extract_job_info(url)
    append_to_json(job_title, company, url, job_description)   # Updated function call

if __name__ == "__main__":
    main()