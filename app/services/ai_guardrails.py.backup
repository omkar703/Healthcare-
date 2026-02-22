"""
AI Guardrails Service for patient chat safety filters.
"""

import logging
import re
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class AIGuardrailsService:
    """Service for implementing AI safety guardrails for patient chats"""
    
    # Emergency keywords that trigger urgent medical attention recommendation
    EMERGENCY_KEYWORDS = [
        "emergency", "urgent", "severe pain", "chest pain", "difficulty breathing",
        "can't breathe", "heart attack", "stroke", "unconscious", "bleeding heavily",
        "severe bleeding", "suicide", "kill myself", "overdose", "poisoning",
        "severe allergic reaction", "anaphylaxis", "seizure", "convulsion"
    ]
    
    # Complex medical queries that should be redirected to doctor
    COMPLEX_QUERY_PATTERNS = [
        r"do i have (cancer|tumor|disease|condition)",
        r"is this (cancer|tumor|serious|dangerous)",
        r"should i (start|stop|change) (medication|treatment|drug)",
        r"what (medication|drug|treatment) should i (take|use)",
        r"diagnose",
        r"am i (dying|going to die)",
        r"prognosis",
        r"survival rate",
        r"stage \d+ (cancer|tumor)"
    ]
    
    # Medical terminology that should be simplified for patients
    MEDICAL_TERMS = {
        "myocardial infarction": "heart attack",
        "cerebrovascular accident": "stroke",
        "hypertension": "high blood pressure",
        "hyperlipidemia": "high cholesterol",
        "diabetes mellitus": "diabetes",
        "neoplasm": "abnormal growth",
        "malignant": "cancerous",
        "benign": "non-cancerous",
        "metastasis": "cancer spread",
        "carcinoma": "cancer",
        "edema": "swelling",
        "dyspnea": "shortness of breath",
        "tachycardia": "fast heart rate",
        "bradycardia": "slow heart rate"
    }
    
    def __init__(self):
        logger.info("Initialized AI Guardrails Service")
    
    def check_emergency(self, query: str) -> bool:
        """
        Check if query contains emergency keywords.
        
        Args:
            query: User query text
            
        Returns:
            True if emergency detected
        """
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.EMERGENCY_KEYWORDS)
    
    def check_complex_query(self, query: str) -> bool:
        """
        Check if query is too complex for patient AI.
        
        Args:
            query: User query text
            
        Returns:
            True if query is complex/diagnostic
        """
        query_lower = query.lower()
        return any(re.search(pattern, query_lower) for pattern in self.COMPLEX_QUERY_PATTERNS)
    
    def simplify_medical_terms(self, text: str) -> str:
        """
        Replace complex medical terms with simpler alternatives.
        
        Args:
            text: Text containing medical terminology
            
        Returns:
            Simplified text
        """
        simplified = text
        for medical_term, simple_term in self.MEDICAL_TERMS.items():
            # Case-insensitive replacement
            pattern = re.compile(re.escape(medical_term), re.IGNORECASE)
            simplified = pattern.sub(simple_term, simplified)
        
        return simplified
    
    def apply_patient_guardrails(
        self,
        query: str,
        ai_response: str
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Apply safety guardrails to patient AI response.
        
        Args:
            query: User query
            ai_response: Raw AI response
            
        Returns:
            Tuple of (filtered_response, metadata)
        """
        metadata = {
            "is_emergency": False,
            "is_complex": False,
            "guardrails_applied": []
        }
        
        # Check for emergency
        if self.check_emergency(query):
            metadata["is_emergency"] = True
            metadata["guardrails_applied"].append("emergency_detected")
            
            emergency_response = """🚨 **URGENT: Seek Immediate Medical Attention**

Based on your message, this may be a medical emergency. Please:

1. **Call emergency services (911/112) immediately** if you're experiencing:
   - Severe chest pain or pressure
   - Difficulty breathing
   - Severe bleeding
   - Loss of consciousness
   - Stroke symptoms (face drooping, arm weakness, speech difficulty)

2. **Go to the nearest emergency room** if symptoms are severe

3. **Contact your doctor immediately** for urgent medical advice

I'm an AI assistant and cannot provide emergency medical care. Your safety is the priority - please seek professional help right away.
"""
            return emergency_response, metadata
        
        # Check for complex/diagnostic queries
        if self.check_complex_query(query):
            metadata["is_complex"] = True
            metadata["guardrails_applied"].append("complex_query_redirect")
            
            redirect_response = f"""I understand you have important questions about your health. However, questions about diagnosis, treatment decisions, or serious medical conditions require professional medical evaluation.

**I recommend:**
- 📞 **Schedule an appointment with your doctor** to discuss your concerns
- 📋 **Bring your medical records** and test results to the appointment
- ✍️ **Write down your questions** beforehand so you don't forget anything

Your doctor can:
- Review your complete medical history
- Perform necessary examinations
- Order appropriate tests
- Provide personalized medical advice

**What I can help with:**
- Explaining general health information
- Helping you understand your test results (in simple terms)
- Answering questions about your medical documents
- Providing general wellness information

Would you like me to help you understand something specific from your medical records instead?
"""
            return redirect_response, metadata
        
        # Simplify medical terminology
        simplified_response = self.simplify_medical_terms(ai_response)
        
        if simplified_response != ai_response:
            metadata["guardrails_applied"].append("terminology_simplified")
        
        # Add disclaimer if response contains medical information
        if any(term in simplified_response.lower() for term in ["test", "result", "level", "value", "normal", "abnormal"]):
            metadata["guardrails_applied"].append("disclaimer_added")
            
            disclaimer = "\n\n---\n\n**Important:** This information is for educational purposes only. Always consult your healthcare provider for medical advice specific to your situation."
            simplified_response += disclaimer
        
        return simplified_response, metadata
    
    def build_patient_system_prompt(self, context: str) -> str:
        """
        Build system prompt for patient AI with safety guidelines.
        
        Args:
            context: RAG context from patient's medical documents
            
        Returns:
            System prompt with guardrails
        """
        return f"""You are a compassionate healthcare AI assistant helping patients understand their medical information.

**CRITICAL SAFETY GUIDELINES:**
1. **Never provide diagnoses** - Always recommend consulting a healthcare professional
2. **Simplify medical terminology** - Use plain language that patients can understand
3. **Be supportive and empathetic** - Health concerns can be stressful
4. **Acknowledge limitations** - Be honest when you don't have enough information
5. **Encourage professional consultation** - For any serious or complex questions

**Your Role:**
- Help patients understand their medical documents and test results
- Explain general health information in simple terms
- Answer questions about their medical records
- Provide emotional support and reassurance
- Direct them to appropriate medical professionals when needed

**What NOT to do:**
- Do NOT diagnose conditions
- Do NOT recommend specific treatments or medications
- Do NOT provide definitive medical advice
- Do NOT use complex medical jargon without explanation
- Do NOT make predictions about prognosis or outcomes

**Context from patient's medical records:**
{context}

Remember: You're here to inform and support, not to replace professional medical care.
"""


# Global instance
ai_guardrails_service = AIGuardrailsService()
