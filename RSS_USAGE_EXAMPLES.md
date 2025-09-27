# RSS Feed Usage Examples for HireGen

## Available RSS Endpoints

### 1. All Jobs RSS Feed
```
https://hiregen.com/rss/jobs.xml
```
- Contains latest 50 job postings from all companies
- Updated automatically when new jobs are posted

### 2. Company-Specific RSS Feed
```
https://hiregen.com/rss/company/{company_subdomain}/jobs.xml
```
Example:
```
https://hiregen.com/rss/company/companyninetynine/jobs.xml
```
- Contains jobs from a specific company
- Useful for companies to share their job openings

### 3. Industry-Specific RSS Feed
```
https://hiregen.com/rss/industry/{industry}/jobs.xml
```
Examples:
```
https://hiregen.com/rss/industry/Entertainment/jobs.xml
https://hiregen.com/rss/industry/Hospital%20%26%20Health%20Care/jobs.xml
```
- Contains jobs from a specific industry
- Useful for job seekers interested in particular sectors

## How to Use RSS Feeds

### For Job Seekers
1. **Subscribe in RSS Reader**: Add the feed URL to your RSS reader (Feedly, Inoreader, etc.)
2. **Browser Integration**: Some browsers support RSS feeds natively
3. **Email Notifications**: Use services like IFTTT to get email alerts for new jobs

### For Companies
1. **Share Company Feed**: Provide your company RSS feed URL to potential candidates
2. **Website Integration**: Embed RSS feed on your company website
3. **Social Media**: Use RSS feeds to automatically post new jobs to social media

### For Job Boards
1. **Syndication**: Use HireGen RSS feeds to display jobs on your job board
2. **API Alternative**: RSS feeds provide a simple way to access job data without API keys

## RSS Feed Structure

Each job in the RSS feed includes:
- **Title**: Job title with company name
- **Link**: Direct URL to the job posting (format: {company_subdomain}.domain.com/jobs/{job_slug})
- **Description**: Job description with key details (experience, type, location, salary)
- **Publication Date**: When the job was posted
- **Category**: Industry classification
- **GUID**: Unique identifier for the job

## Example RSS Item

```xml
<item>
    <title>Writer at Company Ninety Nine</title>
    <link>http://companyninetynine.localhost.com:3000/jobs/writer-1</link>
    <description>We are looking for a talented Writer to join our team in the Entertainment industry. As a mid-level Writer, you will be responsible for creating engaging and compelling content for various projects. This is a contract position that offers an exciting opportunity to showcase your writing skills.

Experience: Mid-Level | Type: Contract | Work Style: Hybrid | Location: Navi Mumbai, India | Salary: ₹ 500,000 - 1,000,000 Yearly</description>
    <pubDate>Thu, 24 Jul 2025 10:32:10 GMT</pubDate>
    <guid>http://companyninetynine.localhost.com:3000/jobs/writer-1</guid>
    <category>Entertainment</category>
</item>
```

## Integration Examples

### JavaScript (Fetch RSS)
```javascript
fetch('https://hiregen.com/rss/jobs.xml')
    .then(response => response.text())
    .then(data => {
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(data, 'text/xml');
        const items = xmlDoc.querySelectorAll('item');
        
        items.forEach(item => {
            const title = item.querySelector('title').textContent;
            const link = item.querySelector('link').textContent;
            const description = item.querySelector('description').textContent;
            console.log(title, link, description);
        });
    });
```

### Python (Parse RSS)
```python
import feedparser

# Parse the RSS feed
feed = feedparser.parse('https://hiregen.com/rss/jobs.xml')

# Access feed information
print(f"Feed Title: {feed.feed.title}")
print(f"Feed Description: {feed.feed.description}")

# Access individual job entries
for entry in feed.entries:
    print(f"Job: {entry.title}")
    print(f"Link: {entry.link}")
    print(f"Description: {entry.description}")
    print(f"Published: {entry.published}")
    print("---")
```

## Benefits of RSS Feeds

1. **Real-time Updates**: Get notified immediately when new jobs are posted
2. **No API Keys Required**: Simple HTTP requests to access job data
3. **Standard Format**: Works with any RSS reader or parser
4. **SEO Benefits**: Helps search engines discover and index job content
5. **Syndication**: Easy to share job content across multiple platforms
6. **Automation**: Can be used to automatically post jobs to social media or other platforms

## Customization

The RSS feeds are automatically generated and include:
- Latest 50 jobs (configurable)
- Clean, readable descriptions
- Proper date formatting
- Industry categorization
- Salary information (when available)
- Location details

For custom RSS feeds or additional features, contact the HireGen development team.
