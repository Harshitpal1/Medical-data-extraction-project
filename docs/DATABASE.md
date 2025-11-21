# Database Schema Documentation

This document describes the database schema for the Medical Data Extraction project.

## Overview

The database uses PostgreSQL (or SQLite for development) with SQLAlchemy ORM. The schema is designed to support medical document processing with HIPAA compliance in mind.

## Entity Relationship Diagram

```
┌─────────────┐
│  Document   │
├─────────────┤
│ id (PK)     │
│ filename    │
│ file_path   │
│ status      │
│ ...         │
└──────┬──────┘
       │
       │ 1:1
       │
┌──────▼──────┐
│   Patient   │
├─────────────┤
│ id (PK)     │
│ document_id │
│ mrn         │
│ ...         │
└──────┬──────┘
       │
       │ 1:N
       │
┌──────▼──────────┐
│ ClinicalRecord  │
├─────────────────┤
│ id (PK)         │
│ document_id     │
│ patient_id      │
│ ...             │
└─────────────────┘

┌─────────────┐
│  AuditLog   │
├─────────────┤
│ id (PK)     │
│ document_id │
│ action      │
│ ...         │
└─────────────┘

┌──────────────────┐
│ ValidationResult │
├──────────────────┤
│ id (PK)          │
│ document_id      │
│ is_valid         │
│ ...              │
└──────────────────┘
```

## Tables

### documents

Stores uploaded medical documents and processing metadata.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique document identifier |
| filename | VARCHAR(255) | NOT NULL | Original filename |
| file_path | VARCHAR(500) | NOT NULL | Path to stored file |
| file_size | INTEGER | | File size in bytes |
| file_type | VARCHAR(50) | | MIME type of file |
| document_type | ENUM | | Type of medical document |
| status | ENUM | DEFAULT 'pending' | Processing status |
| processing_started_at | DATETIME | | When processing started |
| processing_completed_at | DATETIME | | When processing completed |
| ocr_confidence | FLOAT | | Average OCR confidence score |
| ocr_engine | VARCHAR(50) | | OCR engine used |
| raw_text | TEXT | | Extracted text from OCR |
| uploaded_by | VARCHAR(100) | | User who uploaded |
| uploaded_at | DATETIME | DEFAULT NOW | Upload timestamp |
| updated_at | DATETIME | DEFAULT NOW | Last update timestamp |

**Enums:**

document_type:
- prescription
- lab_report
- discharge_summary
- clinical_note
- insurance_form
- imaging_report
- other

status:
- pending
- processing
- completed
- failed

**Indexes:**
- PRIMARY KEY on id
- INDEX on status
- INDEX on uploaded_at

---

### patients

Stores patient information extracted from documents.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique patient record identifier |
| document_id | INTEGER | FOREIGN KEY, UNIQUE | Reference to document |
| mrn | VARCHAR(50) | UNIQUE, INDEX | Medical Record Number |
| patient_name | VARCHAR(100) | | Patient full name |
| date_of_birth | VARCHAR(10) | | DOB in YYYY-MM-DD format |
| phone | VARCHAR(20) | | Contact phone number |
| email | VARCHAR(100) | | Email address |
| address | TEXT | | Full address |
| created_at | DATETIME | DEFAULT NOW | Record creation timestamp |
| updated_at | DATETIME | DEFAULT NOW | Last update timestamp |

**Relationships:**
- One-to-one with documents
- One-to-many with clinical_records

**Indexes:**
- PRIMARY KEY on id
- UNIQUE INDEX on document_id
- UNIQUE INDEX on mrn

---

### clinical_records

Stores clinical information extracted from documents.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique clinical record identifier |
| document_id | INTEGER | FOREIGN KEY | Reference to document |
| patient_id | INTEGER | FOREIGN KEY | Reference to patient |
| date_of_service | VARCHAR(10) | | Service date in YYYY-MM-DD |
| diagnoses | JSON | | Array of diagnoses |
| medications | JSON | | Array of medications |
| procedures | JSON | | Array of procedures |
| insurance_company | VARCHAR(200) | | Insurance company name |
| notes | TEXT | | Additional notes |
| created_at | DATETIME | DEFAULT NOW | Record creation timestamp |
| updated_at | DATETIME | DEFAULT NOW | Last update timestamp |

**Relationships:**
- Many-to-one with documents
- Many-to-one with patients

**Indexes:**
- PRIMARY KEY on id
- INDEX on document_id
- INDEX on patient_id

**JSON Fields:**

