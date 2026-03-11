# EC2 Quick Reference - Copy/Paste Commands

## 1. SSH into EC2
```bash
ssh -i ~/Downloads/yojnamitra-key.pem ec2-user@<YOUR-PUBLIC-IP>
```

## 2. Install Everything
```bash
# Update system
sudo yum update -y

# Install Python and Git
sudo yum install python3.11 python3.11-pip git -y

# Clone repo
git clone https://github.com/siddharth3105/yojnamitra-ai.git
cd yojnamitra-ai

# Install dependencies
pip3.11 install -r requirements.txt --user
```

## 3. Set Environment Variables
```bash
export BEDROCK_ACCESS_KEY_ID=your_access_key_here
export BEDROCK_SECRET_ACCESS_KEY=your_secret_key_here
export BEDROCK_REGION=ap-south-1
export BEDROCK_MODEL_ID=qwen.qwen3-235b-a22b-2507-v1:0
```

## 4. Run Streamlit (Background)
```bash
nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

## 5. Check Status
```bash
# Check if running
ps aux | grep streamlit

# View logs
tail -f streamlit.log
```

## 6. Your App URL
```
http://<YOUR-PUBLIC-IP>:8501
```

## 7. Stop App (if needed)
```bash
# Find process ID
ps aux | grep streamlit

# Kill process
kill <PID>
```

## 8. Restart App
```bash
# Kill old process
pkill -f streamlit

# Start new process
nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

---

## IMPORTANT: Security Group Settings

**In AWS Console → EC2 → Security Groups:**

Add these inbound rules:
- Port 22 (SSH): Your IP or 0.0.0.0/0
- Port 8501 (Streamlit): 0.0.0.0/0
- Port 80 (HTTP - optional): 0.0.0.0/0

---

## Your Checklist

- [ ] Launch EC2 t2.micro instance
- [ ] Download key pair (.pem file)
- [ ] Add port 8501 to security group
- [ ] SSH into instance
- [ ] Install dependencies
- [ ] Clone GitHub repo
- [ ] Set environment variables
- [ ] Run Streamlit
- [ ] Test at http://<PUBLIC-IP>:8501
- [ ] Update documentation with new URL
