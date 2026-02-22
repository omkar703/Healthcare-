"""
AI Guardrails Service for patient chat safety filters with criticality scoring.
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
        r"stage \\d+ (cancer|tumor)"
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
        logger.info("Initialized AI Guardrails Service with Criticality Scoring")
    
    def calculate_criticality_score(self, query: str) -> Tuple[int, List[str]]:
        """
        Calculate criticality score (0-10) for patient query.
        
        Scoring:
        - 9-10: Emergency (severe symptoms requiring immediate care)
        - 7-8: High-risk (urgent doctor consultation needed)
        - 5-6: Diagnostic/treatment queries (doctor consultation recommended)
        - 0-4: General health information (informational response appropriate)
        
        Args:
            query: User query text
            
        Returns:
            Tuple of (score, reasoning_flags)
        """
        score = 0
        flags = []
        query_lower = query.lower()
        
        # Emergency indicators (9-10)
        emergency_severe = [
            "severe chest pain", "can't breathe", "cannot breathe", "difficulty breathing",
            "severe bleeding", "bleeding heavily", "unconscious", "stroke", "heart attack",
            "suicide", "kill myself", "overdose", "poisoning", "anaphylaxis", "seizure",
            "convulsion", "severe allergic reaction"
        ]
        if any(keyword in query_lower for keyword in emergency_severe):
            score = max(score, 9)
            flags.append("emergency_severe")
        
        # High-risk symptoms requiring urgent evaluation (7-8)
        high_risk_symptoms = [
            "sudden numbness", "chest pain", "spreading pain", "radiating pain",
            "persistent severe pain", "persistent fever", "unexplained weight loss",
            "blood in stool", "blood in urine", "severe headache", "vision loss",
            "sudden weakness", "slurred speech", "facial drooping"
        ]
        if any(symptom in query_lower for symptom in high_risk_symptoms):
            score = max(score, 7)
            flags.append("high_risk_symptom")
        
        # Diagnostic queries (5-6) - seeking diagnosis
        diagnostic_patterns = [
            r"do i have (cancer|tumor|disease|diabetes|heart disease|stroke)",
            r"is this (cancer|tumor|serious|life-threatening)",
            r"am i (dying|going to die)",
            r"what (disease|condition) do i have"
        ]
        if any(re.search(pattern, query_lower) for pattern in diagnostic_patterns):
            score = max(score, 6)
            flags.append("diagnostic_query")
        
        # Treatment/medication decision queries (5-6)
        treatment_patterns = [
            r"should i (start|stop|change|discontinue|take|quit)",
            r"what (medication|drug|treatment|medicine) should i",
            r"can i (stop|quit|start|change)",
            r"(stop|start|change) (taking|using) (my )?(medication|drug|treatment|medicine)"
        ]
        if any(re.search(pattern, query_lower) for pattern in treatment_patterns):
            score = max(score, 5)
            flags.append("treatment_query")
        
        # General health questions remain at score 0-4 (default)
        # Examples: "benefits of vitamin D", "how much water", "healthy diet"
        # These will get informational responses
        
        return score, flags
    
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
        Apply safety guardrails to patient AI response using criticality scoring.
        
        Args:
            query: User query
            ai_response: Raw AI response
            
        Returns:
            Tuple of (filtered_response, metadata)
        """
        # Calculate criticality score
        score, flags = self.calculate_criticality_score(query)
        
        metadata = {
            "criticality_score": score,
            "criticality_flags": flags,
            "is_emergency": score >= 9,
            "is_complex": 7 <= score < 9,
            "guardrails_applied": []
        }
        
        # Emergency response (Sc >= 9)
        if score >= 9:
            metadata["guardrails_applied"].append("emergency_response")
            
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
        
        # Doctor referral for high-risk symptoms (7 <= Sc < 9)
        if 7 <= score < 9:
            metadata["guardrails_applied"].append("doctor_referral")
            
            referral_response = """I understand you're experiencing concerning symptoms. Based on what you've described, I recommend scheduling an appointment with your doctor soon for proper evaluation.

**Why you should see a doctor:**
- Your symptoms may require professional medical assessment
- A doctor can perform necessary examinations
- They can order appropriate tests if needed
- You'll receive personalized medical advice

**What to do:**
- 📞 **Call your doctor's office** to schedule an appointment
- 📋 **Note your symptoms** including when they started and any changes
- 📝 **List any questions** you want to ask your doctor

**In the meantime:**
- Monitor your symptoms
- Seek immediate care if symptoms worsen significantly
- Contact your doctor if you have urgent concerns

**What I can help with:**
- Explaining general health information
- Helping you understand your medical records
- Answering questions about your test results

Would you like me to help you understand something from your medical records?
"""
            return referral_response, metadata
        
        # Cautious information for diagnostic/treatment queries (5 <= Sc < 7)
        if 5 <= score < 7:
            metadata["guardrails_applied"].append("cautious_information")
            
            # Simplify the AI response
            simplified_response = self.simplify_medical_terms(ai_response)
            
            cautious_response = f"""{simplified_response}

---

**Important Medical Advice:**

While I can provide general health information, questions about diagnosis or treatment decisions require professional medical evaluation. I strongly recommend:

- 📞 **Consult with your doctor** to discuss your specific situation
- 📋 **Bring your medical records** to your appointment
- ✍️ **Prepare your questions** in advance

Your doctor can review your complete medical history, perform examinations, and provide personalized medical advice tailored to your needs.
"""
            return cautious_response, metadata
        
        # General information response (Sc < 5)
        # Simplify medical terminology
        simplified_response = self.simplify_medical_terms(ai_response)
        
        if simplified_response != ai_response:
            metadata["guardrails_applied"].append("terminology_simplified")
        
        # Add disclaimer if response contains medical information
        if any(term in simplified_response.lower() for term in ["test", "result", "level", "value", "normal", "abnormal", "health", "vitamin", "nutrient"]):
            metadata["guardrails_applied"].append("disclaimer_added")
            
            disclaimer = "\n\n---\n\n**Important:** This information is for educational purposes only. Always consult your healthcare provider for medical advice specific to your situation."
            simplified_response += disclaimer
        
        return simplified_response, metadata
    
    def build_patient_system_prompt(self, context: str) -> str:
        """
        Build system prompt for patient AI with refined safety guidelines.
        
        Args:
            context: RAG context from patient's medical documents
            
        Returns:
            System prompt with guardrails
        """
        return f"""You are a compassionate healthcare AI assistant helping patients understand their medical information.

**Your Primary Role:**
- Help patients understand their medical documents and test results
- Explain general health information in simple, accessible terms
- Provide educational health information
- Offer emotional support and reassurance

**Response Guidelines by Query Type:**

1. **General Health Questions** (vitamins, diet, exercise, lifestyle):
   - Provide clear, evidence-based information
   - Use simple language
   - Include practical examples
   - Be helpful and informative

2. **Test Result Interpretation**:
   - Explain what the values mean in simple terms
   - Indicate if values are in normal range
   - Avoid definitive diagnoses
   - Suggest discussing with doctor for personalized advice

3. **Symptom Questions**:
   - Acknowledge their concern empathetically
   - Provide general information about the symptom
   - Recommend appropriate level of care (routine vs urgent)
   - Never diagnose

**CRITICAL SAFETY RULES:**
- NEVER provide definitive diagnoses
- NEVER recommend specific medications or treatments
- NEVER make predictions about prognosis
- ALWAYS recommend professional consultation for serious concerns
- BE HONEST about limitations

**Context from patient's medical records:**
{context}

Remember: You're here to educate and support, not to replace medical professionals. For general health questions, provide helpful, informative responses.
"""


# Global instance
ai_guardrails_service = AIGuardrailsService()
