#!/bin/bash

# Doctor Credential OCR Test Script
# Tests the OCR endpoint with all doctor credential images

BASE_URL="http://localhost:8000"
DOCS_DIR="_documents/doctors"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================="
echo "Doctor Credential OCR Test"
echo "========================================="
echo ""

# Check if documents directory exists
if [ ! -d "$DOCS_DIR" ]; then
    echo "Error: $DOCS_DIR not found"
    exit 1
fi

# Test each image file
shopt -s nullglob
for file in "$DOCS_DIR"/*.jpg "$DOCS_DIR"/*.jpeg "$DOCS_DIR"/*.png "$DOCS_DIR"/*.webp; do
    [ -f "$file" ] || continue
    
    filename=$(basename "$file")
    echo -e "${BLUE}Testing: $filename${NC}"
    echo "---"
    
    # Call OCR endpoint
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/ocr/doctor-credentials" \
      -F "file=@$file")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" == "200" ]; then
        echo -e "${GREEN}✓ SUCCESS${NC}"
        echo "$body" | jq '.'
    else
        echo -e "${YELLOW}⚠ FAILED (HTTP $http_code)${NC}"
        echo "$body"
    fi
    
    echo ""
    echo "========================================="
    echo ""
done

echo "Test completed!"
echo ""
echo "API Endpoint: POST $BASE_URL/api/v1/ocr/doctor-credentials"
echo "Documentation: http://localhost:8000/docs#/OCR/extract_doctor_credentials_api_v1_ocr_doctor_credentials_post"
