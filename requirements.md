# YojnaMitra AI Assistant - Requirements Document

## Introduction

YojnaMitra AI Assistant is an intelligent conversational AI system designed to help Indian citizens discover, understand, and apply for government schemes. The assistant acts as a proactive guide that collects user information through natural conversation, searches for relevant schemes in real-time, matches users with eligible programs, and provides step-by-step application assistance.

## System Overview

- **Platform**: Streamlit web application
- **AI Model**: AWS Bedrock - Qwen3 235B (`qwen.qwen3-235b-a22b-2507-v1:0`)
- **Embeddings**: Amazon Titan Embeddings v2 (`amazon.titan-embed-text-v2:0`)
- **Database**: DynamoDB for user profiles and scheme data
- **Storage**: AWS S3 for document management
- **Translation**: Amazon Translate for regional languages
- **Deployment**: Streamlit Cloud

## Language Support

### Default Languages (Auto-detected by Qwen3 235B)
- English
- Hindi (हिंदी)
- Hinglish (Hindi-English mix)

### Regional Languages (Via Dropdown Selection + Amazon Translate)
- Tamil (தமிழ்)
- Telugu (తెలుగు)
- Bengali (বাংলা)
- Marathi (मराठी)
- Gujarati (ગુજરાતી)
- Kannada (ಕನ್ನಡ)
- Malayalam (മലയാളം)
- Punjabi (ਪੰਜਾਬੀ)
- Odia (ଓଡ଼ିଆ)
- Assamese (অসমীয়া)

## Core Requirements

### 1. Conversational Onboarding
Users can provide information through natural conversation without filling complex forms. The AI extracts structured data from conversational input and builds a complete user profile.

### 2. Persistent User Memory
All user information is stored permanently in DynamoDB and retrieved in future sessions, eliminating the need to repeat information.

### 3. Real-time Scheme Discovery
The system maintains an up-to-date database of government schemes with eligibility criteria, benefits, required documents, and application URLs.

### 4. Intelligent Scheme Matching
AI automatically finds schemes users are eligible for by calculating eligibility scores based on user profile data (age, income, occupation, state, category, etc.).

### 5. RAG-Enhanced Recommendations
Uses Retrieval-Augmented Generation (RAG) with Amazon Titan Embeddings v2 to provide accurate, context-aware scheme recommendations based on stored scheme knowledge.

### 6. Step-by-Step Application Guidance
Provides clear, numbered steps for applying to schemes with explanations in the user's preferred language.

### 7. Document Collection and Management
Users can upload documents (Aadhaar, PAN, certificates) once and reuse them for multiple applications. Documents are stored securely in AWS S3.

### 8. Multi-language Support
Supports 13 Indian languages with automatic detection for English/Hindi/Hinglish and manual selection for 10 regional languages via Amazon Translate.

### 9. Conversational Context Management
Maintains full conversation history across sessions to provide contextual responses without requiring users to repeat information.

### 10. Security and Privacy
- Encryption at rest (DynamoDB, S3)
- Encryption in transit (HTTPS/TLS)
- IAM roles with least-privilege permissions
- Secure document storage with access controls

## Performance Requirements

- Response time: <3 seconds for 95% of requests
- Support for 1,000+ concurrent users
- Database capacity: 10,000+ schemes
- Document storage: 100,000+ documents

## Cost Optimization

- Uses Qwen3 235B (10x cheaper than Claude Sonnet 4)
- Serverless architecture (pay-per-use)
- Efficient token usage with RAG
- S3 lifecycle policies for document management

## Deployment

- Live URL: https://main.d3knj8ptbtyid3.amplifyapp.com
- GitHub: https://github.com/siddharth3105/yojnamitra-ai
- Platform: AWS Amplify
- Region: AWS ap-south-1 (Mumbai)
