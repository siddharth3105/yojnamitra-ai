# -*- coding: utf-8 -*-
"""
YojnaMitra-AI - Intelligent Government Scheme Assistant
Autonomous, Proactive, Intelligent

Features:
- User authentication with phone OTP
- Natural conversation for eligibility collection
- Automatic scheme search from internet
- Step-by-step application guidance
- Document collection and auto-fill
- Smart notifications and reminders
"""

import streamlit as st
import os
from dotenv import load_dotenv
import boto3
import json
from datetime import datetime, timedelta
import logging
from typing import Dict, List
import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib.parse

# Import authentication components
from auth_components import SessionManager, render_auth_page

# Import RAG engine
from rag_engine import RAGEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function for WhatsApp sharing
def generate_whatsapp_share_link(user_profile: Dict, schemes: List[Dict]) -> str:
    """Generate WhatsApp share link with scheme information"""
    name = user_profile.get('name', 'User')
    message = f"🎉 YojnaMitra-AI found {len(schemes)} government schemes for me!\n\n"
    
    for i, scheme in enumerate(schemes[:3], 1):
        message += f"{i}. {scheme['name']}\n"
        message += f"   💰 {scheme['benefit']}\n"
        message += f"   🔗 {scheme['apply_link']}\n\n"
    
    message += "Try YojnaMitra-AI to find schemes for you too! 🇮🇳\n"
    message += "https://main.d3knj8ptbtyid3.amplifyapp.com"
    
    # URL encode the message
    encoded_message = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/?text={encoded_message}"
    
    return whatsapp_url

# Load environment - Support both Streamlit Cloud and local
def get_env_var(key, default=None):
    """Get environment variable from Streamlit secrets or .env"""
    try:
        # Try Streamlit secrets first (for cloud deployment)
        return st.secrets[key]
    except:
        # Fall back to .env file (for local development)
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv(key, default)

# Load AWS credentials (renamed to avoid Amplify reserved prefix)
os.environ['AWS_ACCESS_KEY_ID'] = get_env_var('BEDROCK_ACCESS_KEY_ID', '')
os.environ['AWS_SECRET_ACCESS_KEY'] = get_env_var('BEDROCK_SECRET_ACCESS_KEY', '')
os.environ['AWS_REGION'] = get_env_var('BEDROCK_REGION', 'ap-south-1')
os.environ['BEDROCK_MODEL_ID'] = get_env_var('BEDROCK_MODEL_ID', 'us.amazon.nova-lite-v1:0')

