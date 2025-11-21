"""
Data Validation Module with HIPAA Compliance
"""
import re
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
from pydantic import BaseModel, Field, validator, EmailStr
from enum import Enum

logger = logging.getLogger(__name__)


class DocumentType(str, Enum):
    """Medical document types"""
    PRESCRIPTION = "prescription"
    LAB_REPORT = "lab_report"
    DISCHARGE_SUMMARY = "discharge_summary"
    CLINICAL_NOTE = "clinical_note"
    INSURANCE_FORM = "insurance_form"
    IMAGING_REPORT = "imaging_report"
    OTHER = "other"


class PatientInfoSchema(BaseModel):
    """Schema for patient information"""
    patient_name: Optional[str] = Field(None, min_length=2, max_length=100)
    date_of_birth: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    mrn: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=500)
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format"""
        if v:
            # Remove non-digit characters
            digits = re.sub(r'\D', '', v)
            if len(digits) < 10 or len(digits) > 15:
                logger.warning(f"Invalid phone number: {v}")
        return v


class ClinicalInfoSchema(BaseModel):
    """Schema for clinical information"""
    date_of_service: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$')
    diagnoses: Optional[List[str]] = []
    medications: Optional[List[str]] = []
    procedures: Optional[List[str]] = []


class InsuranceInfoSchema(BaseModel):
    """Schema for insurance information"""
    insurance_company: Optional[str] = Field(None, max_length=200)


class MedicalDocumentSchema(BaseModel):
    """Complete medical document schema"""
    patient_info: PatientInfoSchema
    clinical_info: ClinicalInfoSchema
    insurance_info: InsuranceInfoSchema
    raw_text: str
    parsed_at: str
    document_type: Optional[DocumentType] = DocumentType.OTHER


class HIPAAValidator:
    """HIPAA compliance validator"""
    
    # HIPAA 18 identifiers
    PHI_PATTERNS = {
        'names': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'fax': r'(?:fax|FAX)[:\s]+\d{3}[-.]?\d{3}[-.]?\d{4}',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'mrn': r'\b(?:MRN|mrn)[:\s]+\d+\b',
        'account_number': r'\b(?:account|acct)[:\s#]+\d+\b',
        'license_number': r'\b(?:license|lic)[:\s#]+[A-Z0-9]+\b',
        'vehicle_id': r'\b(?:VIN|vin)[:\s]+[A-Z0-9]{17}\b',
        'device_id': r'\b(?:device|serial)[:\s#]+[A-Z0-9]+\b',
        'url': r'https?://[^\s]+',
        'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        'biometric': r'(?:fingerprint|biometric|retina)',
        'photo': r'(?:photo|photograph|image|picture)\s+(?:id|identifier)',
    }
    
    def __init__(self):
        """Initialize HIPAA validator"""
        pass
    
    def validate_schema(self, data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate data against medical document schema
        
        Args:
            data: Parsed medical data
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        try:
            # Validate using Pydantic schema
            MedicalDocumentSchema(**data)
            return True, []
        except Exception as e:
            errors.append(str(e))
            logger.error(f"Schema validation failed: {e}")
            return False, errors
    
    def detect_phi(self, text: str) -> Dict[str, List[str]]:
        """
        Detect Protected Health Information in text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary mapping PHI types to detected instances
        """
        phi_detected = {}
        
        for phi_type, pattern in self.PHI_PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                phi_detected[phi_type] = matches
        
        return phi_detected
    
    def redact_phi(self, text: str, redaction_char: str = "X") -> str:
        """
        Redact PHI from text
        
        Args:
            text: Input text
            redaction_char: Character to use for redaction
            
        Returns:
            Redacted text
        """
        redacted_text = text
        
        for phi_type, pattern in self.PHI_PATTERNS.items():
            redacted_text = re.sub(
                pattern,
                lambda m: redaction_char * len(m.group()),
                redacted_text
            )
        
        return redacted_text
    
    def check_data_minimization(self, data: Dict) -> Dict[str, any]:
        """
        Check if data follows HIPAA data minimization principle
        
        Args:
            data: Medical data
            
        Returns:
            Dictionary with minimization recommendations
        """
        recommendations = {
            "compliant": True,
            "warnings": []
        }
        
        # Check for excessive PHI
        if data.get('raw_text'):
            phi_detected = self.detect_phi(data['raw_text'])
            if len(phi_detected) > 10:
                recommendations['compliant'] = False
                recommendations['warnings'].append(
                    "Document contains excessive PHI. Consider data minimization."
                )
        
        return recommendations
    
    def validate_retention_period(
        self, created_date: datetime, retention_days: int = 2555
    ) -> bool:
        """
        Validate if document is within retention period
        
        Args:
            created_date: Document creation date
            retention_days: Maximum retention period (default 7 years)
            
        Returns:
            True if within retention period
        """
        days_elapsed = (datetime.utcnow() - created_date).days
        return days_elapsed <= retention_days
    
    def generate_compliance_report(self, data: Dict) -> Dict[str, any]:
        """
        Generate HIPAA compliance report
        
        Args:
            data: Medical data
            
        Returns:
            Compliance report
        """
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "checks": []
        }
        
        # Schema validation
        is_valid, errors = self.validate_schema(data)
        report['checks'].append({
            "check": "Schema Validation",
            "passed": is_valid,
            "errors": errors
        })
        
        # PHI detection
        if data.get('raw_text'):
            phi_detected = self.detect_phi(data['raw_text'])
            report['checks'].append({
                "check": "PHI Detection",
                "passed": True,
                "phi_types_found": list(phi_detected.keys()),
                "phi_count": sum(len(v) for v in phi_detected.values())
            })
        
        # Data minimization
        minimization = self.check_data_minimization(data)
        report['checks'].append({
            "check": "Data Minimization",
            "passed": minimization['compliant'],
            "warnings": minimization['warnings']
        })
        
        # Overall compliance
        report['compliant'] = all(
            check.get('passed', False) for check in report['checks']
        )
        
        return report


class DataValidator:
    """Main data validator with HIPAA compliance"""
    
    def __init__(self):
        """Initialize data validator"""
        self.hipaa_validator = HIPAAValidator()
    
    def validate(
        self, data: Dict, enable_hipaa_checks: bool = True
    ) -> Dict[str, any]:
        """
        Validate medical data
        
        Args:
            data: Parsed medical data
            enable_hipaa_checks: Enable HIPAA compliance checks
            
        Returns:
            Validation result
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Schema validation
        is_valid, errors = self.hipaa_validator.validate_schema(data)
        if not is_valid:
            result['valid'] = False
            result['errors'].extend(errors)
        
        # HIPAA compliance checks
        if enable_hipaa_checks:
            compliance_report = self.hipaa_validator.generate_compliance_report(data)
            result['hipaa_compliance'] = compliance_report
            
            if not compliance_report['compliant']:
                result['warnings'].append(
                    "Document has HIPAA compliance issues"
                )
        
        return result
