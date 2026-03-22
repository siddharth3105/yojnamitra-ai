# 🚀 Deploy YojnaMitra AI to EC2 - Complete Guide

## ✅ Prerequisites Completed
- Code pushed to GitHub: https://github.com/siddharth3105/yojnamitra-ai
- All syntax errors fixed
- All features implemented and tested

## EC2 Instance Details
- **Public IP**: 13.201.55.10
- **Port**: 8501
- **App URL**: http://13.201.55.10:8501

---

## 🎯 Quick Deploy (Copy-Paste Commands)

### Step 1: Connect to EC2
Go to AWS Console → EC2 → Instances → Select your instance → Click "Connect" → Use "EC2 Instance Connect"

OR use SSH:
```bash
ssh -i your-key.pem ec2-user@13.201.55.10
```

### Step 2: Deploy Latest Code (Single Command)
```bash
cd yojnamitra-ai && git fetch origin && git reset --hard origin/main && pkill -f streamlit && nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

**What this does:**
1. Navigate to app directory
2. Fetch latest code from GitHub
3. Force reset to match GitHub (discard any local changes)
4. Kill old Streamlit process
5. Start new Streamlit in background

### Step 3: Verify Deployment
```bash
tail -30 streamlit.log
```

**Look for these success messages:**
- ✅ "You can now view your Streamlit app in your browser"
- ✅ "Network URL: http://0.0.0.0:8501"
- ✅ No error messages

### Step 4: Check Process is Running
```bash
ps aux | grep streamlit
```

You should see a running streamlit process.

### Step 5: Test Your App
Open in browser: **http://13.201.55.10:8501**

---

## 🔧 Alternative Deployment Methods

### Method 1: If Git Pull Has Conflicts
```bash
cd yojnamitra-ai
git stash
git pull origin main
pkill -f streamlit
nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

### Method 2: Fresh Clone (If Major Issues)
```bash
cd ~
rm -rf yojnamitra-ai
git clone https://github.com/siddharth3105/yojnamitra-ai.git
cd yojnamitra-ai
nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

---

## 🛠️ Troubleshooting

### Issue: Port Already in Use
```bash
# Kill all streamlit processes
pkill -9 -f streamlit

# Verify they're gone
ps aux | grep streamlit

# Start fresh
cd yojnamitra-ai
nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

### Issue: Python Dependencies Missing
```bash
cd yojnamitra-ai
pip install -r requirements.txt
```

### Issue: Environment Variables Not Set
```bash
cd yojnamitra-ai

# Check if .env exists
ls -la .env

# If missing, copy from example
cp .env.example .env

# Then edit with your credentials
nano .env
```

### Issue: Can't Access App from Browser
1. Check EC2 Security Group allows inbound traffic on port 8501
2. Check if Streamlit is running: `ps aux | grep streamlit`
3. Check logs: `tail -50 streamlit.log`

---

## 📊 Monitoring Your App

### View Live Logs
```bash
tail -f streamlit.log
```
Press `Ctrl+C` to stop viewing

### Check App Status
```bash
curl http://localhost:8501
```

### Restart App
```bash
pkill -f streamlit
cd yojnamitra-ai
nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

---

## ✨ What's New in This Deployment

### Features Implemented:
1. ✅ Scheme Filters (match score, category, deadline)
2. ✅ Success Stories section
3. ✅ Download Report feature
4. ✅ Scheme Categories (Agriculture, Health, Education, Business, Housing)
5. ✅ Personalized Reasons for each scheme
6. ✅ Smart Notifications with deadline alerts
7. ✅ WhatsApp Share functionality
8. ✅ Intelligent input validation
9. ✅ Enhanced conversation quality
10. ✅ Save for Later feature
11. ✅ Scheme Comparison tool

### Bug Fixes:
1. ✅ Fixed indentation error (orphaned step-by-step guide text)
2. ✅ Fixed syntax errors in FAQ section
3. ✅ Removed duplicate code blocks
4. ✅ All Python files validated

---

## 🎉 Success Checklist

After deployment, verify:
- [ ] App loads at http://13.201.55.10:8501
- [ ] Welcome message displays correctly
- [ ] Can start conversation with AI
- [ ] Scheme search works
- [ ] All buttons functional (Apply Guide, Quick Apply, Save, Documents)
- [ ] Filters work (match score, category, deadline)
- [ ] Success stories display
- [ ] Download report works
- [ ] WhatsApp share works
- [ ] No error messages in logs

---

## 📞 Need Help?

If deployment fails:
1. Check `streamlit.log` for errors: `tail -50 streamlit.log`
2. Verify Python version: `python --version` (should be 3.8+)
3. Check dependencies: `pip list | grep streamlit`
4. Verify AWS credentials: `aws sts get-caller-identity`

---

**Your YojnaMitra AI app is ready to deploy!** 🚀
