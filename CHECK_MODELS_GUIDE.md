# Check Available Bedrock Models - Quick Guide

## How to Check Which Models Are Ready to Use

I've created a script that will check your AWS account and show you all available Bedrock models.

---

## Option 1: Run on Your Windows Machine

### Step 1: Open Command Prompt
```bash
cd C:\Users\suraj\OneDrive\Desktop\yojnamitra-app
```

### Step 2: Run the check script
```bash
python check_bedrock_models.py
```

This will show you:
- All text generation models available
- All embedding models available
- Which ones are ready to use
- Recommendations for your app

---

## Option 2: Run on EC2 Instance

### Step 1: Connect to EC2
- AWS Console → EC2 → Connect to your instance

### Step 2: Upload and run the script
```bash
cd yojnamitra-ai

# Create the check script
cat > check_bedrock_models.py << 'EOF'
# (Copy the content from check_bedrock_models.py)
EOF

# Run it
python3 check_bedrock_models.py
```

---

## Option 3: Quick AWS CLI Check

If you have AWS CLI installed:

```bash
aws bedrock list-foundation-models \
  --region ap-south-1 \
  --query 'modelSummaries[?contains(outputModalities, `TEXT`)].{Name:modelName, ID:modelId, Provider:providerName}' \
  --output table
```

---

## What You'll See

The script will show:

### 🟢 Amazon Models (Nova, Titan)
- Nova Lite (Recommended!)
- Nova Pro
- Nova Micro
- Titan Text models

### 🟣 Anthropic Models (Claude)
- Claude 3.5 Sonnet
- Claude 3 Opus
- Claude 3 Haiku

### 🔵 Meta Models (Llama)
- Llama 3.3 70B
- Llama 3.2 models
- Llama 3.1 models

### 🟠 Mistral Models
- Mistral Large
- Mistral 7B

### 🟡 Cohere Models
- Command R+
- Command R

### Embedding Models
- Titan Embeddings v2 (Current)
- Titan Embeddings v1
- Cohere Embed

---

## Expected Output Example

```
================================================================================
CHECKING BEDROCK MODELS IN YOUR AWS ACCOUNT
Region: ap-south-1
================================================================================

✅ Found 45 total models in Bedrock

================================================================================
TEXT GENERATION MODELS (For Conversational AI)
================================================================================

🟢 AMAZON MODELS (Recommended - AWS Native)
--------------------------------------------------------------------------------
  ✅ Nova Lite
     Model ID: us.amazon.nova-lite-v1:0
     Status: READY TO USE

  ✅ Nova Pro
     Model ID: us.amazon.nova-pro-v1:0
     Status: READY TO USE

🟣 ANTHROPIC MODELS (Claude)
--------------------------------------------------------------------------------
  ✅ Claude 3.5 Sonnet v2
     Model ID: us.anthropic.claude-3-5-sonnet-20241022-v2:0
     Status: READY TO USE

🔵 META MODELS (Llama)
--------------------------------------------------------------------------------
  ✅ Llama 3.3 70B Instruct
     Model ID: us.meta.llama3-3-70b-instruct-v1:0
     Status: READY TO USE

================================================================================
YOUR CURRENT CONFIGURATION
================================================================================

Current Model: qwen.qwen3-235b-a22b-2507-v1:0
Current Embeddings: amazon.titan-embed-text-v2:0

================================================================================
RECOMMENDATIONS FOR YOJNAMITRA-AI
================================================================================

🏆 BEST CHOICE: Amazon Nova Lite
   Model ID: us.amazon.nova-lite-v1:0
   Reasons:
   ✅ Fastest response time
   ✅ Cheapest ($0.00015/1K tokens)
   ✅ Excellent Hindi support
   ✅ Perfect for conversational AI
   ✅ AWS native (best integration)
```

---

## Troubleshooting

### Error: "No models found"
**Solution**: Check your AWS credentials in .env file

### Error: "Access Denied"
**Solution**: Your IAM user needs `bedrock:ListFoundationModels` permission

### Error: "Region not supported"
**Solution**: Make sure AWS_REGION=ap-south-1 in .env

---

## After Checking

Once you see which models are available, you can:

1. **Choose a model** from the list
2. **Update .env** with the model ID
3. **Restart your app** to use the new model

Example:
```env
# Switch to Nova Lite
BEDROCK_MODEL_ID=us.amazon.nova-lite-v1:0
```

---

## Quick Decision Guide

**If you see Nova Lite** → Use it! (Best choice)
**If no Nova Lite** → Use Claude 3.5 Sonnet (High quality)
**If budget is tight** → Use Llama 3.3 70B (Cheapest)
**If you need reasoning** → Use Claude 3 Opus (Best reasoning)

---

Ready to check? Just run:
```bash
python check_bedrock_models.py
```
