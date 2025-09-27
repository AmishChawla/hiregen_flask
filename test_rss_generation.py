#!/usr/bin/env python3
"""
Test script to demonstrate RSS feed generation from job data
"""

import xml.etree.ElementTree as ET
from datetime import datetime
import re

# Your sample job data
sample_jobs = [
    {
        'user_id': 137, 'job_type': 'Contract', 'salary': None, 
        'job_benefits': '<p>1. Opportunity to work on exciting entertainment projects</p><p>2. Flexible work hours</p><p>3. Competitive compensation</p><p>4. Chance to collaborate with talented professionals</p><p>5. Room for growth and development</p>', 
        'updated_at': '2025-07-24T10:32:04.303207+00:00', 'company_id': 42, 'job_skills': '', 
        'address_city': 'Navi Mumbai', 'working_style': 'Hybrid', 'company_subdomain': 'companyninetynine', 
        'work_experience': 'Mid-Level', 'address_country': 'India', 'job_opening_status': 'Active', 
        'author_name': 'User Testing', 'industry': 'Entertainment', 'address_province': 'Maharashtra', 
        'status': 'published', 'job_title': 'Writer', 'min_salary': 500000.0, 'address_postal_code': '400706', 
        'slug': 'writer-1', 'target_date': '2025-09-22T00:00:00+00:00', 'max_salary': 1000000.0, 
        'job_description': '<p>We are looking for a talented Writer to join our team in the Entertainment industry. As a mid-level Writer, you will be responsible for creating engaging and compelling content for various projects. This is a contract position that offers an exciting opportunity to showcase your writing skills.</p>', 
        'job_opening_views': 63, 'opening_date': '2025-07-24T00:00:00+00:00', 'salary_currency': '₹', 
        'job_requirements': "<p>1. Proven experience as a Writer in the Entertainment industry</p><p>2. Strong writing and editing skills</p><p>3. Ability to meet deadlines and work independently</p><p>4. Creative mindset and attention to detail</p><p>5. Excellent communication skills</p><p>6. Bachelor's degree in English, Journalism, or related field preferred</p>", 
        'id': 74, 'salary_time_unit': 'Yearly', 'created_at': '2025-07-24T10:32:10.386105+00:00'
    },
    {
        'user_id': 137, 'job_type': 'Full Time', 'salary': None, 
        'job_benefits': "<p>1. Competitive salary</p><p>2. Full-time position with benefits</p><p>3. Opportunities for professional development</p><p>4. Collaborative and supportive work environment</p><p>5. Chance to make a positive impact on patients' lives</p>", 
        'updated_at': '2025-07-25T05:34:32.916945+00:00', 'company_id': 42, 'job_skills': '', 
        'address_city': 'New Delhi', 'working_style': 'On-Site', 'company_subdomain': 'companyninetynine', 
        'work_experience': 'Mid-Level', 'address_country': 'India', 'job_opening_status': 'Active', 
        'author_name': 'User Testing', 'industry': 'Hospital & Health Care', 'address_province': 'Delhi', 
        'status': 'published', 'job_title': 'Doctor', 'min_salary': None, 'address_postal_code': '110088', 
        'slug': 'doctor-1', 'target_date': '2025-09-23T00:00:00+00:00', 'max_salary': None, 
        'job_description': '<p>We are seeking a dedicated and experienced Doctor to join our team in the Hospital &amp; Health Care industry. As a Mid-Level Doctor, you will be responsible for providing high-quality medical care to patients, diagnosing illnesses, prescribing treatments, and monitoring patient progress. The ideal candidate will have excellent communication skills, a strong work ethic, and a passion for helping others.</p>', 
        'job_opening_views': 54, 'opening_date': '2025-07-25T00:00:00+00:00', 'salary_currency': 'USD', 
        'job_requirements': '<p>1. Medical degree from an accredited institution</p><p>2. Valid medical license</p><p>3. Mid-level work experience in a hospital or clinic</p><p>4. Strong diagnostic and decision-making skills</p><p>5. Excellent communication and interpersonal skills</p><p>6. Ability to work in a fast-paced environment</p><p>7. Commitment to providing compassionate patient care</p>', 
        'id': 78, 'salary_time_unit': 'year', 'created_at': '2025-07-25T05:34:37.870273+00:00'
    }
]

