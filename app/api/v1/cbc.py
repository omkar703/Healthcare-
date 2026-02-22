"""
CBC parameter extraction API endpoint.
Extracts CBC parameters from medical diagnostic report images or PDFs using AI.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, List
import base64
from pathlib import Path
import json
import io

from app.services.aws_bedrock import bedrock_service

router = APIRouter(prefix="/cbc", tags=["CBC"])

class ParameterData(BaseModel):
    value: float | str
    unit: str
    reference_range: Optional[str] = None
    flag: Optional[str] = None

class CBCExtractionResponse(BaseModel):
    success: bool
    data: Dict[str, ParameterData]

@router.post("/extract", response_model=CBCExtractionResponse)
async def extract_cbc(
    file: UploadFile = File(...)
):
    """
    Extract structured CBC parameters from report image/PDF.
    
    Supports: JPG, JPEG, PNG, WEBP, PDF
    """
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp", "application/pdf", "application/octet-stream"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Supported: JPG, PNG, WEBP, PDF. Got: {file.content_type}"
            )
        
        # Read file
        file_content = await file.read()
        
        # Determine MIME type (with fallback to file extension)
        mime_type = file.content_type
        if mime_type == "application/octet-stream" or not mime_type:
            # Fallback to file extension
            file_ext = Path(file.filename).suffix.lower()
            mime_map = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".webp": "image/webp",
                ".pdf": "application/pdf"
            }
            mime_type = mime_map.get(file_ext, "image/jpeg")
        elif mime_type == "image/jpg":
            mime_type = "image/jpeg"
            
        images_base64 = []
        
        # Convert PDF to images if needed
        if mime_type == "application/pdf":
            try:
                import pypdfium2 as pdfium
                from PIL import Image
                
                pdf = pdfium.PdfDocument(file_content)
                for i in range(len(pdf)):
                    page = pdf[i]
                    bitmap = page.render(scale=2.0)
                    img = bitmap.to_pil()
                    
                    # Convert to base64
                    buffered = io.BytesIO()
                    img.save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    images_base64.append((img_str, "image/jpeg"))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")
        else:
            images_base64.append((base64.b64encode(file_content).decode('utf-8'), mime_type))
            
        all_extracted_data = {}
        
        # Process each page/image
        for img_b64, m_type in images_base64:
            ocr_prompt = """Extract ONLY the following Complete Blood Count (CBC) parameters from this medical report.
Normalize parameter names to those listed below regardless of how they are written in the report (e.g., if you see "Hb" or "HGB", map it to "Hemoglobin", "TLC" to "WBC Count", "PCV" or "HCT" to "Hematocrit / PCV"). 
Do not hallucinate values. If a parameter is not present, omit it from the response.

Strict Parameter Names to Extract:
- Hemoglobin
- RBC Count
- Hematocrit / PCV
- MCV
- MCH
- MCHC
- RDW
- WBC Count
- Neutrophils (%)
- Lymphocytes (%)
- Monocytes (%)
- Eosinophils (%)
- Basophils (%)
- Absolute Neutrophil Count
- Absolute Lymphocyte Count
- Absolute Monocyte Count
- Absolute Eosinophil Count
- Absolute Basophil Count
- Platelet Count
- MPV
- PDW
- PCT

Return the extraction as a structured JSON object where keys are the explicit parameter names above, and the value is an object containing:
- value: The numeric or text value.
- unit: The unit of measurement (if present, else "").
- reference_range: The reference normal range (if present).
- flag: High, Low, etc. (if explicitly marked or obviously out of range).

Return ONLY the JSON object, absolutely no explanatory text.
Example Format:
{
  "Hemoglobin": {
    "value": 12.0,
    "unit": "g/dL",
    "reference_range": "13.0 - 17.0",
    "flag": "Low"
  }
}"""
            
            # Call Claude Vision
            result = bedrock_service.analyze_image(
                image_base64=img_b64,
                prompt=ocr_prompt,
                mime_type=m_type
            )
            
            try:
                page_data = json.loads(result)
                if isinstance(page_data, dict):
                    all_extracted_data.update(page_data)
            except json.JSONDecodeError:
                # Could log but we just skip if malformed JSON to try next page
                pass
                
        if not all_extracted_data:
            raise HTTPException(
                status_code=500,
                detail="AI extraction failed or no CBC parameters were found in the uploaded document."
            )
            
        return CBCExtractionResponse(
            success=True,
            data=all_extracted_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting CBC data: {str(e)}"
        )
