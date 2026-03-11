# Deploy Double Message Fix - Step by Step Guide

## Issue Fixed
✅ AI was displaying messages twice (duplicate display bug)
✅ Fixed in `yojnamitra_ai.py` - removed duplicate message rendering code

---

## STEP 1: Push Fix to GitHub (On Your Windows Machine)

### 1.1 Open Command Prompt or PowerShell
- Press `Win + R`
- Type `cmd` or `powershell`
- Press Enter

### 1.2 Navigate to Your Project Folder
```bash
cd C:\Users\suraj\OneDrive\Desktop\yojnamitra-app
```

### 1.3 Check Git Status
```bash
git status
```
You should see `yojnamitra_ai.py` as modified.

### 1.4 Add the Fixed File
```bash
git add yojnamitra_ai.py
```

### 1.5 Commit the Fix
```bash
git commit -m "Fix double message display bug"
```

### 1.6 Push to GitHub
```bash
git push origin main
```

**If you get authentication error:**
```bash
# Set your GitHub username
git config --global user.name "siddharth3105"

# Set your email
git config --global user.email "your-email@example.com"

# Try pushing again
git push origin main
```

**If it asks for password:**
- Use your GitHub Personal Access Token (not your password)
- Or use GitHub Desktop app for easier authentication

---

## STEP 2: Deploy to EC2 (In Browser)

### 2.1 Open AWS Console
1. Go to: https://console.aws.amazon.com/
2. Login with your credentials
3. Make sure region is set to **ap-south-1 (Mumbai)**

### 2.2 Connect to EC2 Instance
1. Go to **EC2** service (search in top bar)
2. Click **Instances** in left sidebar
3. Find instance: `i-01826124d42c6b8f8a` (Public IP: 13.201.55.10)
4. Select the instance (checkbox)
5. Click **Connect** button (top right)
6. Choose **EC2 Instance Connect** tab
7. Click **Connect** button

**A new browser tab will open with a terminal!**

### 2.3 Navigate to Your App Directory
In the EC2 terminal, type:
```bash
cd yojnamitra-ai
```
Press Enter.

### 2.4 Pull Latest Code from GitHub
```bash
git pull origin main
```
Press Enter.

You should see:
```
Updating 0fb2684..abc1234
Fast-forward
 yojnamitra_ai.py | 4 ----
 1 file changed, 4 deletions(-)
```

### 2.5 Stop Current Streamlit Process
```bash
pkill -f streamlit
```
Press Enter.

Wait 2 seconds.

### 2.6 Verify Streamlit is Stopped
```bash
ps aux | grep streamlit
```
Press Enter.

You should see only one line with "grep streamlit" (not the actual streamlit process).

### 2.7 Restart Streamlit with Fixed Code
```bash
nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```
Press Enter.

You'll see something like:
```
[1] 12345
```

### 2.8 Verify Streamlit is Running
```bash
ps aux | grep streamlit
```
Press Enter.

You should see a line like:
```
ec2-user   12345  2.3  5.6 505948 53036 pts/0    Sl   14:30   0:00 /usr/bin/python3.11 /home/ec2-user/.local/bin/streamlit run yojnamitra_ai.py
```

### 2.9 Check Logs (Optional)
```bash
tail -20 streamlit.log
```
Press Enter.

