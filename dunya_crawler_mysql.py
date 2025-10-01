#!/usr/bin/env python3
"""
Simple Smart Date-Based Crawler - MySQL Version
Console version without Rich - shows all essential logs
"""

import requests
import random
import time
import os
import logging
import mysql.connector
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from mysql_config import MYSQL_CONFIG, TABLE_NAMES

# User agents
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
]

class DunyaCrawlerMySQL:
    def __init__(self):
        self.session = requests.Session()
        self.setup_logging()
        self.setup_database()
        
        # Stats
        self.stats = {
            'current_page': 0,
            'total_articles': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'start_time': datetime.now(),
            'search_pages': [],  # Pages we've checked during binary search
            'target_start_date': None,
            'target_end_date': None,
            'search_phase': "initializing"
        }
        
    def setup_logging(self):
        """Setup proper logging with file and console output"""
        # Create logs directory
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"dunya_crawler_mysql_{timestamp}.log")
        
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
        
        # Minimal initialization logging
        self.logger.info("Dunya Crawler MySQL initialized")
        self.use_emojis = False
        
    def log(self, message: str):
        """Minimal log function"""
        self.logger.info(message)
        
    def get_mysql_connection(self):
        """Get MySQL database connection"""
        try:
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            return conn
        except mysql.connector.Error as e:
            self.log(f"MySQL connection error: {e}")
            return None
        
    def setup_database(self):
        """Create database tables"""
        conn = self.get_mysql_connection()
        if not conn:
            self.log("Failed to connect to MySQL database")
            return
            
        cursor = conn.cursor()
        
        try:
            # Create dunya articles table
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {TABLE_NAMES['dunya_articles']} (
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
            
            # Create dunya page backup table
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {TABLE_NAMES['dunya_pages']} (
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
            self.log("MySQL database tables initialized for Dunya crawler")
            
        except mysql.connector.Error as e:
            self.log(f"Database setup error: {e}")
        finally:
            conn.close()
    
    def get_headers(self):
        """Get random headers"""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Connection": "keep-alive"
        }
    
    def make_request(self, url: str, max_retries: int = 1):
        """Make HTTP request - OPTIMIZED FOR SPEED"""
        try:
            response = self.session.get(url, headers=self.get_headers(), timeout=5)  # Increased for stability
            response.raise_for_status()
            self.stats['successful_requests'] += 1
            return response
        except Exception as e:
            self.stats['failed_requests'] += 1
            self.log(f"Request failed: {e}")
            return None
    
    def extract_article_content(self, html: str):
        """Extract article content"""
        soup = BeautifulSoup(html, 'html.parser')
        
        title_elem = soup.find('h1', class_='post-title') or soup.find('h1')
        title = title_elem.get_text(strip=True) if title_elem else "No title found"
        
        content_elem = soup.find('div', class_='content-text') or soup.find('article')
        content = content_elem.get_text(strip=True) if content_elem else "No content found"
        
        time_elem = soup.find('time')
        published_time = time_elem.get('datetime') if time_elem else None
        
        # Clean content
        sentences = content.split('.')
        unique_sentences = []
        seen = set()
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence.lower() not in seen:
                unique_sentences.append(sentence)
                seen.add(sentence.lower())
        
        content = '. '.join(unique_sentences)
        
        return {
            'title': title,
            'content': content,
            'published_time': published_time
        }
    
    def parse_date(self, date_str: str):
        """Parse date string to datetime object"""
        if not date_str:
            return None
        
        try:
            # Parse ISO format date
            if date_str.endswith('Z'):
                date_str = date_str[:-1] + '+00:00'
            elif '+' not in date_str and 'T' in date_str:
                date_str += '+03:00'  # Assume Turkey timezone
            
            parsed_date = datetime.fromisoformat(date_str)
            # Convert to naive datetime for comparison
            return parsed_date.replace(tzinfo=None)
        except Exception:
            return None
    
    def get_page_date_range(self, page_num: int):
        """Get date from a specific page (check only first article)"""
        base_url = 'https://www.dunya.com/gundem'
        url = base_url if page_num == 1 else f"{base_url}/{page_num}"
        
        self.log(f"Checking page {page_num} for dates...")
        
        response = self.make_request(url)
        if not response:
            self.log(f"Failed to load page {page_num}")
            return None, None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find article links
        article_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/gundem/' in href and 'haberi-' in href:
                if not href.startswith('http'):
                    href = urljoin(base_url, href)
                article_links.append(href)
        
        if not article_links:
            self.log(f"No articles found on page {page_num}")
            return None, None
        
        # Check only the first article to get the date (much faster)
        article_url = article_links[0]  # Only check first article
        self.log(f"Checking first article from page {page_num}: {article_url[:80]}...")
        
        article_response = self.make_request(article_url)
        if not article_response:
            self.log(f"Failed to load article from page {page_num}")
            return None, None
        
        article_data = self.extract_article_content(article_response.text)
        if article_data.get('published_time'):
            parsed_date = self.parse_date(article_data['published_time'])
            if parsed_date:
                self.log(f"Page {page_num}: Article date = {parsed_date.strftime('%Y-%m-%d %H:%M')}")
                return parsed_date, parsed_date  # Same date for min and max
        
        self.log(f"Page {page_num}: No valid date found")
        return None, None
    
    def smart_search_for_end_date(self):
        """Two-phase algorithm: Adaptive jumping + careful page-by-page when close"""
        self.log(f"=== TWO-PHASE ADAPTIVE SEARCH ===")
        self.log(f"Looking for end date: {self.stats['target_end_date'].strftime('%Y-%m-%d')}")
        
        # Phase 1: Adaptive jumping to get close to target
        self.log("Phase 1: Adaptive jumping to get close to target...")
        close_page = self.adaptive_jump_to_target()
        
        # Phase 2: Return the target page for scraping
        self.log("Phase 2: Found target page for scraping")
        return close_page
    
    def adaptive_jump_to_target(self):
        """Phase 1: Use adaptive jumping starting small and increasing gradually"""
        current_page = 1
        jump_size = 1  # Start with small jump
        max_jump_size = 50  # Reduced max jump size
        min_jump_size = 1
        backtrack_count = 0
        max_backtrack = 3  # Maximum backtrack attempts
        
        self.log(f"Starting adaptive jumping from page {current_page} with jump size {jump_size}")
        
        while True:
            # Make a jump
            next_page = current_page + jump_size
            self.log(f"Jumping from page {current_page} to page {next_page} (jump size: {jump_size})")
            
            # Check the jumped page
            min_date, max_date = self.get_page_date_range(next_page)
            
            if min_date is None or max_date is None:
                self.log(f"Page {next_page}: No valid date - reducing jump size")
                jump_size = max(jump_size // 2, min_jump_size)
                continue
            
            self.log(f"Page {next_page}: Date range = {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
            
            # Compare only dates (not time)
            page_date_only = max_date.date()
            target_date_only = self.stats['target_end_date'].date()
            
            # Calculate distance from target (date only)
            days_from_target = (target_date_only - page_date_only).days
            self.log(f"Distance from target: {days_from_target} days (comparing dates only)")
            
            # Check if we found our target date
            if days_from_target == 0:  # Exactly our target date - PERFECT!
                self.log(f"FOUND EXACT TARGET! Page {next_page} has date {page_date_only} = target {target_date_only}")
                return next_page
            elif days_from_target < 0:  # Page date is NEWER than target (we need to go back)
                self.log(f"Page {next_page} is {abs(days_from_target)} days NEWER than target - need to go to older pages")
                # Continue searching with smaller jumps
            
            # If we're very close (within 1 day), switch to careful search
            if days_from_target == 1:
                self.log(f"Very close to target! Switching to careful page-by-page search from page {next_page}")
                return next_page
            
            # ADAPTIVE JUMP SIZE ADJUSTMENT based on distance (more conservative)
            if days_from_target > 30:  # Very far from target
                jump_size = min(jump_size + 5, max_jump_size)  # Add 5 pages
                self.log(f"Too far from target - increasing jump size to {jump_size}")
            elif days_from_target > 20:  # Far from target
                jump_size = min(jump_size + 3, max_jump_size)  # Add 3 pages
                self.log(f"Far from target - increasing jump size to {jump_size}")
            elif days_from_target > 10:  # Moderately far
                jump_size = min(jump_size + 2, max_jump_size)  # Add 2 pages
                self.log(f"Moderately far from target - slightly increasing jump size to {jump_size}")
            elif days_from_target > 5:  # Getting close
                jump_size = max(jump_size, min_jump_size)  # Keep current size
                self.log(f"Getting close to target - keeping jump size at {jump_size}")
            elif days_from_target > 3:  # Close
                jump_size = max(jump_size - 1, min_jump_size)  # Reduce by 1
                self.log(f"Close to target - reducing jump size to {jump_size}")
            else:  # Very close (2-3 days)
                jump_size = max(jump_size - 2, min_jump_size)  # Reduce by 2
                self.log(f"Very close to target - reducing jump size to {jump_size}")
            
            # Move to next page
            current_page = next_page
            backtrack_count = 0  # Reset backtrack count on successful jump
            
            # Safety check
            if current_page > 1000:
                self.log("Reached maximum page limit - stopping search")
                return current_page
    
    def scrape_from_target_page(self, start_page: int):
        """START SCRAPING IMMEDIATELY from target page and keep going until start date"""
        self.log(f"=== IMMEDIATE SCRAPING FROM PAGE {start_page} ===")
        self.log(f"Starting from page {start_page} and going forward until we reach start date {self.stats['target_start_date'].strftime('%Y-%m-%d')}")
        
        total_articles = 0
        page_num = start_page
        
        while True:
            self.log(f"\n--- Processing Page {page_num} ---")
            
            # Get page date to check if we should continue
            min_date, max_date = self.get_page_date_range(page_num)
            if min_date is None or max_date is None:
                self.log(f"Page {page_num}: No valid date - stopping")
                break
            
            # Check if we've reached the start date (compare only dates, not times)
            page_date_only = max_date.date()
            start_date_only = self.stats['target_start_date'].date()
            
            if page_date_only < start_date_only:
                self.log(f"Page {page_num}: Reached start date ({page_date_only}) - stopping")
                break
            
            self.log(f"Page {page_num}: Date {page_date_only} >= start date {start_date_only} - continuing")
            
            # Process this page and save articles
            page_articles = self.process_page_articles(page_num)
            total_articles += page_articles
            self.log(f"Page {page_num}: {page_articles} articles saved")
            
            # Move to next page
            page_num += 1
        
        self.log(f"=== SCRAPING COMPLETE ===")
        self.log(f"Total articles saved: {total_articles}")
        return total_articles
    
    def process_page_articles(self, page_num: int):
        """Process all articles on a specific page"""
        base_url = 'https://www.dunya.com/gundem'
        url = base_url if page_num == 1 else f"{base_url}/{page_num}"
        
        response = self.make_request(url)
        if not response:
            return 0
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find article links
        article_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/gundem/' in href and 'haberi-' in href:
                if not href.startswith('http'):
                    href = urljoin(base_url, href)
                article_links.append(href)
        
        if not article_links:
            return 0
        
        # Process all articles on this page
        page_articles = 0
        for i, article_url in enumerate(article_links):
            article_response = self.make_request(article_url)
            if not article_response:
                continue
            
            article_data = self.extract_article_content(article_response.text)
            article_data['url'] = article_url
            
            # Check if this article is within our date range
            if article_data.get('published_time'):
                article_date = self.parse_date(article_data['published_time'])
                if article_date:
                    # Compare only dates, not times
                    article_date_only = article_date.date()
                    start_date_only = self.stats['target_start_date'].date()
                    end_date_only = self.stats['target_end_date'].date()
                    
                    if start_date_only <= article_date_only <= end_date_only:
                        # Save this article with HTML content
                        article_id = self.save_article(article_data, url, page_num, article_response.text)
                        if article_id:
                            page_articles += 1
                else:
                    self.log(f"Failed to parse date from article {i+1}")
            else:
                self.log(f"No published_time found in article {i+1}")
            
            # Process all articles on this page
        
        print(f"Page {page_num}: {page_articles}/{len(article_links)} articles saved")
        
        return page_articles
    
    def save_article(self, article_data: dict, page_url: str = None, page_number: int = 0, raw_html: str = None):
        """Save article to MySQL database with HTML content"""
        conn = self.get_mysql_connection()
        if not conn:
            return None
            
        cursor = conn.cursor()
        
        try:
            title = str(article_data.get('title', '')).encode('utf-8', errors='replace').decode('utf-8')
            content = str(article_data.get('content', '')).encode('utf-8', errors='replace').decode('utf-8')
            url = str(article_data.get('url', '')).encode('utf-8', errors='replace').decode('utf-8')
            
            # Process HTML content
            html_status = 'success' if raw_html else 'missing'
            html_content = raw_html if raw_html else ''
            
            cursor.execute(f'''
                INSERT IGNORE INTO {TABLE_NAMES['dunya_articles']} 
                (crawl_datetime, news_visible_datetime, news_visible_title_subtitle, 
                 news_visible_body, news_url, news_sub_sitemap_link, page_number,
                 raw_html, html_fetch_datetime, html_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                datetime.now().isoformat(),
                article_data.get('published_time'),
                title,
                content,
                url,
                page_url,
                page_number,
                html_content,
                datetime.now().isoformat(),
                html_status
            ))
            
            conn.commit()
            article_id = cursor.lastrowid
            
            return article_id
            
        except mysql.connector.Error as e:
            self.log(f"MySQL error saving article: {e}")
            return None
        finally:
            conn.close()
    
    def run_smart_crawler(self, start_date: str, end_date: str):
        """Run smart date-based crawler"""
        # Parse dates
        try:
            self.stats['target_start_date'] = datetime.strptime(start_date, '%Y-%m-%d')
            self.stats['target_end_date'] = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD")
            return
        
        if self.stats['target_start_date'] >= self.stats['target_end_date']:
            print("Start date must be before end date")
            return
        
        print(f"Dunya Crawler MySQL: {start_date} to {end_date}")
        self.log(f"Target date range: {start_date} to {end_date}")
        
        try:
            # Phase 1: Smart search to find the page with our end date
            self.stats['search_phase'] = "searching"
            self.log("Phase 1: Finding target page")
            
            end_page = self.smart_search_for_end_date()
            
            if end_page:
                print(f"Found target page: {end_page}")
                self.log(f"Found target page: {end_page}")
            else:
                print("Could not find target page")
                self.log("Could not find target page")
                return
            
            # Phase 2: START SCRAPING IMMEDIATELY from the target page
            total_articles = self.scrape_from_target_page(end_page)
            
            # Final summary
            elapsed = datetime.now() - self.stats['start_time']
            print(f"Crawling completed in {elapsed}")
            print(f"Total articles saved: {total_articles}")
            self.log(f"FINAL SUMMARY - Time: {elapsed}, Articles: {total_articles}")
            
        except KeyboardInterrupt:
            self.log("Stopped by user")
        except Exception as e:
            self.log(f"Error: {e}")

def main():
    """
    Main function - Customize the date range below:
    
    start_date: Older date (beginning of range) in YYYY-MM-DD format
    end_date: Newer date (end of range) in YYYY-MM-DD format
    
    Examples:
    - "2025-09-01" to "2025-09-30"  # Entire September 2025
    - "2025-09-29" to "2025-09-29"  # Single day
    - "2025-08-15" to "2025-09-15"  # One month range
    """
    crawler = DunyaCrawlerMySQL()
    
    # CUSTOMIZE THESE DATES:
    START_DATE = "2025-09-01"  # Older date (start of range)
    END_DATE = "2025-10-01"    # Newer date (end of range)
    
    print(f"Starting Dunya crawler MySQL for date range: {START_DATE} to {END_DATE}")
    crawler.run_smart_crawler(START_DATE, END_DATE)

if __name__ == "__main__":
    main()
