# Dunya News Crawler

A smart date-based news crawler for **Dunya.com** that extracts articles within a specific date range using intelligent page navigation.

## Features

- **Smart Date-Based Crawling**: Intelligently finds and crawls articles between specified start and end dates
- **Adaptive Jump Algorithm**: Uses dynamic page jumping to efficiently locate target date ranges
- **HTML Content Storage**: Downloads and stores complete article HTML content
- **UTF-8 Support**: Full Turkish character support for proper text handling
- **Comprehensive Logging**: Detailed logs with timestamps and progress tracking
- **SQLite Database**: Structured data storage with duplicate prevention
- **Stealth Crawling**: Human-like request patterns to avoid detection

## Database Schema

The crawler stores data in `duniya_news.db` with the following structure:

```sql
CREATE TABLE news_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crawl_datetime DATETIME NOT NULL,
    news_visible_datetime DATETIME,
    news_visible_title_subtitle TEXT,
    news_visible_body LONGTEXT,
    news_url VARCHAR(500) UNIQUE,
    news_sub_sitemap_link VARCHAR(500),
    page_number INTEGER,
    raw_html LONGTEXT,
    html_fetch_datetime DATETIME,
    html_status VARCHAR(50)
)
```

## Usage

### Basic Usage

```python
from dunya_crawler import DunyaCrawler

# Initialize crawler
crawler = DunyaCrawler()

# Crawl articles between specific dates
crawler.run_smart_crawler(
    start_date="2025-09-01",  # Older date
    end_date="2025-09-20"     # Newer date
)
```

### **Customizing Date Range**

You can easily change the date range by modifying the parameters:

```python
# Example 1: Last week's articles
crawler.run_smart_crawler(
    start_date="2025-09-22",  # Start date (older)
    end_date="2025-09-29"     # End date (newer)
)

# Example 2: Specific month
crawler.run_smart_crawler(
    start_date="2025-08-01", 
    end_date="2025-08-31"
)

# Example 3: Single day
crawler.run_smart_crawler(
    start_date="2025-09-29", 
    end_date="2025-09-29"
)
```

**Important Notes:**
- Use ISO date format: `YYYY-MM-DD`
- `start_date` must be older than `end_date`
- The crawler works backwards from newer to older articles

### Command Line Usage

```bash
python dunya_crawler.py
```

## How It Works

1. **Smart Search Phase**: 
   - Uses adaptive jumping to find the page containing the end date
   - Starts with small jumps and increases based on date distance
   - Automatically backtracks if it overshoots the target

2. **Content Extraction Phase**:
   - Scrapes articles from the target page backwards
   - Extracts article URLs from `/gundem` category pages
   - Downloads full HTML content for each article
   - Stops when reaching the start date

3. **Data Storage**:
   - Saves article metadata and full HTML content
   - Prevents duplicate entries using URL uniqueness
   - Maintains crawl timestamps and status information

## Configuration

### Date Format
- Use ISO format: `YYYY-MM-DD`
- Start date should be older than end date
- Example: `start_date="2025-09-01"`, `end_date="2025-09-20"`

### Output Files
- **Database**: `duniya_news.db`
- **Logs**: `logs/dunya_crawler_YYYYMMDD_HHMMSS.log`

## Requirements

```
requests>=2.31.0
beautifulsoup4>=4.12.0
urllib3>=2.0.0
```

## Installation

```bash
pip install requests beautifulsoup4 urllib3
```

## Key Features

### Smart Date Navigation
- Automatically finds the optimal starting page for your date range
- Reduces crawling time by avoiding unnecessary pages
- Handles date parsing and timezone conversion

### Content Extraction
- Extracts article titles, content, and publication dates
- Stores complete HTML for future processing
- Filters relevant article URLs (minimum length requirements)

### Error Handling
- Retry logic for failed requests
- Graceful handling of network timeouts
- Comprehensive error logging

## Example Output

```
=== DUNYA DATE CRAWLER STARTED ===
🎯 Target date range: 2025-09-01 to 2025-09-20
📁 Database: duniya_news.db
🔍 Phase 1: Smart search for end date
📍 Found target page: 21 with date range 2025-09-20
🎯 Phase 2: Scraping from target page
📄 Page 21: Found 25 articles, processed 25
📄 Page 22: Found 24 articles, processed 24
✅ CRAWLING COMPLETED
📊 Total articles saved: 127
```

## Notes

- The crawler respects the website's structure and implements delays between requests
- All text content is stored with UTF-8 encoding
- Duplicate articles are automatically filtered out
- The crawler can resume from where it left off due to database-based tracking
