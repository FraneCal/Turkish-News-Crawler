# Ekonomist News Crawler

A comprehensive news crawler for **Ekonomist.com.tr** that extracts articles from the "Dünya" (World) category using their API endpoint.

## Features

- **API-Based Crawling**: Direct integration with Ekonomist's content API
- **Page-by-Page Processing**: Sequential crawling through paginated content
- **Full HTML Storage**: Downloads and stores complete article HTML
- **Content Extraction**: Extracts structured data (title, content, dates, images)
- **UTF-8 Support**: Full Turkish character support
- **Comprehensive Logging**: Detailed progress tracking and error logging
- **SQLite Database**: Structured storage with duplicate prevention
- **JSON-LD Support**: Extracts structured data when available

## Database Schema

The crawler stores data in `ekonomist_news_v2.db` with the following structure:

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
from ekonomist_crawler_v2 import EkonomistCrawlerV2

# Initialize crawler
crawler = EkonomistCrawlerV2()

# Crawl pages 1 to 10
crawler.crawl_pages(start_page=1, max_pages=10)
```

### **Customizing Pages to Crawl**

You can easily change which pages to crawl by modifying the parameters:

```python
# Example 1: Crawl first 5 pages
crawler.crawl_pages(start_page=1, max_pages=5)

# Example 2: Crawl pages 10-20 (total 11 pages)
crawler.crawl_pages(start_page=10, max_pages=11)

# Example 3: Crawl only page 15
crawler.crawl_pages(start_page=15, max_pages=1)

# Example 4: Crawl many pages (50 pages starting from page 1)
crawler.crawl_pages(start_page=1, max_pages=50)
```

**Parameters Explained:**
- `start_page`: The first page number to crawl (default: 1)
- `max_pages`: How many pages to crawl in total (default: 10)
- The crawler will process pages from `start_page` to `start_page + max_pages - 1`

**Page Range Examples:**
- `start_page=1, max_pages=10` → Crawls pages 1, 2, 3, ..., 10
- `start_page=5, max_pages=3` → Crawls pages 5, 6, 7
- `start_page=20, max_pages=1` → Crawls only page 20

### Command Line Usage

```bash
python ekonomist_crawler_v2.py
```

## How It Works

1. **API Integration**:
   - Makes requests to `https://www.ekonomist.com.tr/kategori-sayfa`
   - Uses parameters: `url=dunya&page={page_number}`
   - Includes proper headers and cookies for authentication

2. **Content Processing**:
   - Parses HTML response to extract article links
   - Visits each individual article URL
   - Downloads complete HTML content
   - Extracts structured data using multiple methods

3. **Data Extraction**:
   - **Title**: From multiple selectors and JSON-LD
   - **Content**: Article body text and HTML
   - **Publication Date**: From JSON-LD or meta tags
   - **Images**: Featured image URLs
   - **Raw HTML**: Complete page source

4. **Storage**:
   - Saves all data to SQLite database
   - Prevents duplicates using URL uniqueness
   - Maintains processing status and timestamps

## Configuration

### Page Range
```python
crawler.run_crawler(
    start_page=1,    # First page to crawl
    end_page=50      # Last page to crawl
)
```

### Output Files
- **Database**: `ekonomist_news_v2.db`
- **Logs**: `logs/ekonomist_crawler_YYYYMMDD_HHMMSS.log`

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

### Multi-Source Content Extraction
- **JSON-LD**: Structured data extraction when available
- **HTML Selectors**: Multiple fallback selectors for robustness
- **Meta Tags**: OpenGraph and Twitter card data
- **Content Cleaning**: Removes ads and irrelevant content

### Content Types Extracted
- Article title and subtitle
- Publication and update timestamps
- Full article content (text and HTML)
- Featured images and media
- Article categories and tags
- Author information (when available)

### Error Handling
- Request timeout handling
- HTTP status code validation
- Content parsing error recovery
- Comprehensive error logging
- Graceful degradation for missing data

## Example Output

```
🚀 Ekonomist Crawler initialized
📁 Log file: logs/ekonomist_crawler_20250929_223208.log
🔄 Crawling pages 1 to 5...

📄 Processing page 1...
   Found 25 article links
   ✅ Saved: Türkiye ekonomisi büyüme hedefine odaklandı (65432 chars HTML)
   ✅ Saved: Enflasyon rakamları beklentileri aştı (58901 chars HTML)
   ...

📄 Processing page 2...
   Found 24 article links
   ✅ Saved: Merkez Bankası faiz kararını açıkladı (72145 chars HTML)
   ...

✅ CRAWLING COMPLETED
📊 Total articles processed: 127
📊 Successfully saved: 125
📊 Failed to save: 2
```

## Database Analysis

Use the included utility to check your database:

```bash
python check_ekonomist_v2_db.py
```

Output example:
```
Ekonomist Database Statistics:
   Total articles: 63
   Articles with HTML: 63
   Articles without HTML: 0
   HTML column exists: True
   Average HTML size: 61320 characters
```

## API Endpoint Details

The crawler uses the following API structure:
- **Base URL**: `https://www.ekonomist.com.tr/kategori-sayfa`
- **Parameters**: 
  - `url=dunya` (World category)
  - `page={number}` (Page number)
- **Method**: GET
- **Response**: HTML with article links in `div.mb-4` elements

## Content Structure

Each article page contains:
- **Article Title**: Main headline
- **Publication Date**: ISO format timestamps
- **Content**: Full article text and HTML
- **Images**: Featured and inline images
- **Metadata**: Categories, tags, author info
- **Structured Data**: JSON-LD when available

## Notes

- The crawler implements random delays between requests (1-3 seconds)
- All content is stored with UTF-8 encoding
- Duplicate articles are automatically filtered
- Failed requests are logged but don't stop the crawler
- The database schema matches the Dunya crawler for consistency
