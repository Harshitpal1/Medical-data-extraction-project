"""
Database Models for Medical Data Extraction
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, Boolean, 
    ForeignKey, JSON, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class DocumentType(str, enum.Enum):
    """Document type enumeration"""
    PRESCRIPTION = "prescription"
    LAB_REPORT = "lab_report"
    DISCHARGE_SUMMARY = "discharge_summary"
    CLINICAL_NOTE = "clinical_note"
    INSURANCE_FORM = "insurance_form"
    IMAGING_REPORT = "imaging_report"
    OTHER = "other"


class ProcessingStatus(str, enum.Enum):
    """Processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base):
    """Document table for uploaded files"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(50))
    document_type = Column(SQLEnum(DocumentType), default=DocumentType.OTHER)
    
    # Processing info
    status = Column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    
    # OCR info
    ocr_confidence = Column(Float)
    ocr_engine = Column(String(50))
    raw_text = Column(Text)
    
    # Audit
    uploaded_by = Column(String(100))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="documents", uselist=False)
    clinical_records = relationship("ClinicalRecord", back_populates="document")
    audit_logs = relationship("AuditLog", back_populates="document")


class Patient(Base):
    """Patient information table"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), unique=True)
    
    # Patient identifiers
    mrn = Column(String(50), unique=True, index=True)
    patient_name = Column(String(100))
    date_of_birth = Column(String(10))
    
    # Contact info
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="patient")
    clinical_records = relationship("ClinicalRecord", back_populates="patient")


class ClinicalRecord(Base):
    """Clinical information table"""
    __tablename__ = "clinical_records"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))
    
    # Clinical data
    date_of_service = Column(String(10))
    diagnoses = Column(JSON)  # List of diagnoses
    medications = Column(JSON)  # List of medications
    procedures = Column(JSON)  # List of procedures
    
    # Insurance
    insurance_company = Column(String(200))
    
    # Additional data
    notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="clinical_records")
    patient = relationship("Patient", back_populates="clinical_records")


class AuditLog(Base):
    """Audit log table for HIPAA compliance"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    
    # Audit info
    action = Column(String(100), nullable=False)  # CREATE, READ, UPDATE, DELETE
    user = Column(String(100))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Details
    details = Column(JSON)
    phi_accessed = Column(Boolean, default=False)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    document = relationship("Document", back_populates="audit_logs")


class ValidationResult(Base):
    """Validation results table"""
    __tablename__ = "validation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    
    # Validation info
    is_valid = Column(Boolean, default=False)
    errors = Column(JSON)
    warnings = Column(JSON)
    
    # HIPAA compliance
    hipaa_compliant = Column(Boolean, default=False)
    phi_detected = Column(JSON)
    compliance_report = Column(JSON)
    
    # Metadata
    validated_at = Column(DateTime, default=datetime.utcnow)
