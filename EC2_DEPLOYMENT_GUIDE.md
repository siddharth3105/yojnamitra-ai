# AWS EC2 Deployment Guide - YojnaMitra AI
## Step-by-Step Instructions (30 minutes)

---

## STEP 1: Launch EC2 Instance (5 minutes)

### 1.1 Go to AWS Console
- Open https://console.aws.amazon.com/
- Sign in to your AWS account
- Region: Select **ap-south-1 (Mumbai)** (top right corner)

### 1.2 Navigate to EC2
- Search for "EC2" in the search bar
- Click "EC2" to open EC2 Dashboard

### 1.3 Launch Instance
- Click **"Launch Instance"** (orange button)

### 1.4 Configure Instance

**Name and tags:**
- Name: `yojnamitra-ai-server`

**Application and OS Images (AMI):**
- Select: **Amazon Linux 2023 AMI** (Free tier eligible)
- Architecture: **64-bit (x86)**

**Instance type:**
- Select: **t2.micro** (Free tier eligible)
- 1 vCPU, 1 GB RAM

**Key pair (login):**
- Click **"Create new key pair"**
- Key pair name: `yojnamitra-key`
- Key pair type: **RSA**
- Private key file format: **`.pem`** (for Mac/Linux) or **`.ppk`** (for Windows/PuTTY)
- Click **"Create key pair"**
- **IMPORTANT:** Save the downloaded key file safely!

**Network settings:**
- Click **"Edit"** next to Network settings
- Auto-assign public IP: **Enable**
- Firewall (security groups): **Create security group**
- Security group name: `yojnamitra-sg`
- Description: `Security group for YojnaMitra AI`

**Add security group rules:**
1. **SSH (already added):**
   - Type: SSH
   - Port: 22
   - Source: My IP (or Anywhere 0.0.0.0/0)

2. **Streamlit (ADD THIS):**
   - Click **"Add security group rule"**
   - Type: Custom TCP
   - Port range: **8501**
   - Source type: **Anywhere** (0.0.0.0/0)
   - Description: Streamlit app

3. **HTTP (Optional - for future):**
   - Click **"Add security group rule"**
   - Type: HTTP
   - Port: 80
   - Source: Anywhere (0.0.0.0/0)

**Configure storage:**
- Size: **8 GB** (default, free tier)
- Volume type: **gp3** (default)

**Advanced details:**
- Leave as default

### 1.5 Launch
- Click **"Launch instance"** (orange button)
- Wait for instance to start (2-3 minutes)
- Status should show: **Running** (green)

### 1.6 Get Public IP
- Click on your instance ID
- Copy the **Public IPv4 address** (e.g., 13.232.xxx.xxx)
- **SAVE THIS IP - YOU'LL NEED IT!**

---

## STEP 2: Connect to EC2 Instance (5 minutes)

### 2.1 Set Key Permissions (Mac/Linux/Git Bash)

Open terminal and run:
```bash
chmod 400 ~/Downloads/yojnamitra-key.pem
```

### 2.2 SSH into Instance

**For Mac/Linux/Git Bash:**
```bash
ssh -i ~/Downloads/yojnamitra-key.pem ec2-user@<YOUR-PUBLIC-IP>
```

**For Windows (PuTTY):**
1. Open PuTTY
2. Host Name: `ec2-user@<YOUR-PUBLIC-IP>`
3. Connection → SSH → Auth → Browse for your `.ppk` file
4. Click "Open"

**First time connection:**
- Type `yes` when asked "Are you sure you want to continue connecting?"

**You should see:**
```
   ,     #_
   ~\_  ####_        Amazon Linux 2023
  ~~  \_#####\
  ~~     \###|
  ~~       \#/ ___   https://aws.amazon.com/linux/amazon-linux-2023
   ~~       V~' '->
    ~~~         /
      ~~._.   _/
         _/ _/
       _/m/'

[ec2-user@ip-xxx-xxx-xxx-xxx ~]$
```

---

## STEP 3: Install Dependencies (5 minutes)

### 3.1 Update System
```bash
sudo yum update -y
```

### 3.2 Install Python 3.11 and Git
```bash
sudo yum install python3.11 python3.11-pip git -y
```

### 3.3 Verify Installation
```bash
python3.11 --version
# Should show: Python 3.11.x

pip3.11 --version
# Should show: pip 23.x.x
```

---

## STEP 4: Clone Repository and Setup (5 minutes)

### 4.1 Clone Your GitHub Repository
```bash
git clone https://github.com/siddharth3105/yojnamitra-ai.git
cd yojnamitra-ai
```

### 4.2 Install Python Dependencies
```bash
pip3.11 install -r requirements.txt --user
```

This will take 3-4 minutes. You'll see packages being installed.

### 4.3 Set Environment Variables

**Create .env file:**
```bash
nano .env
```

**Paste your AWS credentials:**
```bash
BEDROCK_ACCESS_KEY_ID=your_access_key_here
BEDROCK_SECRET_ACCESS_KEY=your_secret_key_here
BEDROCK_REGION=ap-south-1
BEDROCK_MODEL_ID=qwen.qwen3-235b-a22b-2507-v1:0
```

**Save and exit:**
- Press `Ctrl + X`
- Press `Y` (yes)
- Press `Enter`

### 4.4 Export Environment Variables
```bash
export BEDROCK_ACCESS_KEY_ID=your_access_key_here
export BEDROCK_SECRET_ACCESS_KEY=your_secret_key_here
export BEDROCK_REGION=ap-south-1
export BEDROCK_MODEL_ID=qwen.qwen3-235b-a22b-2507-v1:0
```

**Replace `your_access_key_here` and `your_secret_key_here` with your actual AWS credentials!**

---

## STEP 5: Run Streamlit App (2 minutes)

