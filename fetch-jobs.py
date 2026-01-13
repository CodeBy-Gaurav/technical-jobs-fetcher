import requests
import os
from datetime import datetime

# JSearch API (RapidAPI)
RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY')
if not RAPIDAPI_KEY:
    print("❌ RAPIDAPI_KEY not found! Add it to GitHub Secrets.")
    exit(1)

url = "https://jsearch.p.rapidapi.com/search"
headers = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
}

# Better query for TECHNICAL WRITING jobs
querystring = {
    "query": '"technical writer" OR "technical writing" OR "documentation" OR "docs engineer" OR "api documentation" remote',
    "num_pages": "1",
    "page": "1",
    "date_posted": "last_7_days"
}

print("🔄 Fetching Technical Writing jobs...")
response = requests.get(url, headers=headers, params=querystring)

if response.status_code != 200:
    print(f"❌ API Error {response.status_code}: {response.text}")
    exit(1)

data = response.json()
jobs = data.get('data', [])
print(f"✅ Found {len(jobs)} jobs")

# Generate Markdown table matching your API structure
table_lines = ["| Company | Job Title | Location | Apply |", "|---------|-----------|----------|-------|"]

if not jobs:
    table_lines.append("| **No jobs found** | Try again later | - | - |")
else:
    for job in jobs[:15]:  # Max 15 like reference repo
        # Extract fields from YOUR exact API response
        company = job.get('employer_name', 'N/A').replace('|', '\\|').replace('\n', ' ')
        title = job.get('job_title', 'N/A').replace('|', '\\|').replace('\n', ' ')
        location = job.get('job_location', 'Remote') or job.get('job_city', 'Remote')
        apply_url = job.get('job_apply_link', '#')
        employer_url = job.get('employer_website', '#')
        
        # Handle Snowflake Developer example perfectly
        if "Snowflake Developer" in title:
            location_display = f"{job.get('job_city', 'N/A')}, {job.get('job_state', 'N/A')}"
        else:
            location_display = location
        
        # Create exact reference repo format
        table_lines.append(f"| **[{company}]({employer_url})** | **[{title}]({apply_url})** | {location_display} | [Apply]({apply_url}) |")

# Read template and replace placeholders
try:
    with open('jobs-template.md', 'r') as f:
        template = f.read()
except FileNotFoundError:
    print("❌ jobs-template.md not found! Create it first.")
    exit(1)

# Update README with live data
updated_readme = template.replace('<!-- JOBS_TABLE -->', '\n'.join(table_lines))
updated_readme = updated_readme.replace('<!-- UPDATE_DATE -->', datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'))

# Write directly to folder README.md
with open('README.md', 'w') as f:
    f.write(updated_readme)

print("✅ technical-writing-jobs/README.md updated with live jobs!")
print(f"📊 Jobs processed: {len(jobs)}")
