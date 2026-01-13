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

# ✅ FIXED: Use valid date_posted values ONLY
querystring = {
    "query": '"technical writer" OR "technical writing" OR documentation OR "docs engineer" OR "api documentation"',
    "num_pages": "1",
    "page": "1",
    "date_posted": "week"  # ✅ FIXED: was "last_7_days" → now "week"
}

print("🔄 Fetching Technical Writing jobs...")
response = requests.get(url, headers=headers, params=querystring)

if response.status_code != 200:
    print(f"❌ API Error {response.status_code}: {response.text}")
    # Don't exit on error - show empty table instead
    jobs = []
else:
    data = response.json()
    jobs = data.get('data', [])
    print(f"✅ Found {len(jobs)} jobs")

# Generate Markdown table (perfect for your API format)
table_lines = ["| Company | Job Title | Location | Apply |", "|---------|-----------|----------|-------|"]

if not jobs:
    table_lines.append("| colspan=4 | **No technical writing jobs found this week** |")
else:
    for job in jobs[:15]:  # Max 15 jobs
        company = job.get('employer_name', 'N/A').replace('|', '\\|').replace('\n', ' ')
        title = job.get('job_title', 'N/A').replace('|', '\\|').replace('\n', ' ')
        location = job.get('job_location', 'Remote') or job.get('job_city', 'Remote') or 'Remote'
        apply_url = job.get('job_apply_link', '#')
        employer_url = job.get('employer_website', '#')
        
        table_lines.append(f"| **[{company}]({employer_url})** | **[{title}]({apply_url})** | {location} | [Apply]({apply_url}) |")

# Read template and replace
try:
    with open('jobs-template.md', 'r') as f:
        template = f.read()
except FileNotFoundError:
    print("⚠️ jobs-template.md not found - using fallback")
    template = """# 🖋️ Technical Writing Jobs\n\n> **Note:** Auto-updates every 6 hours\n> **Last updated:** <!-- UPDATE_DATE -->\n\n<!-- JOBS_TABLE -->\n\n---\n**No jobs found?** Check back later!"""

# Update README
updated_readme = template.replace('<!-- JOBS_TABLE -->', '\n'.join(table_lines))
updated_readme = updated_readme.replace('<!-- UPDATE_DATE -->', datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'))

with open('README.md', 'w') as f:
    f.write(updated_readme)

print("✅ README.md updated successfully!")
print(f"📊 Jobs processed: {len(jobs)}")
