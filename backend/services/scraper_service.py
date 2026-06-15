import time
import random
import urllib.parse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# A realistic User-Agent to avoid immediate bot detection
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def random_delay():
    """Adds a random delay between 2 and 5 seconds to simulate human behavior."""
    time.sleep(random.uniform(2.0, 5.0))

def extract_linkedin_description(page, url: str) -> str:
    """Visits a specific LinkedIn job URL and extracts the full description."""
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        random_delay()
        
        try:
            # Wait for the description container to appear
            page.wait_for_selector(".show-more-less-html__markup", timeout=5000)
        except PlaywrightTimeoutError:
            pass # It might already be loaded or the selector might be different
            
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        desc_div = soup.find("div", class_="show-more-less-html__markup")
        if desc_div:
            return desc_div.get_text(separator="\n", strip=True)
    except Exception as e:
        print(f"Error extracting LinkedIn desc for {url}: {e}")
    return ""

def extract_indeed_description(page, url: str) -> str:
    """Visits a specific Indeed job URL and extracts the full description."""
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        random_delay()
        
        try:
            # Wait for the description container
            page.wait_for_selector("#jobDescriptionText", timeout=5000)
        except PlaywrightTimeoutError:
            pass
            
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        desc_div = soup.find("div", id="jobDescriptionText")
        if desc_div:
            return desc_div.get_text(separator="\n", strip=True)
    except Exception as e:
        print(f"Error extracting Indeed desc for {url}: {e}")
    return ""

def scrape_linkedin(page, keyword: str, location: str, max_results: int) -> list:
    """Scrapes job listings from LinkedIn Jobs."""
    jobs = []
    query = urllib.parse.quote(keyword)
    loc = urllib.parse.quote(location)
    # Using the public job search URL (no login required)
    search_url = f"https://www.linkedin.com/jobs/search?keywords={query}&location={loc}&f_TPR=r2592000"
    
    try:
        page.goto(search_url, wait_until="domcontentloaded", timeout=20000)
        random_delay()
        
        try:
            page.wait_for_selector(".base-card", timeout=10000)
        except PlaywrightTimeoutError:
            print("No LinkedIn jobs found or blocked by anti-bot.")
            return jobs
            
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        job_cards = soup.find_all("div", class_="base-card")
        basic_jobs = []
        
        for card in job_cards[:max_results]:
            title_el = card.find("h3", class_="base-search-card__title")
            company_el = card.find("h4", class_="base-search-card__subtitle")
            location_el = card.find("span", class_="job-search-card__location")
            date_el = card.find("time")
            link_el = card.find("a", class_="base-card__full-link")
            
            if not title_el or not link_el:
                continue
                
            job_url = link_el.get("href", "").split("?")[0]
            
            basic_jobs.append({
                "title": title_el.get_text(strip=True),
                "company": company_el.get_text(strip=True) if company_el else "Unknown",
                "location": location_el.get_text(strip=True) if location_el else "Unknown",
                "job_type": "Not specified",
                "url": job_url,
                "source": "LinkedIn",
                "posted_date": date_el.get_text(strip=True) if date_el else "Unknown"
            })
            
        # Visit each individual URL to get the full description
        for job in basic_jobs:
            desc = extract_linkedin_description(page, job["url"])
            job["description"] = desc if desc else "Description not available."
            jobs.append(job)
            
    except Exception as e:
        print(f"LinkedIn scraping error: {e}")
        
    return jobs

def scrape_indeed(page, keyword: str, location: str, max_results: int) -> list:
    """Scrapes job listings from Indeed India."""
    jobs = []
    query = urllib.parse.quote(keyword)
    loc = urllib.parse.quote(location)
    search_url = f"https://in.indeed.com/jobs?q={query}&l={loc}"
    
    try:
        page.goto(search_url, wait_until="domcontentloaded", timeout=20000)
        random_delay()
        
        try:
            page.wait_for_selector(".job_seen_beacon", timeout=10000)
        except PlaywrightTimeoutError:
            print("No Indeed jobs found or blocked by Captcha.")
            return jobs
            
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        
        job_cards = soup.find_all("div", class_="job_seen_beacon")
        basic_jobs = []
        
        for card in job_cards[:max_results]:
            title_el = card.find("h2", class_="jobTitle")
            company_el = card.find("span", {"data-testid": "company-name"})
            location_el = card.find("div", {"data-testid": "text-location"})
            link_el = title_el.find("a") if title_el else None
            
            if not title_el or not link_el:
                continue
                
            job_url = link_el.get("href", "")
            if job_url.startswith("/"):
                job_url = "https://in.indeed.com" + job_url
                
            # Ensure we get the clean viewjob URL using the job key (jk)
            parsed_url = urllib.parse.urlparse(job_url)
            qs = urllib.parse.parse_qs(parsed_url.query)
            if 'jk' in qs:
                job_url = f"https://in.indeed.com/viewjob?jk={qs['jk'][0]}"
            else:
                job_url = job_url.split("?")[0]
            
            basic_jobs.append({
                "title": title_el.get_text(strip=True),
                "company": company_el.get_text(strip=True) if company_el else "Unknown",
                "location": location_el.get_text(strip=True) if location_el else "Unknown",
                "job_type": "Not specified",
                "url": job_url,
                "source": "Indeed",
                "posted_date": "Unknown" # Harder to extract without visiting the page
            })
            
        # Visit each individual URL to get the full description
        for job in basic_jobs:
            desc = extract_indeed_description(page, job["url"])
            job["description"] = desc if desc else "Description not available."
            jobs.append(job)
            
    except Exception as e:
        print(f"Indeed scraping error: {e}")
        
    return jobs

def scrape_jobs(keyword: str, location: str = "India", max_results: int = 30) -> list:
    """
    Main function to scrape jobs from multiple sources.
    Designed to run in a background task.
    """
    all_jobs = []
    
    # Split the max_results quota among sources
    max_per_source = max(1, max_results // 2)
    
    # Start synchronous Playwright instance
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # Configure context to mimic a real desktop browser
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        print(f"Starting LinkedIn scrape for '{keyword}' in '{location}'...")
        linkedin_jobs = scrape_linkedin(page, keyword, location, max_per_source)
        all_jobs.extend(linkedin_jobs)
        
        print(f"Starting Indeed scrape for '{keyword}' in '{location}'...")
        indeed_jobs = scrape_indeed(page, keyword, location, max_per_source)
        all_jobs.extend(indeed_jobs)
        
        browser.close()
        
    # Ensure we don't return more than requested
    return all_jobs[:max_results]

# For testing locally if this script is executed directly
if __name__ == "__main__":
    test_jobs = scrape_jobs("Financial Analyst", "Bangalore", max_results=4)
    for i, job in enumerate(test_jobs):
        print(f"\n--- Job {i+1} ---")
        print(f"Title: {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Location: {job['location']}")
        print(f"Source: {job['source']}")
        print(f"URL: {job['url']}")
        print(f"Desc Preview: {job['description'][:100]}...")