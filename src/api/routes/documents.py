"""
Document processing endpoints
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from src.database.connection import get_db
from src.database.models import Document, Patient, ClinicalRecord, AuditLog, ProcessingStatus
from src.ocr.engine import OCREngine
from src.parser.medical_parser import MedicalDataParser
from src.validation.validator import DataValidator
from src.utils.file_utils import allowed_file, save_uploaded_file, validate_file_size
from config import get_config

logger = logging.getLogger(__name__)
config = get_config()

router = APIRouter()


def process_document_task(document_id: int, file_path: str):
    """
    Background task to process document
    
    Args:
        document_id: Document ID
        file_path: Path to uploaded file
    """
    from src.database.connection import db_manager
    
    try:
        with db_manager.session_scope() as db:
            # Get document
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                logger.error(f"Document {document_id} not found")
                return
            
            # Update status
            document.status = ProcessingStatus.PROCESSING
            document.processing_started_at = datetime.utcnow()
            db.commit()
            
            # Initialize OCR engine
            ocr_engine = OCREngine()
            
            # Extract text
            logger.info(f"Extracting text from {file_path}")
            ocr_result = ocr_engine.extract_from_file(file_path)
            
            # Update document with OCR results
            document.raw_text = ocr_result['text']
            document.ocr_confidence = ocr_result['confidence']
            document.ocr_engine = ocr_result['engine']
            db.commit()
            
            # Parse medical data
            logger.info(f"Parsing medical data for document {document_id}")
            parser = MedicalDataParser()
            parsed_data = parser.parse(ocr_result['text'])
            
            # Validate data
            logger.info(f"Validating data for document {document_id}")
            validator = DataValidator()
            validation_result = validator.validate(parsed_data)
            
            # Save patient info
            patient_info = parsed_data.get('patient_info', {})
            if patient_info:
                patient = Patient(
                    document_id=document_id,
                    mrn=patient_info.get('mrn'),
                    patient_name=patient_info.get('patient_name'),
                    date_of_birth=patient_info.get('date_of_birth'),
                    phone=patient_info.get('phone'),
                    email=patient_info.get('email'),
                    address=patient_info.get('address')
                )
                db.add(patient)
                db.commit()
                
                # Save clinical info
                clinical_info = parsed_data.get('clinical_info', {})
                if clinical_info:
                    clinical_record = ClinicalRecord(
                        document_id=document_id,
                        patient_id=patient.id,
                        date_of_service=clinical_info.get('date_of_service'),
                        diagnoses=clinical_info.get('diagnoses', []),
                        medications=clinical_info.get('medications', []),
                        procedures=clinical_info.get('procedures', []),
                        insurance_company=parsed_data.get('insurance_info', {}).get('insurance_company')
                    )
                    db.add(clinical_record)
            
            # Update document status
            document.status = ProcessingStatus.COMPLETED
            document.processing_completed_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Successfully processed document {document_id}")
            
    except Exception as e:
        logger.error(f"Failed to process document {document_id}: {e}")
        with db_manager.session_scope() as db:
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.status = ProcessingStatus.FAILED
                db.commit()


@router.post("/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process medical document
    
    Args:
        file: Uploaded file
        db: Database session
        
    Returns:
        Document information
    """
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(config.ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if not validate_file_size(len(content)):
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {config.MAX_FILE_SIZE} bytes"
        )
    
    try:
        # Save file
        file_path = save_uploaded_file(content, file.filename)
        
        # Create document record
        document = Document(
            filename=file.filename,
            file_path=str(file_path),
            file_size=len(content),
            file_type=file.content_type,
            status=ProcessingStatus.PENDING,
            uploaded_at=datetime.utcnow()
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Create audit log
        audit_log = AuditLog(
            document_id=document.id,
            action="CREATE",
            details={"filename": file.filename, "file_size": len(content)}
        )
        db.add(audit_log)
        db.commit()
        
        # Process document in background
        background_tasks.add_task(process_document_task, document.id, str(file_path))
        
        logger.info(f"Document uploaded: {file.filename} (ID: {document.id})")
        
        return {
            "id": document.id,
            "filename": document.filename,
            "status": document.status.value,
            "message": "Document uploaded successfully and processing started"
        }
        
    except Exception as e:
        logger.error(f"Failed to upload document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}")
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get document information
    
    Args:
        document_id: Document ID
        db: Database session
        
    Returns:
        Document information
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Create audit log
    audit_log = AuditLog(
        document_id=document.id,
        action="READ",
        phi_accessed=True
    )
    db.add(audit_log)
    db.commit()
    
    # Get related data
    patient = db.query(Patient).filter(Patient.document_id == document_id).first()
    clinical_records = db.query(ClinicalRecord).filter(
        ClinicalRecord.document_id == document_id
    ).all()
    
    return {
        "id": document.id,
        "filename": document.filename,
        "status": document.status.value,
        "document_type": document.document_type.value if document.document_type else None,
        "ocr_confidence": document.ocr_confidence,
        "uploaded_at": document.uploaded_at.isoformat() if document.uploaded_at else None,
        "processing_completed_at": document.processing_completed_at.isoformat() if document.processing_completed_at else None,
        "patient": {
            "mrn": patient.mrn if patient else None,
            "patient_name": patient.patient_name if patient else None,
            "date_of_birth": patient.date_of_birth if patient else None
        } if patient else None,
        "clinical_records": [
            {
                "date_of_service": record.date_of_service,
                "diagnoses": record.diagnoses,
                "medications": record.medications,
                "procedures": record.procedures
            }
            for record in clinical_records
        ]
    }


@router.get("/documents")
async def list_documents(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    List all documents
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of documents
    """
    documents = db.query(Document).offset(skip).limit(limit).all()
    
    return {
        "total": db.query(Document).count(),
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "status": doc.status.value,
                "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None
            }
            for doc in documents
        ]
    }


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete document
    
    Args:
        document_id: Document ID
        db: Database session
        
    Returns:
        Deletion confirmation
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Create audit log
    audit_log = AuditLog(
        document_id=document.id,
        action="DELETE",
        phi_accessed=True
    )
    db.add(audit_log)
    
    # Delete document
    db.delete(document)
    db.commit()
    
    logger.info(f"Document deleted: {document_id}")
    
    return {"message": "Document deleted successfully"}
