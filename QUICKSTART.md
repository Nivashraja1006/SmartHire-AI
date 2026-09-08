# SmartHire AI - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Clone & Install
```bash
# Navigate to project directory
cd ranking

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Or Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Step 2: Configure Database
```bash
# Create MySQL database
mysql -u root -p
mysql> CREATE DATABASE smarthire_ai;
mysql> EXIT;

# Create .env file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Edit .env with your database credentials
# SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:password@localhost/smarthire_ai
```

### Step 3: Initialize Database
```bash
# Apply migrations
flask db upgrade

# Or initialize fresh (WARNING: This clears existing data)
# flask db init
# flask db migrate
# flask db upgrade

# Seed initial data (optional)
python seed_data.py
```

### Step 4: Run Application
```bash
# Start development server
python run.py

# Open browser and navigate to http://localhost:5000
```

---

## 📋 Verification

Before running, verify your setup:
```bash
python verify_setup.py
```

This will check:
- ✅ Python version
- ✅ Required packages
- ✅ spaCy models
- ✅ Database connectivity
- ✅ Environment configuration

---

## 🎯 First Steps

### 1. **Create Admin Account**
- Navigate to `/auth/register`
- Choose "Admin" role
- Set password

### 2. **Add Job Position**
- Login to recruiter dashboard
- Click "New Job"
- Enter job title, description, and requirements

### 3. **Upload Resumes**
- Go to "Upload Resumes"
- Select or drag-drop PDF/DOCX files
- Click "Match Candidates"

### 4. **View Results**
- See ranked candidates with match scores
- Click on candidate for detailed breakdown
- Generate PDF reports

---

## 🧪 Test Data

### Generate Sample Data
```bash
python seed_data.py
```

This creates:
- 1 admin user (admin@example.com / admin123)
- 2 recruiters
- 5 sample jobs
- 20 sample candidates with parsed resumes

### Test Users

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@example.com | admin123 |
| Recruiter | recruiter@example.com | recruiter123 |
| Candidate | candidate@example.com | candidate123 |

---

## 📊 API Quick Reference

### Upload Resume
```bash
curl -X POST http://localhost:5000/api/ranking/upload-resume \
  -H "Authorization: Bearer <token>" \
  -F "file=@resume.pdf"
```

### Rank Candidates
```bash
curl -X POST http://localhost:5000/api/ranking/rank \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"job_id": 1, "force": false}'
```

### Get Results
```bash
curl -X GET http://localhost:5000/api/ranking/results/1 \
  -H "Authorization: Bearer <token>"
```

---

## 🐛 Troubleshooting

### Issue: MySQL Connection Error
**Solution:**
- Ensure MySQL is running
- Check credentials in .env
- Verify database exists: `mysql -u root -p -e "SHOW DATABASES;"`

### Issue: Module Not Found
**Solution:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Issue: spaCy Model Not Found
**Solution:**
```bash
python -m spacy download en_core_web_sm
```

### Issue: Port Already in Use
**Solution:**
```bash
# Run on different port
export FLASK_PORT=5001  # Linux/Mac
set FLASK_PORT=5001     # Windows
python run.py
```

---

## 🔐 Security Tips

1. **Change SECRET_KEY** in .env
2. **Use strong database password**
3. **Enable HTTPS** in production
4. **Set FLASK_ENV=production** for deployment
5. **Disable DEBUG mode** in production

---

## 📚 Useful Commands

```bash
# Initialize database migrations
flask db init

# Create migration
flask db migrate -m "add user fields"

# Apply migrations
flask db upgrade

# Rollback migrations
flask db downgrade

# Reset database (WARNING: Deletes all data)
flask db downgrade base  # Revert all migrations
flask db upgrade          # Reapply migrations

# Seed data
python seed_data.py

# Run tests
pytest tests/ -v

# Check for style issues
pylint app/

# Format code
black app/
```

---

## 🚀 Deployment Checklist

Before deploying to production:

- [ ] Change SECRET_KEY in config.py
- [ ] Set FLASK_ENV=production
- [ ] Set DEBUG=False
- [ ] Use strong MySQL password
- [ ] Enable HTTPS/SSL
- [ ] Setup email for notifications
- [ ] Configure logging
- [ ] Run database migrations
- [ ] Test all features
- [ ] Setup backup strategy

---

## 📖 Next Steps

1. **Read Full Documentation**: See `SMARTHIRE_README.md`
2. **Explore APIs**: Visit `/api/docs` (if Swagger enabled)
3. **Customize Scoring**: Edit weights in `app/ai/scoring_engine.py`
4. **Add Skills**: Populate skill database
5. **Configure Email**: Setup for notifications

---

## ✨ Features to Explore

- 🎨 Premium UI with glassmorphism
- 📊 Real-time dashboards with WebSocket
- 🔍 Smart search and filtering
- 📈 Detailed analytics and insights
- 🤖 Explainable AI matching
- 📱 Responsive mobile design
- 🔐 Role-based access control
- 📄 PDF report generation

---

## 💬 Support

- **Documentation**: See `SMARTHIRE_README.md`
- **Issues**: Check GitHub issues
- **Discussion**: Post in discussions forum

---

**Happy Hiring! 🎉**
