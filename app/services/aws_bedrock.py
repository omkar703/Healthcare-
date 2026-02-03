"""
AWS Bedrock service for Claude 3.5 Sonnet integration.
Handles chat completions, embeddings, and vision analysis.
"""

import boto3
import json
from typing import List, Dict, Any, Optional, Iterator
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class BedrockService:
    """AWS Bedrock service for Claude 3.5 Sonnet"""
    
    def __init__(self):
        """Initialize Bedrock client"""
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=settings.BEDROCK_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.model_id = settings.BEDROCK_MODEL_ID
        self.max_tokens = settings.BEDROCK_MAX_TOKENS
        
        logger.info(f"Initialized Bedrock client with model: {self.model_id}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Dict[str, Any] | Iterator[Dict[str, Any]]:
        """
        Generate chat completion using Claude.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0-1)
            stream: Whether to stream the response
            
        Returns:
            Response dict or iterator of response chunks if streaming
        """
        try:
            # Prepare request body
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "temperature": temperature,
                "messages": messages
            }
            
            if system_prompt:
                body["system"] = system_prompt
            
            if stream:
                return self._stream_chat(body)
            else:
                return self._invoke_chat(body)
                
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise
    
    def _invoke_chat(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Non-streaming chat completion"""
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body
    
    def _stream_chat(self, body: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Streaming chat completion"""
        response = self.client.invoke_model_with_response_stream(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        stream = response.get('body')
        if stream:
            for event in stream:
                chunk = event.get('chunk')
                if chunk:
                    chunk_data = json.loads(chunk.get('bytes').decode())
                    yield chunk_data
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using Amazon Titan.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            # Use Amazon Titan for embeddings
            embedding_model = "amazon.titan-embed-text-v1"
            
            body = json.dumps({
                "inputText": text
            })
            
            response = self.client.invoke_model(
                modelId=embedding_model,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            embedding = response_body.get('embedding', [])
            
            logger.debug(f"Generated embedding of dimension: {len(embedding)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def analyze_image(
        self,
        image_base64: str,
        prompt: str,
        mime_type: str = "image/jpeg"
    ) -> str:
        """
        Analyze image using Claude Vision.
        
        Args:
            image_base64: Base64-encoded image
            prompt: Analysis prompt
            mime_type: Image MIME type
            
        Returns:
            Analysis text from Claude
        """
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime_type,
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
            
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "messages": messages
            }
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            
            # Extract text from response
            content = response_body.get('content', [])
            if content and len(content) > 0:
                text_result = content[0].get('text', '')
                
                # Strict JSON extraction
                import re
                json_match = re.search(r'(\{[\s\S]*\})', text_result)
                if json_match:
                    return json_match.group(1)
                
                # Fallback: clean typical markdown but warn
                return text_result.replace("```json", "").replace("```", "").strip()
            
            return ""
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            raise
    
    def extract_medical_markers(self, text: str) -> Dict[str, Any]:
        """
        Extract medical risk markers from text using Claude.
        
        Args:
            text: Medical document text
            
        Returns:
            Dict with extracted markers and risk indicators
        """
        system_prompt = """You are a medical document analysis AI. Extract risk markers from medical documents.
        Focus on:
        - New lumps or masses
        - Nipple discharge (especially bloody)
        - Skin changes (dimpling, peau d'orange)
        - Family history indicators
        - BRCA mutations
        - Abnormal test results
        - Tumor markers
        
        Return a JSON object with extracted markers."""
        
        messages = [
            {
                "role": "user",
                "content": f"Extract medical risk markers from this document:\n\n{text}"
            }
        ]
        
        try:
            response = self.chat_completion(
                messages=messages,
                system_prompt=system_prompt,
                temperature=0.3  # Lower temperature for extraction
            )
            
            # Parse response
            content = response.get('content', [])
            if content and len(content) > 0:
                text_content = content[0].get('text', '{}')
                # Try to parse as JSON
                try:
                    markers = json.loads(text_content)
                    return markers
                except json.JSONDecodeError:
                    # If not valid JSON, return as text
                    return {"raw_analysis": text_content}
            
            return {}
            
        except Exception as e:
            logger.error(f"Error extracting medical markers: {e}")
            return {}


# Global instance
bedrock_service = BedrockService()
