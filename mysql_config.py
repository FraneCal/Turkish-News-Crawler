#!/usr/bin/env python3
"""
MySQL Database Configuration
"""

# MySQL Database Configuration
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'newscrawler',
    'password': 'news_crawler_2025',
    'database': 'news_crawler_db',
    'charset': 'utf8mb4',
    'autocommit': True,
    'use_unicode': True
}

# Table names for different crawlers
TABLE_NAMES = {
    'dunya_articles': 'dunya_news_articles',
    'dunya_pages': 'dunya_page_backup',
    'ekonomist_articles': 'ekonomist_news_articles', 
    'ekonomist_pages': 'ekonomist_page_backup'
}
