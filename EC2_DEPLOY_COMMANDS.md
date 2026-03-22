# 🚀 EC2 Deployment - Quick Commands

## Connect to EC2
```bash
# Option 1: Use AWS Console
# Go to EC2 → Instances → Connect → EC2 Instance Connect

# Option 2: SSH (if you have the key)
ssh -i your-key.pem ec2-user@13.201.55.10
```

---

## Deploy (Copy-Paste This)
```bash
cd yojnamitra-ai && git fetch origin && git reset --hard origin/main && pkill -f streamlit && nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

---

## Verify Deployment
```bash
tail -30 streamlit.log
```

Look for: ✅ "You can now view your Streamlit app in your browser"

---

## Test Your App
**Open in browser:** http://13.201.55.10:8501

---

## Useful Commands

### Check if app is running
```bash
ps aux | grep streamlit
```

### View live logs
```bash
tail -f streamlit.log
```

### Restart app
```bash
pkill -f streamlit && cd yojnamitra-ai && nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

### Check last errors
```bash
tail -50 streamlit.log | grep -i error
```

---

## That's It! 🎉

Your app should be live at: **http://13.201.55.10:8501**