diagnoses example:
```json
["Hypertension (I10)", "Type 2 Diabetes Mellitus (E11.9)"]
```

medications example:
```json
["Lisinopril 10mg daily", "Metformin 500mg twice daily"]
```

procedures example:
```json
["Complete physical examination", "Blood pressure check"]
```

---

### audit_logs

Stores audit trail for HIPAA compliance.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique audit log identifier |
| document_id | INTEGER | FOREIGN KEY | Reference to document |
| action | VARCHAR(100) | NOT NULL | Action performed |
| user | VARCHAR(100) | | User who performed action |
| ip_address | VARCHAR(45) | | IP address of user |
| user_agent | VARCHAR(500) | | Browser/client user agent |
| details | JSON | | Additional action details |
| phi_accessed | BOOLEAN | DEFAULT FALSE | Whether PHI was accessed |
| timestamp | DATETIME | DEFAULT NOW, INDEX | Action timestamp |

**Relationships:**
- Many-to-one with documents

**Actions:**
- CREATE: Document uploaded
- READ: Document viewed/retrieved
- UPDATE: Document updated
- DELETE: Document deleted

**Indexes:**
- PRIMARY KEY on id
- INDEX on document_id
- INDEX on timestamp

---

### validation_results

Stores validation and HIPAA compliance check results.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique validation result identifier |
| document_id | INTEGER | FOREIGN KEY | Reference to document |
| is_valid | BOOLEAN | DEFAULT FALSE | Overall validation status |
| errors | JSON | | Array of validation errors |
| warnings | JSON | | Array of warnings |
| hipaa_compliant | BOOLEAN | DEFAULT FALSE | HIPAA compliance status |
| phi_detected | JSON | | PHI types detected |
| compliance_report | JSON | | Full compliance report |
| validated_at | DATETIME | DEFAULT NOW | Validation timestamp |

**Indexes:**
- PRIMARY KEY on id
- INDEX on document_id

---

## Database Migrations

The project uses Alembic for database migrations (though migrations are not yet implemented in the codebase).

### Initial Setup

```bash
# Initialize database
python -c "from src.database.connection import init_db; init_db()"
```

### Creating Tables

Tables are automatically created using SQLAlchemy's `create_all()` method:

```python
from src.database.models import Base
from sqlalchemy import create_engine

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
```

## Data Retention

According to HIPAA requirements, medical records should be retained for at least 6 years. The default configuration retains data for 7 years (2555 days).

Data retention is enforced through:
1. Validation checks on document age
2. Scheduled cleanup jobs (to be implemented)
3. Audit logging of all deletions

## Security Considerations

### PHI Protection

- All tables containing PHI should be encrypted at rest
- Database connections should use SSL/TLS
- Access should be restricted via role-based access control
- Regular database backups with encryption

### Sensitive Fields

The following fields contain PHI and require special protection:

**patients table:**
- patient_name
- date_of_birth
- phone
- email
- address
- mrn

**clinical_records table:**
- diagnoses
- medications
- procedures
- notes

**documents table:**
- raw_text

### Audit Requirements

All access to PHI must be logged in the audit_logs table with:
- User identification
- Timestamp
- Action performed
- IP address
- Whether PHI was accessed

## Indexes and Performance

### Recommended Indexes

```sql
-- Documents
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_uploaded_at ON documents(uploaded_at);

-- Patients
CREATE UNIQUE INDEX idx_patients_mrn ON patients(mrn);

-- Audit Logs
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_document_id ON audit_logs(document_id);
```

### Query Optimization

For large datasets, consider:

1. Partitioning audit_logs by timestamp
2. Archiving old documents
3. Implementing full-text search for raw_text
4. Caching frequently accessed patient records

## Backup and Recovery

### Backup Strategy

1. **Full Backups**: Daily at 2:00 AM
2. **Incremental Backups**: Every 6 hours
3. **Transaction Logs**: Continuous
4. **Retention**: 30 days for incremental, 1 year for monthly

### Recovery Procedures

```bash
# PostgreSQL backup
pg_dump -h localhost -U meduser medical_data_db > backup.sql

# PostgreSQL restore
psql -h localhost -U meduser medical_data_db < backup.sql
```

## Schema Version

Current schema version: 1.0.0

## Future Enhancements

Planned schema improvements:

1. Add versioning for patient records
2. Implement soft deletes for compliance
3. Add provider/physician table
4. Add facility/location table
5. Implement document versioning
6. Add user authentication tables
7. Add role-based access control tables

## Support

For database-related issues or questions, please open an issue on GitHub.
