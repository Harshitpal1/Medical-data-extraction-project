"""
Unit tests for data validation
"""
import pytest
from datetime import datetime

from src.validation.validator import HIPAAValidator, DataValidator


class TestHIPAAValidator:
    """Test cases for HIPAA validator"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.validator = HIPAAValidator()
    
    def test_detect_phi_names(self):
        """Test PHI detection for names"""
        text = "Patient: John Smith visited the clinic."
        phi = self.validator.detect_phi(text)
        assert 'names' in phi
    
    def test_detect_phi_phone(self):
        """Test PHI detection for phone numbers"""
        text = "Contact: 555-123-4567"
        phi = self.validator.detect_phi(text)
        assert 'phone' in phi
    
    def test_detect_phi_email(self):
        """Test PHI detection for email"""
        text = "Email: patient@example.com"
        phi = self.validator.detect_phi(text)
        assert 'email' in phi
    
    def test_detect_phi_ssn(self):
        """Test PHI detection for SSN"""
        text = "SSN: 123-45-6789"
        phi = self.validator.detect_phi(text)
        assert 'ssn' in phi
    
    def test_redact_phi(self):
        """Test PHI redaction"""
        text = "Patient email: test@example.com"
        redacted = self.validator.redact_phi(text)
        assert "@" not in redacted or "X" in redacted
    
    def test_validate_schema_valid(self):
        """Test schema validation with valid data"""
        data = {
            "patient_info": {
                "patient_name": "John Doe",
                "mrn": "12345"
            },
            "clinical_info": {},
            "insurance_info": {},
            "raw_text": "test",
            "parsed_at": datetime.utcnow().isoformat()
        }
        is_valid, errors = self.validator.validate_schema(data)
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_retention_period(self):
        """Test retention period validation"""
        created_date = datetime.utcnow()
        is_valid = self.validator.validate_retention_period(created_date)
        assert is_valid
    
    def test_generate_compliance_report(self):
        """Test compliance report generation"""
        data = {
            "patient_info": {},
            "clinical_info": {},
            "insurance_info": {},
            "raw_text": "Patient: John Smith, Phone: 555-1234",
            "parsed_at": datetime.utcnow().isoformat()
        }
        report = self.validator.generate_compliance_report(data)
        
        assert 'timestamp' in report
        assert 'checks' in report
        assert 'compliant' in report


class TestDataValidator:
    """Test cases for data validator"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.validator = DataValidator()
    
    def test_validate_valid_data(self):
        """Test validation with valid data"""
        data = {
            "patient_info": {
                "patient_name": "Jane Doe"
            },
            "clinical_info": {},
            "insurance_info": {},
            "raw_text": "test",
            "parsed_at": datetime.utcnow().isoformat()
        }
        result = self.validator.validate(data)
        assert 'valid' in result
        assert 'errors' in result
        assert 'warnings' in result
    
    def test_validate_with_hipaa_checks(self):
        """Test validation with HIPAA compliance checks"""
        data = {
            "patient_info": {},
            "clinical_info": {},
            "insurance_info": {},
            "raw_text": "test",
            "parsed_at": datetime.utcnow().isoformat()
        }
        result = self.validator.validate(data, enable_hipaa_checks=True)
        assert 'hipaa_compliance' in result
