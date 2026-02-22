"""
Simple test script for AI Guardrails Criticality Scoring System
No external dependencies required
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.ai_guardrails import AIGuardrailsService


def test_criticality_scoring():
    """Test criticality scoring with all scenarios"""
    service = AIGuardrailsService()
    
    print("=" * 80)
    print("CRITICALITY SCORING TESTS")
    print("=" * 80)
    
    test_cases = [
        # Emergency queries (Score >= 9)
        ("I have severe chest pain spreading to my jaw", 9, "emergency_severe"),
        ("I can't breathe properly and my chest feels tight", 9, "emergency_severe"),
        ("I'm bleeding heavily and can't stop it", 9, "emergency_severe"),
        
        # High-risk symptoms (Score 7-8)
        ("I have sudden numbness in my left arm", 7, "high_risk_symptom"),
        ("I'm feeling chest pain", 7, "high_risk_symptom"),
        
        # Diagnostic queries (Score 5-6)
        ("Do I have cancer based on my test results?", 6, "diagnostic_query"),
        ("What disease do I have?", 6, "diagnostic_query"),
        
        # Treatment queries (Score 5-6)
        ("Should I stop taking my medication?", 5, "treatment_query"),
        
        # General health questions (Score < 5)
        ("What are the benefits of Vitamin D?", 0, None),
        ("How much water should I drink daily?", 0, None),
        ("What is a healthy diet for a 30-year-old?", 0, None),
        ("Can you explain what my cholesterol levels mean?", 0, None),
        ("What exercises are good for heart health?", 0, None),
    ]
    
    passed = 0
    failed = 0
    
    for query, expected_min_score, expected_flag in test_cases:
        score, flags = service.calculate_criticality_score(query)
        
        # Check score
        if expected_flag is None:
            # General queries should have score < 5
            if score < 5:
                status = "✓ PASS"
                passed += 1
            else:
                status = "✗ FAIL"
                failed += 1
        else:
            # Check if score meets minimum and flag is present
            if score >= expected_min_score and expected_flag in flags:
                status = "✓ PASS"
                passed += 1
            else:
                status = "✗ FAIL"
                failed += 1
        
        print(f"\n{status}")
        print(f"Query: {query}")
        print(f"Score: {score} (expected >= {expected_min_score})")
        print(f"Flags: {flags} (expected: {expected_flag})")
    
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)
    
    return failed == 0


def test_guardrails_application():
    """Test guardrails application with different scores"""
    service = AIGuardrailsService()
    
    print("\n" + "=" * 80)
    print("GUARDRAILS APPLICATION TESTS")
    print("=" * 80)
    
    test_scenarios = [
        {
            "name": "Emergency Response",
            "query": "I have severe chest pain",
            "ai_response": "Mock AI response",
            "expected_score_min": 9,
            "expected_guardrail": "emergency_response",
            "expected_in_response": ["🚨", "911"]
        },
        {
            "name": "Doctor Referral",
            "query": "I have sudden numbness in my left arm",
            "ai_response": "Mock AI response",
            "expected_score_min": 7,
            "expected_guardrail": "doctor_referral",
            "expected_in_response": ["schedule an appointment"]
        },
        {
            "name": "Cautious Information",
            "query": "Do I have cancer?",
            "ai_response": "Based on general information, cancer diagnosis requires...",
            "expected_score_min": 5,
            "expected_guardrail": "cautious_information",
            "expected_in_response": ["consult with your doctor"]
        },
        {
            "name": "General Information",
            "query": "What are the benefits of Vitamin D?",
            "ai_response": "Vitamin D is essential for bone health, immune function, and overall wellness.",
            "expected_score_min": 0,
            "expected_guardrail": "disclaimer_added",
            "expected_in_response": ["Vitamin D", "educational purposes"]
        }
    ]
    
    passed = 0
    failed = 0
    
    for scenario in test_scenarios:
        response, metadata = service.apply_patient_guardrails(
            scenario["query"],
            scenario["ai_response"]
        )
        
        # Check score
        score_ok = metadata["criticality_score"] >= scenario["expected_score_min"]
        
        # Check guardrail applied
        guardrail_ok = scenario["expected_guardrail"] in metadata["guardrails_applied"]
        
        # Check response content
        content_ok = all(
            expected.lower() in response.lower() 
            for expected in scenario["expected_in_response"]
        )
        
        if score_ok and guardrail_ok and content_ok:
            status = "✓ PASS"
            passed += 1
        else:
            status = "✗ FAIL"
            failed += 1
        
        print(f"\n{status} - {scenario['name']}")
        print(f"Query: {scenario['query']}")
        print(f"Score: {metadata['criticality_score']} (expected >= {scenario['expected_score_min']})")
        print(f"Guardrails: {metadata['guardrails_applied']}")
        print(f"Response preview: {response[:100]}...")
    
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_scenarios)} tests")
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    print("\n🧪 Testing AI Guardrails Criticality Scoring System\n")
    
    # Run tests
    scoring_ok = test_criticality_scoring()
    application_ok = test_guardrails_application()
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    if scoring_ok and application_ok:
        print("✓ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("✗ SOME TESTS FAILED")
        if not scoring_ok:
            print("  - Criticality scoring tests failed")
        if not application_ok:
            print("  - Guardrails application tests failed")
        sys.exit(1)