### 5.1 Test Run (Foreground)
```bash
streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0
```

**You should see:**
```
  You can now view your Streamlit app in your browser.

  Network URL: http://172.31.x.x:8501
  External URL: http://13.232.xxx.xxx:8501
```

### 5.2 Test in Browser
- Open browser
- Go to: `http://<YOUR-PUBLIC-IP>:8501`
- You should see YojnaMitra AI app!

### 5.3 Stop Test (if working)
- Press `Ctrl + C` in terminal

---

## STEP 6: Run App in Background (Persistent) (3 minutes)

### 6.1 Run with nohup (keeps running after logout)
```bash
nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

**You should see:**
```
[1] 12345
nohup: ignoring input and appending output to 'streamlit.log'
```

### 6.2 Verify It's Running
```bash
ps aux | grep streamlit
```

**You should see:**
```
ec2-user  12345  ... streamlit run yojnamitra_ai.py
```

### 6.3 Check Logs (Optional)
```bash
tail -f streamlit.log
```

Press `Ctrl + C` to exit log view.

### 6.4 Test in Browser Again
- Go to: `http://<YOUR-PUBLIC-IP>:8501`
- App should be running!

### 6.5 Logout (App Keeps Running)
```bash
exit
```

**Your app is now live at:** `http://<YOUR-PUBLIC-IP>:8501`

---

## STEP 7: Make It Permanent (Auto-start on Reboot) (5 minutes)

### 7.1 Create Systemd Service

SSH back into your instance:
```bash
ssh -i ~/Downloads/yojnamitra-key.pem ec2-user@<YOUR-PUBLIC-IP>
```

Create service file:
```bash
sudo nano /etc/systemd/system/yojnamitra.service
```

Paste this content:
```ini
[Unit]
Description=YojnaMitra AI Streamlit App
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/yojnamitra-ai
Environment="BEDROCK_ACCESS_KEY_ID=your_access_key_here"
Environment="BEDROCK_SECRET_ACCESS_KEY=your_secret_key_here"
Environment="BEDROCK_REGION=ap-south-1"
Environment="BEDROCK_MODEL_ID=qwen.qwen3-235b-a22b-2507-v1:0"
ExecStart=/home/ec2-user/.local/bin/streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**IMPORTANT:** Replace `your_access_key_here` and `your_secret_key_here` with your actual credentials!

Save and exit (`Ctrl + X`, `Y`, `Enter`).

### 7.2 Enable and Start Service
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable yojnamitra.service

# Start service
sudo systemctl start yojnamitra.service

# Check status
sudo systemctl status yojnamitra.service
```

**You should see:**
```
● yojnamitra.service - YojnaMitra AI Streamlit App
   Loaded: loaded
   Active: active (running)
```

### 7.3 Useful Commands
```bash
# Stop app
sudo systemctl stop yojnamitra.service

# Restart app
sudo systemctl restart yojnamitra.service

# View logs
sudo journalctl -u yojnamitra.service -f
```

---

## STEP 8: Update Documentation (5 minutes)

### Your New URL
```
http://<YOUR-PUBLIC-IP>:8501
```

**Example:** `http://13.232.123.45:8501`

### Update These Files:
1. `HACKATHON_PPT_CONTENT.md` - Replace all Amplify URLs
2. `README.md` - Update live demo link
3. `AWS_INFRASTRUCTURE.md` - Add EC2 to services list
4. `HACKATHON_SUBMISSION.md` - Update demo URL

---

## TROUBLESHOOTING

### App Not Loading?

**1. Check Security Group:**
- EC2 Console → Security Groups
- Verify port 8501 is open (0.0.0.0/0)

**2. Check App is Running:**
```bash
ps aux | grep streamlit
```

**3. Check Logs:**
```bash
tail -f ~/yojnamitra-ai/streamlit.log
# or
sudo journalctl -u yojnamitra.service -f
```

**4. Restart App:**
```bash
sudo systemctl restart yojnamitra.service
```

**5. Check Firewall:**
```bash
sudo iptables -L -n
```

### Can't SSH?

**1. Check Key Permissions:**
```bash
chmod 400 ~/Downloads/yojnamitra-key.pem
```

**2. Check Security Group:**
- Port 22 should be open for your IP

**3. Check Instance State:**
- Should be "Running" in EC2 Console

### App Crashes?

**1. Check Memory:**
```bash
free -h
```

**2. Upgrade Instance:**
- Stop instance
- Change instance type to t2.small (2GB RAM)
- Start instance

---

## COST ESTIMATE

**t2.micro (Free Tier):**
- First 750 hours/month: **FREE** (first 12 months)
- After free tier: **$8.50/month**

**Data Transfer:**
- First 100 GB/month: **FREE**
- After: $0.09/GB

**Total Cost:**
- First year: **FREE** (if within free tier limits)
- After: **~$10-15/month**

---

## NEXT STEPS

1. ✅ Test your app at `http://<YOUR-PUBLIC-IP>:8501`
2. ✅ Update all documentation with new URL
3. ✅ Record demo video
4. ✅ Update PPT with EC2 deployment info
5. ✅ Submit hackathon!

---

## AWS SERVICES NOW USED (7 SERVICES!)

1. ✅ **AWS EC2** - Compute (hosting Streamlit)
2. ✅ **Amazon Bedrock** - AI/ML (Qwen3 235B + Titan v2)
3. ✅ **Amazon DynamoDB** - Database
4. ✅ **Amazon S3** - Storage
5. ✅ **Amazon Translate** - Multi-language
6. ✅ **CloudWatch** - Monitoring
7. ✅ **VPC** - Networking (automatic with EC2)

**You can now say: "Deployed on 7 AWS services!"**

---

## NEED HELP?

If you get stuck at any step, let me know which step and what error you're seeing!
