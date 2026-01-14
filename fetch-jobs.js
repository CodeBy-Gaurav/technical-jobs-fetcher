const fs = require('fs').promises;
const https = require('https');

// ✅ BUILT-IN JOB SOURCES (always have listings)
const JOB_BOARDS = [
  {
    name: "RemoteOK", 
    url: "https://remoteok.com/api",
    type: "api"
  },
  {
    name: "GitLab", 
    url: "https://jobs.gitlab.com/jobs",
    type: "html"
  },
  {
    name: "Postman", 
    url: "https://boards-api.greenhouse.io/v1/boards/postman/jobs",
    type: "api"
  },
  {
    name: "Twilio", 
    url: "https://boards-api.greenhouse.io/v1/boards/twilio/jobs", 
    type: "api"
  },
  {
    name: "MongoDB",
    url: "https://boards-api.greenhouse.io/v1/boards/mongodb/jobs",
    type: "api"
  }
];

const KEYWORDS = [
  'writer', 'writing', 'documentation', 'docs', 'technical',
  'content', 'advocate', 'developer', 'staff', 'knowledge'
];

async function fetchPage(url) {
  return new Promise((resolve, reject) => {
    https.get(url, {timeout: 8000}, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    }).on('error', () => resolve(''));
  });
}

function findJobs(data, source) {
  const jobs = [];
  
  try {
    const json = JSON.parse(data);
    const jobList = Array.isArray(json) ? json : 
                   (json.jobs || json.data || json.postings || json.job_postings || []);
    
    jobList.forEach(job => {
      const title = (job.position || job.title || job.name || '').toLowerCase();
      
      // ✅ BETTER KEYWORDS - actual technical writing roles
      const writingKeywords = [
        'writer', 'writing', 'documentation', 'docs', 'technical writer',
        'content', 'documentation engineer', 'technical content',
        'developer advocate', 'technical evangelist', 'staff writer',
        'knowledge', 'developer relations', 'technical marketing'
      ];
      
      if (writingKeywords.some(kw => title.includes(kw))) {
        // ✅ FIXED LOCATION HANDLING
        let location = 'Remote';
        if (job.location) {
          if (typeof job.location === 'string') {
            location = job.location;
          } else if (typeof job.location === 'object') {
            location = job.location.city || job.location.name || 'Remote';
            if (job.location.country) location += `, ${job.location.country}`;
          }
        }
        
        jobs.push({
          title: job.position || job.title || job.name,
          company: source.name,
          location: location,
          url: job.apply_url || job.absolute_url || job.url || source.url,
          source: job.url || source.url
        });
      }
    });
  } catch(e) {
    console.log(`⚠️ JSON parse failed for ${source.name}`);
  }
  
  return jobs.slice(0, 8); // Limit per source
}


async function fetchAllJobs() {
  console.log('🔍 Scanning job boards...\n');
  const allJobs = [];

  for (const source of JOB_BOARDS) {
    console.log(`📡 ${source.name}`);
    
    const data = await fetchPage(source.url);
    const jobs = findJobs(data, source);
    
    allJobs.push(...jobs);
    console.log(`   ✅ ${jobs.length} matches`);
    
    await new Promise(r => setTimeout(r, 500));
  }

  return allJobs;
}

function dedupe(jobs) {
  const seen = new Set();
  return jobs.filter(job => {
    const key = `${job.title}-${job.company}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

async function updateReadme(jobs) {
  if (!jobs.length) {
    console.log('⚠️ No real writing jobs found');
    return;
  }

  // Dedupe first
  const uniqueJobs = dedupe(jobs);
  
  const tableHeader = `| Company | Job Title | Location | Apply |
|---------|-----------|----------|--------|`;

  const tableRows = uniqueJobs.slice(0, 12).map(job => 
    `| **${job.company}** | **[${job.title}](${job.url})** | ${job.location || 'Remote'} | [ Apply](${job.apply_url || job.url}) |`
  ).join('\n');

  const table = `${tableHeader}\n| --- | --- | --- | --- |\n${tableRows}`;

  const content = `<!-- JOBS-START -->
#  **Live Technical Writing Jobs** (${uniqueJobs.length} found)

${table}

**Sources:** RemoteOK, Postman, Twilio, GitLab  
*Updated: ${new Date().toLocaleString('en-US', {timeZone: 'UTC'})} UTC*  
<!-- JOBS-END -->`;

  let readme = await fs.readFile('README.md', 'utf8');
  const updatedReadme = readme.replace(
    /<!--\s*JOBS-START\s*-->[\s\S]*?<!--\s*JOBS-END\s*-->/i, 
    content
  );
  
  await fs.writeFile('README.md', updatedReadme, 'utf8');
  
  console.log(`✅ TABLE FIXED: ${uniqueJobs.length} CLEAN jobs written`);
  console.log('📋 Sample:', uniqueJobs.slice(0, 2).map(j => `${j.company}: ${j.title} (${j.location})`).join('\n'));
}

async function main() {
  console.log('🖋️ Technical Writing Jobs\n');
  
  const jobs = await fetchAllJobs();
  console.log(`\n📊 TOTAL: ${jobs.length} results!`);
  
  if (jobs.length) {
    console.log('\n🎯 Matches:');
    jobs.slice(0, 5).forEach((job, i) => {
      console.log(`${i+1}. ${job.title} @ ${job.company}`);
    });
  }
  
  await updateReadme(jobs);
}

main();
