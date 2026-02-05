# Breast Cancer Risk Assessment API

## Overview

This API calculates a comprehensive breast health score (0-100) and categorizes risk levels based on patient screening data, symptoms, family history, and lifestyle factors.

## Endpoint

**POST** `/api/v1/breast-cancer/assess`

## Scoring Logic

### Starting Point
- **Perfect Health Score**: 100

### Risk Categories

#### HIGH RISK (Score: 0-40)
**Automatic Triggers (Critical Flags):**
- Hard or fixed breast lump → -50 points
- Bloody nipple discharge → -40 points
- Known BRCA1/2 mutation → -45 points
- Skin dimpling (peau d'orange) → -35 points
- Nipple retraction/inversion → -30 points
- Prior chest radiation before age 30 → -35 points

**Action:** ⚠️ **URGENT** - Consult a specialist immediately  
**Lab Tests:** Stage 2 + Genetic Screening

---

#### MEDIUM RISK (Score: 41-75)
**Moderate Risk Factors:**
- New breast lump (soft) → -20 points
- Dense breast tissue → -15 points
- First-degree relative with breast cancer → -18 points
- Family cancer before age 50 → -15 points
- Localized non-cyclical pain → -15 points
- Persistent pain → -12 points
- Long-term HRT use → -12 points
- Nipple sores/crusting → -12 points
- Long-term OCP use → -10 points
- Breast size/shape changes → -10 points

**Action:** ⚡ Consult a doctor for further evaluation  
**Lab Tests:** Stage 2

---

#### LOW RISK (Score: 76-100)
**Minor Risk Factors:**
- Second-degree relative with cancer → -8 points
- Obesity (BMI > 30) → -8 points
- Skin redness → -8 points
- Tobacco use → -6 points
- Alcohol use → -5 points
- Sedentary lifestyle → -5 points

**Action:** ✅ Continue regular screening and maintain healthy lifestyle  
**Lab Tests:** Stage 1

---

#### STAGE 3 (Cancer Patients)
**Trigger:** `previousCancer = true`

**Action:** 🏥 Active cancer treatment/surveillance  
**Lab Tests:** Stage 3 (Biopsy + Treatment Monitoring)

---

## Lab Test Mapping

### Stage 1 (Basic Health Panel)
**Cardiovascular/Lipid:**
- Total Cholesterol
- HDL/LDL Cholesterol
- Triglycerides

**Insulin/Diabetes:**
- Fasting Glucose
- HbA1c

**Kidney Function:**
- Serum Creatinine
- eGFR
- BUN

**Liver Function:**
- ALT, ALP
- Total Bilirubin
- Albumin

**Complete Blood Count:**
- Hemoglobin, Hematocrit
- WBC, Platelet Count
- Iron, Ferritin

**Thyroid:**
- TSH, Free T3, Free T4

**Vitamins:**
- Vitamin D, B12
- Calcium, Magnesium

---

### Stage 2 (Medium/High Risk)
**All Stage 1 Tests +**

**Genetic Testing:**
- BRCA1 Gene Mutation Test
- BRCA2 Gene Mutation Test

**Tumor Markers:**
- CA 15-3 (Cancer Antigen 15-3)
- CA 27-29 (Cancer Antigen 27-29)
- CEA (Carcinoembryonic Antigen)

**Imaging:**
- Mammogram (Diagnostic)
- Breast Ultrasound
- Breast MRI (if high genetic risk)

---

### Stage 3 (Cancer Monitoring)
**All Stage 1 Tests +**

**Biopsy/Pathology:**
- Core Needle Biopsy
- Histopathology Report
- Immunohistochemistry (ER, PR, HER2)
- Ki-67 Proliferation Index

**Advanced Tumor Markers:**
- CA 15-3, CA 27-29, CEA

**Genetic Testing:**
- BRCA1/BRCA2 Analysis
- Oncotype DX (if applicable)

**Treatment Monitoring:**
- CBC - Frequent
- Liver/Kidney Function - Monthly

**Imaging:**
- PET-CT Scan (Staging)
- Bone Scan
- Chest CT Scan
- Radiation Treatment Planning

---

## Request Schema

```json
{
  "patientId": "uuid",
  "screeningHistory": {
    "age": 45,
    "denseBreastTissue": true,
    "priorConditions": ["BENIGN_LUMP"],
    "lastScreeningDate": "2025-01-15",
    "screeningUpToDate": true
  },
  "familyGeneticRisk": {
    "knownBRCAMutation": false,
    "firstDegreeRelativeBreastCancer": true,
    "secondDegreeRelativeBreastCancer": false,
    "familyCancerBefore50": true
  },
  "currentSymptoms": {
    "newLump": true,
    "hardOrFixedLump": false,
    "localizedPain": true,
    "persistentPain": false,
    "cyclicalPainOnly": false
  },
  "skinNippleChanges": {
    "dimpling": false,
    "nippleRetraction": false,
    "dischargeType": "NONE",
    "nippleSores": false,
    "skinRedness": false
  },
  "shapeSizeChanges": {
    "sizeChange": false,
    "shapeChange": false,
    "asymmetry": false
  },
  "hormonalHistory": {
    "longTermOCPUse": true,
    "longTermHRTUse": false,
    "earlyMenarcheAge": false,
    "lateMenopause": false
  },
  "lifestyle": {
    "alcoholUse": false,
    "tobaccoUse": false,
    "sedentaryLifestyle": false,
    "obesity": false
  },
  "priorCancerRadiation": {
    "chestRadiationBefore30": false,
    "previousCancer": false
  }
}
```

## Response Schema

```json
{
  "patientId": "uuid",
  "score": 54,
  "riskLevel": "Medium",
  "recommendation": "⚡ Consult a doctor for further evaluation. Your assessment indicates moderate risk factors that warrant professional medical review and additional testing.",
  "requiredLabTests": [
    "Total Cholesterol",
    "HDL Cholesterol",
    "BRCA1 Gene Mutation Test",
    "CA 15-3 (Cancer Antigen 15-3)",
    "Mammogram (Diagnostic)",
    "..."
  ],
  "labTestStage": "Stage 2",
  "reasoning": "Breast Health Score: 54/100\n\nSCORE CALCULATION:\n  • New breast lump (soft): -20 points\n  • Localized non-cyclical pain: -15 points\n  • Dense breast tissue: -15 points\n  • First-degree relative with breast cancer: -18 points\n  • Family cancer history before age 50: -15 points\n  • Long-term OCP use: -10 points",
  "criticalFlags": []
}
```

## Example Usage

### cURL

```bash
curl -X POST "http://localhost:8000/api/v1/breast-cancer/assess" \
  -H "Content-Type: application/json" \
  -d '{
    "patientId": "550e8400-e29b-41d4-a716-446655440000",
    "screeningHistory": {
      "age": 45,
      "denseBreastTissue": true,
      "priorConditions": [],
      "screeningUpToDate": true
    },
    "familyGeneticRisk": {
      "knownBRCAMutation": false,
      "firstDegreeRelativeBreastCancer": true,
      "secondDegreeRelativeBreastCancer": false,
      "familyCancerBefore50": false
    },
    "currentSymptoms": {
      "newLump": false,
      "hardOrFixedLump": false,
      "localizedPain": false,
      "persistentPain": false,
      "cyclicalPainOnly": true
    },
    "skinNippleChanges": {
      "dimpling": false,
      "nippleRetraction": false,
      "dischargeType": "NONE",
      "nippleSores": false,
      "skinRedness": false
    },
    "shapeSizeChanges": {
      "sizeChange": false,
      "shapeChange": false,
      "asymmetry": false
    },
    "hormonalHistory": {
      "longTermOCPUse": false,
      "longTermHRTUse": false,
      "earlyMenarcheAge": false,
      "lateMenopause": false
    },
    "lifestyle": {
      "alcoholUse": false,
      "tobaccoUse": false,
      "sedentaryLifestyle": false,
      "obesity": false
    },
    "priorCancerRadiation": {
      "chestRadiationBefore30": false,
      "previousCancer": false
    }
  }'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/breast-cancer/assess",
    json={
        "patientId": "550e8400-e29b-41d4-a716-446655440000",
        "screeningHistory": {
            "age": 45,
            "denseBreastTissue": True,
            # ... rest of data
        }
    }
)

result = response.json()
print(f"Score: {result['score']}")
print(f"Risk Level: {result['riskLevel']}")
print(f"Recommendation: {result['recommendation']}")
```

## Error Responses

### 500 Internal Server Error
```json
{
  "detail": "Error calculating breast cancer assessment: <error message>"
}
```

## Retrieve Latest Assessment

**GET** `/api/v1/breast-cancer/assess/{patient_uuid}`

Retrieves the most recent assessment for a patient.

### Response
Same as POST response schema.

### Error Responses

#### 404 Not Found
```json
{
  "detail": "Patient not found"
}
```

```json
{
  "detail": "No breast cancer assessment found for this patient. Please submit an assessment first."
}
```

## Notes

1. **Automatic Storage**: All assessments are automatically stored in the patient's record for historical tracking.

2. **Critical Flags**: If any critical flag is detected, the patient is automatically categorized as HIGH risk regardless of score.

3. **Stage 3 Override**: If `previousCancer = true`, the patient is immediately assigned Stage 3 monitoring.

4. **Score Bounds**: Final score is clamped between 0-100.

5. **Interactive Documentation**: Visit `/docs` for interactive Swagger UI to test the API.

## Production Considerations

- Implement rate limiting for API calls
- Add authentication/authorization
- Enable audit logging for all assessments
- Encrypt sensitive patient data
- Set up monitoring alerts for HIGH risk assessments
- Integrate with electronic health records (EHR)