def format_salary_range(job):
    """Format salary range for display"""
    if job.get('min_salary') and job.get('max_salary'):
        return f"{job['salary_currency']} {job['min_salary']:,.0f} - {job['max_salary']:,.0f} {job.get('salary_time_unit', '')}"
    elif job.get('min_salary'):
        return f"{job['salary_currency']} {job['min_salary']:,.0f}+ {job.get('salary_time_unit', '')}"
    elif job.get('max_salary'):
        return f"{job['salary_currency']} up to {job['max_salary']:,.0f} {job.get('salary_time_unit', '')}"
    else:
        return "Salary not specified"

def clean_html_description(html_text):
    """Remove HTML tags and clean up description"""
    if not html_text:
        return ""
    # Remove HTML tags
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', html_text)
    # Clean up extra whitespace
    text = ' '.join(text.split())
    return text

def generate_rss_from_jobs(jobs_data, company_name="Company Ninety Nine"):
    """Generate RSS feed from jobs data using ElementTree"""
    
    # Create RSS structure
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    
    # Channel metadata
    ET.SubElement(channel, "title").text = f"Latest Jobs - {company_name}"
    ET.SubElement(channel, "link").text = "https://hiregen.com/jobs"
    ET.SubElement(channel, "description").text = f"Latest job openings at {company_name} on HireGen"
    ET.SubElement(channel, "language").text = "en-us"
    ET.SubElement(channel, "lastBuildDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    # Add jobs as items
    for job in jobs_data:
        item = ET.SubElement(channel, "item")
        
        # Job title
        title = f"{job['job_title']} at {company_name}"
        ET.SubElement(item, "title").text = title
        
        # Job URL - format: {company_subdomain}.domain.com/jobs/{job_slug}
        job_url = f"http://{job['company_subdomain']}.localhost.com:3000/jobs/{job['slug']}"
        ET.SubElement(item, "link").text = job_url
        
        # Job description (clean HTML and add details)
        description = clean_html_description(job.get('job_description', ''))
        if len(description) > 300:
            description = description[:300] + "..."
        
        # Add job details
        details = []
        if job.get('work_experience'):
            details.append(f"Experience: {job['work_experience']}")
        if job.get('job_type'):
            details.append(f"Type: {job['job_type']}")
        if job.get('working_style'):
            details.append(f"Work Style: {job['working_style']}")
        if job.get('address_city') and job.get('address_country'):
            details.append(f"Location: {job['address_city']}, {job['address_country']}")
        
        salary_info = format_salary_range(job)
        if salary_info != "Salary not specified":
            details.append(f"Salary: {salary_info}")
        
        if details:
            description += "\n\n" + " | ".join(details)
        
        ET.SubElement(item, "description").text = description
        
        # Publication date
        pub_date = datetime.fromisoformat(job['created_at'].replace('Z', '+00:00'))
        ET.SubElement(item, "pubDate").text = pub_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        # Unique identifier
        ET.SubElement(item, "guid").text = job_url
        
        # Category
        if job.get('industry'):
            ET.SubElement(item, "category").text = job['industry']
    
    return ET.tostring(rss, encoding='unicode')

if __name__ == "__main__":
    # Generate RSS feed
    rss_content = generate_rss_from_jobs(sample_jobs)
    
    # Print the RSS feed
    print("Generated RSS Feed:")
    print("=" * 50)
    print(rss_content)
    
    # Save to file
    with open('sample_jobs_rss.xml', 'w', encoding='utf-8') as f:
        f.write(rss_content)
    
    print("\n" + "=" * 50)
    print("RSS feed saved to 'sample_jobs_rss.xml'")
    print("You can open this file in a browser or RSS reader to see the formatted feed.")
