"""
Test OCR accuracy and compare Textract vs Vision model extraction.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.document_processor import document_processor
import base64


def test_patient_document():
    """Test OCR on patient medical document"""
    print("="*80)
    print("TESTING PATIENT MEDICAL DOCUMENT OCR")
    print("="*80)
    
    # Test file
    test_file = "_documents/patients/AHD-0425-PA-0007561_JITENDRA TRIVEDI DS_28-04-2025_1019-21_AM.pdf_page_9.png"
    
    print(f"\nFile: {test_file}")
    print("\n--- TIER 1: OCR Extraction (Textract) ---")
    
    try:
        # Test Tier 1 extraction
        tier_1_text = document_processor.process_tier_1(test_file, "image/png")
        print(f"\nExtracted {len(tier_1_text)} characters")
        print("\nFirst 500 characters:")
        print(tier_1_text[:500])
        
        # Test Tier 2 vision analysis
        print("\n\n--- TIER 2: Vision Analysis (Claude Vision) ---")
        tier_2_data = document_processor.process_tier_2(
            file_path=test_file,
            tier_1_text=tier_1_text,
            mime_type="image/png"
        )
        
        if tier_2_data.get('visual_analysis'):
            print("\nVision Analysis:")
            print(tier_2_data['visual_analysis'][:500])
        
        if tier_2_data.get('risk_markers'):
            print("\n\nRisk Markers Detected:")
            print(tier_2_data['risk_markers'])
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


def test_doctor_credential():
    """Test OCR on doctor credential documents"""
    print("\n\n" + "="*80)
    print("TESTING DOCTOR CREDENTIAL OCR")
    print("="*80)
    
    # Get all files in doctors directory
    doctor_dir = Path("_documents/doctors")
    if not doctor_dir.exists():
        print(f"Directory not found: {doctor_dir}")
        return

    files = [f for f in doctor_dir.glob("*") if f.is_file() and f.name != ".gitkeep"]
    
    print(f"Found {len(files)} documents in {doctor_dir}")
    
    for test_file in files:
        print(f"\nProcessing: {test_file.name}")
        print("-" * 50)
        
        try:
            # Test credential extraction
            if test_file.suffix.lower() == ".webp":
                print("  Skipping Textract for WEBP (unsupported format)")
                credentials = None
            else:
                credentials = document_processor.extract_doctor_credentials(str(test_file))
            
            print("Textract Extraction:")
            if credentials:
                for key, value in credentials.items():
                    print(f"  {key}: {value}")
            else:
                print("  No structured data extracted")
            
            # Hybrid / Vision Analysis
            print("\nVision Model Analysis:")
            with open(test_file, 'rb') as f:
                image_bytes = f.read()
            
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Determine mime type
            mime_type = "image/jpeg"
            if test_file.suffix.lower() == ".png":
                mime_type = "image/png"
            elif test_file.suffix.lower() == ".webp":
                mime_type = "image/webp"
                
            from app.services.aws_bedrock import bedrock_service
            
            vision_result = bedrock_service.analyze_image(
                image_base64=image_base64,
                prompt="""Extract the doctor's credential information from this image into the following JSON format:
                {
                  "universityName": "Name of the university or institution",
                  "doctorName": "full name of the doctor with title",
                  "degreeName": "Specific degree name (e.g. MBBS, MD)",
                  "licenseNumber": "Registration or license number",
                  "issueDate": "Date of issue in YYYY-MM-DD format if available"
                }
                Ensure precision and accuracy. If a field is not visible, use null.""",
                mime_type=mime_type
            )
            print(f"  Result: {vision_result.strip()}")
            
        except Exception as e:
            print(f"  Error: {e}")


def test_rag_patient_document():
    """Test RAG processing on patient document"""
    print("\n\n" + "="*80)
    print("TESTING RAG PROCESSING")
    print("="*80)
    
    test_file = "_documents/patients/BLR-0425-PA-0037318_SASHANK P K 0037318 2 OF 2_28-04-2025_1007-19_AM@E.pdf_page_29.png"
    
    print(f"\nFile: {test_file}")
    
    try:
        # Full pipeline test
        print("\n--- Tier 1: OCR ---")
        tier_1_text = document_processor.process_tier_1(test_file, "image/png")
        print(f"Extracted {len(tier_1_text)} characters")
        
        print("\n--- Tier 2: Vision Analysis ---")
        tier_2_data = document_processor.process_tier_2(
            file_path=test_file,
            tier_1_text=tier_1_text,
            mime_type="image/png"
        )
        
        print("\n--- Tier 3: Chunking & Embedding ---")
        chunks_data = document_processor.process_tier_3(
            text=tier_1_text,
            enriched_data=tier_2_data,
            document_id="test-doc-123",
            patient_uuid="test-patient-456"
        )
        
        print(f"\nCreated {len(chunks_data)} chunks")
        print(f"Embedding dimension: {len(chunks_data[0]['embedding']) if chunks_data else 'N/A'}")
        
        if chunks_data:
            print(f"\nFirst chunk preview:")
            print(chunks_data[0]['chunk_text'][:300])
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🔍 OCR ACCURACY TEST\n")
    
    # Test patient document
    test_patient_document()
    
    # Test doctor credential
    test_doctor_credential()
    
    # Test RAG processing
    test_rag_patient_document()
    
    print("\n\n✅ OCR Testing Complete!")
