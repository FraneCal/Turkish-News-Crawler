#!/usr/bin/env python3
"""
Ekonomist.com.tr Crawler V2 - MySQL Version
Matches database schema with Dunya crawler
"""

import requests
import random
import time
import os
import logging
import re
import json
import mysql.connector
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from mysql_config import MYSQL_CONFIG, TABLE_NAMES

# User agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
]

class EkonomistCrawlerMySQL:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.ekonomist.com.tr"
        self.api_url = "https://www.ekonomist.com.tr/kategori-sayfa"
        
        self.setup_logging()
        self.setup_database()
        self.setup_session()
        
        # Stats
        self.stats = {
            'current_page': 0,
            'total_articles': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'start_time': datetime.now(),
            'articles_with_html': 0,
            'articles_without_html': 0
        }
        
    def setup_logging(self):
        """Setup proper logging with UTF-8 support"""
        # Create logs directory
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"ekonomist_mysql_{timestamp}.log")
        
        # Setup logging configuration with UTF-8 support
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()  # Console output
            ]
        )
        
        # Set console encoding to UTF-8 if possible
        import sys
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8')
                sys.stderr.reconfigure(encoding='utf-8')
            except:
                pass
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Ekonomist Crawler MySQL initialized")
        
    def log(self, message: str):
        """Minimal log function"""
        try:
            self.logger.info(message)
        except UnicodeEncodeError:
            safe_message = message.encode('utf-8', errors='replace').decode('utf-8')
            self.logger.info(safe_message)
    
    def get_mysql_connection(self):
        """Get MySQL database connection"""
        try:
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            return conn
        except mysql.connector.Error as e:
            self.log(f"MySQL connection error: {e}")
            return None
        
    def setup_database(self):
        """Create database tables matching Dunya crawler schema"""
        conn = self.get_mysql_connection()
        if not conn:
            self.log("Failed to connect to MySQL database")
            return
            
        cursor = conn.cursor()
        
        try:
            # Main articles table - matching dunya_crawler schema
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {TABLE_NAMES['ekonomist_articles']} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    crawl_datetime DATETIME NOT NULL,
                    news_visible_datetime DATETIME,
                    news_visible_title_subtitle TEXT,
                    news_visible_body LONGTEXT,
                    news_url VARCHAR(500) UNIQUE,
                    news_sub_sitemap_link VARCHAR(500),
                    page_number INT,
                    raw_html LONGTEXT,
                    html_fetch_datetime DATETIME,
                    html_status VARCHAR(50)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            ''')
            
            # Page backup table - matching dunya_crawler schema
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {TABLE_NAMES['ekonomist_pages']} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    page_number INT,
                    page_url VARCHAR(500),
                    articles_found INT,
                    articles_processed INT,
                    crawl_datetime DATETIME,
                    status VARCHAR(50)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            ''')
            
            conn.commit()
            self.log("MySQL database tables initialized for Ekonomist crawler")
            
        except mysql.connector.Error as e:
            self.log(f"Database setup error: {e}")
        finally:
            conn.close()
        
    def setup_session(self):
        """Setup session with headers and cookies"""
        # Headers from the curl request
        headers = {
            'accept': '*/*',
            'accept-language': 'en-IN,en;q=0.9,hi-IN;q=0.8,hi;q=0.7,en-GB;q=0.6,en-US;q=0.5',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://www.ekonomist.com.tr/dunya',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        
        # Simplified cookies
        cookies = {
            '_ga': 'GA1.1.1373746519.1759164882',
            'pId': 'vnet2e63e008-3ef8-4f81-a89c-cf82770a1b1d'
        }
        
        self.session.headers.update(headers)
        self.session.cookies.update(cookies)
        
        self.log("Session configured")
        
    def make_request(self, url: str, timeout: int = 10):
        """Make HTTP request with error handling"""
        try:
            # Random delay to be polite
            time.sleep(random.uniform(1, 3))
            
            # Rotate user agent occasionally
            if random.random() < 0.3:
                self.session.headers['user-agent'] = random.choice(USER_AGENTS)
            
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            self.stats['successful_requests'] += 1
            return response
            
        except requests.RequestException as e:
            self.log(f"Request failed: {e}")
            self.stats['failed_requests'] += 1
            return None
            
    def fetch_page_articles(self, page_num: int):
        """Fetch articles from a specific page using the API"""
        params = {
            'url': 'dunya',
            'page': str(page_num)
        }
        
        self.log(f"Fetching page {page_num} from API...")
        
        # Make request with parameters
        try:
            response = requests.get(self.api_url, headers=self.session.headers, 
                                  cookies=self.session.cookies, params=params, timeout=15)
            response.raise_for_status()
            self.stats['successful_requests'] += 1
        except requests.RequestException as e:
            self.log(f"Request failed: {e}")
            self.stats['failed_requests'] += 1
            return []
        
        if not response.text:
            self.log(f"Empty response from page {page_num}")
            return []
            
        # Parse HTML response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract article links
        articles = []
        article_divs = soup.find_all('div', class_='mb-4')
        self.log(f"Found {len(article_divs)} div.mb-4 elements")
        
        for i, div in enumerate(article_divs):
            try:
                # Find the article link
                link = div.find('a', class_='news-card horizontal')
                if not link or not link.get('href'):
                    continue
                    
                href = link['href']
                
                # Skip if not a dunya article
                if not href.startswith('/dunya/'):
                    continue
                
                # Get title
                title_elem = link.find('strong')
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                # Get image URL
                img_elem = link.find('img')
                image_url = img_elem.get('src', '') if img_elem else ''
                
                # Build full URL
                full_url = urljoin(self.base_url, href)
                
                articles.append({
                    'url': full_url,
                    'href': href,
                    'title': title,
                    'image_url': image_url
                })
                
                self.log(f"Found article: {title[:50]}... -> {href}")
                
            except Exception as e:
                self.log(f"Error parsing article div: {e}")
                continue
                
        self.log(f"Page {page_num}: Found {len(articles)} articles")
        return articles
        
    def extract_article_content(self, html_content: str):
        """Extract article data from HTML - matching dunya_crawler format"""
        soup = BeautifulSoup(html_content, 'html.parser')
        article_data = {}
        
        try:
            # Extract title from multiple sources
            title = None
            
            # Try JSON-LD first
            json_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_scripts:
                try:
                    json_data = json.loads(script.string)
                    if json_data.get('@type') == 'NewsArticle':
                        title = json_data.get('headline') or json_data.get('name')
                        if title:
                            break
                except:
                    continue
            
            # Fallback to meta tags
            if not title:
                meta_title = soup.find('meta', property='og:title')
                if meta_title:
                    title = meta_title.get('content', '')
            
            # Fallback to h1
            if not title:
                h1 = soup.find('h1')
                if h1:
                    title = h1.get_text(strip=True)
            
            article_data['title'] = title or 'No title found'
            
            # Extract published date
            published_time = None
            
            # Try JSON-LD first
            for script in json_scripts:
                try:
                    json_data = json.loads(script.string)
                    if json_data.get('@type') == 'NewsArticle':
                        published_time = json_data.get('datePublished')
                        if published_time:
                            break
                except:
                    continue
            
            # Fallback to meta tags
            if not published_time:
                meta_date = soup.find('meta', property='article:published_time')
                if meta_date:
                    published_time = meta_date.get('content', '')
            
            article_data['published_time'] = published_time
            
            # Extract content/body
            content = ''
            
            # Try JSON-LD first
            for script in json_scripts:
                try:
                    json_data = json.loads(script.string)
                    if json_data.get('@type') == 'NewsArticle':
                        content = json_data.get('articleBody', '')
                        if content:
                            break
                except:
                    continue
            
            # Fallback to common content selectors
            if not content:
                content_selectors = [
                    '.entry-content',
                    '.post-content', 
                    '.article-content',
                    '.content',
                    'article'
                ]
                
                for selector in content_selectors:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        content = content_elem.get_text(strip=True)
                        break
            
            article_data['content'] = content or 'No content found'
            
        except Exception as e:
            self.log(f"Error extracting article content: {e}")
            article_data = {
                'title': 'Extraction error',
                'content': '',
                'published_time': None
            }
        
        return article_data
        
    def fetch_article_html(self, article_url: str):
        """Fetch the full HTML content of an article"""
        self.log(f"Fetching article HTML: {article_url}")
        
        article_response = self.make_request(article_url, timeout=15)
        
        if not article_response:
            return None, 'failed'
            
        return article_response.text, 'success'
        
    def save_article(self, article_data: dict, page_num: int, raw_html: str = None, html_status: str = 'missing'):
        """Save article to MySQL database - matching dunya_crawler schema"""
        conn = self.get_mysql_connection()
        if not conn:
            return None
            
        cursor = conn.cursor()
        
        try:
            # Process data with UTF-8 encoding
            title = article_data.get('title', '')
            content = article_data.get('content', '')
            url = article_data.get('url', '')
            published_time = article_data.get('published_time')
            
            # Process HTML content
            html_content = raw_html if raw_html else ''
            
            cursor.execute(f'''
                INSERT IGNORE INTO {TABLE_NAMES['ekonomist_articles']} 
                (crawl_datetime, news_visible_datetime, news_visible_title_subtitle, 
                 news_visible_body, news_url, news_sub_sitemap_link, page_number,
                 raw_html, html_fetch_datetime, html_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                datetime.now().isoformat(),
                published_time,
                title,
                content,
                url,
                f"{self.api_url}?url=dunya&page={page_num}",  # sitemap link
                page_num,
                html_content,
                datetime.now().isoformat(),
                html_status
            ))
            
            conn.commit()
            article_db_id = cursor.lastrowid
            
            # Check if article was actually inserted (not ignored due to duplicate)
            if article_db_id == 0:
                # Check if it's a duplicate
                cursor.execute(f'SELECT id FROM {TABLE_NAMES["ekonomist_articles"]} WHERE news_url = %s', (url,))
                existing = cursor.fetchone()
                if existing:
                    self.log(f"Duplicate article skipped: {url}")
                    return existing[0]  # Return existing ID
                else:
                    self.log(f"Article insert failed for unknown reason: {url}")
                    return None
            
            return article_db_id
            
        except mysql.connector.Error as e:
            self.log(f"MySQL error saving article {url}: {e}")
            return None
        finally:
            conn.close()
            
    def save_page_info(self, page_num: int, articles_found: int, articles_processed: int, status: str = 'completed'):
        """Save page processing info"""
        conn = self.get_mysql_connection()
        if not conn:
            return
            
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'''
                INSERT OR REPLACE INTO {TABLE_NAMES['ekonomist_pages']} 
                (page_number, page_url, articles_found, articles_processed, crawl_datetime, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                page_num,
                f"{self.api_url}?url=dunya&page={page_num}",
                articles_found,
                articles_processed,
                datetime.now().isoformat(),
                status
            ))
            
            conn.commit()
            
        except mysql.connector.Error as e:
            self.log(f"Error saving page info: {e}")
        finally:
            conn.close()
            
    def process_page(self, page_num: int):
        """Process a single page - fetch articles and their HTML content"""
        self.stats['current_page'] = page_num
        # Fetch articles from the page
        articles = self.fetch_page_articles(page_num)
        
        if not articles:
            self.save_page_info(page_num, 0, 0, 'no_articles')
            return 0
            
        # Process each article
        processed_count = 0
        
        for i, article in enumerate(articles, 1):
            
            # Fetch article HTML
            html_content, html_status = self.fetch_article_html(article['url'])
            
            # Extract article content from HTML
            if html_content:
                article_content = self.extract_article_content(html_content)
                article.update(article_content)
            
            # Save article to database
            article_id = self.save_article(article, page_num, html_content, html_status)
            
            if article_id:
                processed_count += 1
                self.stats['total_articles'] += 1
                
                if html_status == 'success':
                    self.stats['articles_with_html'] += 1
                else:
                    self.stats['articles_without_html'] += 1
                    
                pass
            else:
                self.log(f"Failed to save article {i}")
                
        # Save page info
        self.save_page_info(page_num, len(articles), processed_count, 'completed')
        
        print(f"Page {page_num}: {processed_count}/{len(articles)} articles saved")
        return processed_count
        
    def crawl_pages(self, start_page: int = 1, max_pages: int = 10):
        """Crawl multiple pages"""
        print(f"Ekonomist Crawler MySQL: pages {start_page} to {start_page + max_pages - 1}")
        self.log(f"Pages to crawl: {start_page} to {start_page + max_pages - 1}")
        
        total_processed = 0
        
        try:
            for page_num in range(start_page, start_page + max_pages):
                processed = self.process_page(page_num)
                total_processed += processed
                
                # Add delay between pages
                if page_num < start_page + max_pages - 1:
                    time.sleep(random.uniform(3, 8))
                    
        except KeyboardInterrupt:
            self.log("Crawler interrupted by user")
        except Exception as e:
            self.log(f"Unexpected error: {e}")
            
        # Final summary
        elapsed = datetime.now() - self.stats['start_time']
        print(f"Crawling completed in {elapsed}")
        print(f"Total articles processed: {total_processed}")
        self.log(f"FINAL SUMMARY - Time: {elapsed}, Articles: {total_processed}")
        
        return total_processed

def main():
    """
    Main function - Customize the parameters below to change what gets crawled:
    
    start_page: First page to crawl (1, 2, 3, etc.)
    max_pages: How many pages to crawl in total
    
    Examples:
    - crawler.crawl_pages(start_page=1, max_pages=5)   # Pages 1-5
    - crawler.crawl_pages(start_page=10, max_pages=3)  # Pages 10-12
    - crawler.crawl_pages(start_page=1, max_pages=50)  # Pages 1-50
    """
    # Create crawler
    crawler = EkonomistCrawlerMySQL()
    
    # CUSTOMIZE THESE PARAMETERS:
    START_PAGE = 1      # Change this to start from a different page
    MAX_PAGES = 50       # Change this to crawl more/fewer pages
    
    print(f"Starting Ekonomist crawler MySQL: pages {START_PAGE} to {START_PAGE + MAX_PAGES - 1}")
    crawler.crawl_pages(start_page=START_PAGE, max_pages=MAX_PAGES)

if __name__ == "__main__":
    main()
