# Football Focus API - Troubleshooting Guide

## Common Issues and Solutions

### 1. Supabase Client Proxy Error

**Error:** `Client.__init__() got an unexpected keyword argument 'proxy'`

**Cause:** Version incompatibility between Supabase client and its dependencies.

**Solutions:**

#### Option A: Clean Installation (Recommended)
```bash
# Remove existing virtual environment
rm -rf venv  # On Windows: rmdir /s venv

# Run the setup script
python setup.py
```

#### Option B: Manual Dependency Fix
```bash
# Uninstall conflicting packages
pip uninstall supabase gotrue httpx -y

# Install specific compatible versions
pip install httpx==0.25.2
pip install gotrue==2.5.0
pip install supabase==2.7.4
```

#### Option C: Use Simple HTTP Version
If dependency issues persist, use the alternative implementation:
```bash
# Use the simple HTTP version instead
python app_simple.py
```

### 2. Environment Variables Not Found

**Error:** `SUPABASE_URL and SUPABASE_KEY must be set`

**Solution:**
```bash
# Copy environment template
cp env_template.txt .env

# Edit .env file with your credentials
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your-anon-key
```

### 3. Database Connection Issues

**Error:** Connection timeouts or authentication failures

**Solutions:**

#### Check Supabase Credentials
1. Go to your Supabase dashboard
2. Navigate to Settings > API
3. Copy the correct URL and anon key
4. Ensure no trailing slashes in URL

#### Test Connection
```bash
# Use the test endpoint
curl http://localhost:5000/api/test

# Or use the simple version
python app_simple.py
# Then test: curl http://localhost:5000/api/test
```

### 4. Import Errors

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
# Ensure you're in the virtual environment
# Windows:
venv\Scripts\activate

# Unix/Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Port Already in Use

**Error:** `Address already in use: Port 5000`

**Solutions:**
```bash
# Option 1: Use different port
python run.py --port 8000

# Option 2: Kill process using port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Unix/Linux/macOS:
lsof -ti:5000 | xargs kill -9
```

### 6. CORS Issues

**Error:** Cross-origin request blocked

**Solution:**
CORS is already enabled in the Flask app. If issues persist:

```python
# In app.py, update CORS configuration
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
```

### 7. No Data Returned

**Error:** Empty responses from API

**Possible Causes:**
1. Database tables are empty
2. Fixture service hasn't run yet
3. Wrong table structure

**Solutions:**
```bash
# Check if tables exist and have data
curl http://localhost:5000/api/test

# Run the fixture service to generate articles
cd ../crew_ai/fixture_service
python run_service.py --process-only

# Check article count
curl http://localhost:5000/api/stats
```

## Step-by-Step Debugging

### 1. Basic Environment Check
```bash
# Check Python version (should be 3.8+)
python --version

# Check if virtual environment exists
ls venv/  # Should show Scripts/ (Windows) or bin/ (Unix)

# Check if .env file exists
cat .env  # Should show your Supabase credentials
```

### 2. Dependency Check
```bash
# Activate virtual environment
source venv/bin/activate  # Unix
# OR
venv\Scripts\activate  # Windows

# Check installed packages
pip list | grep -E "(flask|supabase|gotrue|httpx)"

# Should show:
# Flask         3.0.0
# supabase      2.7.4
# gotrue        2.5.0
# httpx         0.25.2
```

### 3. Database Connection Test
```bash
# Test with simple version first
python app_simple.py

# In another terminal:
curl http://localhost:5000/health
curl http://localhost:5000/api/test
```

### 4. Full API Test
```bash
# If simple version works, try full version
python app.py

# Run comprehensive tests
python test_api.py
```

## Alternative Solutions

### Use Docker (If Available)
```dockerfile
# Create Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app_simple.py"]
```

```bash
# Build and run
docker build -t football-api .
docker run -p 5000:5000 --env-file .env football-api
```

### Use Different Python Version
If using Python 3.12+, try with Python 3.10 or 3.11:
```bash
# Using pyenv (if available)
pyenv install 3.11.0
pyenv local 3.11.0

# Create new virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Getting Help

### Collect Debug Information
When reporting issues, include:

1. **Python Version:** `python --version`
2. **Operating System:** Windows/macOS/Linux
3. **Package Versions:** `pip list`
4. **Error Message:** Full traceback
5. **Environment Variables:** (Do NOT include actual keys)
   ```bash
   echo "SUPABASE_URL set: $(test -n "$SUPABASE_URL" && echo "YES" || echo "NO")"
   echo "SUPABASE_KEY set: $(test -n "$SUPABASE_KEY" && echo "YES" || echo "NO")"
   ```

### Common Commands for Debugging
```bash
# Full clean reinstall
rm -rf venv
python setup.py

# Test with simple version
python app_simple.py

# Check logs
tail -f *.log

# Test specific endpoint
curl -v http://localhost:5000/api/gameweek/latest
```

## Quick Fixes Summary

| Issue | Quick Fix |
|-------|-----------|
| Proxy error | Use `app_simple.py` |
| Missing env vars | Copy `env_template.txt` to `.env` |
| Import errors | Activate venv: `source venv/bin/activate` |
| Port in use | Use different port: `python run.py --port 8000` |
| No data | Run fixture service first |
| Connection fails | Check Supabase credentials |

## Success Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed correctly
- [ ] .env file configured with valid Supabase credentials
- [ ] Database tables exist and have data
- [ ] API starts without errors
- [ ] Health check returns 200: `curl http://localhost:5000/health`
- [ ] Test endpoint works: `curl http://localhost:5000/api/test`
- [ ] Articles endpoint returns data: `curl http://localhost:5000/api/articles`

If all items are checked, your API should be working correctly!
