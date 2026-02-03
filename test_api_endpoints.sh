#!/bin/bash

# Healthcare AI Microservice - API Test Script
# This script tests all the main endpoints with valid data

BASE_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "Healthcare AI Microservice - API Tests"
echo "========================================="
echo ""

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/health")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Health check successful"
    echo "$body" | jq .
else
    echo -e "${RED}✗ FAIL${NC} - Health check failed (HTTP $http_code)"
fi
echo ""

# Test 2: Get Health Score (requires existing patient UUID)
echo -e "${YELLOW}Test 2: Get Health Score${NC}"
PATIENT_UUID="550e8400-e29b-41d4-a716-446655440000"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/v1/patients/$PATIENT_UUID/health-score")
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Health score retrieved"
    echo "$response" | sed '$d' | jq .
elif [ "$http_code" == "404" ]; then
    echo -e "${YELLOW}⚠ SKIP${NC} - Patient not found (expected if no test data)"
else
    echo -e "${RED}✗ FAIL${NC} - Unexpected error (HTTP $http_code)"
fi
echo ""

# Test 3: Get Risk Assessment
echo -e "${YELLOW}Test 3: Get Risk Assessment${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/v1/patients/$PATIENT_UUID/risk-assessment")
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Risk assessment retrieved"
    echo "$response" | sed '$d' | jq .
elif [ "$http_code" == "404" ]; then
    echo -e "${YELLOW}⚠ SKIP${NC} - Patient not found (expected if no test data)"
else
    echo -e "${RED}✗ FAIL${NC} - Unexpected error (HTTP $http_code)"
fi
echo ""

# Test 4: Patient Chat
echo -e "${YELLOW}Test 4: Patient Chat${NC}"
chat_payload='{
  "message": "What are my latest test results?",
  "conversation_id": null
}'

response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/patients/$PATIENT_UUID/chat" \
  -H "Content-Type: application/json" \
  -d "$chat_payload")
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Chat response received"
    echo "$response" | sed '$d' | jq .
elif [ "$http_code" == "404" ]; then
    echo -e "${YELLOW}⚠ SKIP${NC} - Patient not found (expected if no test data)"
else
    echo -e "${RED}✗ FAIL${NC} - Chat failed (HTTP $http_code)"
    echo "$response" | sed '$d'
fi
echo ""

# Test 5: Doctor Chat
echo -e "${YELLOW}Test 5: Doctor Chat${NC}"
DOCTOR_UUID="660f9511-f30c-52e5-b827-557766551111"
doctor_chat_payload='{
  "patient_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Summarize this patient'\''s health status",
  "conversation_id": null,
  "additional_context": "Patient reports fatigue"
}'

response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/doctors/$DOCTOR_UUID/chat" \
  -H "Content-Type: application/json" \
  -d "$doctor_chat_payload")
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Doctor chat response received"
    echo "$response" | sed '$d' | jq .
elif [ "$http_code" == "404" ]; then
    echo -e "${YELLOW}⚠ SKIP${NC} - Doctor or patient not found (expected if no test data)"
else
    echo -e "${RED}✗ FAIL${NC} - Doctor chat failed (HTTP $http_code)"
    echo "$response" | sed '$d'
fi
echo ""

# Test 6: Get Doctor's Patients
echo -e "${YELLOW}Test 6: Get Doctor's Patients${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/v1/doctors/$DOCTOR_UUID/patients")
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Patient list retrieved"
    echo "$response" | sed '$d' | jq .
elif [ "$http_code" == "404" ]; then
    echo -e "${YELLOW}⚠ SKIP${NC} - Doctor not found (expected if no test data)"
else
    echo -e "${RED}✗ FAIL${NC} - Failed to get patients (HTTP $http_code)"
fi
echo ""

# Test 7: RAG Refresh
echo -e "${YELLOW}Test 7: RAG Index Refresh${NC}"
rag_payload='{
  "patient_uuid": "550e8400-e29b-41d4-a716-446655440000"
}'

response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/rag/refresh" \
  -H "Content-Type: application/json" \
  -d "$rag_payload")
http_code=$(echo "$response" | tail -n1)

if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - RAG refresh initiated"
    echo "$response" | sed '$d' | jq .
elif [ "$http_code" == "404" ]; then
    echo -e "${YELLOW}⚠ SKIP${NC} - Patient not found (expected if no test data)"
else
    echo -e "${RED}✗ FAIL${NC} - RAG refresh failed (HTTP $http_code)"
fi
echo ""

# Test 8: Document Upload (requires test file)
echo -e "${YELLOW}Test 8: Document Upload${NC}"
if [ -f "_documents/doctors/MBBS-DEGREE-rotated.jpg" ]; then
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/patients/$PATIENT_UUID/documents/upload" \
      -F "file=@_documents/doctors/MBBS-DEGREE-rotated.jpg")
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" == "201" ]; then
        echo -e "${GREEN}✓ PASS${NC} - Document uploaded successfully"
        echo "$response" | sed '$d' | jq .
        
        # Extract document_id for status check
        DOCUMENT_ID=$(echo "$response" | sed '$d' | jq -r '.document_id')
        
        # Test 9: Check Document Status
        echo ""
        echo -e "${YELLOW}Test 9: Check Document Processing Status${NC}"
        sleep 2  # Wait a bit for processing to start
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/v1/patients/documents/$DOCUMENT_ID/status")
        http_code=$(echo "$response" | tail -n1)
        
        if [ "$http_code" == "200" ]; then
            echo -e "${GREEN}✓ PASS${NC} - Document status retrieved"
            echo "$response" | sed '$d' | jq .
        else
            echo -e "${RED}✗ FAIL${NC} - Status check failed (HTTP $http_code)"
        fi
    elif [ "$http_code" == "404" ]; then
        echo -e "${YELLOW}⚠ SKIP${NC} - Patient not found (expected if no test data)"
    else
        echo -e "${RED}✗ FAIL${NC} - Upload failed (HTTP $http_code)"
        echo "$response" | sed '$d'
    fi
else
    echo -e "${YELLOW}⚠ SKIP${NC} - Test file not found"
fi
echo ""

echo "========================================="
echo "Test Summary"
echo "========================================="
echo "Note: Some tests may be skipped if test data (patients/doctors) is not seeded in the database."
echo "To seed test data, run: docker compose exec api python app/mock_data/seed_database.py"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo "========================================="