You should see:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://172.31.41.134:8501
External URL: http://13.201.55.10:8501
```

Press `Ctrl+C` to exit log view.

---

## STEP 3: Test the Fix

### 3.1 Open Your App
Open browser and go to:
```
http://13.201.55.10:8501
```

### 3.2 Test the Chat
1. Login with your phone number
2. Type a message: "Hello"
3. **Check**: AI should respond ONLY ONCE (not twice!)
4. Type another message: "I am 25 years old"
5. **Check**: AI should respond ONLY ONCE

### 3.3 Test Language Feature
1. Look at sidebar - you should see "🌐 Language / भाषा" dropdown
2. Select "हिंदी (Hindi)"
3. Type a message
4. **Check**: AI response should be in Hindi

---

## STEP 4: Verify Everything Works

### Checklist:
- [ ] App loads at http://13.201.55.10:8501
- [ ] Login works
- [ ] Chat works
- [ ] AI responds only ONCE (not twice) ✅ FIXED
- [ ] Language dropdown appears in sidebar
- [ ] Language translation works
- [ ] Scheme matching works
- [ ] "Get Step-by-Step Guide" button works

---

## Troubleshooting

### Problem: Git push fails with authentication error
**Solution:**
```bash
# Use GitHub Desktop app instead
# OR generate Personal Access Token:
# 1. Go to GitHub.com → Settings → Developer Settings → Personal Access Tokens
# 2. Generate new token (classic)
# 3. Select "repo" scope
# 4. Copy token
# 5. Use token as password when pushing
```

### Problem: EC2 terminal shows "Permission denied"
**Solution:**
```bash
# Make sure you're in the right directory
pwd
# Should show: /home/ec2-user/yojnamitra-ai

# If not, navigate there:
cd /home/ec2-user/yojnamitra-ai
```

### Problem: Streamlit won't start
**Solution:**
```bash
# Check if port 8501 is already in use
sudo lsof -i :8501

# If something is using it, kill it:
sudo kill -9 <PID>

# Then restart Streamlit
nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

### Problem: App shows old version (still double messages)
**Solution:**
```bash
# Clear browser cache:
# Press Ctrl+Shift+R (hard refresh)

# OR

# In EC2, verify you pulled latest code:
cd yojnamitra-ai
git log -1
# Should show: "Fix double message display bug"

# If not, pull again:
git pull origin main
```

### Problem: Language dropdown not showing
**Solution:**
```bash
# In EC2, check if you have the latest code:
cd yojnamitra-ai
git log -2
# Should show both commits:
# 1. "Fix double message display bug"
# 2. "Add language selection with Amazon Translate"

# If not:
git pull origin main
pkill -f streamlit
nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

---

## Quick Commands Reference

### On Windows (Git):
```bash
cd C:\Users\suraj\OneDrive\Desktop\yojnamitra-app
git status
git add yojnamitra_ai.py
git commit -m "Fix double message display bug"
git push origin main
```

### On EC2 (Deploy):
```bash
cd yojnamitra-ai
git pull origin main
pkill -f streamlit
nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
ps aux | grep streamlit
```

### Check Status:
```bash
# On EC2:
ps aux | grep streamlit          # Check if running
tail -20 streamlit.log           # Check logs
curl http://localhost:8501       # Test locally
```

---

## Success Indicators

✅ **Git Push Success:**
```
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Writing objects: 100% (3/3), 320 bytes | 320.00 KiB/s, done.
Total 3 (delta 2), reused 0 (delta 0)
To https://github.com/siddharth3105/yojnamitra-ai.git
   0fb2684..abc1234  main -> main
```

✅ **Git Pull Success:**
```
Updating 0fb2684..abc1234
Fast-forward
 yojnamitra_ai.py | 4 ----
 1 file changed, 4 deletions(-)
```

✅ **Streamlit Running:**
```
ec2-user   12345  2.3  5.6 505948 53036 pts/0    Sl   14:30   0:00 /usr/bin/python3.11 /home/ec2-user/.local/bin/streamlit run yojnamitra_ai.py
```

✅ **App Working:**
- Opens at http://13.201.55.10:8501
- AI responds only once per message
- Language dropdown visible
- No errors in console

---

## Need Help?

If you get stuck at any step:
1. Take a screenshot of the error
2. Copy the exact error message
3. Note which step you're on
4. Ask for help with specific details

**Common Issues:**
- Git authentication → Use GitHub Desktop or Personal Access Token
- EC2 connection → Use EC2 Instance Connect (browser-based)
- Streamlit not starting → Check logs with `tail -50 streamlit.log`
- Old version showing → Hard refresh browser (Ctrl+Shift+R)

---

**You're almost there! Just follow these steps one by one. Good luck! 🚀**
