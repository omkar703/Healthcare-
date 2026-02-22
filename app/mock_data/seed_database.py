"""
Database seeding script to populate with mock data.
Run this after starting Docker services.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import uuid

from app.database import SessionLocal, init_db
from app.models import Patient, Doctor, MedicalDocument, DocumentType, ProcessingStatus
from app.mock_data.patients import MockPatientGenerator
from app.mock_data.doctors import MockDoctorGenerator
from app.mock_data.documents import MockDocumentGenerator


def seed_database():
    """Seed database with mock data"""
    print("🌱 Seeding database with mock data...")
    
    # Initialize database
    init_db()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Generate mock patients
        print("\n📋 Generating mock patients...")
        mock_patients = MockPatientGenerator.generate_patients(15)
        patient_objects = []
        
        for mock_patient in mock_patients:
            patient = Patient(
                patient_uuid=uuid.UUID(mock_patient["patient_uuid"]),
                demographic_data=mock_patient["demographic_data"],
                onboarding_questionnaire=mock_patient["onboarding_questionnaire"]
            )
            db.add(patient)
            patient_objects.append((patient, mock_patient))
        
        db.commit()
        print(f"✅ Created {len(patient_objects)} patients")
        
        # Generate mock doctors
        print("\n👨‍⚕️ Generating mock doctors...")
        mock_doctors = MockDoctorGenerator.generate_doctors(7)
        
        for mock_doctor in mock_doctors:
            doctor = Doctor(
                doctor_uuid=uuid.UUID(mock_doctor["doctor_uuid"]),
                name=mock_doctor["name"],
                email=mock_doctor["email"],
                specialization=mock_doctor["specialization"],
                credentials=mock_doctor["credentials"],
                verification_status=mock_doctor["verification_status"]
            )
            db.add(doctor)
        
        db.commit()
        print(f"✅ Created {len(mock_doctors)} doctors")
        
        # Generate mock documents for each patient
        print("\n📄 Generating mock medical documents...")
        document_count = 0
        
        for patient_obj, mock_patient in patient_objects:
            # Generate documents
            mock_documents = MockDocumentGenerator.generate_documents_for_patient(mock_patient)
            
            for mock_doc in mock_documents:
                # Save document content to file
                patient_dir = Path(f"_documents/patients/{patient_obj.patient_uuid}")
                patient_dir.mkdir(parents=True, exist_ok=True)
                
                file_path = patient_dir / mock_doc["filename"]
                with open(file_path, "w") as f:
                    f.write(mock_doc["content"])
                
                # Create database record
                document = MedicalDocument(
                    document_id=uuid.UUID(mock_doc["document_id"]),
                    patient_uuid=patient_obj.patient_uuid,
                    file_path=str(file_path),
                    original_filename=mock_doc["filename"],
                    file_size_bytes=len(mock_doc["content"]),
                    mime_type="text/plain",
                    document_type=DocumentType(mock_doc["document_type"]),
                    processing_status=ProcessingStatus.UPLOADED
                )
                db.add(document)
                document_count += 1
        
        db.commit()
        print(f"✅ Created {document_count} medical documents")
        
        # Print summary
        print("\n" + "="*80)
        print("✨ Database seeding complete!")
        print("="*80)
        print(f"\n📊 Summary:")
        print(f"  - Patients: {len(patient_objects)}")
        print(f"  - Doctors: {len(mock_doctors)}")
        print(f"  - Documents: {document_count}")
        print(f"\n💡 You can now:")
        print(f"  1. Start the API: docker-compose up")
        print(f"  2. Access Swagger UI: http://localhost:8000/docs")
        print(f"  3. Test patient onboarding and chat endpoints")
        print()
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
