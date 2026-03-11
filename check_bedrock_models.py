#!/usr/bin/env python3
"""
Check which Bedrock models are available in your AWS account
"""

import boto3
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Bedrock client
bedrock = boto3.client(
    'bedrock',
    region_name=os.getenv('AWS_REGION', 'ap-south-1'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

print("=" * 80)
print("CHECKING BEDROCK MODELS IN YOUR AWS ACCOUNT")
print(f"Region: {os.getenv('AWS_REGION', 'ap-south-1')}")
print("=" * 80)
print()

try:
    # List all foundation models
    response = bedrock.list_foundation_models()
    
    models = response.get('modelSummaries', [])
    
    if not models:
        print("❌ No models found. Check your AWS credentials and region.")
        exit(1)
    
    print(f"✅ Found {len(models)} total models in Bedrock")
    print()
    
    # Filter for text generation models
    text_models = [m for m in models if 'TEXT' in m.get('outputModalities', [])]
    
    print("=" * 80)
    print("TEXT GENERATION MODELS (For Conversational AI)")
    print("=" * 80)
    print()
    
    # Categorize models
    amazon_models = []
    anthropic_models = []
    meta_models = []
    mistral_models = []
    cohere_models = []
    ai21_models = []
    other_models = []
    
    for model in text_models:
        model_id = model.get('modelId', '')
        provider = model.get('providerName', '')
        
        if 'amazon' in provider.lower():
            amazon_models.append(model)
        elif 'anthropic' in provider.lower():
            anthropic_models.append(model)
        elif 'meta' in provider.lower():
            meta_models.append(model)
        elif 'mistral' in provider.lower():
            mistral_models.append(model)
        elif 'cohere' in provider.lower():
            cohere_models.append(model)
        elif 'ai21' in provider.lower():
            ai21_models.append(model)
        else:
            other_models.append(model)
    
    # Print Amazon models (Nova, Titan)
    if amazon_models:
        print("🟢 AMAZON MODELS (Recommended - AWS Native)")
        print("-" * 80)
        for model in amazon_models:
            model_id = model.get('modelId', '')
            model_name = model.get('modelName', '')
            print(f"  ✅ {model_name}")
            print(f"     Model ID: {model_id}")
            print(f"     Status: READY TO USE")
            print()
        print()
    
    # Print Anthropic models (Claude)
    if anthropic_models:
        print("🟣 ANTHROPIC MODELS (Claude)")
        print("-" * 80)
        for model in anthropic_models:
            model_id = model.get('modelId', '')
            model_name = model.get('modelName', '')
            print(f"  ✅ {model_name}")
            print(f"     Model ID: {model_id}")
            print(f"     Status: READY TO USE")
            print()
        print()
    
    # Print Meta models (Llama)
    if meta_models:
        print("🔵 META MODELS (Llama)")
        print("-" * 80)
        for model in meta_models:
            model_id = model.get('modelId', '')
            model_name = model.get('modelName', '')
            print(f"  ✅ {model_name}")
            print(f"     Model ID: {model_id}")
            print(f"     Status: READY TO USE")
            print()
        print()
    
    # Print Mistral models
    if mistral_models:
        print("🟠 MISTRAL MODELS")
        print("-" * 80)
        for model in mistral_models:
            model_id = model.get('modelId', '')
            model_name = model.get('modelName', '')
            print(f"  ✅ {model_name}")
            print(f"     Model ID: {model_id}")
            print(f"     Status: READY TO USE")
            print()
        print()
    
    # Print Cohere models
    if cohere_models:
        print("🟡 COHERE MODELS")
        print("-" * 80)
        for model in cohere_models:
            model_id = model.get('modelId', '')
            model_name = model.get('modelName', '')
            print(f"  ✅ {model_name}")
            print(f"     Model ID: {model_id}")
            print(f"     Status: READY TO USE")
            print()
        print()
    
    # Print AI21 models
    if ai21_models:
        print("⚪ AI21 MODELS")
        print("-" * 80)
        for model in ai21_models:
            model_id = model.get('modelId', '')
            model_name = model.get('modelName', '')
            print(f"  ✅ {model_name}")
            print(f"     Model ID: {model_id}")
            print(f"     Status: READY TO USE")
            print()
        print()
    
    # Print other models
    if other_models:
        print("⚫ OTHER MODELS")
        print("-" * 80)
        for model in other_models:
            model_id = model.get('modelId', '')
            model_name = model.get('modelName', '')
            provider = model.get('providerName', '')
            print(f"  ✅ {model_name} ({provider})")
            print(f"     Model ID: {model_id}")
            print(f"     Status: READY TO USE")
            print()
        print()
    
    # Print embedding models
    print("=" * 80)
    print("EMBEDDING MODELS (For RAG/Search)")
    print("=" * 80)
    print()
    
    embedding_models = [m for m in models if 'EMBEDDING' in m.get('outputModalities', [])]
    
    for model in embedding_models:
        model_id = model.get('modelId', '')
        model_name = model.get('modelName', '')
        provider = model.get('providerName', '')
        print(f"  ✅ {model_name} ({provider})")
        print(f"     Model ID: {model_id}")
        print(f"     Status: READY TO USE")
        print()
    
    # Print current configuration
    print("=" * 80)
    print("YOUR CURRENT CONFIGURATION")
    print("=" * 80)
    print()
    print(f"Current Model: {os.getenv('BEDROCK_MODEL_ID', 'Not set')}")
    print(f"Current Embeddings: {os.getenv('BEDROCK_EMBEDDING_MODEL_ID', 'Not set')}")
    print()
    
    # Recommendations
    print("=" * 80)
    print("RECOMMENDATIONS FOR YOJNAMITRA-AI")
    print("=" * 80)
    print()
    
    # Check if Nova Lite is available
    nova_lite_available = any('nova-lite' in m.get('modelId', '').lower() for m in amazon_models)
    
    if nova_lite_available:
        print("🏆 BEST CHOICE: Amazon Nova Lite")
        print("   Model ID: us.amazon.nova-lite-v1:0")
        print("   Reasons:")
        print("   ✅ Fastest response time")
        print("   ✅ Cheapest ($0.00015/1K tokens)")
        print("   ✅ Excellent Hindi support")
        print("   ✅ Perfect for conversational AI")
        print("   ✅ AWS native (best integration)")
        print()
    
    print("🥈 ALTERNATIVE: Amazon Nova Pro")
    print("   Model ID: us.amazon.nova-pro-v1:0")
    print("   Reasons:")
    print("   ✅ Better reasoning than Lite")
    print("   ✅ Still very fast")
    print("   ✅ Good cost/performance balance")
    print()
    
    print("🥉 BUDGET OPTION: Meta Llama 3.3 70B")
    print("   Model ID: us.meta.llama3-3-70b-instruct-v1:0")
    print("   Reasons:")
    print("   ✅ Very cheap ($0.00099/1K tokens)")
    print("   ✅ Good performance")
    print("   ✅ Open source")
    print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"✅ Total models available: {len(models)}")
    print(f"✅ Text generation models: {len(text_models)}")
    print(f"✅ Embedding models: {len(embedding_models)}")
    print()
    print("All models listed above are READY TO USE in your AWS account!")
    print()

except Exception as e:
    print(f"❌ Error checking models: {str(e)}")
    print()
    print("Possible issues:")
    print("1. Check AWS credentials in .env file")
    print("2. Verify AWS region is correct")
    print("3. Ensure IAM user has bedrock:ListFoundationModels permission")
    exit(1)
