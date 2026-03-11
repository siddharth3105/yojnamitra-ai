# Deploy Language Feature NOW - Quick Commands

## Step 1: Push to GitHub (Run on your Windows machine)

```bash
# Add the modified file
git add yojnamitra_ai.py LANGUAGE_FEATURE_ADDED.md DEPLOY_LANGUAGE_FEATURE.md

# Commit with message
git commit -m "Add language selection with Amazon Translate support"

# Push to GitHub
git push origin main
```

If you get authentication errors, use:
```bash
git config --global user.name "siddharth3105"
git config --global user.email "your-email@example.com"
```

## Step 2: Deploy to EC2 (Run in EC2 Instance Connect browser terminal)

### 2.1 Connect to EC2
- Go to AWS Console → EC2 → Instances
- Select instance `i-01826124d42c6b8f8a`
- Click "Connect" → "EC2 Instance Connect" → "Connect"

### 2.2 Pull Latest Code
```bash
cd yojnamitra-ai
git pull origin main
```

### 2.3 Stop Current Streamlit Process
```bash
pkill -f streamlit
```

### 2.4 Set Environment Variables (if not already set)
```bash
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_REGION="ap-south-1"
export BEDROCK_MODEL_ID="qwen.qwen3-235b-a22b-2507-v1:0"
```

### 2.5 Restart Streamlit
```bash
nohup streamlit run yojnamitra_ai.py --server.port=8501 --server.address=0.0.0.0 > streamlit.log 2>&1 &
```

### 2.6 Verify It's Running
```bash
ps aux | grep streamlit
tail -f streamlit.log
```

Press `Ctrl+C` to stop viewing the log.

## Step 3: Test the Feature

1. Open browser: http://13.201.55.10:8501
2. Look for "🌐 Language / भाषा" dropdown in the sidebar
3. Select a language (e.g., "हिंदी (Hindi)")
4. Type a message and verify the AI response is translated

## Troubleshooting

### If language dropdown doesn't appear:
```bash
# Check if code was pulled correctly
cd yojnamitra-ai
git log -1
# Should show "Add language selection with Amazon Translate support"

# Check if Streamlit is running
ps aux | grep streamlit

# Check logs for errors
tail -50 streamlit.log
```

### If translation doesn't work:
- Verify AWS credentials have Amazon Translate permissions
- Check IAM policy includes `translate:TranslateText`
- Check logs: `tail -50 streamlit.log`

## Expected Result

After deployment, you should see:
- Language dropdown at the top of the sidebar
- 12 language options (English/Hindi/Hinglish Auto + 11 regional languages)
- AI responses translated to selected language
- Welcome message translated to selected language

## Quick Status Check

```bash
# On EC2, run this to verify everything:
cd yojnamitra-ai && \
git log -1 --oneline && \
ps aux | grep streamlit | grep -v grep && \
echo "✅ Deployment successful! Visit http://13.201.55.10:8501"
```
