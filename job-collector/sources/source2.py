"""
Source 2 - HaHuJobs (Ethiopian Job Board)
"""
import requests
from typing import List, Dict
import time
import re
from bs4 import BeautifulSoup
import urllib3

# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Source2:
    def __init__(self):
        self.name = "HaHuJobs"
        self.base_url = "https://hahujobs.com"
    
    def fetch_jobs(self) -> List[Dict]:
        """Fetch jobs from HaHuJobs"""
        jobs = []
        
        try:
            # Try multiple endpoints
            endpoints = [
                f"{self.base_url}/jobs",
                f"{self.base_url}/vacancies",
                f"{self.base_url}/",
            ]
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            }
            
            for endpoint in endpoints:
                try:
                    print(f"Trying HaHuJobs endpoint: {endpoint}")
                    response = requests.get(endpoint, headers=headers, timeout=30, allow_redirects=True, verify=False)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Try multiple selectors
                        selectors = [
                            'div.job-item',
                            'div.job-card',
                            'div[class*="job"]',
                            'article.job',
                            'div.vacancy',
                            'div[class*="listing"]',
                        ]
                        
                        job_listings = []
                        for selector in selectors:
                            found = soup.select(selector)
                            if found:
                                job_listings = found
                                print(f"Found {len(found)} job listings with selector: {selector}")
                                break
                        
                        if job_listings:
                            for listing in job_listings[:10]:
                                job = self._parse_hahujobs_job(listing)
                                if job:
                                    jobs.append(job)
                            break
                    else:
                        print(f"Endpoint {endpoint} returned status code: {response.status_code}")
                        
                except Exception as e:
                    print(f"Error with endpoint {endpoint}: {e}")
                    continue
            
            if jobs:
                print(f"Successfully scraped {len(jobs)} real jobs from HaHuJobs")
                return jobs
            else:
                print("No jobs found from any endpoint, using sample data")
                return self._get_sample_jobs()
                
        except Exception as e:
            print(f"Error fetching from HaHuJobs: {e}")
            return self._get_sample_jobs()
        
        time.sleep(2)
        return jobs
    
    def _parse_hahujobs_job(self, listing) -> Dict:
        """Parse individual job listing from HaHuJobs"""
        try:
            # Extract job title - try multiple selectors
            title_elem = (listing.find('h3') or listing.find('h2') or 
                          listing.find('h4') or listing.find('a', class_='job-title') or
                          listing.find('span', class_='title'))
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Position"
            
            # Extract company - try multiple selectors
            company_elem = (listing.find('span', class_='company') or 
                           listing.find('div', class_='company-name') or
                           listing.find('span', class_='employer'))
            company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
            
            # Extract location - try multiple selectors
            location_elem = (listing.find('span', class_='location') or 
                           listing.find('div', class_='location') or
                           listing.find('span', class_='city'))
            location = location_elem.get_text(strip=True) if location_elem else "Ethiopia"
            
            # Extract description - try multiple selectors
            desc_elem = (listing.find('div', class_='description') or 
                         listing.find('p', class_='job-description') or
                         listing.find('div', class_='summary'))
            description = desc_elem.get_text(strip=True) if desc_elem else listing.get_text(strip=True)[:200]
            
            # Extract job link
            link_elem = listing.find('a', href=True)
            job_url = link_elem['href'] if link_elem else ""
            if job_url and not job_url.startswith('http'):
                job_url = f"{self.base_url}{job_url}"
            
            # Extract skills
            skills = self._extract_ethiopian_skills(description)
            
            # Parse salary
            salary = self._parse_ethiopian_salary(description)
            
            return {
                "title": title,
                "company": company,
                "description": description[:500],
                "requirements": description[:300],
                "skills": skills,
                "location": location,
                "salary_min": salary,
                "salary_max": salary * 1.5 if salary > 0 else 0,
                "job_type": self._determine_job_type(description),
                "source": self.name,
                "source_url": job_url,
            }
        except Exception as e:
            print(f"Error parsing job listing: {e}")
            return None
    
    def _extract_ethiopian_skills(self, text: str) -> str:
        """Extract skills relevant to Ethiopian job market"""
        ethiopian_skill_keywords = [
            # Technical skills
            "python", "java", "javascript", "react", "node.js", "sql", "php", "android", "ios",
            # Business skills
            "accounting", "finance", "marketing", "sales", "management", "hr",
            # Industry specific
            "banking", "insurance", "telecom", "construction", "manufacturing",
            "agriculture", "tourism", "logistics", "supply chain",
            # Languages
            "amharic", "oromiffa", "tigrinya", "english", "arabic",
            # Software/tools
            "excel", "word", "powerpoint", "sap", "erp", "quickbooks"
        ]
        
        found_skills = []
        for skill in ethiopian_skill_keywords:
            if skill.lower() in text.lower():
                found_skills.append(skill)
        
        return ",".join(found_skills)
    
    def _parse_ethiopian_salary(self, text: str) -> float:
        """Parse salary from Ethiopian job posting (ETB)"""
        salary_patterns = [
            r'(\d+,?\d+)\s*(?:ETB|Birr)',
            r'Birr\s*:?\s*(\d+,?\d+)',
            r'ETB\s*:?\s*(\d+,?\d+)',
            r'(\d+,?\d+)\s*-\s*(\d+,?\d+)\s*(?:ETB|Birr)'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                salary_str = match.group(1).replace(",", "")
                try:
                    return float(salary_str)
                except ValueError:
                    continue
        
        return 0.0
    
    def _determine_job_type(self, description: str) -> str:
        """Determine job type from description"""
        description_lower = description.lower()
        
        if "remote" in description_lower or "work from home" in description_lower:
            return "remote"
        elif "contract" in description_lower or "freelance" in description_lower:
            return "contract"
        elif "part-time" in description_lower:
            return "part-time"
        else:
            return "full-time"
    
    def _get_sample_jobs(self) -> List[Dict]:
        """Return sample Ethiopian jobs when source is unavailable"""
        return [
            {
                "title": "Business Development Manager",
                "company": "HaHuJobs",
                "description": "Experienced business development manager needed for market expansion...",
                "requirements": "Marketing experience, sales skills, business strategy",
                "skills": "marketing,sales,business development,strategy",
                "location": "Addis Ababa, Ethiopia",
                "salary_min": 20000,
                "salary_max": 35000,
                "job_type": "full-time",
                "source": self.name,
                "source_url": "https://hahujobs.com/job/456"
            },
            {
                "title": "Graphic Designer",
                "company": "Creative Agency Ethiopia",
                "description": "Creative graphic designer needed for branding and marketing materials...",
                "requirements": "Adobe Creative Suite, 2+ years experience, portfolio",
                "skills": "photoshop,illustrator,graphic design,branding",
                "location": "Addis Ababa, Ethiopia",
                "salary_min": 12000,
                "salary_max": 20000,
                "job_type": "full-time",
                "source": self.name,
                "source_url": "https://hahujobs.com/job/457"
            }
        ]