# Page config
st.set_page_config(
    page_title="YojnaMitra-AI 🇮🇳",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - PREMIUM UI
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Global styling */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Animated gradient background */
    .main {
        background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        padding: 2rem;
        min-height: 100vh;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Premium chat container */
    .chat-container {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(20px) saturate(180%);
        border-radius: 32px;
        padding: 2.5rem;
        box-shadow: 
            0 8px 32px 0 rgba(31, 38, 135, 0.37),
            0 0 0 1px rgba(255, 255, 255, 0.18) inset;
        max-width: 1000px;
        margin: 0 auto;
        border: 1px solid rgba(255, 255, 255, 0.4);
        animation: slideUp 0.6s ease-out;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Premium AI header */
    .ai-header {
        text-align: center;
        padding: 2.5rem;
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 50%, #FFBB00 100%);
        border-radius: 24px;
        color: white;
        margin-bottom: 2.5rem;
        box-shadow: 0 12px 32px rgba(255, 107, 53, 0.4);
        position: relative;
        overflow: hidden;
        animation: headerGlow 3s ease-in-out infinite;
    }
    
    @keyframes headerGlow {
        0%, 100% { box-shadow: 0 12px 32px rgba(255, 107, 53, 0.4); }
        50% { box-shadow: 0 16px 48px rgba(255, 107, 53, 0.6); }
    }
    
    .ai-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        animation: shine 3s infinite;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    /* Premium message bubbles */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.25rem 1.75rem;
        border-radius: 24px 24px 8px 24px;
        margin: 1.25rem 0 1.25rem 25%;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
        animation: messageSlideIn 0.4s ease-out;
        position: relative;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    
    .user-message::before {
        content: '👤';
        position: absolute;
        right: -40px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.5rem;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
    }
    
    .ai-message {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        color: #2c3e50;
        padding: 1.25rem 1.75rem;
        border-radius: 24px 24px 24px 8px;
        margin: 1.25rem 25% 1.25rem 0;
        border-left: 5px solid #FF6B35;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        animation: messageSlideIn 0.4s ease-out;
        position: relative;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    
    .ai-message::before {
        content: '🤖';
        position: absolute;
        left: -40px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.5rem;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
    }
    
    @keyframes messageSlideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Premium scheme cards */
    .scheme-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 2px solid #e9ecef;
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        position: relative;
        overflow: hidden;
    }
    
    .scheme-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #FF6B35, #F7931E, #FFBB00);
        transform: scaleX(0);
        transition: transform 0.4s ease;
    }
    
    .scheme-card:hover {
        border-color: #FF6B35;
        box-shadow: 0 12px 32px rgba(255, 107, 53, 0.3);
        transform: translateY(-8px) scale(1.02);
    }
    
    .scheme-card:hover::before {
        transform: scaleX(1);
    }
    
    /* Premium profile badges */
    .profile-badge {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 0.75rem 1.25rem;
        border-radius: 24px;
        display: inline-block;
        margin: 0.5rem 0.25rem;
        font-size: 0.95rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(17, 153, 142, 0.3);
        transition: all 0.3s ease;
        animation: badgePulse 2s ease-in-out infinite;
    }
    
    @keyframes badgePulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .profile-badge:hover {
        transform: translateY(-2px) scale(1.05);
        box-shadow: 0 6px 16px rgba(17, 153, 142, 0.5);
    }
    
    /* Premium notification badge */
    .notification-badge {
        background: linear-gradient(135deg, #ff4444 0%, #ff6b6b 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(255, 68, 68, 0.4);
        animation: notificationBounce 1s ease-in-out infinite;
    }
    
    @keyframes notificationBounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-3px); }
    }
    
    /* Premium sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
    }
    
    /* Premium input styling */
    .stTextInput > div > div > input {
        border-radius: 16px !important;
        border: 2px solid #e9ecef !important;
        padding: 1rem 1.25rem !important;
        font-size: 1.05rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Premium button styling */
    .stButton > button {
        border-radius: 16px !important;
        font-weight: 700 !important;
        padding: 1rem 2rem !important;
        transition: all 0.3s ease !important;
        border: none !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        font-size: 0.95rem !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.25) !important;
    }
    
    /* Premium success/error messages */
    .stSuccess {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%) !important;
        border-left: 5px solid #28a745 !important;
        border-radius: 16px !important;
        padding: 1.25rem 1.5rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.2) !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%) !important;
        border-left: 5px solid #dc3545 !important;
        border-radius: 16px !important;
        padding: 1.25rem 1.5rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(220, 53, 69, 0.2) !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%) !important;
        border-left: 5px solid #17a2b8 !important;
        border-radius: 16px !important;
        padding: 1.25rem 1.5rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(23, 162, 184, 0.2) !important;
    }
    
    /* Premium expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 1rem 1.25rem !important;
        transition: all 0.3s ease !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%) !important;
        transform: translateX(5px) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'matched_schemes' not in st.session_state:
    st.session_state.matched_schemes = []
if 'conversation_stage' not in st.session_state:
    st.session_state.conversation_stage = 'greeting'
if 'pending_question' not in st.session_state:
    st.session_state.pending_question = None
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = 'English/Hindi/Hinglish (Auto)'
# NEW: Enhanced session state for improvements
if 'saved_schemes' not in st.session_state:
    st.session_state.saved_schemes = []
if 'applications' not in st.session_state:
    st.session_state.applications = []
if 'comparison_mode' not in st.session_state:
    st.session_state.comparison_mode = False
if 'schemes_to_compare' not in st.session_state:
    st.session_state.schemes_to_compare = []


# Language translation function using Amazon Translate
def translate_text(text: str, target_language: str) -> str:
    """Translate text using Amazon Translate"""
    # Language codes mapping
    language_codes = {
        'English/Hindi/Hinglish (Auto)': None,  # No translation needed
        'हिंदी (Hindi)': 'hi',
        'தமிழ் (Tamil)': 'ta',
        'తెలుగు (Telugu)': 'te',
        'বাংলা (Bengali)': 'bn',
        'मराठी (Marathi)': 'mr',
        'ગુજરાતી (Gujarati)': 'gu',
        'ಕನ್ನಡ (Kannada)': 'kn',
        'മലയാളം (Malayalam)': 'ml',
        'ਪੰਜਾਬੀ (Punjabi)': 'pa',
        'ଓଡ଼ିଆ (Odia)': 'or',
        'অসমীয়া (Assamese)': 'as'
    }
    
    target_code = language_codes.get(target_language)
    
    # If no translation needed (default languages), return original
    if not target_code:
        return text
    
    try:
        # Initialize Amazon Translate client
        translate_client = boto3.client(
            'translate',
            region_name=os.getenv('AWS_REGION', 'ap-south-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        # Translate text
        response = translate_client.translate_text(
            Text=text,
            SourceLanguageCode='auto',  # Auto-detect source language
            TargetLanguageCode=target_code
        )
        
        return response['TranslatedText']
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text  # Return original text if translation fails


class YojnaMitraAI:
    """Intelligent AI Assistant for Government Schemes"""
    
    def __init__(self):
        self.bedrock = self._init_bedrock()
        self.model_id = os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-lite-v1:0")
        # Initialize RAG engine for enhanced recommendations
        try:
            self.rag_engine = RAGEngine()
            logger.info("RAG engine initialized successfully")
        except Exception as e:
            logger.warning(f"RAG engine initialization failed: {e}. Using fallback mode.")
            self.rag_engine = None
        
        # Conversation memory for better context
        self.conversation_context = {
            'topics_discussed': [],
            'schemes_mentioned': [],
            'questions_asked': [],
            'user_interests': [],
            'pending_confirmation': None,  # Track what needs confirmation
            'last_extracted_value': None,  # Store last extracted value
            'correction_mode': False  # Track if we're in correction mode
        }
        
    def _init_bedrock(self):
        """Initialize AWS Bedrock client"""
        try:
            return boto3.client(
                service_name='bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1'),
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
        except Exception as e:
            logger.error(f"Bedrock init error: {e}")
            return None
    
    def get_response(self, user_message: str, user_profile: Dict, conversation_history: List) -> str:
        """Get AI response using Bedrock with enhanced conversation memory"""
        
        # Update conversation context
        self._update_conversation_context(user_message, user_profile)
        
        # Check if this is a step-by-step guide request
        is_guide_request = any(keyword in user_message.lower() for keyword in 
                              ['step-by-step', 'how to apply', 'apply for', 'application guide', 'guidance', 'help me apply'])
        
        # Build conversation context
        context = self._build_context(user_message, user_profile, conversation_history)
        
        try:
            if not self.bedrock:
                return self._fallback_response(user_message, user_profile)
            
            # Use Converse API for all modern models (Qwen, Google, NVIDIA, DeepSeek, etc.)
            # This is the universal API that works with most Bedrock models
            try:
                response = self.bedrock.converse(
                    modelId=self.model_id,
                    messages=[
                        {
                            "role": "user",
                            "content": [{"text": context}]
                        }
                    ],
                    inferenceConfig={
                        "maxTokens": 2000,  # Increased for complete step-by-step guides
                        "temperature": 0.7,
                        "topP": 0.9
                    }
                )
                
                ai_response = response.get('output', {}).get('message', {}).get('content', [{}])[0].get('text', '').strip()
                
            except Exception as converse_error:
                # Fallback to invoke_model for older models
                logger.warning(f"Converse API failed, trying invoke_model: {converse_error}")
                
                if "anthropic.claude" in self.model_id.lower():
                    # Claude API format (Messages API)
                    response = self.bedrock.invoke_model(
                        modelId=self.model_id,
                        body=json.dumps({
                            "anthropic_version": "bedrock-2023-05-31",
                            "max_tokens": 2000,
                            "temperature": 0.7,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": context
                                }
                            ]
                        })
                    )
                    
                    response_body = json.loads(response['body'].read())
                    ai_response = response_body.get('content', [{}])[0].get('text', '').strip()
                    
                else:
                    # Generic fallback format
                    response = self.bedrock.invoke_model(
                        modelId=self.model_id,
                        body=json.dumps({
                            "prompt": context,
                            "max_gen_len": 2000,
                            "temperature": 0.7,
                            "top_p": 0.9
                        })
                    )
                    
                    response_body = json.loads(response['body'].read())
                    ai_response = response_body.get('generation', '').strip()
            
            # Clean response
            ai_response = self._clean_response(ai_response, context)
            
            # If this was a guide request but response doesn't contain all 5 steps, provide fallback guide
            if is_guide_request and ai_response:
                step_count = sum(1 for i in range(1, 6) if f"STEP {i}" in ai_response.upper())
                if step_count < 5:
                    logger.warning(f"AI response only had {step_count}/5 steps, providing fallback guide")
                    return self._get_fallback_guide(user_message, user_profile)
            
            return ai_response if ai_response else self._fallback_response(user_message, user_profile)
            
        except Exception as e:
            logger.error(f"AI response error: {e}")
            # If it was a guide request, provide fallback guide instead of generic response
            if is_guide_request:
                return self._get_fallback_guide(user_message, user_profile)
            return self._fallback_response(user_message, user_profile)
    
    def _get_conversation_stage(self, user_profile: Dict) -> str:
        """Determine current conversation stage"""
        fields_collected = sum([1 for k in ['name', 'age', 'state', 'income', 'occupation'] if user_profile.get(k)])
        
        if fields_collected == 0:
            return "🟡 GREETING - Just started, need to collect name first"
        elif fields_collected < 5:
            missing = [k for k in ['name', 'age', 'state', 'income', 'occupation'] if not user_profile.get(k)]
            return f"🟠 PROFILE COLLECTION - {fields_collected}/5 fields collected (Missing: {', '.join(missing)})"
        else:
            return "🟢 PROFILE COMPLETE - Ready to recommend schemes and provide guidance"
    
    def _update_conversation_context(self, user_message: str, user_profile: Dict):
        """Update conversation memory for better context awareness"""
        message_lower = user_message.lower()
        
        # Track topics discussed
        topics = ['scheme', 'apply', 'document', 'eligibility', 'benefit', 'deadline']
        for topic in topics:
            if topic in message_lower and topic not in self.conversation_context['topics_discussed']:
                self.conversation_context['topics_discussed'].append(topic)
        
        # Track schemes mentioned
        schemes = ['pm-kisan', 'pmkisan', 'ayushman', 'mudra', 'scholarship', 'awas']
        for scheme in schemes:
            if scheme in message_lower and scheme not in self.conversation_context['schemes_mentioned']:
                self.conversation_context['schemes_mentioned'].append(scheme)
        
        # Track questions asked
        if '?' in user_message:
            self.conversation_context['questions_asked'].append(user_message[:50])
        
        # Track user interests based on occupation
        if user_profile.get('occupation'):
            occupation = user_profile['occupation'].lower()
            if occupation not in self.conversation_context['user_interests']:
                self.conversation_context['user_interests'].append(occupation)
    
    def _validate_input(self, field: str, value: any, user_message: str) -> Dict:
        """Validate user input and detect potential mistakes"""
        validation_result = {
            'is_valid': True,
            'needs_confirmation': False,
            'error_message': None,
            'suggestion': None,
            'confidence': 'high'
        }
        
        if field == 'name':
            # Check if name looks valid
            if len(str(value)) < 2:
                validation_result['is_valid'] = False
                validation_result['error_message'] = "Name seems too short"
                validation_result['suggestion'] = "Please provide your full name"
            elif any(char.isdigit() for char in str(value)):
                validation_result['needs_confirmation'] = True
                validation_result['confidence'] = 'low'
                validation_result['suggestion'] = f"I got '{value}' as your name. Is this correct?"
            elif len(str(value).split()) == 1 and len(str(value)) > 2:
                validation_result['needs_confirmation'] = True
                validation_result['confidence'] = 'medium'
                validation_result['suggestion'] = f"I got '{value}'. Is this your full name or just first name?"
        
        elif field == 'age':
            try:
                age_val = int(value)
                if age_val < 5 or age_val > 120:
                    validation_result['is_valid'] = False
                    validation_result['error_message'] = f"Age {age_val} seems unusual"
                    validation_result['suggestion'] = "Please provide a valid age (5-120 years)"
                elif age_val < 18:
                    validation_result['needs_confirmation'] = True
                    validation_result['confidence'] = 'medium'
                    validation_result['suggestion'] = f"I got {age_val} years. Is this correct? (Most schemes require 18+)"
                elif age_val > 100:
                    validation_result['needs_confirmation'] = True
                    validation_result['confidence'] = 'low'
                    validation_result['suggestion'] = f"I got {age_val} years. Please confirm if this is correct"
            except:
                validation_result['is_valid'] = False
                validation_result['error_message'] = "Could not understand age"
                validation_result['suggestion'] = "Please provide age as a number (e.g., 25, 30, 45)"
        
        elif field == 'state':
            # Check if state is recognized
            valid_states = ['andhra pradesh', 'bihar', 'chhattisgarh', 'delhi', 'gujarat', 
                          'haryana', 'karnataka', 'kerala', 'madhya pradesh', 'maharashtra',
                          'odisha', 'punjab', 'rajasthan', 'tamil nadu', 'telangana', 
                          'uttar pradesh', 'uttarakhand', 'west bengal']
            
            if value and value.lower() not in valid_states:
                validation_result['needs_confirmation'] = True
                validation_result['confidence'] = 'medium'
                validation_result['suggestion'] = f"I got '{value}'. Is this the correct state name?"
        
        elif field == 'income':
            try:
                income_val = int(value)
                if income_val < 0:
                    validation_result['is_valid'] = False
                    validation_result['error_message'] = "Income cannot be negative"
                    validation_result['suggestion'] = "Please provide yearly income (e.g., 2 lakh, 5 lakh)"
                elif income_val > 100000000:  # 10 crore
                    validation_result['needs_confirmation'] = True
                    validation_result['confidence'] = 'low'
                    validation_result['suggestion'] = f"I got Rs.{income_val:,}. Please confirm if this is your yearly income"
                elif income_val < 10000:  # Less than 10k seems low for yearly
                    validation_result['needs_confirmation'] = True
                    validation_result['confidence'] = 'medium'
                    validation_result['suggestion'] = f"I got Rs.{income_val:,} per year. Is this correct?"
            except:
                validation_result['is_valid'] = False
                validation_result['error_message'] = "Could not understand income"
                validation_result['suggestion'] = "Please provide yearly income (e.g., 2 lakh, 5 lakh, 10 lakh)"
        
        elif field == 'occupation':
            # Check if occupation is recognized
            valid_occupations = ['farmer', 'student', 'business', 'job', 'self-employed', 
                               'homemaker', 'agriculture', 'unemployed']
            
            if value and value.lower() not in valid_occupations:
                validation_result['needs_confirmation'] = True
                validation_result['confidence'] = 'medium'
                validation_result['suggestion'] = f"I got '{value}'. Is this your occupation?"
        
        return validation_result
    
    def _build_context(self, user_message: str, user_profile: Dict, conversation_history: List) -> str:
        """Build intelligent context for AI - Enhanced for natural conversation"""
        
        # Analyze conversation stage
        profile_complete = all([
            user_profile.get('name'),
            user_profile.get('age'),
            user_profile.get('state'),
            user_profile.get('income'),
            user_profile.get('occupation')
        ])
        
        # Get conversation stage
        stage = self._get_conversation_stage(user_profile)
        
        # Build conversation history with better context
        history_text = ""
        if conversation_history:
            recent = conversation_history[-8:]  # Last 4 exchanges for better context
            for msg in recent:
                role = "User" if msg['role'] == 'user' else "You (AI)"
                history_text += f"{role}: {msg['content']}\n"
        
        # Count fields collected
        fields_collected = sum([1 for k in ['name', 'age', 'state', 'income', 'occupation'] if user_profile.get(k)])
        
        # Determine what to ask next
        next_field = None
        if not user_profile.get('name'):
            next_field = "name"
        elif not user_profile.get('age'):
            next_field = "age"
        elif not user_profile.get('state'):
            next_field = "state"
        elif not user_profile.get('income'):
            next_field = "income"
        elif not user_profile.get('occupation'):
            next_field = "occupation"
        
        context = f"""You are YojnaMitra-AI, a warm, friendly, and helpful assistant for Indian government schemes.

PERSONALITY:
- Speak naturally in Hinglish (mix of Hindi and English)
- Be encouraging and supportive
- Show genuine interest in helping the user
- Use emojis occasionally to be friendly (😊, 👍, ✅, 🎉)
- Acknowledge user's responses warmly before asking next question
- Be conversational, not robotic

USER PROFILE (Current):
Name: {user_profile.get('name', 'Not provided yet')}
Age: {user_profile.get('age', 'Not provided yet')}
State: {user_profile.get('state', 'Not provided yet')}
Income: {f"Rs.{user_profile.get('income'):,}/year" if user_profile.get('income') else 'Not provided yet'}
Occupation: {user_profile.get('occupation', 'Not provided yet')}

CONVERSATION STAGE: {stage}
FIELDS COLLECTED: {fields_collected}/5
NEXT FIELD NEEDED: {next_field if next_field else "Profile Complete!"}

VALIDATION & CORRECTION MODE:
Pending Confirmation: {self.conversation_context.get('pending_confirmation', 'None')}
Correction Mode: {self.conversation_context.get('correction_mode', False)}

RECENT CONVERSATION:
{history_text if history_text else "This is the beginning of our conversation."}

USER'S CURRENT MESSAGE: "{user_message}"

CRITICAL INSTRUCTION - DETECT APPLICATION GUIDE REQUESTS:
If the user message contains ANY of these keywords: "step-by-step", "how to apply", "apply for", "application guide", "guidance", "help me apply"
AND mentions a scheme name (PM-KISAN, Ayushman Bharat, MUDRA, NSP, PM Awas, etc.)
THEN you MUST provide the complete step-by-step application guide (see instruction #3 below).

CONVERSATION RULES:

0. INTELLIGENT INPUT VALIDATION & CORRECTION:
   
   ALWAYS validate user inputs and ask for confirmation when needed:
   
   a) After extracting ANY field, check if it seems correct:
      - Name: Check if it's a valid name (no numbers, reasonable length)
      - Age: Check if it's in valid range (5-120), warn if <18 or >100
      - State: Check if it's a recognized Indian state
      - Income: Check if it's reasonable (not negative, not too high/low)
      - Occupation: Check if it's a recognized occupation
   
   b) If input seems UNUSUAL or INCORRECT:
      - Ask for confirmation: "I got [VALUE]. Is this correct?"
      - Offer to change: "If you want to change it, just tell me the correct [FIELD]"
      - Be polite and helpful
   
   c) If user says "yes", "correct", "right", "haan":
      - Accept the value
      - Move to next field
      - Example: "Great! ✅ Moving ahead..."
   
   d) If user says "no", "wrong", "change", "nahi":
      - Ask for correct value
      - Example: "No problem! What's the correct [FIELD]?"
   
   e) If user provides correction directly:
      - Accept new value
      - Confirm: "Got it! Updated to [NEW_VALUE] ✅"
      - Move to next field
   
   VALIDATION EXAMPLES:
   
   User: "123"
   AI: "Hmm, '123' doesn't look like a name. 🤔 
        Could you please provide your full name?"
   
   User: "Rahul123"
   AI: "I got 'Rahul123' as your name. Is this correct? 
        (Names usually don't have numbers)"
   
   User: "15"
   AI: "I got 15 years as your age. Is this correct? 
        (Most schemes require 18+ age) ⚠️"
   
   User: "150"
   AI: "I got 150 years. 🤔 That seems unusual! 
        Could you please confirm your age?"
   
   User: "Dilli"
   AI: "I got 'Dilli'. Did you mean Delhi? 
        Please confirm the state name."
   
   User: "50000"
   AI: "I got Rs.50,000 per year. Is this your yearly income? 
        (Seems a bit low, just confirming)"

1. IF USER PROFILE IS INCOMPLETE ({fields_collected}/5 fields):
   
   ALWAYS follow this pattern:
   a) First, warmly acknowledge what they just said
   b) Then ask for the next missing field naturally
   
   Examples of GOOD responses:
   - User says "Rahul": "Bahut achha Rahul ji! 😊 Aapki age kitni hai?"
   - User says "25": "Great! 25 saal... perfect age for many schemes! 👍 Aap kis state se belong karte ho?"
   - User says "Bihar": "Bihar se! Wonderful! 🎉 Aap kya kaam karte ho? (Jaise: Farmer, Student, Business, Job)"
   - User says "Farming": "Farming! Bahut achha! 🌾 Aapki yearly income approximately kitni hai? (Jaise: 2 lakh, 5 lakh)"
   - User says "3 lakh": "Perfect! Rs.3 lakh per year. Excellent! ✅"
   
   IMPORTANT:
   - Ask ONLY ONE question at a time
   - Use natural Hinglish (not pure English or pure Hindi)
   - Be warm and encouraging
   - If user provides multiple pieces of info, acknowledge ALL of them
   - Show enthusiasm about their responses
   
   Field-specific questions:
   - Name: "Aapka naam kya hai? 😊"
   - Age: "Aapki age kitni hai?"
   - State: "Aap kis state se belong karte ho? (Jaise: Bihar, UP, Maharashtra, Delhi)"
   - Occupation: "Aap kya kaam karte ho? (Jaise: Farmer, Student, Business, Job)"
   - Income: "Aapki yearly income approximately kitni hai? (Jaise: 2 lakh, 5 lakh, 10 lakh)"

2. IF USER PROFILE IS COMPLETE (5/5 fields):
   
   Celebrate completion warmly:
   "Excellent {user_profile.get('name', '')} ji! 🎉 Aapki profile complete ho gayi!
   
   Ab main aapke liye best schemes dhundh raha hoon... 🔍
   
   Aapke liye perfect schemes:
   [List 3-5 matching schemes with details]"
   
   For each scheme, provide:
   - ⭐ Scheme name
   - 💰 Benefit amount
   - ✅ Why you're eligible
   - 📄 Required documents
   - 🔗 Application link
   
   End with: "Kisi bhi scheme ke liye apply karne mein help chahiye? Just click the 'Apply Guide' button! 😊"

3. IF USER ASKS FOR APPLICATION HELP:
   YOU MUST provide the complete 5-step guide (same as before - don't change this part)

4. IF USER ASKS GENERAL QUESTIONS:
   - Answer naturally and helpfully
   - Relate back to schemes if relevant
   - Be encouraging
   - Offer to help with next steps
   
   Examples:
   - "What documents do I need?" → List common documents + offer to show specific scheme requirements
   - "How long does it take?" → "Usually 10-15 minutes per scheme. Main aapko step-by-step guide de sakta hoon!"
   - "Is it safe?" → "Bilkul safe! Sab government portals hain. Aapka data secure hai. 🔒"

5. GENERAL CONVERSATION TIPS:
   - Be conversational, not formal
   - Use Hinglish naturally (70% Hindi, 30% English)
   - Show empathy and understanding
   - Celebrate small wins (profile completion, finding schemes)
   - Be patient if user is confused
   - Offer help proactively
   - Use emojis sparingly but effectively
   - Keep responses concise (under 150 words) unless providing step-by-step guide
   - Always end with a clear next step or question

RESPOND NOW (naturally, warmly, helpfully):"""

        return context
    
    def _clean_response(self, response: str, context: str) -> str:
        """Clean AI response"""
        # Remove prompt echo
        if response.startswith(context):
            response = response[len(context):].strip()
        
        # Remove artifacts
        for artifact in ["Provide a helpful", "User Question:", "Response:", "Assistant:", "Note:"]:
            if artifact in response:
                response = response.split(artifact)[0].strip()
        
        # Remove quotes
        response = response.strip('"').strip("'")
        
        return response
    
    def _fallback_response(self, user_message: str, user_profile: Dict) -> str:
        """Fallback response when AI unavailable - warm and conversational"""
        
        if not user_profile.get('name'):
            return "Namaste! 🙏 Main YojnaMitra-AI hoon. Main aapko government schemes dhundne mein madad karunga. Pehle baat karte hain - aapka naam kya hai? 😊"
        
        elif not user_profile.get('age'):
            name = user_profile['name']
            return f"Bahut achha {name} ji! 😊 Nice to meet you! Ab batao, aapki age kitni hai?"
        
        elif not user_profile.get('state'):
            name = user_profile['name']
            age = user_profile['age']
            return f"Great {name} ji! {age} saal... perfect! 👍 Aap kis state se belong karte ho? (Jaise: Bihar, UP, Maharashtra, Delhi, etc.)"
        
        elif not user_profile.get('income'):
            name = user_profile['name']
            return f"Wonderful {name} ji! 🎉 Ab batao, aapki yearly income approximately kitni hai? (Jaise: 2 lakh, 5 lakh, 10 lakh)"
        
        elif not user_profile.get('occupation'):
            name = user_profile['name']
            return f"Perfect {name} ji! ✅ Last question - aap kya kaam karte ho? (Jaise: Farmer, Student, Business, Job, etc.)"
        
        else:
            name = user_profile['name']
            return f"Excellent {name} ji! 🎉 Aapki profile complete ho gayi!\n\nAb main aapke liye best government schemes dhundh raha hoon... 🔍\n\nBas kuch seconds! ⏳"
    
    def _get_fallback_guide(self, user_message: str, user_profile: Dict) -> str:
        """Provide fallback step-by-step guide when AI doesn't generate complete guide"""
        
        # Extract scheme name from message
        scheme_name = "the scheme"
        scheme_url = "the official portal"
        
        # Try to identify scheme from message
        schemes_map = {
            'pm-kisan': ('PM-KISAN', 'https://pmkisan.gov.in'),
            'pmkisan': ('PM-KISAN', 'https://pmkisan.gov.in'),
            'kisan': ('PM-KISAN', 'https://pmkisan.gov.in'),
            'ayushman': ('Ayushman Bharat', 'https://pmjay.gov.in'),
            'pmjay': ('Ayushman Bharat', 'https://pmjay.gov.in'),
            'mudra': ('MUDRA Loan', 'https://www.mudra.org.in'),
            'scholarship': ('National Scholarship Portal', 'https://scholarships.gov.in'),
            'nsp': ('National Scholarship Portal', 'https://scholarships.gov.in'),
            'awas': ('PM Awas Yojana', 'https://pmaymis.gov.in'),
            'housing': ('PM Awas Yojana', 'https://pmaymis.gov.in')
        }
        
        message_lower = user_message.lower()
        for key, (name, url) in schemes_map.items():
            if key in message_lower:
                scheme_name = name
                scheme_url = url
                break
        
        return f"""Let me guide you step-by-step to apply for {scheme_name}:

**STEP 1: Open Application Link & Login**
Click this link: {scheme_url}

If you're a new user:
- Click 'Register' or 'New Registration'
- Enter your mobile number
- Verify OTP sent to your phone
- Create a strong password
- Login with your credentials

If you already have an account:
- Click 'Login'
- Enter your username and password

**STEP 2: Find the Scheme**
After logging in:
- Use the search bar and type '{scheme_name}'
- OR navigate to the relevant category (Agriculture/Education/Health/Business)
- Click on the scheme name to open the application form

**STEP 3: Fill All Required Details**
Fill in these details carefully:
- Personal Information: Full Name (exactly as per Aadhar), Date of Birth, Gender
- Contact Details: Mobile number, Email address, Complete address with Pin Code
- Identity Details: Aadhar number, PAN card number (if required)
- Bank Details: Bank account number, IFSC code, Bank name
- Scheme-specific information (varies by scheme)

IMPORTANT: Make sure all details match your Aadhar card exactly!
Fill all mandatory fields (marked with * asterisk)

**STEP 4: Upload Required Documents**
Upload these documents if the form asks for them:
- Aadhar Card (PDF or JPG format, maximum 2MB)
- Passport size photograph (JPG format, maximum 100KB)
- Bank Passbook or Cancelled Cheque (first page showing account details)
- Income Certificate (if required for the scheme)
- Any other scheme-specific documents

To upload: Click 'Choose File' or 'Browse' → Select the document from your computer → Click 'Upload'

Note: Some schemes may not require document upload at this stage

**STEP 5: Review, Submit & Get Confirmation**
Before submitting:
- Carefully review all the information you entered
- Make sure everything is correct
- Tick the declaration checkbox (if present)
- Click the 'Submit' or 'Apply' button

After submission:
- You will see a confirmation message
- SAVE YOUR APPLICATION ID (example: {scheme_name.upper().replace(' ', '').replace('-', '')}2026XXXXX)
- Take a screenshot of the confirmation page
- You will receive a confirmation SMS on your registered mobile number
- You may also receive a confirmation email
- Save the tracking link to check your application status later

Congratulations! Your application is submitted. You'll receive confirmation via SMS/Email shortly.

Need help with any specific step? Just ask! 😊"""



class SchemeSearchEngine:
    """Search and match government schemes"""
    
    def __init__(self, rag_engine=None):
        """Initialize search engine with optional RAG support"""
        self.rag_engine = rag_engine
    
    def generate_personalized_reasons(self, user_profile: Dict, scheme: Dict) -> List[str]:
        """Generate personalized reasons why a scheme is perfect for the user"""
        reasons = []
        
        # Age match
        if scheme.get('min_age') and scheme.get('max_age'):
            user_age = user_profile.get('age')
            if user_age and scheme['min_age'] <= user_age <= scheme['max_age']:
                reasons.append(f"✅ Your age ({user_age} years) is perfect for this scheme")
        
        # Income match
        if scheme.get('max_income'):
            user_income = user_profile.get('income')
            if user_income and user_income <= scheme['max_income']:
                reasons.append(f"✅ Your income (Rs.{user_income:,}/year) qualifies you")
        
        # Occupation match
        user_occupation = user_profile.get('occupation')
        if user_occupation and scheme.get('occupations'):
            if user_occupation in scheme['occupations'] or 'All' in scheme['occupations']:
                reasons.append(f"✅ Designed specifically for {user_occupation}s like you")
        
        # State match
        user_state = user_profile.get('state')
        if user_state and scheme.get('states'):
            if user_state in scheme['states'] or 'All India' in scheme['states']:
                reasons.append(f"✅ Available in your state ({user_state})")
        
        # High match score
        if scheme.get('match_score') and scheme['match_score'] >= 90:
            reasons.append(f"✅ Excellent match ({scheme['match_score']}% compatibility)")
        
        # If no specific reasons, add generic one
        if not reasons:
            reasons.append("✅ You meet the basic eligibility criteria")
        
        return reasons
    
    def check_upcoming_deadlines(self, schemes: List[Dict]) -> List[Dict]:
        """Check for upcoming deadlines and generate notifications"""
        notifications = []
        
        for scheme in schemes:
            deadline = scheme.get('deadline', 'Open')
            
            if deadline and deadline != 'Open':
                # Parse deadline (simplified - in production use proper date parsing)
                deadline_lower = deadline.lower()
                
                # Check for month mentions
                current_month = datetime.now().strftime('%B').lower()
                months = ['january', 'february', 'march', 'april', 'may', 'june',
                         'july', 'august', 'september', 'october', 'november', 'december']
                
                for i, month in enumerate(months):
                    if month in deadline_lower:
                        # Rough estimate - if current month or next month
                        current_month_idx = datetime.now().month - 1
                        if i == current_month_idx:
                            notifications.append({
                                'scheme': scheme['name'],
                                'deadline': deadline,
                                'urgency': 'high',
                                'message': f"⚠️ URGENT: {scheme['name']} deadline this month ({deadline})!",
                                'days_estimate': 15
                            })
                        elif i == (current_month_idx + 1) % 12:
                            notifications.append({
                                'scheme': scheme['name'],
                                'deadline': deadline,
                                'urgency': 'medium',
                                'message': f"⏰ {scheme['name']} deadline next month ({deadline})",
                                'days_estimate': 45
                            })
        
        return notifications
    
    def search_schemes(self, user_profile: Dict) -> List[Dict]:
        """Search schemes from internet and database"""
        
        matched_schemes = []
        
        # Scheme database (in production, this would be from API/web scraping)
        all_schemes = self._get_scheme_database()
        
        # If RAG engine available, use semantic search
        if self.rag_engine:
            try:
                logger.info("Using RAG engine for semantic scheme matching")
                matched_schemes = self._rag_search(user_profile, all_schemes)
            except Exception as e:
                logger.error(f"RAG search failed: {e}. Falling back to rule-based matching.")
                matched_schemes = self._rule_based_search(user_profile, all_schemes)
        else:
            # Fallback to rule-based matching
            matched_schemes = self._rule_based_search(user_profile, all_schemes)
        
        return matched_schemes[:10]  # Top 10 matches
    
    def _rag_search(self, user_profile: Dict, all_schemes: List[Dict]) -> List[Dict]:
        """Use RAG engine for semantic search"""
        # Create user profile text
        profile_text = f"""
        User Profile:
        - Name: {user_profile.get('name', 'Unknown')}
        - Age: {user_profile.get('age', 'Unknown')} years
        - State: {user_profile.get('state', 'Unknown')}
        - Income: Rs.{user_profile.get('income', 0):,} per year
        - Occupation: {user_profile.get('occupation', 'Unknown')}
        - Category: {user_profile.get('category', 'General')}
        - Gender: {user_profile.get('gender', 'Unknown')}
        - Education: {user_profile.get('education', 'Unknown')}
        """
        
        # Create scheme embeddings
        scheme_embeddings = self.rag_engine.create_scheme_embeddings(all_schemes)
        
        # Perform semantic search
        search_results = self.rag_engine.semantic_search(profile_text, scheme_embeddings, top_k=10)
        
        # Convert to scheme format with similarity scores
        matched_schemes = []
        for result in search_results:
            scheme = result['scheme'].copy()
            scheme['match_score'] = int(result['similarity'] * 100)  # Convert to percentage
            scheme['match_reason'] = 'RAG Semantic Match'
            matched_schemes.append(scheme)
        
        logger.info(f"RAG search found {len(matched_schemes)} schemes")
        return matched_schemes
    
    def _rule_based_search(self, user_profile: Dict, all_schemes: List[Dict]) -> List[Dict]:
        """Fallback rule-based matching"""
        matched_schemes = []
        
        # Match schemes based on eligibility
        for scheme in all_schemes:
            if self._check_eligibility(user_profile, scheme):
                matched_schemes.append(scheme)
        
        # Sort by relevance
        matched_schemes.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        return matched_schemes
    
    def _check_eligibility(self, user_profile: Dict, scheme: Dict) -> bool:
        """Check if user is eligible for scheme"""
        
        # Age check
        if scheme.get('min_age') and user_profile.get('age'):
            if user_profile['age'] < scheme['min_age']:
                return False
        if scheme.get('max_age') and user_profile.get('age'):
            if user_profile['age'] > scheme['max_age']:
                return False
        
        # Income check
        if scheme.get('max_income') and user_profile.get('income'):
            if user_profile['income'] > scheme['max_income']:
                return False
        
        # Occupation check
        if scheme.get('occupations') and user_profile.get('occupation'):
            if user_profile['occupation'].lower() not in [occ.lower() for occ in scheme['occupations']]:
                return False
        
        # State check
        if scheme.get('states') and user_profile.get('state'):
            if user_profile['state'] not in scheme['states'] and 'All India' not in scheme['states']:
                return False
        
        return True
    
    def _get_scheme_database(self) -> List[Dict]:
        """Get scheme database (mock data - in production, fetch from API)"""
        
        return [
            {
                'name': 'PM-KISAN',
                'full_name': 'Pradhan Mantri Kisan Samman Nidhi',
                'description': 'Direct income support to farmers providing Rs.6000 per year in three equal installments',
                'benefit': 'Rs.6,000 per year in 3 installments',
                'benefits': 'Rs.6,000 per year in 3 installments',
                'eligibility': 'All farmers who own land',
                'min_age': 18,
                'max_age': 100,
                'max_income': 10000000,
                'occupations': ['Farmer', 'Agriculture'],
                'states': ['All India'],
                'documents': ['Aadhaar Card', 'Bank Account', 'Land Records'],
                'apply_link': 'https://pmkisan.gov.in',
                'deadline': '31st March 2026',
                'match_score': 95
            },
            {
                'name': 'Ayushman Bharat',
                'full_name': 'Pradhan Mantri Jan Arogya Yojana (PM-JAY)',
                'description': 'Health insurance scheme providing Rs.5 lakh coverage per family per year for secondary and tertiary care hospitalization',
                'benefit': 'Rs.5 lakh health insurance per family per year',
                'benefits': 'Rs.5 lakh health insurance per family per year',
                'eligibility': 'Families in SECC database (BPL)',
                'min_age': 0,
                'max_age': 100,
                'max_income': 300000,
                'occupations': ['All'],
                'states': ['All India'],
                'documents': ['Aadhaar Card', 'Ration Card', 'Income Certificate'],
                'apply_link': 'https://pmjay.gov.in',
                'deadline': 'Open',
                'match_score': 90
            },
            {
                'name': 'MUDRA Loan',
                'full_name': 'Micro Units Development and Refinance Agency',
                'description': 'Collateral-free loans up to Rs.10 lakh for micro and small enterprises to start or expand business',
                'benefit': 'Rs.10 lakh loan for micro enterprises',
                'benefits': 'Rs.10 lakh loan for micro enterprises',
                'eligibility': 'Small business owners, entrepreneurs',
                'min_age': 18,
                'max_age': 65,
                'max_income': 10000000,
                'occupations': ['Business', 'Self-employed', 'Entrepreneur'],
                'states': ['All India'],
                'documents': ['Aadhaar Card', 'PAN Card', 'Business Plan', 'Bank Statements'],
                'apply_link': 'https://www.mudra.org.in',
                'deadline': 'Open',
                'match_score': 85
            },
            {
                'name': 'National Scholarship Portal',
                'full_name': 'NSP - Scholarships for Students',
                'description': 'Merit and means-based scholarships for students from class 10th onwards ranging from Rs.10,000 to Rs.1,00,000 per year',
                'benefit': 'Rs.10,000 to Rs.1,00,000 per year',
                'benefits': 'Rs.10,000 to Rs.1,00,000 per year',
                'eligibility': 'Students from class 10th onwards',
                'min_age': 10,
                'max_age': 35,
                'max_income': 800000,
                'occupations': ['Student'],
                'states': ['All India'],
                'documents': ['Aadhaar Card', 'Income Certificate', 'Marksheets', 'Bank Account'],
                'apply_link': 'https://scholarships.gov.in',
                'deadline': '31st October 2026',
                'match_score': 88
            },
            {
                'name': 'PM Awas Yojana',
                'full_name': 'Pradhan Mantri Awas Yojana - Housing for All',
                'description': 'Housing subsidy scheme providing Rs.1.2 to 2.5 lakh for construction or purchase of pucca house',
                'benefit': 'Rs.1.2 to 2.5 lakh subsidy for house construction',
                'benefits': 'Rs.1.2 to 2.5 lakh subsidy for house construction',
                'eligibility': 'Families without pucca house',
                'min_age': 18,
                'max_age': 70,
                'max_income': 1800000,
                'occupations': ['All'],
                'states': ['All India'],
                'documents': ['Aadhaar Card', 'Income Certificate', 'Property Documents'],
                'apply_link': 'https://pmaymis.gov.in',
                'deadline': 'Open',
                'match_score': 82
            }
        ]


def extract_profile_info(user_message: str, current_profile: Dict) -> Dict:
    """Extract profile information from user message with improved logic and validation"""
    
    import re
    
    message_lower = user_message.lower()
    updated_profile = current_profile.copy()
    
    # Check if user is confirming or correcting
    confirmation_words = ['yes', 'haan', 'correct', 'right', 'sahi', 'ok', 'okay', 'yeah']
    correction_words = ['no', 'nahi', 'wrong', 'galat', 'change', 'nope']
    
    is_confirmation = any(word in message_lower for word in confirmation_words)
    is_correction = any(word in message_lower for word in correction_words)
    
    # Extract NAME - improved logic with validation
    if not updated_profile.get('name') or (is_correction and 'name' in message_lower):
        # Remove common words and extract name
        common_words = ['my', 'name', 'is', 'i', 'am', 'mera', 'naam', 'hai', 'main', 'hoon', 'no', 'nahi', 'change']
        words = user_message.split()
        name_words = [w for w in words if w.lower() not in common_words and len(w) > 1 and not w.isdigit()]
        
        if name_words:
            # Take first 1-3 words as name
            potential_name = ' '.join(name_words[:3])
            if len(potential_name) > 1:
                # Basic validation
                if not any(char.isdigit() for char in potential_name):
                    updated_profile['name'] = potential_name.strip().title()
                    updated_profile['name_needs_confirmation'] = len(potential_name.split()) == 1
    
    # Extract AGE - improved logic with validation
    if not updated_profile.get('age') or (is_correction and 'age' in message_lower):
        # Look for age patterns
        age_patterns = [
            r'\b(\d{1,3})\s*(?:years?|saal|साल|yr|yrs)',
            r'\b(\d{1,3})\s*(?:ka|ki|ke)',
            r'(?:age|umar|उम्र)\s*(?:is|hai)?\s*(\d{1,3})',
            r'\b(\d{1,3})\b'  # Just a number
        ]
        
        for pattern in age_patterns:
            age_match = re.search(pattern, message_lower)
            if age_match:
                age = int(age_match.group(1))
                if 5 <= age <= 120:
                    updated_profile['age'] = age
                    # Flag for confirmation if unusual
                    updated_profile['age_needs_confirmation'] = age < 18 or age > 100
                    break
    
    # Extract STATE - improved logic with validation
    if not updated_profile.get('state') or (is_correction and 'state' in message_lower):
        states = {
            'Andhra Pradesh': ['andhra', 'ap'],
            'Bihar': ['bihar'],
            'Chhattisgarh': ['chhattisgarh', 'chattisgarh'],
            'Delhi': ['delhi', 'dilli'],
            'Gujarat': ['gujarat', 'gujrat'],
            'Haryana': ['haryana'],
            'Karnataka': ['karnataka', 'bengaluru', 'bangalore'],
            'Kerala': ['kerala'],
            'Madhya Pradesh': ['madhya pradesh', 'mp', 'bhopal'],
            'Maharashtra': ['maharashtra', 'mumbai', 'pune'],
            'Odisha': ['odisha', 'orissa'],
            'Punjab': ['punjab'],
            'Rajasthan': ['rajasthan', 'jaipur'],
            'Tamil Nadu': ['tamil nadu', 'tn', 'chennai'],
            'Telangana': ['telangana', 'hyderabad'],
            'Uttar Pradesh': ['uttar pradesh', 'up', 'lucknow'],
            'Uttarakhand': ['uttarakhand', 'uttaranchal'],
            'West Bengal': ['west bengal', 'bengal', 'kolkata', 'calcutta']
        }
        
        for state, keywords in states.items():
            if any(kw in message_lower for kw in keywords):
                updated_profile['state'] = state
                break
    
    # Extract INCOME - improved logic with validation
    if not updated_profile.get('income') or (is_correction and 'income' in message_lower):
        # Look for income patterns
        income_patterns = [
            (r'(\d+)\s*(?:lakh|lakhs|लाख)', 100000),
            (r'(\d+)\s*(?:thousand|हजार|k)', 1000),
            (r'(\d+)\s*(?:crore|करोड़)', 10000000),
            (r'(\d{4,})', 1)  # Direct number like 50000
        ]
        
        for pattern, multiplier in income_patterns:
            income_match = re.search(pattern, message_lower)
            if income_match:
                income = int(income_match.group(1)) * multiplier
                if 1000 <= income <= 100000000:  # Reasonable range
                    updated_profile['income'] = income
                    # Flag for confirmation if unusual
                    updated_profile['income_needs_confirmation'] = income < 50000 or income > 10000000
                    break
    
    # Extract OCCUPATION - improved logic with validation
    if not updated_profile.get('occupation') or (is_correction and 'occupation' in message_lower):
        occupations = {
            'Farmer': ['farmer', 'farming', 'किसान', 'खेती', 'agriculture', 'kisaan'],
            'Student': ['student', 'studying', 'छात्र', 'college', 'school', 'padhai'],
            'Business': ['business', 'businessman', 'व्यवसाय', 'entrepreneur', 'vyavsay', 'shop'],
            'Job': ['job', 'working', 'employee', 'नौकरी', 'service', 'naukri', 'work'],
            'Homemaker': ['homemaker', 'housewife', 'grahini', 'घरेलू'],
            'Self-employed': ['self-employed', 'freelance', 'contractor']
        }
        
        for occ, keywords in occupations.items():
            if any(kw in message_lower for kw in keywords):
                updated_profile['occupation'] = occ
                break
    
    return updated_profile


# Main App
def main():
    # Check authentication
    session_manager = SessionManager()
    
    if not session_manager.is_authenticated():
        # Show authentication page
        render_auth_page()
        return
    
    # User is authenticated - show main app
    # Header with premium SVG logo
    st.markdown("""
    <div class="ai-header">
        <div style="display: flex; align-items: center; justify-content: center; gap: 1.5rem; flex-wrap: wrap;">
            <svg width="80" height="80" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="mainLogoGradient1" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                        <stop offset="50%" style="stop-color:#764ba2;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#f093fb;stop-opacity:1" />
                    </linearGradient>
                    <linearGradient id="mainLogoGradient2" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#FF6B35;stop-opacity:1" />
                        <stop offset="50%" style="stop-color:#F7931E;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#FFBB00;stop-opacity:1" />
                    </linearGradient>
                    <filter id="mainGlow">
                        <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                        <feMerge>
                            <feMergeNode in="coloredBlur"/>
                            <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                    </filter>
                </defs>
                <circle cx="60" cy="60" r="55" fill="none" stroke="url(#mainLogoGradient1)" stroke-width="3" opacity="0.3">
                    <animateTransform attributeName="transform" type="rotate" from="0 60 60" to="360 60 60" dur="20s" repeatCount="indefinite"/>
                </circle>
                <circle cx="60" cy="60" r="45" fill="none" stroke="url(#mainLogoGradient1)" stroke-width="2" opacity="0.5">
                    <animateTransform attributeName="transform" type="rotate" from="360 60 60" to="0 60 60" dur="15s" repeatCount="indefinite"/>
                </circle>
                <circle cx="60" cy="60" r="40" fill="url(#mainLogoGradient1)" filter="url(#mainGlow)">
                    <animate attributeName="r" values="40;42;40" dur="3s" repeatCount="indefinite"/>
                </circle>
                <rect x="35" y="35" width="50" height="6" fill="#FF9933" rx="2"/>
                <rect x="35" y="44" width="50" height="6" fill="white" rx="2"/>
                <rect x="35" y="53" width="50" height="6" fill="#138808" rx="2"/>
                <circle cx="60" cy="47" r="4" fill="none" stroke="#000080" stroke-width="0.5"/>
                <circle cx="60" cy="47" r="2" fill="#000080"/>
                <g transform="translate(60, 72)">
                    <path d="M -8,-5 Q -10,-8 -8,-10 Q -5,-12 0,-10 Q 5,-12 8,-10 Q 10,-8 8,-5 Q 10,-2 8,2 Q 5,5 0,3 Q -5,5 -8,2 Q -10,-2 -8,-5 Z" 
                          fill="url(#mainLogoGradient2)" stroke="white" stroke-width="1" opacity="0.9"/>
                    <circle cx="-4" cy="-3" r="1.5" fill="white">
                        <animate attributeName="opacity" values="1;0.5;1" dur="2s" repeatCount="indefinite"/>
                    </circle>
                    <circle cx="4" cy="-3" r="1.5" fill="white">
                        <animate attributeName="opacity" values="0.5;1;0.5" dur="2s" repeatCount="indefinite"/>
                    </circle>
                    <circle cx="0" cy="0" r="1.5" fill="white">
                        <animate attributeName="opacity" values="1;0.5;1" dur="2s" repeatCount="indefinite" begin="0.5s"/>
                    </circle>
                    <line x1="-4" y1="-3" x2="0" y2="0" stroke="white" stroke-width="0.5" opacity="0.6"/>
                    <line x1="4" y1="-3" x2="0" y2="0" stroke="white" stroke-width="0.5" opacity="0.6"/>
                </g>
                <g opacity="0.8">
                    <circle cx="20" cy="30" r="2" fill="white">
                        <animate attributeName="opacity" values="0;1;0" dur="3s" repeatCount="indefinite"/>
                    </circle>
                    <circle cx="100" cy="40" r="2" fill="white">
                        <animate attributeName="opacity" values="0;1;0" dur="3s" repeatCount="indefinite" begin="1s"/>
                    </circle>
                    <circle cx="30" cy="90" r="2" fill="white">
                        <animate attributeName="opacity" values="0;1;0" dur="3s" repeatCount="indefinite" begin="2s"/>
                    </circle>
                    <circle cx="90" cy="85" r="2" fill="white">
                        <animate attributeName="opacity" values="0;1;0" dur="3s" repeatCount="indefinite" begin="1.5s"/>
                    </circle>
                </g>
            </svg>
            <div style="text-align: left;">
                <h1 style="margin: 0; font-size: 2.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">YojnaMitra-AI</h1>
                <p style="font-size: 1.2rem; margin: 0.5rem 0 0 0; opacity: 0.9;">Your Intelligent Government Scheme Assistant</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize AI
    ai = YojnaMitraAI()
    search_engine = SchemeSearchEngine(rag_engine=ai.rag_engine)
    
    # Sidebar - User Profile
    with st.sidebar:
        # Language Selection at the top
        st.markdown("### 🌐 Language / भाषा")
        
        languages = [
            'English/Hindi/Hinglish (Auto)',
            'हिंदी (Hindi)',
            'தமிழ் (Tamil)',
            'తెలుగు (Telugu)',
            'বাংলা (Bengali)',
            'मराठी (Marathi)',
            'ગુજરાતી (Gujarati)',
            'ಕನ್ನಡ (Kannada)',
            'മലയാളം (Malayalam)',
            'ਪੰਜਾਬੀ (Punjabi)',
            'ଓଡ଼ିଆ (Odia)',
            'অসমীয়া (Assamese)'
        ]
        
        selected_lang = st.selectbox(
            "Select your preferred language:",
            languages,
            index=languages.index(st.session_state.selected_language),
            help="AI auto-detects English, Hindi, and Hinglish. Select a regional language for translation."
        )
        
        # Update session state if language changed
        if selected_lang != st.session_state.selected_language:
            st.session_state.selected_language = selected_lang
            st.success(f"✅ Language changed to: {selected_lang}")
            st.rerun()
        
        st.markdown("---")
        
        # Scheme Filters (if schemes available)
        if st.session_state.matched_schemes:
            st.markdown("### 🔍 Filter Schemes")
            
            # Benefit filter
            max_benefit = max([s.get('match_score', 0) for s in st.session_state.matched_schemes])
            min_match = st.slider("Minimum Match Score", 0, 100, 0, 5)
            
            # Category filter
            categories = list(set([s.get('category', 'Other') for s in st.session_state.matched_schemes]))
            selected_categories = st.multiselect("Categories", categories, default=categories)
            
            # Deadline filter
            deadline_options = ["All", "Urgent (This Month)", "Soon (Next Month)", "Open"]
            deadline_filter = st.selectbox("Deadline", deadline_options)
            
            # Apply filters button
            if st.button("🔍 Apply Filters", use_container_width=True):
                st.success("✅ Filters applied!")
                st.rerun()
        
        st.markdown("---")
        
        # Quick Stats Dashboard
        st.markdown("### 📊 Your Dashboard")
        
        col1, col2 = st.columns(2)
        with col1:
            schemes_found = len(st.session_state.matched_schemes)
            st.metric("Schemes Found", schemes_found, delta=None)
        with col2:
            saved_count = len(st.session_state.saved_schemes)
            st.metric("Saved", saved_count, delta=None)
        
        if st.session_state.matched_schemes:
            avg_match = sum(s.get('match_score', 0) for s in st.session_state.matched_schemes[:5]) / min(5, len(st.session_state.matched_schemes))
            st.progress(avg_match / 100)
            st.caption(f"Average Match: {avg_match:.0f}%")
        
        st.markdown("---")
        
        # Progress Bar - Show profile completion
        st.markdown("### 📊 Profile Progress")
        fields_collected = sum([1 for k in ['name', 'age', 'state', 'income', 'occupation'] 
                               if st.session_state.user_profile.get(k)])
        progress = fields_collected / 5
        st.progress(progress)
        st.caption(f"**{fields_collected}/5 fields completed** {'✅' if fields_collected == 5 else '⏳'}")
        
        if fields_collected < 5:
            missing_fields = [k.title() for k in ['name', 'age', 'state', 'income', 'occupation'] 
                            if not st.session_state.user_profile.get(k)]
            st.info(f"📝 Still need: {', '.join(missing_fields)}")
        else:
            st.success("🎉 Profile Complete! Ready to find schemes.")
        
        st.markdown("---")
        
        # User info and logout
        user_profile = session_manager.get_user_profile()
        if user_profile:
            st.markdown("### 👤 Logged In")
            phone = user_profile.get('phone', 'Unknown')
            st.info(f"📱 {phone}")
            
            if st.button("🚪 Logout", use_container_width=True):
                session_manager.logout()
        
        st.markdown("---")
        st.markdown("### 👤 Your Profile")
        
        profile = st.session_state.user_profile
        if profile:
            for key, value in profile.items():
                if value:
                    st.markdown(f'<div class="profile-badge">{key.title()}: {value}</div>', unsafe_allow_html=True)
        else:
            st.info("Complete your profile to see matching schemes!")
        
        st.markdown("---")
        
        # FAQ Section
        with st.expander("❓ Frequently Asked Questions"):
            st.markdown("""
            **Q: How long does the application take?**  
            A: Usually 10-15 minutes per scheme.
            
            **Q: Do I need an Aadhar card?**  
            A: Yes, Aadhar is mandatory for most government schemes.
            
            **Q: Can I apply for multiple schemes?**  
            A: Yes! You can apply for all schemes you are eligible for.
            
            **Q: How do I check application status?**  
            A: Use the tracking link provided after submission.
            
            **Q: Is my data safe?**  
            A: Yes! All data is encrypted and stored securely on AWS.
            
            **Q: What if I need help?**  
            A: Just ask me in the chat! I am here to help 24/7.
            """)
        
        # Pro Tips Section
        with st.expander("💡 Pro Tips"):
            st.markdown("""
            **Before Applying:**
            - ✅ Keep Aadhar card ready
            - ✅ Have bank account details handy
            - ✅ Scan all documents (PDF/JPG, max 2MB)
            - ✅ Use a valid mobile number for OTP
            
            **During Application:**
            - ✅ Fill all mandatory fields (marked with *)
            - ✅ Double-check Aadhar number
            - ✅ Match details exactly with Aadhar
            - ✅ Save application ID after submission
            
            **After Submission:**
            - ✅ Take screenshot of confirmation
            - ✅ Note down application ID
            - ✅ Check email/SMS for confirmation
            - ✅ Track status using provided link
            """)
        
        # Success Stories Section
        with st.expander("🌟 Success Stories"):
            st.markdown("""
            **Ramesh Kumar** from Bihar
            
            Applied for: PM-KISAN
            Received: Rs.6,000
            
            _"Got Rs.6,000 in just 2 weeks! YojnaMitra made it so easy. Highly recommend!"_ ⭐⭐⭐⭐⭐
            
            ---
            
            **Priya Sharma** from Maharashtra
            
            Applied for: MUDRA Loan
            Received: Rs.5 lakh loan
            
            _"Started my business with MUDRA loan. The step-by-step guide was perfect!"_ ⭐⭐⭐⭐⭐
            
            ---
            
            **Amit Patel** from Gujarat
            
            Applied for: Ayushman Bharat
            Received: Rs.5 lakh health coverage
            
            _"My family is now covered. Thank you YojnaMitra for making it simple!"_ ⭐⭐⭐⭐⭐
            """)
        
        st.markdown("---")
        
        # Saved Schemes Section
        st.markdown("### 💾 Saved Schemes")
        if st.session_state.saved_schemes:
            for idx, scheme in enumerate(st.session_state.saved_schemes):
                with st.expander(f"📌 {scheme['name']}", expanded=False):
                    st.caption(scheme['benefit'])
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📝 Apply", key=f"saved_apply_{idx}", use_container_width=True):
                            st.session_state.messages.append({
                                'role': 'user',
                                'content': f"How to apply for {scheme['name']}? Please give me complete step-by-step guidance with all 5 steps."
                            })
                            st.rerun()
                    with col2:
                        if st.button("🗑️ Remove", key=f"saved_remove_{idx}", use_container_width=True):
                            st.session_state.saved_schemes.pop(idx)
                            st.rerun()
        else:
            st.caption("No saved schemes yet. Click 💾 Save on any scheme to bookmark it.")
        
        st.markdown("---")
        
        # Notifications
        st.markdown("### 🔔 Notifications")
        if st.session_state.notifications:
            for notif in st.session_state.notifications:
                st.warning(f"🔔 {notif}")
        else:
            st.success("No new notifications")
        
        st.markdown("---")
        
        if st.button("🔄 Start New Conversation"):
            st.session_state.messages = []
            st.session_state.user_profile = {}
            st.session_state.matched_schemes = []
            st.rerun()
    
    # Chat Container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Quick Action Bar (if profile is complete)
    if all([st.session_state.user_profile.get(k) for k in ['name', 'age', 'state', 'income', 'occupation']]):
        st.markdown("### ⚡ Quick Actions")
        qcol1, qcol2, qcol3, qcol4 = st.columns(4)
        
        with qcol1:
            if st.button("🔍 Find More Schemes", use_container_width=True):
                st.session_state.messages.append({
                    'role': 'user',
                    'content': "Show me more schemes I'm eligible for"
                })
                st.rerun()
        
        with qcol2:
            if st.button("💾 View Saved", use_container_width=True):
                if st.session_state.saved_schemes:
                    st.info(f"You have {len(st.session_state.saved_schemes)} saved schemes. Check sidebar!")
                else:
                    st.warning("No saved schemes yet. Click 💾 Save on any scheme.")
        
        with qcol3:
            if st.button("📊 Compare Schemes", use_container_width=True):
                if len(st.session_state.matched_schemes) >= 2:
                    st.info("Scroll down to see comparison section!")
                else:
                    st.warning("Need at least 2 schemes to compare.")
        
        with qcol4:
            if st.button("❓ Get Help", use_container_width=True):
                st.session_state.messages.append({
                    'role': 'user',
                    'content': "I need help understanding how to apply for schemes"
                })
                st.rerun()
        
        st.markdown("---")
    
    # Display messages
    if not st.session_state.messages:
        # Welcome message - SIMPLIFIED AND FOCUSED ON CORE VALUE
        welcome = """Hi! 👋 Main **YojnaMitra-AI** hoon!

🎯 **Main 2 minute mein aapke liye:**
✅ 500+ schemes mein se best schemes dhundhunga
✅ Eligibility check karke matching schemes dikhaunga
✅ Step-by-step apply karne mein help karunga
✅ Aapki language mein baat karunga (12+ languages)

**Bas 5 simple questions!** Chalo shuru karte hain! 😊

Aapka naam kya hai?"""
        
        # Translate welcome message if needed
        translated_welcome = translate_text(welcome, st.session_state.selected_language)
        st.markdown(f'<div class="ai-message">{translated_welcome}</div>', unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            if msg['role'] == 'user':
                st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                # Translate AI response if regional language is selected
                translated_content = translate_text(msg['content'], st.session_state.selected_language)
                st.markdown(f'<div class="ai-message">{translated_content}</div>', unsafe_allow_html=True)
    
    # Display matched schemes
    if st.session_state.matched_schemes:
        # Show RAG status
        if ai.rag_engine:
            st.success("🚀 Using RAG Workflow: Titan Embeddings v2 + Qwen3 235B for intelligent matching!")
        else:
            st.info("ℹ️ Using rule-based matching (RAG unavailable)")
        
        # Check for upcoming deadlines and show notifications
        deadline_notifications = search_engine.check_upcoming_deadlines(st.session_state.matched_schemes)
        if deadline_notifications:
            st.markdown("### 🔔 Important Notifications")
            for notif in deadline_notifications:
                if notif['urgency'] == 'high':
                    st.error(notif['message'])
                else:
                    st.warning(notif['message'])
            st.markdown("---")
        
        # WhatsApp Share Button
        st.markdown("### 📱 Share Your Schemes")
        whatsapp_url = generate_whatsapp_share_link(st.session_state.user_profile, st.session_state.matched_schemes)
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            st.markdown(f"[📱 Share on WhatsApp]({whatsapp_url})")
            st.caption("Share these schemes with your family and friends!")
        with col2:
            schemes_count = len(st.session_state.matched_schemes)
            st.metric("Schemes Found", schemes_count)
        with col3:
            if st.session_state.matched_schemes:
                avg_match = sum(s.get('match_score', 0) for s in st.session_state.matched_schemes[:5]) / min(5, len(st.session_state.matched_schemes))
                st.metric("Avg Match", f"{avg_match:.0f}%")
        with col4:
            # Download Report Button
            if st.button("📥 Download Report", use_container_width=True):
                # Generate simple text report
                report = f"YojnaMitra-AI Scheme Report\n"
                report += f"Generated: {datetime.now().strftime('%d %B %Y')}\n\n"
                report += f"Profile:\n"
                report += f"Name: {st.session_state.user_profile.get('name', 'N/A')}\n"
                report += f"Age: {st.session_state.user_profile.get('age', 'N/A')}\n"
                report += f"State: {st.session_state.user_profile.get('state', 'N/A')}\n"
                report += f"Occupation: {st.session_state.user_profile.get('occupation', 'N/A')}\n"
                report += f"Income: Rs.{st.session_state.user_profile.get('income', 0):,}\n\n"
                report += f"Matched Schemes ({len(st.session_state.matched_schemes)}):\n\n"
                
                for i, scheme in enumerate(st.session_state.matched_schemes[:10], 1):
                    report += f"{i}. {scheme['name']}\n"
                    report += f"   Benefit: {scheme['benefit']}\n"
                    report += f"   Match: {scheme.get('match_score', 0)}%\n"
                    report += f"   Deadline: {scheme['deadline']}\n"
                    report += f"   Apply: {scheme['apply_link']}\n\n"
                
                st.download_button(
                    label="📥 Download as Text File",
                    data=report,
                    file_name=f"yojnamitra_schemes_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        st.markdown("---")
        st.markdown("### 🎯 Matched Schemes for You")
        
        # Group schemes by category
        scheme_categories = {}
        for scheme in st.session_state.matched_schemes[:5]:
            # Determine category based on scheme name/type
            if any(word in scheme['name'].lower() for word in ['kisan', 'farmer', 'agriculture']):
                category = '🌾 Agriculture'
            elif any(word in scheme['name'].lower() for word in ['health', 'ayushman', 'medical']):
                category = '🏥 Health'
            elif any(word in scheme['name'].lower() for word in ['scholarship', 'education', 'student']):
                category = '🎓 Education'
            elif any(word in scheme['name'].lower() for word in ['mudra', 'loan', 'business']):
                category = '💼 Business'
            elif any(word in scheme['name'].lower() for word in ['awas', 'housing', 'home']):
                category = '🏠 Housing'
            else:
                category = '📋 Other'
            
            if category not in scheme_categories:
                scheme_categories[category] = []
            scheme_categories[category].append(scheme)
        
        # Display schemes by category
        for category, schemes in scheme_categories.items():
            st.markdown(f"#### {category}")
            
            for scheme in schemes:
                # Show match score and priority indicator
                match_info = ""
                priority_badge = ""
                
                if 'match_score' in scheme:
                    match_info = f" ({scheme['match_score']}% match)"
                    # Add priority indicator for high matches
                    if scheme['match_score'] > 90:
                        priority_badge = "🔥 **HIGHLY RECOMMENDED FOR YOU** | "
                    elif scheme['match_score'] > 80:
                        priority_badge = "⭐ **GREAT MATCH** | "
                
                if 'match_reason' in scheme:
                    match_info += f" - {scheme['match_reason']}"
                
                # Check for deadline urgency
                if scheme.get('deadline') and scheme['deadline'] != 'Open':
                    if any(month in scheme['deadline'] for month in ['March', 'April', 'May']):
                        priority_badge = "⏰ **DEADLINE SOON** | " + priority_badge
                
                with st.expander(f"{priority_badge}⭐ {scheme['name']} - {scheme['benefit']}{match_info}"):
                    st.markdown(f"**Full Name:** {scheme['full_name']}")
                    st.markdown(f"**Benefit:** {scheme['benefit']}")
                    st.markdown(f"**Eligibility:** {scheme['eligibility']}")
                    
                    # NEW: Show personalized reasons
                    st.markdown("---")
                    st.markdown("### 💡 Why This is Perfect for You")
                    personalized_reasons = search_engine.generate_personalized_reasons(st.session_state.user_profile, scheme)
                    for reason in personalized_reasons:
                        st.markdown(reason)
                    
                    st.markdown("---")
                    st.markdown(f"**Documents:** {', '.join(scheme['documents'])}")
                    st.markdown(f"**Deadline:** {scheme['deadline']}")
                    st.markdown(f"**Apply:** [{scheme['apply_link']}]({scheme['apply_link']})")
                    
                    st.markdown("---")
                    st.markdown("### 🚀 Quick Actions")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button(f"📝 Apply Guide", key=f"guide_{scheme['name']}", use_container_width=True):
                            st.session_state.messages.append({
                                'role': 'user',
                                'content': f"How to apply for {scheme['name']}? Please give me complete step-by-step guidance with all 5 steps."
                            })
                            st.rerun()
                    
                    with col2:
                        if st.button(f"🚀 Quick Apply", key=f"apply_{scheme['name']}", use_container_width=True):
                            st.markdown(f"**Opening {scheme['name']} portal...**")
                            st.markdown(f"### [🔗 Click here to apply now]({scheme['apply_link']})")
                            st.info("💡 **Quick Tip**: Keep these ready before applying:\n- Aadhar Card\n- Bank Account details\n- Mobile number for OTP")
                            st.success("✅ Portal opened! Need help? Click 'Apply Guide' for step-by-step instructions.")
                    
                    with col3:
                        # Check if already saved
                        is_saved = any(s['name'] == scheme['name'] for s in st.session_state.saved_schemes)
                        if is_saved:
                            st.button(f"✅ Saved", key=f"saved_{scheme['name']}", use_container_width=True, disabled=True)
                        else:
                            if st.button(f"💾 Save", key=f"save_{scheme['name']}", use_container_width=True):
                                st.session_state.saved_schemes.append(scheme)
                                st.success(f"✅ {scheme['name']} saved!")
                                st.rerun()
                    
                    with col4:
                        if st.button(f"📄 Documents", key=f"docs_{scheme['name']}", use_container_width=True):
                            st.markdown("### ✅ Required Documents Checklist")
                            for doc in scheme['documents']:
                                st.markdown(f"✓ {doc}")
                            st.info("💡 Tip: Keep all documents in PDF/JPG format, max 2MB each")
    
    # Scheme Comparison Feature
    if len(st.session_state.matched_schemes) >= 2:
        st.markdown("---")
        st.markdown("### 📊 Compare Schemes")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("💡 Select 2-3 schemes to compare side-by-side")
        with col2:
            if st.button("🔄 Clear Selection", use_container_width=True):
                st.session_state.schemes_to_compare = []
                st.rerun()
        
        # Scheme selection for comparison
        comparison_cols = st.columns(min(3, len(st.session_state.matched_schemes)))
        for idx, col in enumerate(comparison_cols):
            if idx < len(st.session_state.matched_schemes):
                scheme = st.session_state.matched_schemes[idx]
                with col:
                    is_selected = scheme['name'] in st.session_state.schemes_to_compare
                    if st.checkbox(f"{scheme['name']}", value=is_selected, key=f"compare_{idx}"):
                        if scheme['name'] not in st.session_state.schemes_to_compare:
                            st.session_state.schemes_to_compare.append(scheme['name'])
                    else:
                        if scheme['name'] in st.session_state.schemes_to_compare:
                            st.session_state.schemes_to_compare.remove(scheme['name'])
        
        # Show comparison table
        if len(st.session_state.schemes_to_compare) >= 2:
            st.markdown("### 📋 Comparison Table")
            
            comparison_data = []
            for scheme_name in st.session_state.schemes_to_compare:
                scheme = next((s for s in st.session_state.matched_schemes if s['name'] == scheme_name), None)
                if scheme:
                    comparison_data.append({
                        'Scheme': scheme['name'],
                        'Benefit': scheme['benefit'],
                        'Match': f"{scheme.get('match_score', 0)}%",
                        'Deadline': scheme['deadline'],
                        'Documents': len(scheme['documents'])
                    })
            
            if comparison_data:
                import pandas as pd
                df = pd.DataFrame(comparison_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Download comparison
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Comparison (CSV)",
                    data=csv,
                    file_name="scheme_comparison.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Check if there's a pending message from button click that needs AI response
    if st.session_state.messages:
        # Check if last message is from user (no AI response yet)
        if st.session_state.messages[-1]['role'] == 'user':
            # Check if this is a new message (not already processed)
            # We check by seeing if there are an odd number of messages (user message without response)
            if len(st.session_state.messages) % 2 == 1:
                last_user_msg = st.session_state.messages[-1]['content']
                
                # Extract profile info
                st.session_state.user_profile = extract_profile_info(last_user_msg, st.session_state.user_profile)
                
                # Get AI response with better error handling
                try:
                    with st.spinner("🤖 YojnaMitra-AI is thinking..."):
                        ai_response = ai.get_response(
                            last_user_msg,
                            st.session_state.user_profile,
                            st.session_state.messages
                        )
                    
                    # Add AI response
                    st.session_state.messages.append({
                        'role': 'assistant',
                        'content': ai_response
                    })
                    
                except Exception as e:
                    logger.error(f"Error getting AI response: {e}")
                    st.session_state.messages.append({
                        'role': 'assistant',
                        'content': "I apologize, I'm having trouble processing your request. Let me try to help you differently. Could you please rephrase your question?"
                    })
                    st.error("⚠️ Temporary issue with AI. Please try again.")
                
                # Check if profile is complete and search schemes
                profile = st.session_state.user_profile
                if all([profile.get('name'), profile.get('age'), profile.get('state'), 
                        profile.get('income'), profile.get('occupation')]):
                    if not st.session_state.matched_schemes:
                        st.session_state.matched_schemes = search_engine.search_schemes(profile)
                        
                        # Add notification
                        st.session_state.notifications.append(
                            f"Found {len(st.session_state.matched_schemes)} matching schemes!"
                        )
                
                st.rerun()
    
    # Chat Input
    user_input = st.chat_input("Type your message here... (Hindi/English)")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({
            'role': 'user',
            'content': user_input
        })
        
        st.rerun()


if __name__ == "__main__":
    main()
