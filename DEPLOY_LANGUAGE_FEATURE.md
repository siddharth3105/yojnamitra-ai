# 🚀 Deploy Language Selection Feature - Step by Step

## Issue: Language selector not showing on deployed app

### Root Cause
The changes are in your local files but haven't been pushed to GitHub and deployed to EC2 yet.

---

## ✅ SOLUTION: Complete Deployment Steps

### STEP 1: Commit Changes to GitHub (Run on your local machine)

```bash
# Check what files changed
git status

# Add the modified file
git add yojnamitra_ai.py

# Add documentation files
git add LANGUAGE_FEATURE_ADDED.md DEPLOY_LANGUAGE_FEATURE.md

# Commit with message
git commit -m "Add language selection feature with Amazon Translate integration"

# Push to GitHub
git push origin main
```

---

### STEP 2: Deploy to EC2 (Run in EC2 Instance Connect terminal)

#### 2.1 Navigate to project directory
```bash
cd yojnamitra-ai
```

#### 2.2 Pull latest code from GitHub
```bash
git pull origin main
```

**Expected output:**
```
Updating xxxxx..xxxxx
Fast-forward
 yojnamitra_ai.py | XX insertions(+), XX deletions(-)
```

#### 2.3 Verify the changes are there
```bash
grep -n "Language / भाषा" yojnamitra_ai.py
```

**Expected output:** Should show line number where language selector code is

#### 2.4 Stop current Streamlit process
```bash
pkill -f streamlit
```

#### 2.5 Verify Streamlit stopped
```bash
ps aux | grep streamlit
```

**Expected output:** Should show only the grep command itself, no streamlit process

#### 2.6 Set environment variables
```bash
export BEDROCK_ACCESS_KEY_ID=<your_key>
export BEDROCK_SECRET_ACCESS_KEY=<your_secret>
export BEDROCK_REGION=ap-south-1
export BEDROCK_MODEL_ID=qwen.qwen3-235b-a22b-2507-v1:0
```

#### 2.7 Restart Streamlit
```bash
nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

#### 2.8 Verify Streamlit started
```bash
ps aux | grep streamlit
```

**Expected output:** Should show streamlit process running

#### 2.9 Check logs for errors
```bash
tail -30 streamlit.log
```

**Look for:**
- "You can now view your Streamlit app in your browser"
- No error messages
- External URL: http://13.201.55.10:8501

#### 2.10 Monitor logs in real-time (optional)
```bash
tail -f streamlit.log
```

Press `Ctrl+C` to exit

---

### STEP 3: Test the Feature

1. **Open browser:** http://13.201.55.10:8501
2. **Hard refresh:** Press `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
3. **Check sidebar:** Look for "🌐 Language / भाषा" at the top
4. **Test selector:** Click dropdown and select a language
5. **Verify translation:** AI responses should translate

---

## 🐛 Troubleshooting

### Issue 1: "git pull" says "Already up to date"
**Cause:** Changes not pushed to GitHub yet  
**Solution:** Run STEP 1 first (commit and push from local machine)

### Issue 2: Language selector still not showing
**Cause:** Browser cache  
**Solution:** 
- Hard refresh: `Ctrl+Shift+R`
- Or clear browser cache
- Or try incognito/private window

### Issue 3: Streamlit won't start
**Cause:** Port already in use or syntax error  
**Solution:**
```bash
# Check for syntax errors
python3 -m py_compile yojnamitra_ai.py

# If no errors, kill all streamlit processes
pkill -9 -f streamlit

# Then restart
nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

### Issue 4: Translation not working
**Cause:** Amazon Translate permissions  
**Solution:** Check AWS credentials have Translate permissions

### Issue 5: "Module not found" error
**Cause:** Missing dependencies  
**Solution:**
```bash
pip install boto3 --upgrade
```

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] App loads at http://13.201.55.10:8501
- [ ] Sidebar shows "🌐 Language / भाषा"
- [ ] Dropdown has 12 language options
- [ ] Default is "English/Hindi/Hinglish (Auto)"
- [ ] Selecting a language shows success message
- [ ] AI responses get translated (for regional languages)
- [ ] No errors in streamlit.log

---

## 📸 What You Should See

### Sidebar (Top Section):
```
┌─────────────────────────────┐
│ 🌐 Language / भाषा          │
│                             │
│ Select your preferred       │
│ language:                   │
│ ┌─────────────────────────┐ │
│ │ English/Hindi/Hinglish  │ │
│ │ (Auto)              ▼   │ │
│ └─────────────────────────┘ │
│                             │
│ ───────────────────────────│
│                             │
│ ### 👤 Logged In            │
│ 📱 +91XXXXXXXXXX            │
└─────────────────────────────┘
```

### Dropdown Options:
```
English/Hindi/Hinglish (Auto)
हिंदी (Hindi)
தமிழ் (Tamil)
తెలుగు (Telugu)
বাংলা (Bengali)
मराठी (Marathi)
ગુજરાતી (Gujarati)
ಕನ್ನಡ (Kannada)
മലയാളം (Malayalam)
ਪੰਜਾਬੀ (Punjabi)
ଓଡ଼ିଆ (Odia)
অসমীয়া (Assamese)
```

---

## 🎥 For Demo Video

Once working, record:
1. **Show sidebar** - Language selector at top
2. **Select Tamil** - Show dropdown and selection
3. **AI responds** - Show translated response in Tamil
4. **Select Bengali** - Show another language
5. **AI responds** - Show translated response in Bengali

---

## 📞 Quick Commands Reference

### On Local Machine (Windows):
```bash
git add yojnamitra_ai.py LANGUAGE_FEATURE_ADDED.md
git commit -m "Add language selection with Amazon Translate"
git push origin main
```

### On EC2 Instance:
```bash
cd yojnamitra-ai
git pull origin main
pkill -f streamlit
export BEDROCK_ACCESS_KEY_ID=<your_key>
export BEDROCK_SECRET_ACCESS_KEY=<your_secret>
export BEDROCK_REGION=ap-south-1
export BEDROCK_MODEL_ID=qwen.qwen3-235b-a22b-2507-v1:0
nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
tail -f streamlit.log
```

---

## 🎯 Expected Result

After successful deployment:
- ✅ Language selector visible in sidebar
- ✅ 12 languages available
- ✅ Real-time translation working
- ✅ No errors in logs
- ✅ App responsive and fast

---

**Status:** Ready to deploy  
**Next Step:** Run STEP 1 (commit to GitHub) then STEP 2 (deploy to EC2)

**Built with ❤️ for 500M+ Indians**  
**Powered by AWS | Qwen3 235B | Amazon Translate**
