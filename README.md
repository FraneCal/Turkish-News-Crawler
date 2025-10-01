# News Crawler Setup Guide

Complete setup guide for the Dunya and Ekonomist news crawlers with virtual environment configuration.

## 📋 Prerequisites

- **Python 3.8+** installed on your system
- **Git** (optional, for version control)
- **Windows/Linux/macOS** compatible

## 🚀 Quick Setup

### 1. Clone or Download Project

```bash
# If using Git
git clone <repository-url>
cd NewsCrawler

# Or download and extract the project files
```

### 2. Create Virtual Environment

#### **Windows:**
```bash
# Create virtual environment
python -m venv news_crawler_env

# Activate virtual environment
news_crawler_env\Scripts\activate

# Verify activation (should show (news_crawler_env) in prompt)
```

#### **Linux/macOS:**
```bash
# Create virtual environment
python3 -m venv news_crawler_env

# Activate virtual environment
source news_crawler_env/bin/activate

# Verify activation (should show (news_crawler_env) in prompt)
```

### 3. Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
# Check installed packages
pip list

# Test Python imports
python -c "import requests, sqlite3, bs4; print('✅ All dependencies installed successfully!')"
```

## 📦 Dependencies

The `requirements.txt` file includes:

```txt
requests>=2.31.0
beautifulsoup4>=4.12.0
urllib3>=2.0.0
lxml>=4.9.0
```

### Manual Installation (if needed):
```bash
pip install requests beautifulsoup4 urllib3 lxml
```

## 🏃‍♂️ Running the Crawlers

### **Dunya Crawler:**
```bash
# Activate virtual environment first
news_crawler_env\Scripts\activate  # Windows
# OR
source news_crawler_env/bin/activate  # Linux/macOS

# Run Dunya crawler
python dunya_crawler.py

# Or import and use programmatically
python -c "
from dunya_crawler import DunyaCrawler
crawler = DunyaCrawler()
crawler.run_smart_crawler('2025-09-01', '2025-09-20')
"
```

### **Ekonomist Crawler:**
```bash
# Activate virtual environment first
news_crawler_env\Scripts\activate  # Windows
# OR
source news_crawler_env/bin/activate  # Linux/macOS

# Run Ekonomist crawler
python ekonomist_crawler_v2.py

# Or import and use programmatically
python -c "
from ekonomist_crawler_v2 import EkonomistCrawler
crawler = EkonomistCrawler()
crawler.run_crawler(start_page=1, end_page=10)
"
```

## 🗂️ Project Structure

```
NewsCrawler/
├── 📄 dunya_crawler.py              # Main Dunya crawler
├── 📄 ekonomist_crawler_v2.py       # Main Ekonomist crawler
├── 📄 requirements.txt              # Python dependencies
├── 📄 .gitignore                    # Git ignore file
├── 📁 news_crawler_env/             # Virtual environment (created by you)
├── 📁 logs/                         # Crawler execution logs
├── 📁 archive/                      # Old/unused files
├── 📁 debug_files/                  # Debug and analysis scripts
├── 📊 duniya_news.db                # Dunya articles database
├── 📊 ekonomist_news_v2.db          # Ekonomist articles database
├── 📖 README_Setup.md               # This setup guide
├── 📖 README_Dunya_Crawler.md       # Dunya crawler documentation
└── 📖 README_Ekonomist_Crawler.md   # Ekonomist crawler documentation
```

## ⚙️ Configuration

### **Environment Variables (Optional):**
```bash
# Set custom database paths
export DUNYA_DB_PATH="custom_dunya.db"
export EKONOMIST_DB_PATH="custom_ekonomist.db"

# Set log level
export LOG_LEVEL="INFO"
```

### **Custom Configuration:**
```python
# Dunya Crawler
from dunya_crawler import DunyaCrawler
crawler = DunyaCrawler(db_path="my_custom_dunya.db")

# Ekonomist Crawler  
from ekonomist_crawler_v2 import EkonomistCrawler
crawler = EkonomistCrawler(db_path="my_custom_ekonomist.db")
```

## 🔧 Troubleshooting

### **Common Issues:**

#### **1. Virtual Environment Not Activating:**
```bash
# Windows - try different activation methods
news_crawler_env\Scripts\activate.bat
# OR
news_crawler_env\Scripts\Activate.ps1

