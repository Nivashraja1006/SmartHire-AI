#!/usr/bin/env python
"""
SmartHire AI - Setup & Verification Script
Verifies all dependencies and configurations
"""

import sys
import os
import subprocess

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_mysql():
    """Check MySQL connectivity."""
    try:
        import pymysql
        print("✅ PyMySQL installed")
        return True
    except ImportError:
        print("❌ PyMySQL not installed (pip install PyMySQL)")
        return False

def check_spacy_model():
    """Check spaCy model."""
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
        print("✅ spaCy en_core_web_sm model installed")
        return True
    except OSError:
        print("⚠️  spaCy model not found. Installing...")
        subprocess.run([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'])
        return True
    except ImportError:
        print("❌ spaCy not installed")
        return False

def check_dependencies():
    """Check all required dependencies."""
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'flask_socketio',
        'pymysql',
        'spacy',
        'nltk',
        'scikit-learn',
        'pdfplumber',
        'python-docx',
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    return len(missing) == 0, missing

def check_env_file():
    """Check .env file exists."""
    if os.path.exists('.env'):
        print("✅ .env file exists")
        return True
    else:
        print("⚠️  .env file not found. Creating template...")
        create_env_template()
        return False

def create_env_template():
    """Create .env template file."""
    template = """# SmartHire AI Configuration

# Database
SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:password@localhost/smarthire_ai
SQLALCHEMY_TRACK_MODIFICATIONS=False

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-super-secret-key-change-this

# Upload Settings
UPLOAD_FOLDER=instance/uploads
MAX_CONTENT_LENGTH=26214400  # 25MB

# AI Settings
USE_LOCAL_SENTENCE_TRANSFORMER=False
LOCAL_SENTENCE_MODEL=all-MiniLM-L6-v2

# Server
DEBUG=True
PORT=5000
HOST=0.0.0.0

# Email (Optional)
MAIL_SERVER=localhost
MAIL_PORT=25
MAIL_USERNAME=
MAIL_PASSWORD=

# Admin User (Set at first run)
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
"""
    with open('.env', 'w') as f:
        f.write(template)
    print("✅ Created .env.template")

def verify_database():
    """Verify database connection."""
    try:
        import pymysql
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password=os.getenv('MYSQL_PASSWORD', 'password'),
            database='smarthire_ai'
        )
        conn.close()
        print("✅ MySQL connection successful")
        return True
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        print("   Ensure MySQL is running and credentials are correct in .env")
        return False

def check_migrations():
    """Check if database is migrated."""
    if os.path.exists('migrations'):
        print("✅ Migrations folder exists")
        return True
    else:
        print("⚠️  Migrations not initialized")
        return False

def run_verification():
    """Run all verifications."""
    print("\n" + "="*60)
    print("🔧 SmartHire AI - Setup Verification")
    print("="*60 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("PyMySQL", check_mysql),
        ("Dependencies", lambda: check_dependencies()[0]),
        ("Environment File", check_env_file),
        ("spaCy Model", check_spacy_model),
        ("Migrations", check_migrations),
        ("Database Connection", verify_database),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n[{name}]")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"⚠️  Check failed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Verification Summary")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🚀 All checks passed! Ready to run:")
        print("   python run.py")
    else:
        print("\n⚠️  Please fix the issues above before running the application.")
    
    return passed == total

if __name__ == '__main__':
    success = run_verification()
    sys.exit(0 if success else 1)
