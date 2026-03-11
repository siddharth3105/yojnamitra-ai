# Code Quality & Deployment Guide

## 🎯 Goal
Ensure YojnaMitra-AI runs smoothly with zero errors, now and in the future.

---

## ✅ Pre-Deployment Checklist

### 1. Validate Code Syntax
Run the validation script before every commit:

```bash
python validate_code.py
```

This checks all Python files for syntax errors.

### 2. Test Locally
```bash
streamlit run yojnamitra_ai.py
```

Open http://localhost:8501 and test:
- ✅ App loads without errors
- ✅ Authentication works
- ✅ Chat conversation works
- ✅ Scheme recommendations appear
- ✅ Language selection works
- ✅ FAQ expands correctly

### 3. Check Git Status
```bash
git status
```

Make sure you're committing the right files.

### 4. Commit with Clear Message
```bash
git add .
git commit -m "Clear description of what changed"
git push origin main
```

### 5. Deploy to EC2
```bash
# On EC2 Instance Connect
cd yojnamitra-ai
git pull origin main
pkill -f streamlit
nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

### 6. Verify Deployment
```bash
tail -20 streamlit.log
```

Look for: "You can now view your Streamlit app in your browser"

### 7. Test Live App
Open: http://13.201.55.10:8501

---

## 🚫 Common Mistakes to Avoid

### 1. Orphaned else/elif blocks
❌ **BAD:**
```python
if condition:
    do_something()

else:  # No matching if!
    do_something_else()
```

✅ **GOOD:**
```python
if condition:
    do_something()
else:
    do_something_else()
```

### 2. Unclosed strings
❌ **BAD:**
```python
text = "Hello world
```

✅ **GOOD:**
```python
text = "Hello world"
```

### 3. Mismatched quotes in multiline strings
❌ **BAD:**
```python
st.markdown("""
Text with apostrophe: you're
""")  # Can cause issues
```

✅ **GOOD:**
```python
st.markdown("""
Text with apostrophe: you are
""")
```

### 4. Duplicate code blocks
❌ **BAD:**
```python
def function():
    if x:
        return "yes"
    else:
        return "no"
    
    # Unreachable duplicate code below
    if x:
        return "yes"
```

✅ **GOOD:**
```python
def function():
    if x:
        return "yes"
    else:
        return "no"
```

### 5. Missing imports
❌ **BAD:**
```python
# Using random.choice() without import
result = random.choice(options)
```

✅ **GOOD:**
```python
import random
result = random.choice(options)
```

---

## 🔧 Quick Fix Commands

### If app crashes on EC2:
```bash
# Check logs
tail -50 streamlit.log

# Restart app
pkill -f streamlit
nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

### If git has conflicts:
```bash
# Force reset to GitHub version
git fetch origin
git reset --hard origin/main
```

### If syntax error appears:
```bash
# Check which file has error
python -m py_compile yojnamitra_ai.py

# Or use our validator
python validate_code.py
```

---

## 📋 File Structure

```
yojnamitra-ai/
├── yojnamitra_ai.py          # Main app (1400+ lines)
├── auth_components.py         # Authentication
├── database.py                # Database operations
├── rag_engine.py              # RAG for scheme matching
├── s3_storage.py              # AWS S3 storage
├── check_bedrock_models.py    # Model checker
├── validate_code.py           # Code validator (NEW!)
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
└── streamlit.log              # App logs
```

---

## 🎯 Best Practices

### 1. Always validate before commit
```bash
python validate_code.py
```

### 2. Test locally first
```bash
streamlit run yojnamitra_ai.py
```

### 3. Use clear commit messages
```bash
git commit -m "Add feature X" # Good
git commit -m "fix"           # Bad
```

### 4. Check logs after deployment
```bash
tail -20 streamlit.log
```

### 5. Keep .env file secure
- Never commit .env to GitHub
- Use .env.example for template
- Update EC2 .env separately

---

## 🚀 Deployment Workflow

```
1. Make changes locally
   ↓
2. Run validate_code.py
   ↓
3. Test with streamlit run
   ↓
4. Commit to GitHub
   ↓
5. Pull on EC2
   ↓
6. Restart Streamlit
   ↓
7. Check logs
   ↓
8. Test live app
```

---

## 📞 Troubleshooting

### App won't start
1. Check syntax: `python validate_code.py`
2. Check logs: `tail -50 streamlit.log`
3. Check Python version: `python --version` (should be 3.8+)
4. Check dependencies: `pip install -r requirements.txt`

### Git issues
1. Check status: `git status`
2. Check remote: `git remote -v`
3. Force reset: `git reset --hard origin/main`

### AWS issues
1. Check credentials in .env
2. Check AWS region (ap-south-1)
3. Check Bedrock model access
4. Check IAM permissions

---

## ✅ Current Status

All files validated: ✅
- yojnamitra_ai.py ✅
- auth_components.py ✅
- database.py ✅
- rag_engine.py ✅
- s3_storage.py ✅
- check_bedrock_models.py ✅

**Your app is production-ready!** 🎉

---

## 📝 Notes

- Always run `validate_code.py` before pushing
- Test locally before deploying to EC2
- Keep logs clean with regular monitoring
- Update this guide as you add new features

**Happy coding!** 🚀
