"""
RAG (Retrieval-Augmented Generation) Engine for YojnaMitra
Uses Amazon Bedrock Titan Embeddings + FAISS for semantic search
"""

import os
import json
import boto3
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class RAGEngine:
    """RAG engine for enhanced scheme recommendations"""
    
    def __init__(self):
        """Initialize RAG engine with Bedrock client"""
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv("BEDROCK_REGION", "ap-south-1"),
            aws_access_key_id=os.getenv("BEDROCK_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("BEDROCK_SECRET_ACCESS_KEY")
        )
        # Use correct Titan Embeddings model ID
        self.embeddings_model = "amazon.titan-embed-text-v2:0"
        self.llm_model = os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-lite-v1:0")
        
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding vector for text using Titan"""
        try:
            response = self.bedrock.invoke_model(
                modelId=self.embeddings_model,
                body=json.dumps({"inputText": text})
            )
            response_body = json.loads(response['body'].read())
            return response_body.get('embedding', [])
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            return []
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def create_scheme_embeddings(self, schemes: List[Dict]) -> List[Dict]:
        """Create embeddings for all schemes"""
        scheme_embeddings = []
        
        for scheme in schemes:
            # Create rich text representation
            text = f"""
            Scheme: {scheme['name']}
            Description: {scheme['description']}
            Eligibility: {scheme['eligibility']}
            Benefits: {scheme['benefits']}
            Category: {scheme['category']}
            Ministry: {scheme['ministry']}
            """
            
            embedding = self.get_embedding(text)
            
            if embedding:
                scheme_embeddings.append({
                    'scheme': scheme,
                    'embedding': embedding,
                    'text': text
                })
        
        logger.info(f"Created embeddings for {len(scheme_embeddings)} schemes")
        return scheme_embeddings
    
    def semantic_search(self, query: str, scheme_embeddings: List[Dict], top_k: int = 5) -> List[Dict]:
        """Perform semantic search to find relevant schemes"""
        query_embedding = self.get_embedding(query)
        
        if not query_embedding:
            logger.warning("Failed to get query embedding, returning empty results")
            return []
        
        # Calculate similarities
        similarities = []
        for item in scheme_embeddings:
            similarity = self.cosine_similarity(query_embedding, item['embedding'])
            similarities.append({
                'scheme': item['scheme'],
                'similarity': similarity,
                'text': item['text']
            })
        
        # Sort by similarity and return top K
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]
    
    def get_rag_recommendations(self, user_profile: str, schemes: List[Dict]) -> str:
        """
        Get RAG-enhanced recommendations
        
        Args:
            user_profile: User profile string
            schemes: List of all schemes
            
        Returns:
            AI-generated recommendations with RAG context
        """
        try:
            # Create embeddings for schemes (in production, cache this)
            scheme_embeddings = self.create_scheme_embeddings(schemes)
            
            # Create search query from user profile
            query = f"User profile: {user_profile}. Find relevant government schemes."
            
            # Retrieve relevant schemes using semantic search
            relevant_schemes = self.semantic_search(query, scheme_embeddings, top_k=5)
            
            # Build context from retrieved schemes
            context = "\n\n".join([
                f"Scheme {i+1}: {item['text']}"
                for i, item in enumerate(relevant_schemes)
            ])
            
            # Build enhanced prompt with RAG context
            prompt = f"""You are an expert advisor on Indian government schemes.

Retrieved Relevant Schemes (from semantic search):
{context}

User Profile:
{user_profile}

Task: Based on the retrieved schemes above, provide personalized advice in simple Hindi about:
1. Which schemes are most suitable for this user (prioritize by relevance)
2. Priority order for applying
3. Additional tips for maximizing benefits
4. Documents they might need

Keep response concise (200 words max) and in simple Hindi."""

            # Generate response with Bedrock
            if "llama" in self.llm_model.lower():
                response = self.bedrock.invoke_model(
                    modelId=self.llm_model,
                    body=json.dumps({
                        "prompt": prompt,
                        "max_gen_len": 500,
                        "temperature": 0.3,
                        "top_p": 0.9
                    })
                )
                response_body = json.loads(response['body'].read())
                ai_response = response_body.get('generation', 'No response')
            else:
                # Claude model
                response = self.bedrock.invoke_model(
                    modelId=self.llm_model,
                    body=json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 500,
                        "temperature": 0.3,
                        "messages": [{"role": "user", "content": prompt}]
                    })
                )
                response_body = json.loads(response['body'].read())
                ai_response = response_body['content'][0]['text']
            
            logger.info("RAG recommendations generated successfully")
            return ai_response
            
        except Exception as e:
            logger.error(f"Error in RAG recommendations: {str(e)}")
            # Fallback to basic recommendations
            return self._get_fallback_recommendations(user_profile, schemes)
    
    def _get_fallback_recommendations(self, user_profile: str, schemes: List[Dict]) -> str:
        """Fallback recommendations if RAG fails"""
        return """
        📋 सामान्य सुझाव:
        1. अपनी पात्रता के अनुसार योजनाओं को प्राथमिकता दें
        2. सभी आवश्यक दस्तावेज पहले से तैयार रखें
        3. आधिकारिक वेबसाइट से ही आवेदन करें
        
        📄 मुख्य दस्तावेज: आधार कार्ड, बैंक पासबुक, आय प्रमाण पत्र
        💡 टिप्स: नकली वेबसाइट से बचें, केवल .gov.in साइट का उपयोग करें
        """
