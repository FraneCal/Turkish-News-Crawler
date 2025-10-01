# News Crawler Web Application

A complete web interface for displaying Turkish news data from Dunya and Ekonomist sources, stored in MySQL database.

## Features

- 🌐 **Web Dashboard**: Beautiful, responsive web interface
- 📊 **Real-time Statistics**: Live article counts and statistics
- 🔍 **Article Browsing**: Browse articles by source with pagination
- 📱 **Mobile Responsive**: Works on all devices
- 🔌 **REST API**: JSON endpoints for data access
- 🗄️ **MySQL Database**: Scalable data storage
- 🚀 **Production Ready**: Nginx + systemd service

## Quick Start

### 1. Install Dependencies
```bash
cd /root/NewsCrawler
pip3 install -r requirements.txt
```

### 2. Deploy Web Application
```bash
./deploy.sh
```

### 3. Access Your Application
- **Web Interface**: `http://72.60.182.36`
- **API**: `http://72.60.182.36/api/stats`

## Manual Setup (Alternative)

### 1. Install Web Dependencies
```bash
pip3 install Flask gunicorn mysql-connector-python
```

### 2. Start the Web Application
```bash
python3 app.py
```

### 3. Configure Nginx (Optional)
```bash
# Install nginx
apt install nginx

# Copy configuration
cp nginx_config.conf /etc/nginx/sites-available/news-crawler
ln -sf /etc/nginx/sites-available/news-crawler /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and restart
nginx -t
systemctl restart nginx
```

### 4. Configure Systemd Service
```bash
# Copy service file
cp news-crawler.service /etc/systemd/system/

# Enable and start
systemctl daemon-reload
systemctl enable news-crawler.service
systemctl start news-crawler.service
```

## Web Interface Features

### Dashboard (`/`)
- Real-time statistics
- Recent articles from both sources
- Quick navigation links
- Auto-refreshing data

### Dunya Articles (`/dunya`)
- Browse all Dunya articles
- Pagination support
- Article details and original links

### Ekonomist Articles (`/ekonomist`)
- Browse all Ekonomist articles
- Pagination support
- Article details and original links

### Article Details (`/article/<id>/<source>`)
- Full article content
- Raw HTML content (collapsible)
- Article metadata
- Original article links

## API Endpoints

### Statistics API
```
GET /api/stats
```
Returns:
```json
{
  "dunya_articles": 150,
  "ekonomist_articles": 200,
  "total_articles": 350,
  "dunya_today": 5,
  "ekonomist_today": 8,
  "total_today": 13
}
```

### Recent Articles API
```
GET /api/recent?limit=10
```
Returns:
```json
[
  {
    "source": "dunya",
    "title": "Article Title",
    "url": "https://...",
    "published_date": "2025-01-15T10:30:00",
    "crawl_date": "2025-01-15T10:35:00"
  }
]
```

## Database Schema

### Dunya Articles Table
```sql
CREATE TABLE dunya_news_articles (
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
);
```

### Ekonomist Articles Table
```sql
CREATE TABLE ekonomist_news_articles (
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
);
```

## Running Crawlers

### Dunya Crawler (MySQL)
```bash
python3 dunya_crawler_mysql.py
```

### Ekonomist Crawler (MySQL)
```bash
python3 ekonomist_crawler_mysql.py
```

## Service Management

### Check Status
```bash
systemctl status news-crawler.service
```

### Restart Service
```bash
systemctl restart news-crawler.service
```

### View Logs
```bash
journalctl -u news-crawler.service -f
```

### Stop Service
```bash
systemctl stop news-crawler.service
```

## Security Considerations

1. **Firewall**: Configure UFW to allow HTTP/HTTPS traffic
2. **SSL**: Set up Let's Encrypt for HTTPS
3. **Database**: Secure MySQL with strong passwords
4. **Updates**: Keep system and dependencies updated

## Customization

### Change Port
Edit `run_web.py`:
```python
app.run(host='0.0.0.0', port=8080)  # Change port
```

### Custom Domain
Edit `nginx_config.conf`:
```nginx
server_name your-domain.com;
```

### Database Configuration
Edit `mysql_config.py`:
```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'your_user',
    'password': 'your_password',
    'database': 'your_database',
    'charset': 'utf8mb4'
}
```

## Troubleshooting

### Web App Not Starting
```bash
# Check logs
journalctl -u news-crawler.service -f

# Check if port is in use
netstat -tlnp | grep :5000
```

### Database Connection Issues
```bash
# Test MySQL connection
mysql -u root -p -e "SHOW DATABASES;"

# Check MySQL service
systemctl status mysql
```

### Nginx Issues
```bash
# Test configuration
nginx -t

# Check nginx logs
tail -f /var/log/nginx/error.log
```

## File Structure

```
/root/NewsCrawler/
├── app.py                          # Flask web application
├── run_web.py                      # Production runner
├── mysql_config.py                 # Database configuration
├── dunya_crawler_mysql.py          # Dunya crawler (MySQL)
├── ekonomist_crawler_mysql.py      # Ekonomist crawler (MySQL)
├── requirements.txt                 # Python dependencies
├── deploy.sh                       # Deployment script
├── news-crawler.service            # Systemd service file
├── nginx_config.conf               # Nginx configuration
├── templates/                      # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── articles.html
│   └── article_detail.html
└── logs/                          # Application logs
```

## Support

For issues or questions:
1. Check the logs: `journalctl -u news-crawler.service -f`
2. Verify database connection: `mysql -u root -p`
3. Test web interface: `curl http://localhost:5000`
4. Check nginx status: `systemctl status nginx`
