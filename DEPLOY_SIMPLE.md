# 🚀 Simple Deployment Guide
## Get Your App Online in 30 Minutes

---

## ⚡ Fastest Option: Streamlit Community Cloud (FREE)

**Time:** 15 minutes  
**Cost:** $0  
**Difficulty:** Easy  
**Best for:** Hackathon demo

### Step 1: Prepare Your Code (5 minutes)

```bash
# 1. Create .streamlit/config.toml
mkdir .streamlit
```

Create `.streamlit/config.toml`:
```toml
[server]
headless = true
port = 8501

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

Create `.streamlit/secrets.toml` (for Streamlit Cloud):
```toml
AWS_ACCESS_KEY_ID = "YOUR_AWS_ACCESS_KEY"
AWS_SECRET_ACCESS_KEY = "YOUR_AWS_SECRET_KEY"
AWS_REGION = "ap-south-1"
BEDROCK_MODEL_ID = "qwen.qwen3-235b-a22b-2507-v1:0"
BEDROCK_EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
```

Update `yojnamitra_ai.py` to read from Streamlit secrets:
```python
# Replace load_dotenv() section with:
import streamlit as st

# Try Streamlit secrets first, then .env
try:
    AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]
    AWS_REGION = st.secrets["AWS_REGION"]
    BEDROCK_MODEL_ID = st.secrets["BEDROCK_MODEL_ID"]
except:
    from dotenv import load_dotenv
    load_dotenv()
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION')
    BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID')
```

### Step 2: Push to GitHub (5 minutes)

```bash
# Initialize git (if not done)
git init
git add .
git commit -m "YojnaMitra-AI ready for deployment"

# Create repo on github.com
# Then:
git remote add origin https://github.com/[your-username]/yojnamitra-ai.git
git branch -M main
git push -u origin main
```

**IMPORTANT:** Add `.streamlit/secrets.toml` to `.gitignore`:
```bash
echo ".streamlit/secrets.toml" >> .gitignore
git add .gitignore
git commit -m "Add secrets to gitignore"
git push
```

### Step 3: Deploy to Streamlit Cloud (5 minutes)

1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `yojnamitra-ai`
5. Main file path: `yojnamitra_ai.py`
6. Click "Advanced settings"
7. Add secrets from `.streamlit/secrets.toml`
8. Click "Deploy"

**Wait 2-3 minutes for deployment...**

### Step 4: Get Your URL

Your app will be live at:
```
https://[your-username]-yojnamitra-ai-[random].streamlit.app
```

**Done! 🎉**

---

## 🔧 Alternative: AWS EC2 (If Streamlit Fails)

**Time:** 30 minutes  
**Cost:** ~$0.01/hour (t2.micro)  
**Difficulty:** Medium

### Step 1: Launch EC2 Instance

```bash
# Using AWS CLI
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t2.micro \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxx \
  --region ap-south-1
```

Or use AWS Console:
1. Go to EC2 Dashboard
2. Click "Launch Instance"
3. Choose "Ubuntu Server 22.04 LTS"
4. Instance type: t2.micro (free tier)
5. Create/select key pair
6. Security group: Allow port 8501
7. Launch

### Step 2: Connect to EC2

```bash
# Get public IP from AWS Console
ssh -i your-key.pem ubuntu@[your-ec2-ip]
```

### Step 3: Setup Environment

```bash
# Update system
sudo apt update
sudo apt install -y python3-pip

# Clone your repo
git clone https://github.com/[your-username]/yojnamitra-ai.git
cd yojnamitra-ai

# Install dependencies
pip3 install -r requirements.txt

# Create .env file
nano .env
# Paste your AWS credentials
# Save: Ctrl+X, Y, Enter
```

### Step 4: Run App

```bash
# Run in background
nohup streamlit run yojnamitra_ai.py --server.port 8501 --server.address 0.0.0.0 &

