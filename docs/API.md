# API Documentation

Complete reference for the Medical Data Extraction API.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API does not require authentication. In production, implement proper authentication mechanisms (JWT, OAuth2, etc.).

## Endpoints

### Health & Status

#### Health Check

```http
GET /health
```

Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2023-11-20T10:30:00.000Z"
}
```

#### Readiness Check

```http
GET /readiness
```

Returns the readiness status of the API.

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2023-11-20T10:30:00.000Z"
}
```

---

### Documents

#### Upload Document

```http
POST /documents/upload
```

Upload a medical document for processing.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `file`: Medical document file (PDF, PNG, JPG, JPEG, TIFF)

**Supported File Types:**
- PDF (.pdf)
- Images (.png, .jpg, .jpeg, .tiff)

**File Size Limit:** 10MB

**Example Request (cURL):**
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@medical_record.pdf"
```

**Example Request (Python):**
```python
import requests

url = "http://localhost:8000/api/v1/documents/upload"
files = {"file": open("medical_record.pdf", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

**Response (200 OK):**
```json
{
  "id": 1,
  "filename": "medical_record.pdf",
  "status": "pending",
  "message": "Document uploaded successfully and processing started"
}
```

**Error Responses:**

400 Bad Request - Invalid file type:
```json
{
  "detail": "File type not allowed. Allowed types: pdf, png, jpg, jpeg, tiff"
}
```

400 Bad Request - File too large:
```json
{
  "detail": "File too large. Maximum size: 10485760 bytes"
}
```

---

#### Get Document

```http
GET /documents/{document_id}
```

Retrieve information about a processed document.

**Parameters:**
- `document_id` (path, required): Document ID

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/documents/1"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "filename": "medical_record.pdf",
  "status": "completed",
  "document_type": "clinical_note",
  "ocr_confidence": 0.95,
  "uploaded_at": "2023-11-20T10:30:00.000Z",
  "processing_completed_at": "2023-11-20T10:31:00.000Z",
  "patient": {
    "mrn": "12345678",
    "patient_name": "John Doe",
    "date_of_birth": "1980-01-15"
  },
  "clinical_records": [
    {
      "date_of_service": "2023-11-20",
      "diagnoses": ["Hypertension", "Type 2 Diabetes"],
      "medications": ["Lisinopril 10mg", "Metformin 500mg"],
      "procedures": ["Physical examination"]
    }
  ]
}
```

**Error Responses:**

404 Not Found:
```json
{
  "detail": "Document not found"
}
```

---

#### List Documents

```http
GET /documents
```

List all uploaded documents with pagination.

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 10)

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/documents?skip=0&limit=10"
```

**Response (200 OK):**
```json
{
  "total": 25,
  "documents": [
    {
      "id": 1,
      "filename": "medical_record.pdf",
      "status": "completed",
      "uploaded_at": "2023-11-20T10:30:00.000Z"
    },
    {
      "id": 2,
      "filename": "lab_report.pdf",
      "status": "processing",
      "uploaded_at": "2023-11-20T11:00:00.000Z"
    }
  ]
}
```

---

#### Delete Document

```http
DELETE /documents/{document_id}
```

Delete a document and all associated data.

**Parameters:**
- `document_id` (path, required): Document ID

**Example Request:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/documents/1"
```

**Response (200 OK):**
```json
{
  "message": "Document deleted successfully"
}
```

**Error Responses:**

404 Not Found:
```json
{
  "detail": "Document not found"
}
```

---

## Processing Status

Documents go through the following processing stages:

1. **pending**: Document uploaded, waiting for processing
2. **processing**: Document is being processed (OCR, parsing, validation)
3. **completed**: Document successfully processed
4. **failed**: Processing failed (check logs for details)

## Data Models

### Document

```json
{
  "id": "integer",
  "filename": "string",
  "file_path": "string",
  "file_size": "integer",
  "file_type": "string",
  "document_type": "string (enum)",
  "status": "string (enum)",
  "ocr_confidence": "float",
  "ocr_engine": "string",
  "uploaded_at": "datetime",
  "processing_completed_at": "datetime"
}
```

### Patient

```json
{
  "id": "integer",
  "mrn": "string",
  "patient_name": "string",
  "date_of_birth": "string (YYYY-MM-DD)",
  "phone": "string",
  "email": "string",
  "address": "string"
}
```

### Clinical Record

```json
{
  "id": "integer",
  "date_of_service": "string (YYYY-MM-DD)",
  "diagnoses": "array of strings",
  "medications": "array of strings",
  "procedures": "array of strings",
  "insurance_company": "string"
}
```

## Error Handling

The API uses standard HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a `detail` field with more information:

```json
{
  "detail": "Error message here"
}
```

## Rate Limiting

Rate limiting is configured via the `RATE_LIMIT` environment variable (default: 100 requests per hour).

When rate limit is exceeded:

**Response (429 Too Many Requests):**
```json
{
  "detail": "Rate limit exceeded"
}
```

## CORS

CORS is configured via the `CORS_ORIGINS` environment variable. By default, it allows:
- http://localhost:3000
- http://localhost:8000

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Example Workflows

### Complete Document Processing Workflow

1. Upload document:
```python
import requests
import time

# Upload
url = "http://localhost:8000/api/v1/documents/upload"
files = {"file": open("medical_record.pdf", "rb")}
response = requests.post(url, files=files)
doc_id = response.json()["id"]

# Wait for processing
while True:
    response = requests.get(f"{url}/{doc_id}")
    status = response.json()["status"]
    
    if status == "completed":
        print("Processing complete!")
        print(response.json())
        break
    elif status == "failed":
        print("Processing failed!")
        break
    
    time.sleep(2)
```

### Batch Processing

```python
import requests
from pathlib import Path

url = "http://localhost:8000/api/v1/documents/upload"
documents = Path("documents/").glob("*.pdf")

for doc_path in documents:
    files = {"file": open(doc_path, "rb")}
    response = requests.post(url, files=files)
    print(f"Uploaded {doc_path.name}: {response.json()}")
```

## Webhooks (Future Enhancement)

Webhook support for processing completion notifications is planned for future releases.

## Support

For API issues or questions, please open an issue on GitHub.
