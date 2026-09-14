# Job Sources Configuration

## Overview

The AI Job Matching System includes a job collector that fetches jobs from Ethiopian job boards and international platforms. The system is specifically optimized for the Ethiopian job market.

## Ethiopian Job Sources

### 1. Ethiojobs (Source1)

### Description
Ethiopia's leading job board with thousands of local and international job postings.

### Website
https://www.ethiojobs.com

### Features
- **Industry Coverage**: IT, Banking, Telecom, Manufacturing, Agriculture, Tourism
- **Salary Range**: Jobs listed in Ethiopian Birr (ETB)
- **Location Focus**: Addis Ababa and major Ethiopian cities
- **Skill Extraction**: Optimized for Ethiopian job market skills
- **Languages**: Amharic, English, Oromiffa job postings

### Configuration
No API credentials required - uses web scraping with BeautifulSoup.

### Job Categories
- Software Development
- Accounting & Finance
- Engineering
- Marketing & Sales
- Human Resources
- Banking & Insurance
- Telecom & Technology

### 2. HaHuJobs (Source2)

### Description
Popular Ethiopian job platform with focus on Ethiopian companies and positions.

### Website
https://hahujobs.com

### Features
- **Local Focus**: Primarily Ethiopian companies
- **Career Resources**: CV tips, interview preparation
- **Company Profiles**: Detailed company information
- **Salary Information**: Transparent salary ranges in ETB

### Configuration
No API credentials required - uses web scraping.

### Job Categories
- Business Development
- Graphic Design
- Customer Service
- Administration
- Teaching & Education
- Healthcare

### 3. Reporter Jobs Gazette (Source3)

### Description
Job section from Reporter Ethiopia, one of Ethiopia's leading media outlets.

### Website
https://reporterethiopia.com/jobs

### Features
- **Media Industry Jobs**: Journalism, editing, content creation
- **Corporate Jobs**: From major Ethiopian corporations
- **Government Jobs**: Public sector positions
- **NGO Jobs**: International organization positions in Ethiopia

### Configuration
No API credentials required - uses web scraping.

### Job Categories
- Journalism & Media
- Public Relations
- Corporate Communications
- Digital Marketing
- Content Creation

### 4. Afriwork (Source4)

### Description
Pan-African job platform with significant Ethiopian job listings.

### Website
https://www.afriwork.com/jobs/ethiopia

### Features
- **African Focus**: Jobs across African countries
- **Ethiopia Section**: Dedicated Ethiopian job category
- **International Companies**: Multinational corporations operating in Ethiopia
- **Remote Opportunities**: Remote work for Ethiopian professionals

### Configuration
No API credentials required - uses web scraping.

### Job Categories
- Project Management
- Engineering
- IT & Technology
- Agriculture
- Tourism & Hospitality
- Logistics & Supply Chain

## Additional Ethiopian Job Sources

The system can be extended to include more Ethiopian job platforms:

### Popular Ethiopian Job Boards
- **Srafelagi** - Construction and engineering jobs
- **SemayJobs** - Various industry positions
- **Enjera** - Technology and startup jobs
- **Shega Jobs** - Professional services
- **EthiopiaWork** - General job listings
- **GeezJobs** - Language and translation jobs
- **Reporter Jobs** - Media and journalism
- **Ethiopian Reporter Jobs** - Corporate communications
- **Addis Zemen Jobs** - Addis Ababa focused
- **ET Careers** - Career development positions
- **Ezega Jobs** - Entry to mid-level positions
- **Harmee Jobs** - Various industries
- **AddisJobs** - Addis Ababa jobs
- **Shola Jobs** - Shola area positions
- **Elelanajobs** - Technology jobs
- **EffoyJobs** - Customer service
- **JobWeb Ethiopia** - Web-based job board
- **JustJobSet** - IT and tech jobs
- **Palm Jobs** - Hospitality
- **Dereja** - General listings
- **Hawassa Job Board** - Regional jobs

### International Sources with Ethiopian Jobs
- **LinkedIn Jobs** - Filter for Ethiopia
- **Indeed** - Ethiopia job search
- **Google Jobs** - Ethiopian job listings
- **UN Careers** - UN positions in Ethiopia
- **UNDP Careers** - UNDP Ethiopia jobs
- **ReliefWeb Jobs** - NGO jobs in Ethiopia
- **DevNetJobs** - Development jobs
- **Impactpool** - Impact jobs in Ethiopia

### Social Media Sources
- **Telegram Ethiopian Job Channels** - Telegram job groups
- **Facebook Ethiopian Job Groups** - Facebook job communities
- **Company Career Pages** - Ethiopian company websites
- **NGO Career Portals** - NGO websites with Ethiopia offices

## Ethiopian Job Market Features

### Salary Information
Jobs are listed in Ethiopian Birr (ETB):
- **Entry Level**: 8,000 - 15,000 ETB/month
- **Mid Level**: 15,000 - 30,000 ETB/month
- **Senior Level**: 30,000 - 60,000 ETB/month
- **Executive**: 60,000+ ETB/month

### Language Requirements
Most Ethiopian jobs require:
- **Amharic** - Native language proficiency
- **English** - Business language proficiency
- **Oromiffa/Tigrinya** - Regional language preferences

### Popular Skills in Ethiopian Market
- **Technical**: Python, Java, JavaScript, Excel, SAP
- **Business**: Accounting, Finance, Marketing, Sales
- **Languages**: Amharic, English, Arabic
- **Industry**: Banking, Telecom, Construction, Agriculture