# Check if running
curl http://localhost:8501
```

### Step 5: Access Your App

Open browser:
```
http://[your-ec2-public-ip]:8501
```

**Done! 🎉**

---

## 🎯 Recommended: Streamlit Cloud

**Why:**
- ✅ Free
- ✅ Automatic HTTPS
- ✅ Easy to update (just push to GitHub)
- ✅ No server management
- ✅ Custom domain support

**Why Not EC2:**
- ⚠️ Costs money (small but not free)
- ⚠️ Need to manage server
- ⚠️ No automatic HTTPS
- ⚠️ Need to keep it running

---

## 🐛 Troubleshooting

### Streamlit Cloud: "Module not found"
```bash
# Make sure requirements.txt has all dependencies
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

### Streamlit Cloud: "Secrets not found"
1. Go to app settings
2. Click "Secrets"
3. Paste contents of `.streamlit/secrets.toml`
4. Save

### EC2: "Connection refused"
```bash
# Check security group allows port 8501
aws ec2 describe-security-groups --group-ids sg-xxxxxxxx

# Add rule if needed
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxx \
  --protocol tcp \
  --port 8501 \
  --cidr 0.0.0.0/0
```

### EC2: "App not running"
```bash
# Check if streamlit is running
ps aux | grep streamlit

# Check logs
tail -f nohup.out

# Restart if needed
pkill -f streamlit
nohup streamlit run yojnamitra_ai.py --server.port 8501 --server.address 0.0.0.0 &
```

---

## 📝 After Deployment

### Update Your Documentation

**README.md:**
```markdown
## 🌐 Live Demo

**URL:** https://[your-app-url].streamlit.app

Try it now! No installation needed.
```

**HACKATHON_SUBMISSION.md:**
```markdown
## Demo

**Live Demo:** https://[your-app-url].streamlit.app
**Video Demo:** [YouTube link]
**GitHub:** https://github.com/[your-username]/yojnamitra-ai
```

### Test Your Deployment

1. Open your live URL
2. Test Hinglish conversation
3. Take screenshot
4. Share URL with friends

---

## ⏱️ Time Estimate

| Method | Setup | Deploy | Total |
|--------|-------|--------|-------|
| **Streamlit Cloud** | 10 min | 5 min | 15 min |
| AWS EC2 | 15 min | 15 min | 30 min |
| AWS Amplify | 20 min | 20 min | 40 min |

**Recommendation:** Use Streamlit Cloud (fastest, free, easiest)

---

## 🎉 Success Checklist

After deployment:
- [ ] App is accessible via public URL
- [ ] Hinglish conversation works
- [ ] AI responds correctly
- [ ] No errors in logs
- [ ] URL added to README
- [ ] URL added to submission
- [ ] Screenshot taken
- [ ] Shared with team/friends

---

## 🚨 Important Notes

### Security
- ✅ Streamlit Cloud secrets are encrypted
- ✅ Don't commit `.streamlit/secrets.toml` to GitHub
- ✅ Add to `.gitignore`

### Cost
- ✅ Streamlit Cloud: FREE
- ⚠️ EC2 t2.micro: ~$0.01/hour (~$7/month)
- ⚠️ Bedrock usage: Pay per request

### Limits
- Streamlit Cloud: 1GB RAM, 1 CPU
- Should be enough for demo
- If slow, mention in submission

---

## 💡 Pro Tips

1. **Deploy Early** - Don't wait until last minute
2. **Test Thoroughly** - Check all features work
3. **Have Backup** - Keep local demo ready
4. **Monitor Usage** - Check Bedrock costs
5. **Share URL** - Add to all documentation

---

## 🎯 Quick Decision

**If you have:**
- **< 30 minutes:** Use Streamlit Cloud
- **30-60 minutes:** Use EC2 if Streamlit fails
- **> 60 minutes:** Try AWS Amplify

**Best choice:** Streamlit Cloud (15 minutes, free, easy)

---

**Ready to deploy? Start with Streamlit Cloud! 🚀**