# Linux/macOS - check bash vs zsh
source news_crawler_env/bin/activate
```

#### **2. Permission Errors (Windows):**
```bash
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### **3. SSL Certificate Errors:**
```bash
# Upgrade certificates
pip install --upgrade certifi
# OR
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
```

#### **4. UTF-8 Encoding Issues (Windows):**
```bash
# Set environment variables
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=utf-8
```

#### **5. Database Lock Errors:**
```bash
# Close any open database connections
# Delete .db-journal files if they exist
del *.db-journal
```

### **Dependency Issues:**
```bash
# Clear pip cache
pip cache purge

# Reinstall all packages
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

## 🧪 Testing Installation

### **Quick Test Script:**
```python
# test_setup.py
import sys
import sqlite3
import requests
from bs4 import BeautifulSoup

def test_setup():
    print(f"✅ Python version: {sys.version}")
    
    try:
        # Test database
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.close()
        print("✅ SQLite working")
    except Exception as e:
        print(f"❌ SQLite error: {e}")
    
    try:
        # Test requests
        response = requests.get("https://httpbin.org/get", timeout=5)
        print("✅ Requests working")
    except Exception as e:
        print(f"❌ Requests error: {e}")
    
    try:
        # Test BeautifulSoup
        soup = BeautifulSoup("<html><body>test</body></html>", 'html.parser')
        print("✅ BeautifulSoup working")
    except Exception as e:
        print(f"❌ BeautifulSoup error: {e}")

if __name__ == "__main__":
    test_setup()
```

Run test:
```bash
python test_setup.py
```

## 📊 Output Files

### **Database Files:**
- `duniya_news.db` - Dunya articles with full HTML content
- `ekonomist_news_v2.db` - Ekonomist articles with full HTML content

### **Log Files:**
- `logs/dunya_crawler_YYYYMMDD_HHMMSS.log` - Dunya crawler logs
- `logs/ekonomist_crawler_YYYYMMDD_HHMMSS.log` - Ekonomist crawler logs

### **Database Schema:**
Both databases use the same schema for consistency:
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
);
```

## 🔄 Virtual Environment Management

### **Deactivate Virtual Environment:**
```bash
deactivate
```

### **Recreate Virtual Environment:**
```bash
# Remove old environment
rm -rf news_crawler_env  # Linux/macOS
# OR
rmdir /s news_crawler_env  # Windows

# Create new environment
python -m venv news_crawler_env
news_crawler_env\Scripts\activate  # Windows
# OR  
source news_crawler_env/bin/activate  # Linux/macOS

# Reinstall dependencies
pip install -r requirements.txt
```

### **Export Current Environment:**
```bash
# Generate requirements from current environment
pip freeze > requirements_current.txt
```

## 📝 Development Setup

### **For Development:**
```bash
# Install additional development tools
pip install pytest black flake8 mypy

# Add to requirements_dev.txt
echo "pytest>=7.0.0" >> requirements_dev.txt
echo "black>=22.0.0" >> requirements_dev.txt
echo "flake8>=4.0.0" >> requirements_dev.txt
```

### **IDE Configuration:**
- **VS Code/Cursor**: Select the virtual environment interpreter
  - `Ctrl+Shift+P` → "Python: Select Interpreter" 
  - Choose `news_crawler_env/Scripts/python.exe` (Windows) or `news_crawler_env/bin/python` (Linux/macOS)

## 🆘 Support

If you encounter issues:

1. **Check Python version**: `python --version` (should be 3.8+)
2. **Verify virtual environment**: Look for `(news_crawler_env)` in your prompt
3. **Check dependencies**: `pip list` should show all required packages
4. **Check logs**: Look in the `logs/` directory for detailed error messages
5. **Database issues**: Ensure no other processes are using the database files

## 🎯 Quick Start Summary

```bash
# 1. Create and activate virtual environment
python -m venv news_crawler_env
news_crawler_env\Scripts\activate  # Windows
source news_crawler_env/bin/activate  # Linux/macOS

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run crawlers
python dunya_crawler.py
python ekonomist_crawler_v2.py

# 4. Check results
ls *.db  # Should show duniya_news.db and ekonomist_news_v2.db
```

Happy crawling! 🕷️📰
