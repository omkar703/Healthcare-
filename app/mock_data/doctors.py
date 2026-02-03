"""
Mock doctor data generator with realistic credentials.
"""

import uuid
from datetime import datetime, timedelta
import random


class MockDoctorGenerator:
    """Generate realistic mock doctor data"""
    
    FIRST_NAMES = ["James", "Michael", "Robert", "David", "William", "Priya", "Anjali", "Rajesh", "Amit", "Sanjay"]
    LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Singh", "Patel", "Kumar", "Sharma", "Gupta", "Chen"]
    
    SPECIALIZATIONS = [
        "Oncology",
        "General Practice",
        "Radiology",
        "Surgical Oncology",
        "Breast Surgery",
        "Pathology",
        "Internal Medicine"
    ]
    
    UNIVERSITIES = [
        "All India Institute of Medical Sciences (AIIMS)",
        "Johns Hopkins University",
        "Harvard Medical School",
        "Stanford University School of Medicine",
        "University of California, San Francisco",
        "Mayo Clinic Alix School of Medicine",
        "University of Pennsylvania",
        "Columbia University",
        "Duke University School of Medicine",
        "University of Michigan Medical School"
    ]
    
    DEGREES = [
        "Doctor of Medicine (MD)",
        "Bachelor of Medicine and Bachelor of Surgery (MBBS)",
        "Doctor of Osteopathic Medicine (DO)"
    ]
    
    @staticmethod
    def generate_verified_doctor():
        """Generate a verified doctor profile"""
        first_name = random.choice(MockDoctorGenerator.FIRST_NAMES)
        last_name = random.choice(MockDoctorGenerator.LAST_NAMES)
        specialization = random.choice(MockDoctorGenerator.SPECIALIZATIONS)
        university = random.choice(MockDoctorGenerator.UNIVERSITIES)
        degree = random.choice(MockDoctorGenerator.DEGREES)
        
        # Generate realistic license number
        license_prefix = "MCI" if "AIIMS" in university or "MBBS" in degree else "MD"
        license_number = f"{license_prefix}-{random.randint(2010, 2020)}-{random.randint(1000, 9999)}"
        
        # Issue date (5-15 years ago)
        years_ago = random.randint(5, 15)
        issue_date = datetime.now() - timedelta(days=years_ago * 365)
        
        return {
            "doctor_uuid": str(uuid.uuid4()),
            "name": f"Dr. {first_name} {last_name}",
            "email": f"{first_name.lower()}.{last_name.lower()}@hospital.com",
            "specialization": specialization,
            "credentials": {
                "universityName": university,
                "doctorName": f"Dr. {first_name} {last_name}",
                "degreeName": degree,
                "licenseNumber": license_number,
                "issueDate": issue_date.strftime("%Y-%m-%d"),
                "expiryDate": (issue_date + timedelta(days=3650)).strftime("%Y-%m-%d"),  # 10 years validity
                "verification_status": "VERIFIED"
            },
            "verification_status": "VERIFIED",
            "created_at": datetime.now().isoformat()
        }
    
    @staticmethod
    def generate_pending_doctor():
        """Generate a pending verification doctor profile"""
        first_name = random.choice(MockDoctorGenerator.FIRST_NAMES)
        last_name = random.choice(MockDoctorGenerator.LAST_NAMES)
        specialization = random.choice(MockDoctorGenerator.SPECIALIZATIONS)
        university = random.choice(MockDoctorGenerator.UNIVERSITIES)
        degree = random.choice(MockDoctorGenerator.DEGREES)
        
        license_prefix = "MCI" if "AIIMS" in university or "MBBS" in degree else "MD"
        license_number = f"{license_prefix}-{random.randint(2015, 2023)}-{random.randint(1000, 9999)}"
        
        years_ago = random.randint(1, 5)
        issue_date = datetime.now() - timedelta(days=years_ago * 365)
        
        return {
            "doctor_uuid": str(uuid.uuid4()),
            "name": f"Dr. {first_name} {last_name}",
            "email": f"{first_name.lower()}.{last_name.lower()}@hospital.com",
            "specialization": specialization,
            "credentials": {
                "universityName": university,
                "doctorName": f"Dr. {first_name} {last_name}",
                "degreeName": degree,
                "licenseNumber": license_number,
                "issueDate": issue_date.strftime("%Y-%m-%d"),
                "expiryDate": (issue_date + timedelta(days=3650)).strftime("%Y-%m-%d"),
                "verification_status": "PENDING_MANUAL_REVIEW"
            },
            "verification_status": "PENDING",
            "created_at": datetime.now().isoformat()
        }
    
    @staticmethod
    def generate_doctors(count=7):
        """Generate a mix of verified and pending doctors"""
        doctors = []
        
        # 80% verified, 20% pending
        verified_count = int(count * 0.8)
        pending_count = count - verified_count
        
        for _ in range(verified_count):
            doctors.append(MockDoctorGenerator.generate_verified_doctor())
        
        for _ in range(pending_count):
            doctors.append(MockDoctorGenerator.generate_pending_doctor())
        
        return doctors


if __name__ == "__main__":
    # Test generation
    doctors = MockDoctorGenerator.generate_doctors(7)
    print(f"Generated {len(doctors)} mock doctors")
    for i, doctor in enumerate(doctors, 1):
        print(f"\nDoctor {i}:")
        print(f"  Name: {doctor['name']}")
        print(f"  Specialization: {doctor['specialization']}")
        print(f"  University: {doctor['credentials']['universityName']}")
        print(f"  License: {doctor['credentials']['licenseNumber']}")
        print(f"  Status: {doctor['verification_status']}")
