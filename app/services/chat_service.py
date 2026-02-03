"""
Enhanced chat service with streaming and conversation history.
"""

from typing import AsyncIterator, Dict, Any, List
from sqlalchemy.orm import Session
import uuid
import json
from datetime import datetime

from app.models import PatientConversation, DoctorConversation
from app.services.aws_bedrock import bedrock_service
from app.services.rag_service import rag_service
import logging

logger = logging.getLogger(__name__)


class ChatService:
    """Enhanced chat service with streaming and history"""
    
    def __init__(self):
        self.bedrock = bedrock_service
        self.rag = rag_service
    
    async def patient_chat_streaming(
        self,
        patient_uuid: str,
        message: str,
        conversation_id: str = None,
        db: Session = None
    ) -> AsyncIterator[str]:
        """
        Streaming patient chat with conversation history.
        
        Yields:
            JSON strings with chunks of the response
        """
        try:
            # Get or create conversation
            if conversation_id:
                conversation = db.query(PatientConversation).filter(
                    PatientConversation.conversation_id == conversation_id
                ).first()
            else:
                conversation = None
            
            if not conversation:
                conversation = PatientConversation(
                    conversation_id=uuid.uuid4(),
                    patient_uuid=patient_uuid,
                    messages=[],
                    rag_context_ids=[]
                )
                db.add(conversation)
            
            # Get RAG context
            context_data = self.rag.get_context_for_chat(
                query=message,
                patient_uuid=patient_uuid,
                db=db,
                is_doctor=False
            )
            
            # Build system prompt
            system_prompt = """You are a compassionate healthcare AI assistant helping patients understand their medical information.
            
            Guidelines:
            - Be empathetic and supportive
            - Explain medical terms in simple language
            - If the query seems urgent or critical, acknowledge it and recommend seeing a doctor
            - Use the provided context from their medical records to give personalized responses
            - Never provide definitive diagnoses - always recommend consulting healthcare professionals
            - Be honest if you don't have enough information
            
            Context from patient's medical records:
            """ + context_data['context_text']
            
            # Build message history
            messages = []
            if conversation.messages:
                # Add last 5 messages for context
                for msg in conversation.messages[-5:]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Stream response
            full_response = ""
            for chunk in self.bedrock._stream_chat({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.bedrock.max_tokens,
                "temperature": 0.7,
                "messages": messages,
                "system": system_prompt
            }):
                # Extract text from chunk
                if chunk.get('type') == 'content_block_delta':
                    delta = chunk.get('delta', {})
                    if delta.get('type') == 'text_delta':
                        text = delta.get('text', '')
                        full_response += text
                        
                        # Yield chunk
                        yield json.dumps({
                            "type": "chunk",
                            "content": text,
                            "conversation_id": str(conversation.conversation_id)
                        }) + "\n"
            
            # Save conversation
            conversation.messages.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.utcnow().isoformat()
            })
            conversation.messages.append({
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.utcnow().isoformat()
            })
            conversation.rag_context_ids = context_data['chunk_ids']
            
            db.commit()
            
            # Yield completion
            yield json.dumps({
                "type": "complete",
                "conversation_id": str(conversation.conversation_id),
                "sources": context_data['source_documents']
            }) + "\n"
            
        except Exception as e:
            logger.error(f"Error in streaming chat: {e}")
            yield json.dumps({
                "type": "error",
                "message": str(e)
            }) + "\n"
    
    async def doctor_chat_streaming(
        self,
        doctor_uuid: str,
        patient_uuid: str,
        message: str,
        conversation_id: str = None,
        additional_context: str = None,
        db: Session = None
    ) -> AsyncIterator[str]:
        """
        Streaming doctor chat with conversation history.
        
        Yields:
            JSON strings with chunks of the response
        """
        try:
            # Get or create conversation
            if conversation_id:
                conversation = db.query(DoctorConversation).filter(
                    DoctorConversation.conversation_id == conversation_id
                ).first()
            else:
                conversation = None
            
            if not conversation:
                conversation = DoctorConversation(
                    conversation_id=uuid.uuid4(),
                    doctor_uuid=doctor_uuid,
                    patient_uuid=patient_uuid,
                    messages=[],
                    additional_context=additional_context or "",
                    rag_context_ids=[]
                )
                db.add(conversation)
            
            # Get RAG context (higher top_k for doctors)
            context_data = self.rag.get_context_for_chat(
                query=message,
                patient_uuid=patient_uuid,
                db=db,
                is_doctor=True
            )
            
            # Build system prompt
            system_prompt = f"""You are a medical AI assistant helping analyze patient medical records and provide clinical insights.
            
            Guidelines:
            - Provide detailed medical analysis
            - Use medical terminology appropriately
            - Highlight concerning findings
            - Suggest further tests or interventions if needed
            - Reference specific values and dates from medical records
            
            Additional Context: {additional_context or 'None'}
            
            Medical Records Context:
            """ + context_data['context_text']
            
            # Build message history
            messages = []
            if conversation.messages:
                # Add last 10 messages for context (more for doctors)
                for msg in conversation.messages[-10:]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Stream response
            full_response = ""
            for chunk in self.bedrock._stream_chat({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.bedrock.max_tokens,
                "temperature": 0.5,  # Lower for medical accuracy
                "messages": messages,
                "system": system_prompt
            }):
                # Extract text from chunk
                if chunk.get('type') == 'content_block_delta':
                    delta = chunk.get('delta', {})
                    if delta.get('type') == 'text_delta':
                        text = delta.get('text', '')
                        full_response += text
                        
                        # Yield chunk
                        yield json.dumps({
                            "type": "chunk",
                            "content": text,
                            "conversation_id": str(conversation.conversation_id)
                        }) + "\n"
            
            # Save conversation
            conversation.messages.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.utcnow().isoformat()
            })
            conversation.messages.append({
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.utcnow().isoformat()
            })
            conversation.rag_context_ids = context_data['chunk_ids']
            
            db.commit()
            
            # Yield completion
            yield json.dumps({
                "type": "complete",
                "conversation_id": str(conversation.conversation_id),
                "sources": context_data['source_documents']
            }) + "\n"
            
        except Exception as e:
            logger.error(f"Error in streaming chat: {e}")
            yield json.dumps({
                "type": "error",
                "message": str(e)
            }) + "\n"
    
    def get_conversation_history(
        self,
        conversation_id: str,
        db: Session,
        is_doctor: bool = False
    ) -> Dict[str, Any]:
        """Get conversation history"""
        try:
            if is_doctor:
                conversation = db.query(DoctorConversation).filter(
                    DoctorConversation.conversation_id == conversation_id
                ).first()
            else:
                conversation = db.query(PatientConversation).filter(
                    PatientConversation.conversation_id == conversation_id
                ).first()
            
            if not conversation:
                return None
            
            return {
                "conversation_id": str(conversation.conversation_id),
                "messages": conversation.messages,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return None


# Global instance
chat_service = ChatService()
