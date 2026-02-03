"""
Doctor Credential OCR API endpoints.
Standalone OCR service for extracting doctor credentials from degree/license images.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import base64
from pathlib import Path
import json

from app.services.aws_bedrock import bedrock_service

router = APIRouter(prefix="/ocr", tags=["OCR"])


class DoctorCredentialOCR(BaseModel):
    """Doctor credential OCR response"""
    universityName: Optional[str] = None
    doctorName: Optional[str] = None
    degreeName: Optional[str] = None
    licenseNumber: Optional[str] = None
    issueDate: Optional[str] = None


@router.post("/doctor-credentials", response_model=DoctorCredentialOCR)
async def extract_doctor_credentials(
    file: UploadFile = File(...)
):
    """
    Extract doctor credentials from degree/license image using OCR.
    
    Supports: JPG, JPEG, PNG, WEBP
    
    Returns structured JSON with:
    - universityName
    - doctorName
    - degreeName
    - licenseNumber
    - issueDate
    """
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp", "application/octet-stream"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Supported: JPG, PNG, WEBP. Got: {file.content_type}"
            )
        
        # Read file
        file_content = await file.read()
        
        # Convert to base64
        image_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # Determine MIME type (with fallback to file extension)
        mime_type = file.content_type
        if mime_type == "application/octet-stream" or not mime_type:
            # Fallback to file extension
            file_ext = Path(file.filename).suffix.lower()
            mime_map = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".webp": "image/webp"
            }
            mime_type = mime_map.get(file_ext, "image/jpeg")
        elif mime_type == "image/jpg":
            mime_type = "image/jpeg"
        
        # OCR prompt for credential extraction
        ocr_prompt = """Extract the doctor's credential information from this image into the following JSON format:
{
  "universityName": "Name of the university or institution",
  "doctorName": "Full name of the doctor with title (Dr./Shri/Smt)",
  "degreeName": "Specific degree name (e.g. MBBS, MD, Bachelor of Medicine)",
  "licenseNumber": "Registration or license number (e.g. MCI, PRN)",
  "issueDate": "Date of issue in YYYY-MM-DD format if available"
}

Rules:
- Extract EXACTLY what you see on the certificate
- Use null for fields not visible
- Format dates as YYYY-MM-DD
- Include full degree names, not abbreviations
- Return ONLY the JSON object, no explanatory text"""
        
        # Call Claude Vision
        result = bedrock_service.analyze_image(
            image_base64=image_base64,
            prompt=ocr_prompt,
            mime_type=mime_type
        )
        
        # Parse JSON response
        try:
            credentials = json.loads(result)
            
            # Validate structure
            return DoctorCredentialOCR(
                universityName=credentials.get("universityName"),
                doctorName=credentials.get("doctorName"),
                degreeName=credentials.get("degreeName"),
                licenseNumber=credentials.get("licenseNumber"),
                issueDate=credentials.get("issueDate")
            )
            
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return error with raw response
            raise HTTPException(
                status_code=500,
                detail=f"OCR returned invalid JSON. Raw response: {result[:200]}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing credential image: {str(e)}"
        )