### Location Distribution
- **Addis Ababa**: 60% of jobs
- **Regional Cities**: 30% of jobs
- **Remote**: 10% of jobs

## Running the Job Collector

### Collect Ethiopian Jobs
```bash
cd job-collector
python main.py
```

### Continuous Collection
Edit `job-collector/main.py` to enable scheduler:
```python
if __name__ == "__main__":
    collector = JobCollector()
    
    # Run continuously
    schedule.every(1).hours.do(collector.run_once)
    while True:
        schedule.run_pending()
        time.sleep(60)
```

## Data Processing for Ethiopian Jobs

### Job Cleaning
- **Text Normalization**: Handle Amharic characters
- **Location Standardization**: Ethiopian city names
- **Salary Conversion**: ETB to standardized format
- **Skill Extraction**: Ethiopian market-specific skills

### Duplicate Detection
- **Job Signature**: Based on title, company, location
- **URL Deduplication**: Source URL matching
- **Content Similarity**: Description comparison

## Adding More Ethiopian Sources

### Web Scraping Template
To add a new Ethiopian job source:

1. Create `job-collector/sources/source5.py`:
```python
"""
Source 5 - Your Ethiopian Job Board
"""
import requests
from typing import List, Dict
import time
import re
from bs4 import BeautifulSoup

class Source5:
    def __init__(self):
        self.name = "YourEthiopianSource"
        self.base_url = "https://ethiopian-job-board.com"
    
    def fetch_jobs(self) -> List[Dict]:
        """Fetch jobs from Ethiopian source"""
        jobs = []
        
        try:
            response = requests.get(f"{self.base_url}/jobs", timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse job listings based on the site's HTML structure
            job_listings = soup.find_all('div', class_='job-item')
            
            for listing in job_listings:
                job = self._parse_job(listing)
                if job:
                    jobs.append(job)
                    
        except Exception as e:
            print(f"Error: {e}")
            return self._get_sample_jobs()
        
        time.sleep(2)
        return jobs
    
    def _parse_job(self, listing) -> Dict:
        """Parse individual job listing"""
        # Extract job details
        title = listing.find('h3').get_text(strip=True)
        company = listing.find('span', class_='company').get_text(strip=True)
        # ... more parsing
        
        return {
            "title": title,
            "company": company,
            "description": description,
            "skills": self._extract_ethiopian_skills(description),
            "location": "Ethiopia",
            "salary_min": salary,
            "salary_max": salary * 1.5,
            "job_type": "full-time",
            "source": self.name,
            "source_url": job_url,
        }
    
    def _extract_ethiopian_skills(self, text: str) -> str:
        """Extract Ethiopian market-specific skills"""
        skills = ["python", "java", "amharic", "english", "accounting"]
        found = [skill for skill in skills if skill.lower() in text.lower()]
        return ",".join(found)
    
    def _get_sample_jobs(self) -> List[Dict]:
        """Fallback sample jobs"""
        return [{"title": "Sample Job", "company": "Sample Company", ...}]
```

2. Add to `job-collector/main.py`:
```python
from sources.source5 import Source5

self.sources = [
    Source1(),  # Ethiojobs
    Source2(),  # HaHuJobs
    Source3(),  # Reporter Jobs
    Source4(),  # Afriwork
    Source5()   # Your new source
]
```

## Ethiopian Job Market Insights

### Current Trends
- **Digital Jobs**: Growing demand for IT and digital skills
- **Remote Work**: Increasing remote opportunities
- **Startup Ecosystem**: Growing startup job market
- **Government Jobs**: Stable public sector employment
- **NGO Jobs**: Strong international NGO presence

### Industry Growth
- **Technology**: Fastest growing sector
- **Banking**: Stable employment
- **Construction**: Infrastructure development
- **Agriculture**: Modernization creating new opportunities
- **Tourism**: Post-pandemic recovery

### Skill Demand
- **Digital Skills**: High demand
- **Language Skills**: Amharic + English essential
- **Technical Skills**: Programming, data analysis
- **Soft Skills**: Communication, problem-solving

## Troubleshooting

### Common Issues

**Website structure changed:**
- Ethiopian job boards frequently update their HTML structure
- Update CSS selectors in source files
- Test individual sources before full deployment

**Encoding issues with Amharic:**
- Ensure UTF-8 encoding is handled
- Use proper character encoding in requests
- Test with Amharic job titles

**Rate limiting:**
- Ethiopian sites may have strict rate limits
- Use appropriate delays between requests
- Consider caching strategies

**Salary parsing:**
- Ethiopian salary formats vary
- ETB vs Birr vs just numbers
- Monthly vs annual salaries

## Best Practices for Ethiopian Job Collection

1. **Respect robots.txt** from Ethiopian websites
2. **Use appropriate delays** between requests
3. **Handle Amharic characters** properly
4. **Parse ETB salaries** correctly
5. **Filter for Ethiopia** on international platforms
6. **Validate job locations** as Ethiopian cities
7. **Test during Ethiopian business hours** for best results
8. **Monitor website changes** in Ethiopian job boards

## Future Enhancements

Planned for Ethiopian job collection:
- Add more Ethiopian job boards (20+ sources)
- Implement Telegram channel scraping
- Add Facebook job group monitoring
- Company career page integration
- Amharic language processing
- Ethiopian city location validation
- Regional job distribution analysis
- Salary trend analysis for Ethiopian market
- Integration with Ethiopian government job portals
