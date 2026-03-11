# AWS Amplify Fix - Streamlit Deployment Issue

## Problem
AWS Amplify Hosting is designed for **static sites** (React, Vue, Angular) or **SSR frameworks** (Next.js, Nuxt.js). 

Streamlit is a **Python web server** that needs to run continuously, which Amplify Hosting doesn't support.

## Solution Options (AWS-Native)

### Option 1: AWS App Runner (RECOMMENDED - Easiest AWS Solution)

**Why App Runner:**
- Designed for containerized web apps
- Fully managed (like Amplify)
- Auto-scaling
- Pay-per-use
- Perfect for Streamlit

**Steps:**

1. **Build and push Docker image to ECR:**
```bash
# Authenticate to ECR
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.ap-south-1.amazonaws.com

# Create ECR repository
aws ecr create-repository --repository-name yojnamitra-ai --region ap-south-1

# Build Docker image
docker build -t yojnamitra-ai .

# Tag image
docker tag yojnamitra-ai:latest <account-id>.dkr.ecr.ap-south-1.amazonaws.com/yojnamitra-ai:latest

# Push to ECR
docker push <account-id>.dkr.ecr.ap-south-1.amazonaws.com/yojnamitra-ai:latest
```

2. **Create App Runner service:**
```bash
aws apprunner create-service \
  --service-name yojnamitra-ai \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "<account-id>.dkr.ecr.ap-south-1.amazonaws.com/yojnamitra-ai:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8501",
        "RuntimeEnvironmentVariables": {
          "BEDROCK_ACCESS_KEY_ID": "your-key",
          "BEDROCK_SECRET_ACCESS_KEY": "your-secret",
          "BEDROCK_REGION": "ap-south-1"
        }
      }
    },
    "AutoDeploymentsEnabled": true
  }' \
  --instance-configuration '{
    "Cpu": "1 vCPU",
    "Memory": "2 GB"
  }' \
  --region ap-south-1
```

3. **Get service URL:**
```bash
aws apprunner describe-service --service-arn <service-arn> --region ap-south-1
```

**Cost:** ~$25-30/month (1 vCPU, 2GB RAM, always running)

---

### Option 2: AWS Elastic Beanstalk (Traditional AWS PaaS)

**Steps:**

1. **Create application.py (WSGI wrapper):**
```python
# application.py
import subprocess
import os

def application(environ, start_response):
    # Start Streamlit in background
    subprocess.Popen(['streamlit', 'run', 'yojnamitra_ai.py', '--server.port=8501'])
    
    status = '200 OK'
    headers = [('Content-type', 'text/html')]
    start_response(status, headers)
    return [b"Streamlit app running on port 8501"]
```

2. **Deploy to Elastic Beanstalk:**
```bash
# Install EB CLI
pip install awsebcli

# Initialize EB
eb init -p python-3.11 yojnamitra-ai --region ap-south-1

# Create environment
eb create yojnamitra-env

# Deploy
eb deploy
```

**Cost:** ~$15-20/month (t2.micro)

---

### Option 3: AWS EC2 (Manual but Full Control)

**Steps:**

1. **Launch EC2 instance:**
   - Go to EC2 Console
   - Launch t2.micro (free tier)
   - Amazon Linux 2023
   - Security group: Allow port 8501

2. **SSH and setup:**
```bash
# SSH into instance
ssh -i your-key.pem ec2-user@<public-ip>

# Install Python and dependencies
sudo yum update -y
sudo yum install python3 python3-pip git -y

# Clone repository
git clone https://github.com/siddharth3105/yojnamitra-ai.git
cd yojnamitra-ai

# Install dependencies
pip3 install -r requirements.txt

# Set environment variables
export BEDROCK_ACCESS_KEY_ID=your-key
export BEDROCK_SECRET_ACCESS_KEY=your-secret
export BEDROCK_REGION=ap-south-1

# Run Streamlit with nohup (keeps running after logout)
nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 &
```

3. **Access app:**
   - http://<ec2-public-ip>:8501

**Cost:** Free (t2.micro free tier) or $8-10/month

---

### Option 4: AWS ECS Fargate (Serverless Containers)

**Steps:**

1. **Push Docker image to ECR** (same as App Runner step 1)

2. **Create ECS cluster:**
```bash
aws ecs create-cluster --cluster-name yojnamitra-cluster --region ap-south-1
```

3. **Create task definition:**
```bash
aws ecs register-task-definition \
  --family yojnamitra-task \
  --network-mode awsvpc \
  --requires-compatibilities FARGATE \
  --cpu 512 \
  --memory 1024 \
  --container-definitions '[{
    "name": "yojnamitra-container",
    "image": "<account-id>.dkr.ecr.ap-south-1.amazonaws.com/yojnamitra-ai:latest",
    "portMappings": [{
      "containerPort": 8501,
      "protocol": "tcp"
    }],
    "environment": [
      {"name": "BEDROCK_ACCESS_KEY_ID", "value": "your-key"},
      {"name": "BEDROCK_SECRET_ACCESS_KEY", "value": "your-secret"},
      {"name": "BEDROCK_REGION", "value": "ap-south-1"}
    ]
  }]' \
  --region ap-south-1
```

4. **Create service with ALB:**
```bash
aws ecs create-service \
  --cluster yojnamitra-cluster \
  --service-name yojnamitra-service \
  --task-definition yojnamitra-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration '{
    "awsvpcConfiguration": {
      "subnets": ["subnet-xxx"],
      "securityGroups": ["sg-xxx"],
      "assignPublicIp": "ENABLED"
    }
  }' \
  --region ap-south-1
```

**Cost:** ~$15-20/month (0.5 vCPU, 1GB RAM)

---

## Quick Fix for TODAY (Hackathon Deadline)

### Fastest AWS Solution: EC2 (30 minutes)

1. **Launch EC2 t2.micro** (free tier)
2. **Run the commands above** to deploy Streamlit
3. **Get public IP** and update documentation
4. **Record demo video** while it's running

### Alternative: Streamlit Cloud (5 minutes, not AWS but uses AWS backend)

1. Go to https://share.streamlit.io/
2. Connect GitHub repo
3. Deploy (uses AWS services in backend: Bedrock, DynamoDB, S3)
4. Get public URL

---

## What Went Wrong with Amplify?

AWS Amplify Hosting supports:
- ✅ Static sites (HTML, CSS, JS)
- ✅ React, Vue, Angular (build to static)
- ✅ Next.js, Nuxt.js (SSR frameworks)
- ❌ Python web servers (Flask, Django, Streamlit)
- ❌ Long-running processes

For Python web apps, use:
- AWS App Runner (easiest)
- AWS Elastic Beanstalk
- AWS EC2
- AWS ECS/Fargate

---

## Recommendation for Hackathon

**Use AWS EC2 (t2.micro) - Free Tier:**
- Fastest to deploy (30 min)
- Still AWS-hosted
- Free tier eligible
- Full control
- Can mention "Deployed on AWS EC2" in presentation

**Then add to PPT:**
- "Deployed on AWS EC2 (compute)"
- "Uses 7 AWS services: EC2, Bedrock, DynamoDB, S3, Translate, CloudWatch, CloudFront"
- Still 100% AWS infrastructure

---

## Need Help?

Choose one option and I'll guide you through step-by-step!
