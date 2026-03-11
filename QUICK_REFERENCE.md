# 🚀 Quick Reference - YojnaMitra-AI

## Before Every Change
```bash
python validate_code.py
```

## Test Locally
```bash
streamlit run yojnamitra_ai.py
```

## Commit to GitHub
```bash
git add .
git commit -m "Your message"
git push origin main
```

## Deploy to EC2
```bash
cd yojnamitra-ai && git pull origin main && pkill -f streamlit && nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

## Check Logs
```bash
tail -20 streamlit.log
```

## Test Live App
http://13.201.55.10:8501

---

## If Something Breaks

### Syntax Error?
```bash
python validate_code.py
```

### Git Conflict?
```bash
git fetch origin
git reset --hard origin/main
```

### App Won't Start?
```bash
tail -50 streamlit.log
pkill -f streamlit
nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

---

**That's it! Keep it simple.** 🎯
