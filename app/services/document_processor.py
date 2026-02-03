"""
Document processing service implementing the 3-tier pipeline:
- Tier 1: OCR/Text Extraction
- Tier 2: Vision Analysis & Enrichment
- Tier 3: Chunking & Vector Indexing
"""

import base64
from pathlib import Path
from typing import Dict, Any, List
import PyPDF2
from PIL import Image
import io
import logging

from app.services.aws_bedrock import bedrock_service
from app.services.aws_textract import textract_service
from app.config import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """3-Tier document processing pipeline"""
    
    def __init__(self):
        self.bedrock = bedrock_service
        self.textract = textract_service
    
    # ==================== TIER 1: INGESTION & RAW EXTRACTION ====================
    
    def process_tier_1(self, file_path: str, mime_type: str, use_vision_fallback: bool = True) -> str:
        """
        Tier 1: Extract raw text from document using hybrid approach.
        Uses Textract first, then Vision model for verification/enhancement.
        
        Args:
            file_path: Path to document file
            mime_type: MIME type of document
            use_vision_fallback: Use vision model if Textract quality is poor
            
        Returns:
            Extracted raw text
        """
        try:
            logger.info(f"Processing Tier 1 for: {file_path}")
            
            if mime_type == "application/pdf":
                return self._extract_text_from_pdf(file_path)
            elif mime_type.startswith("image/"):
                # Use hybrid approach for images
                return self._extract_text_from_image_hybrid(file_path, use_vision_fallback)
            elif mime_type == "text/plain":
                return self._read_text_file(file_path)
            else:
                raise ValueError(f"Unsupported MIME type: {mime_type}")
                
        except Exception as e:
            logger.error(f"Error in Tier 1 processing: {e}")
            raise
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using PyPDF2"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_blocks = []
                
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_blocks.append(text)
                
                extracted_text = '\n\n'.join(text_blocks)
                logger.info(f"Extracted {len(extracted_text)} characters from PDF")
                return extracted_text
                
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def _extract_text_from_image_hybrid(self, file_path: str, use_vision_fallback: bool = True) -> str:
        """
        Extract text from image using hybrid Textract + Vision approach.
        This improves accuracy for handwritten text and complex layouts.
        """
        try:
            # First, try Textract for structured extraction
            textract_text = ""
            try:
                with open(file_path, 'rb') as file:
                    image_bytes = file.read()
                
                textract_text = self.textract.extract_text_from_image(image_bytes)
                logger.info(f"Textract extracted {len(textract_text)} characters")
            except Exception as e:
                logger.warning(f"Textract extraction failed: {e}")
            
            # If Textract result is poor or empty, use Vision model
            if use_vision_fallback and (not textract_text or len(textract_text) < 50):
                logger.info("Using Vision model for OCR enhancement")
                vision_text = self._extract_text_with_vision(file_path)
                
                if vision_text and len(vision_text) > len(textract_text):
                    logger.info(f"Vision model extracted {len(vision_text)} characters (better than Textract)")
                    return vision_text
            
            # For medical documents, always enhance with vision for better accuracy
            if textract_text and use_vision_fallback:
                logger.info("Enhancing Textract result with Vision model")
                vision_text = self._extract_text_with_vision(file_path)
                
                # Combine both for best results
                if vision_text:
                    combined_text = f"{textract_text}\n\n[Vision Model Enhanced Extraction]\n{vision_text}"
                    logger.info(f"Combined extraction: {len(combined_text)} characters")
                    return combined_text
            
            return textract_text
            
        except Exception as e:
            logger.error(f"Error in hybrid text extraction: {e}")
            raise
    
    def _extract_text_with_vision(self, file_path: str) -> str:
        """Extract text using Claude Vision model"""
        try:
            with open(file_path, 'rb') as file:
                image_bytes = file.read()
            
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Determine MIME type
            file_ext = Path(file_path).suffix.lower()
            mime_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif'
            }
            mime_type = mime_type_map.get(file_ext, 'image/jpeg')
            
            # Use Vision model for OCR
            prompt = """Extract ALL text from this medical document image. 
            Include:
            - All visible text, numbers, and values
            - Table data with proper structure
            - Handwritten notes if present
            - Medical terminology and abbreviations
            - Test results and measurements
            
            Preserve the layout and structure as much as possible.
            Return ONLY the extracted text, no additional commentary."""
            
            vision_text = self.bedrock.analyze_image(
                image_base64=image_base64,
                prompt=prompt,
                mime_type=mime_type
            )
            
            return vision_text
            
        except Exception as e:
            logger.error(f"Error extracting text with vision: {e}")
            return ""
    
    def _read_text_file(self, file_path: str) -> str:
        """Read plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error reading text file: {e}")
            raise
    
    # ==================== TIER 2: VISION ANALYSIS & ENRICHMENT ====================
    
    def process_tier_2(
        self,
        file_path: str,
        tier_1_text: str,
        mime_type: str
    ) -> Dict[str, Any]:
        """
        Tier 2: Analyze images and enrich with visual descriptions.
        
        Args:
            file_path: Path to document file
            tier_1_text: Raw text from Tier 1
            mime_type: MIME type of document
            
        Returns:
            Enriched data with visual analysis
        """
        try:
            logger.info(f"Processing Tier 2 for: {file_path}")
            
            enriched_data = {
                'visual_analysis': None,
                'risk_markers': {},
                'medical_entities': []
            }
            
            # Only perform vision analysis if enabled and file is an image
            if settings.ENABLE_VISION_ANALYSIS and mime_type.startswith("image/"):
                enriched_data['visual_analysis'] = self._analyze_medical_image(file_path)
            
            # Extract medical markers from text using Claude
            if tier_1_text:
                enriched_data['risk_markers'] = self.bedrock.extract_medical_markers(tier_1_text)
            
            logger.info(f"Tier 2 complete with {len(enriched_data)} enrichments")
            return enriched_data
            
        except Exception as e:
            logger.error(f"Error in Tier 2 processing: {e}")
            raise
    
    def _analyze_medical_image(self, file_path: str) -> str:
        """Analyze medical image using Claude Vision"""
        try:
            # Read and encode image
            with open(file_path, 'rb') as file:
                image_bytes = file.read()
            
            # Convert to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Determine MIME type
            file_ext = Path(file_path).suffix.lower()
            mime_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif'
            }
            mime_type = mime_type_map.get(file_ext, 'image/jpeg')
            
            # Analyze with Claude Vision
            prompt = """Analyze this medical image and describe:
            1. Type of medical document (lab report, X-ray, mammogram, etc.)
            2. Key findings and abnormalities
            3. Any visible risk markers or concerning features
            4. Relevant measurements or values
            
            Be specific and focus on medically relevant information."""
            
            analysis = self.bedrock.analyze_image(
                image_base64=image_base64,
                prompt=prompt,
                mime_type=mime_type
            )
            
            logger.info(f"Vision analysis complete: {len(analysis)} characters")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing medical image: {e}")
            return ""
    
    # ==================== TIER 3: CHUNKING & VECTOR INDEXING ====================
    
    def process_tier_3(
        self,
        text: str,
        enriched_data: Dict[str, Any],
        document_id: str,
        patient_uuid: str
    ) -> List[Dict[str, Any]]:
        """
        Tier 3: Chunk text and generate embeddings for RAG.
        
        Args:
            text: Combined text from Tier 1 and Tier 2
            enriched_data: Enriched data from Tier 2
            document_id: Document UUID
            patient_uuid: Patient UUID
            
        Returns:
            List of chunks with embeddings and metadata
        """
        try:
            logger.info(f"Processing Tier 3 for document: {document_id}")
            
            # Combine text with visual analysis if available
            full_text = text
            if enriched_data.get('visual_analysis'):
                full_text += f"\n\n[Visual Analysis]\n{enriched_data['visual_analysis']}"
            
            # Chunk the text
            chunks = self._chunk_text(full_text)
            
            # Generate embeddings for each chunk
            chunk_data = []
            for idx, chunk_text in enumerate(chunks):
                # Generate embedding
                embedding = self.bedrock.generate_embedding(chunk_text)
                
                # Prepare chunk_metadata
                chunk_metadata = {
                    'document_id': document_id,
                    'chunk_index': idx,
                    'total_chunks': len(chunks)
                }
                if enriched_data:
                    chunk_metadata['risk_markers'] = enriched_data.get('risk_markers', [])
                
                chunk_data.append({
                    'chunk_text': chunk_text,
                    'chunk_index': idx,
                    'embedding': embedding,
                    'chunk_metadata': chunk_metadata
                })
            
            logger.info(f"Created {len(chunk_data)} chunks with embeddings")
            return chunk_data
            
        except Exception as e:
            logger.error(f"Error in Tier 3 processing: {e}")
            raise
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Chunk text into semantic segments.
        
        Args:
            text: Full text to chunk
            
        Returns:
            List of text chunks
        """
        chunk_size = settings.CHUNK_SIZE
        chunk_overlap = settings.CHUNK_OVERLAP
        
        # Simple chunking by character count with overlap
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < text_length:
                # Look for period, newline, or other sentence endings
                for i in range(end, max(start, end - 200), -1):
                    if text[i] in '.!?\n':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - chunk_overlap
        
        return chunks
    
    # ==================== HELPER METHODS ====================
    
    def extract_doctor_credentials(self, file_path: str) -> Dict[str, str]:
        """
        Extract doctor credentials from degree/license document.
        
        Args:
            file_path: Path to credential document
            
        Returns:
            Dict with extracted credentials
        """
        try:
            with open(file_path, 'rb') as file:
                image_bytes = file.read()
            
            credentials = self.textract.extract_doctor_credentials(image_bytes)
            logger.info(f"Extracted credentials: {credentials}")
            return credentials
            
        except Exception as e:
            logger.error(f"Error extracting credentials: {e}")
            raise


# Global instance
document_processor = DocumentProcessor()
