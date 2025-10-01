#!/usr/bin/env python3
"""
Flask Web Application for News Crawler Data
Displays MySQL database data in a web interface
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import mysql.connector
from datetime import datetime, timedelta
import json
from mysql_config import MYSQL_CONFIG, TABLE_NAMES

app = Flask(__name__)

def get_mysql_connection():
    """Get MySQL database connection"""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn
    except mysql.connector.Error as e:
        print(f"MySQL connection error: {e}")
        return None

@app.route('/')
def index():
    """Main page showing statistics and recent articles"""
    conn = get_mysql_connection()
    if not conn:
        return "Database connection failed", 500
    
    cursor = conn.cursor()
    
    try:
        # Get statistics
        stats = {}
        
        # Dunya articles count
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAMES['dunya_articles']}")
        stats['dunya_articles'] = cursor.fetchone()[0]
        
        # Ekonomist articles count
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAMES['ekonomist_articles']}")
        stats['ekonomist_articles'] = cursor.fetchone()[0]
        
        # Add total_articles for template compatibility
        stats['total_articles'] = stats['dunya_articles'] + stats['ekonomist_articles']
        
        # Recent articles from both sources
        cursor.execute(f"""
            SELECT 'dunya' as source, news_visible_title_subtitle, news_url, news_visible_datetime, 
                   DATE(crawl_datetime) as crawl_date
            FROM {TABLE_NAMES['dunya_articles']} 
            ORDER BY crawl_datetime DESC 
            LIMIT 10
        """)
        dunya_recent = cursor.fetchall()
        
        cursor.execute(f"""
            SELECT 'ekonomist' as source, news_visible_title_subtitle, news_url, news_visible_datetime,
                   DATE(crawl_datetime) as crawl_date
            FROM {TABLE_NAMES['ekonomist_articles']} 
            ORDER BY crawl_datetime DESC 
            LIMIT 10
        """)
        ekonomist_recent = cursor.fetchall()
        
        # Combine and sort recent articles
        all_recent = list(dunya_recent) + list(ekonomist_recent)
        all_recent.sort(key=lambda x: x[4] if x[4] else datetime.min, reverse=True)
        
        return render_template('index.html', stats=stats, recent_articles=all_recent[:20])
        
    except mysql.connector.Error as e:
        return f"Database error: {e}", 500
    finally:
        conn.close()

@app.route('/dunya')
def dunya_articles():
    """Display Dunya articles"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    conn = get_mysql_connection()
    if not conn:
        return "Database connection failed", 500
    
    cursor = conn.cursor()
    
    try:
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAMES['dunya_articles']}")
        total_articles = cursor.fetchone()[0]
        
        # Get articles for current page
        cursor.execute(f"""
            SELECT id, news_visible_title_subtitle, news_visible_body, news_url, 
                   news_visible_datetime, crawl_datetime, page_number
            FROM {TABLE_NAMES['dunya_articles']} 
            ORDER BY crawl_datetime DESC 
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        
        articles = cursor.fetchall()
        
        total_pages = (total_articles + per_page - 1) // per_page
        
        return render_template('articles.html', 
                             articles=articles, 
                             source='Dunya',
                             current_page=page,
                             total_pages=total_pages,
                             total_articles=total_articles)
        
    except mysql.connector.Error as e:
        return f"Database error: {e}", 500
    finally:
        conn.close()

@app.route('/ekonomist')
def ekonomist_articles():
    """Display Ekonomist articles"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    conn = get_mysql_connection()
    if not conn:
        return "Database connection failed", 500
    
    cursor = conn.cursor()
    
    try:
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAMES['ekonomist_articles']}")
        total_articles = cursor.fetchone()[0]
        
        # Get articles for current page
        cursor.execute(f"""
            SELECT id, news_visible_title_subtitle, news_visible_body, news_url, 
                   news_visible_datetime, crawl_datetime, page_number
            FROM {TABLE_NAMES['ekonomist_articles']} 
            ORDER BY crawl_datetime DESC 
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        
        articles = cursor.fetchall()
        
        total_pages = (total_articles + per_page - 1) // per_page
        
        return render_template('articles.html', 
                             articles=articles, 
                             source='Ekonomist',
                             current_page=page,
                             total_pages=total_pages,
                             total_articles=total_articles)
        
    except mysql.connector.Error as e:
        return f"Database error: {e}", 500
    finally:
        conn.close()

@app.route('/article/<int:article_id>/<source>')
def view_article(article_id, source):
    """View individual article"""
    conn = get_mysql_connection()
    if not conn:
        return "Database connection failed", 500
    
    cursor = conn.cursor()
    
    try:
        table_name = TABLE_NAMES['dunya_articles'] if source == 'dunya' else TABLE_NAMES['ekonomist_articles']
        
        cursor.execute(f"""
            SELECT news_visible_title_subtitle, news_visible_body, news_url, 
                   news_visible_datetime, crawl_datetime, page_number, raw_html
            FROM {table_name} 
            WHERE id = %s
        """, (article_id,))
        
        article = cursor.fetchone()
        
        if not article:
            return "Article not found", 404
        
        return render_template('article_detail.html', 
                             article=article, 
                             source=source.capitalize())
        
    except mysql.connector.Error as e:
        return f"Database error: {e}", 500
    finally:
        conn.close()

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    conn = get_mysql_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    
    try:
        stats = {}
        
        # Dunya stats
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAMES['dunya_articles']}")
        stats['dunya_articles'] = cursor.fetchone()[0]
        
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAMES['dunya_articles']} WHERE DATE(crawl_datetime) = CURDATE()")
        stats['dunya_today'] = cursor.fetchone()[0]
        
        # Ekonomist stats
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAMES['ekonomist_articles']}")
        stats['ekonomist_articles'] = cursor.fetchone()[0]
        
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAMES['ekonomist_articles']} WHERE DATE(crawl_datetime) = CURDATE()")
        stats['ekonomist_today'] = cursor.fetchone()[0]
        
        # Total stats
        stats['total_articles'] = stats['dunya_articles'] + stats['ekonomist_articles']
        stats['total_today'] = stats['dunya_today'] + stats['ekonomist_today']
        
        return jsonify(stats)
        
    except mysql.connector.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        conn.close()

@app.route('/api/recent')
def api_recent():
    """API endpoint for recent articles"""
    limit = request.args.get('limit', 10, type=int)
    
    conn = get_mysql_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"""
            SELECT 'dunya' as source, news_visible_title_subtitle, news_url, 
                   news_visible_datetime, crawl_datetime
            FROM {TABLE_NAMES['dunya_articles']} 
            ORDER BY crawl_datetime DESC 
            LIMIT %s
        """, (limit,))
        dunya_recent = cursor.fetchall()
        
        cursor.execute(f"""
            SELECT 'ekonomist' as source, news_visible_title_subtitle, news_url, 
                   news_visible_datetime, crawl_datetime
            FROM {TABLE_NAMES['ekonomist_articles']} 
            ORDER BY crawl_datetime DESC 
            LIMIT %s
        """, (limit,))
        ekonomist_recent = cursor.fetchall()
        
        # Combine results
        all_articles = []
        for article in dunya_recent:
            all_articles.append({
                'source': article[0],
                'title': article[1],
                'url': article[2],
                'published_date': article[3].isoformat() if article[3] else None,
                'crawl_date': article[4].isoformat() if article[4] else None
            })
        
        for article in ekonomist_recent:
            all_articles.append({
                'source': article[0],
                'title': article[1],
                'url': article[2],
                'published_date': article[3].isoformat() if article[3] else None,
                'crawl_date': article[4].isoformat() if article[4] else None
            })
        
        # Sort by crawl date
        all_articles.sort(key=lambda x: x['crawl_date'] or '', reverse=True)
        
        return jsonify(all_articles[:limit])
        
    except mysql.connector.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
