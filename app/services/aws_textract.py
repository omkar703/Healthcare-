"""
AWS Textract service for OCR text extraction.
"""

import boto3
from typing import Dict, Any, List
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class TextractService:
    """AWS Textract service for document OCR"""
    
    def __init__(self):
        """Initialize Textract client"""
        self.client = boto3.client(
            service_name='textract',
            region_name=settings.TEXTRACT_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
        logger.info("Initialized Textract client")
    
    def extract_text_from_image(self, image_bytes: bytes) -> str:
        """
        Extract text from image using Textract.
        
        Args:
            image_bytes: Image file bytes
            
        Returns:
            Extracted text as string
        """
        try:
            response = self.client.detect_document_text(
                Document={'Bytes': image_bytes}
            )
            
            # Extract text from blocks
            text_blocks = []
            for block in response.get('Blocks', []):
                if block['BlockType'] == 'LINE':
                    text_blocks.append(block.get('Text', ''))
            
            extracted_text = '\n'.join(text_blocks)
            logger.info(f"Extracted {len(extracted_text)} characters from image")
            
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            raise
    
    def extract_structured_data(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Extract structured data from document (e.g., forms, tables).
        
        Args:
            image_bytes: Image file bytes
            
        Returns:
            Dict with structured data
        """
        try:
            response = self.client.analyze_document(
                Document={'Bytes': image_bytes},
                FeatureTypes=['FORMS', 'TABLES']
            )
            
            structured_data = {
                'forms': self._extract_forms(response),
                'tables': self._extract_tables(response),
                'raw_text': self._extract_raw_text(response)
            }
            
            return structured_data
            
        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")
            raise
    
    def _extract_forms(self, response: Dict[str, Any]) -> Dict[str, str]:
        """Extract key-value pairs from forms"""
        forms = {}
        
        blocks = response.get('Blocks', [])
        key_map = {}
        value_map = {}
        block_map = {}
        
        # Build maps
        for block in blocks:
            block_id = block['Id']
            block_map[block_id] = block
            
            if block['BlockType'] == 'KEY_VALUE_SET':
                if 'KEY' in block.get('EntityTypes', []):
                    key_map[block_id] = block
                elif 'VALUE' in block.get('EntityTypes', []):
                    value_map[block_id] = block
        
        # Extract key-value pairs
        for key_id, key_block in key_map.items():
            key_text = self._get_text(key_block, block_map)
            
            # Find associated value
            if 'Relationships' in key_block:
                for relationship in key_block['Relationships']:
                    if relationship['Type'] == 'VALUE':
                        for value_id in relationship['Ids']:
                            if value_id in value_map:
                                value_text = self._get_text(value_map[value_id], block_map)
                                forms[key_text] = value_text
        
        return forms
    
    def _extract_tables(self, response: Dict[str, Any]) -> List[List[str]]:
        """Extract tables from document"""
        tables = []
        blocks = response.get('Blocks', [])
        
        # Find table blocks
        for block in blocks:
            if block['BlockType'] == 'TABLE':
                table = self._parse_table(block, blocks)
                if table:
                    tables.append(table)
        
        return tables
    
    def _parse_table(self, table_block: Dict[str, Any], all_blocks: List[Dict[str, Any]]) -> List[List[str]]:
        """Parse a table block into 2D array"""
        # Implementation simplified for now
        return []
    
    def _extract_raw_text(self, response: Dict[str, Any]) -> str:
        """Extract raw text from response"""
        text_blocks = []
        for block in response.get('Blocks', []):
            if block['BlockType'] == 'LINE':
                text_blocks.append(block.get('Text', ''))
        
        return '\n'.join(text_blocks)
    
    def _get_text(self, block: Dict[str, Any], block_map: Dict[str, Dict[str, Any]]) -> str:
        """Get text from a block"""
        text = ''
        if 'Relationships' in block:
            for relationship in block['Relationships']:
                if relationship['Type'] == 'CHILD':
                    for child_id in relationship['Ids']:
                        child = block_map.get(child_id)
                        if child and child['BlockType'] == 'WORD':
                            text += child.get('Text', '') + ' '
        
        return text.strip()
    
    def extract_doctor_credentials(self, image_bytes: bytes) -> Dict[str, str]:
        """
        Extract doctor credentials from degree/license documents.
        
        Args:
            image_bytes: Image file bytes
            
        Returns:
            Dict with extracted credentials
        """
        try:
            # Extract structured data
            structured_data = self.extract_structured_data(image_bytes)
            
            # Look for common credential fields
            forms = structured_data.get('forms', {})
            raw_text = structured_data.get('raw_text', '')
            
            credentials = {
                'universityName': '',
                'doctorName': '',
                'degreeName': '',
                'licenseNumber': '',
                'issueDate': '',
                'expiryDate': ''
            }
            
            # Try to extract from forms first
            for key, value in forms.items():
                key_lower = key.lower()
                if 'university' in key_lower or 'institution' in key_lower:
                    credentials['universityName'] = value
                elif 'name' in key_lower and 'doctor' in key_lower:
                    credentials['doctorName'] = value
                elif 'degree' in key_lower:
                    credentials['degreeName'] = value
                elif 'license' in key_lower or 'registration' in key_lower:
                    credentials['licenseNumber'] = value
                elif 'issue' in key_lower and 'date' in key_lower:
                    credentials['issueDate'] = value
                elif 'expiry' in key_lower or 'valid' in key_lower:
                    credentials['expiryDate'] = value
            
            # If forms didn't work, use raw text parsing
            if not credentials['universityName']:
                # Simple text parsing (can be enhanced with regex)
                lines = raw_text.split('\n')
                for line in lines:
                    line_lower = line.lower()
                    if 'university' in line_lower or 'institute' in line_lower:
                        credentials['universityName'] = line.strip()
                        break
            
            logger.info(f"Extracted credentials: {credentials}")
            return credentials
            
        except Exception as e:
            logger.error(f"Error extracting doctor credentials: {e}")
            raise


# Global instance
textract_service = TextractService()
