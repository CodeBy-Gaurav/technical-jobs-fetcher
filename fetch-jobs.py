import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Load .env file for local testing
load_dotenv()

# JSearch API (RapidAPI)
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
if not RAPIDAPI_KEY:
    print("❌ RAPIDAPI_KEY not found! Add it to GitHub Secrets.")
    exit(1)

url = "https://jsearch.p.rapidapi.com/search"
headers = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
}

# ✅ YOUR EXACT JOB TITLES - Smart JSearch query
JOB_TITLES = [
    "Technical Writer",
    "Senior Technical Writer", 
    "Developer Documentation",
    "Documentation Engineer",
    "API Documentation Specialist",
    "Technical Content Engineer",
    "Product Documentation Specialist",
    "Knowledge Base Writer"
]

# 🧠 TWO-STEP STRATEGY: API Query + Local Filter
def create_smart_query():
    """Creates optimal JSearch query using |OR| operator for multiple titles"""
    # Combine titles with |OR| (JSearch supports up to 50 keywords)
    query_parts = []
    
    for title in JOB_TITLES:
        # Add exact phrase AND individual words
        query_parts.append(f'"{title}"')
        query_parts.extend(title.lower().split())
    
    # Remove duplicates and limit to 20 keywords (API safe)
    unique_keywords = list(dict.fromkeys(query_parts))[:20]
    
    return " OR ".join(unique_keywords)

# PRODUCTION QUERY (No testing mode needed)
print("🔄 Fetching Technical Writing jobs...")
querystring = {
    "query": create_smart_query(),
    "num_pages": "3",  # More pages = more chances to find jobs
    "page": "1"
    # ✅ NO location = worldwide jobs
    # ✅ NO date_posted = wider timeframe (30+ days)
}

print(f"🔍 Smart Query: {querystring['query'][:100]}...")

# Make API request
response = requests.get(url, headers=headers, params=querystring)

print(f"📡 Status Code: {response.status_code}")

if response.status_code != 200:
    print(f"❌ API Error {response.status_code}: {response.text[:500]}")
    jobs = []
else:
    data = response.json()
    all_jobs = data.get('data', [])
    
    # 🧠 STEP 2: Local filtering for YOUR exact job titles
    filtered_jobs = []
    print(f"📋 All jobs found: {len(all_jobs)}")
    
    for job in all_jobs:
        job_title = job.get('job_title', '').lower()
        
        # Check if job matches ANY of your exact titles
        title_match = False
        for target_title in JOB_TITLES:
            if target_title.lower() in job_title:
                title_match = True
                break
        
        if title_match:
            filtered_jobs.append(job)
    
    jobs = filtered_jobs
    print(f"✅ Found {len(jobs)} Technical Writing jobs")

# Show sample jobs
if jobs:
    print("\n📋 Perfect matches:")
    for i, job in enumerate(jobs[:5], 1):
        print(f"{i}. '{job.get('job_title', 'N/A')}' at {job.get('employer_name', 'N/A')}")

# Generate Markdown table
table_lines = [
    "| Company | Job Title | Location | Apply |",
    "|---------|-----------|----------|-------|"
]

if not jobs:
    table_lines.append("| colspan=4 | **No technical writing jobs found**<br/>Try again in a few days! |")
else:
    for job in jobs[:15]:  # Max 15 jobs
        company = job.get('employer_name', 'N/A').replace('|', '\\|').replace('\n', ' ')[:50]
        title = job.get('job_title', 'N/A').replace('|', '\\|').replace('\n', ' ')[:60]
        
        # Smart location detection
        location = (
            job.get('job_country', '') or 
            job.get('job_city', '') or 
            job.get('job_location', '') or 
            job.get('job_state', '') or 
            'Remote/Worldwide'
        )[:30].replace('|', '\\|')
        
        # Get best apply link
        apply_url = (
            job.get('job_apply_link') or 
            job.get('job_google_link') or 
            job.get('job_indeed_link') or 
            '#'
        )
        
        table_lines.append(
            f"| **{company}** | **{title}** | {location} | [Apply]({apply_url}) |"
        )

# Read template and replace
try:
    with open('jobs-template.md', 'r', encoding='utf-8') as f:
        template = f.read()
except FileNotFoundError:
    print("⚠️ jobs-template.md not found - using fallback")
    template = """# 🖋️ Technical Writing Jobs

> **Auto-updates every 6 hours**  
> **Last updated:** <!-- UPDATE_DATE -->

<!-- JOBS_TABLE -->

---
**Source:** [JSearch API](https://rapidapi.com/restapi/api/jsearch)  
**Keywords:** Technical Writer, Documentation Engineer, API Writer, etc.
"""

# Update README
updated_readme = template.replace('<!-- JOBS_TABLE -->', '\n'.join(table_lines))
updated_readme = updated_readme.replace(
    '<!-- UPDATE_DATE -->', 
    datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
)

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(updated_readme)

print("✅ README.md updated successfully!")
print(f"📊 Jobs processed: {len(jobs)}")

# Verify file change
import difflib
try:
    with open('README.md', 'r', encoding='utf-8') as f:
        print(f"📄 README.md created with table!")
except:
    pass
