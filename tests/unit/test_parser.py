"""
Unit tests for medical data parser
"""
import pytest
from datetime import datetime

from src.parser.medical_parser import MedicalDataParser


class TestMedicalDataParser:
    """Test cases for medical data parser"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.parser = MedicalDataParser()
    
    def test_extract_patient_name(self):
        """Test patient name extraction"""
        text = "Patient Name: John Doe"
        result = self.parser.extract_patient_info(text)
        assert 'patient_name' in result
        assert "John Doe" in result['patient_name']
    
    def test_extract_mrn(self):
        """Test MRN extraction"""
        text = "MRN: 12345678"
        result = self.parser.extract_patient_info(text)
        assert 'mrn' in result
        assert result['mrn'] == "12345678"
    
    def test_extract_date_of_birth(self):
        """Test date of birth extraction"""
        text = "Date of Birth: 01/15/1980"
        result = self.parser.extract_patient_info(text)
        assert 'date_of_birth' in result
    
    def test_extract_phone(self):
        """Test phone number extraction"""
        text = "Phone: 555-123-4567"
        result = self.parser.extract_patient_info(text)
        assert 'phone' in result
    
    def test_extract_email(self):
        """Test email extraction"""
        text = "Email: patient@example.com"
        result = self.parser.extract_patient_info(text)
        assert 'email' in result
        assert result['email'] == "patient@example.com"
    
    def test_extract_diagnoses(self):
        """Test diagnosis extraction"""
        text = "Diagnosis: Hypertension, Type 2 Diabetes"
        result = self.parser.extract_clinical_info(text)
        assert 'diagnoses' in result
        assert len(result['diagnoses']) > 0
    
    def test_extract_medications(self):
        """Test medication extraction"""
        text = "Medications: Lisinopril 10mg, Metformin 500mg"
        result = self.parser.extract_clinical_info(text)
        assert 'medications' in result
        assert len(result['medications']) > 0
    
    def test_parse_date(self):
        """Test date parsing"""
        date_str = "01/15/2023"
        parsed = self.parser.parse_date(date_str)
        assert parsed == "2023-01-15"
    
    def test_parse_date_invalid(self):
        """Test invalid date parsing"""
        date_str = "invalid_date"
        parsed = self.parser.parse_date(date_str)
        assert parsed is None
    
    def test_parse_complete_document(self):
        """Test parsing complete document"""
        text = """
        Patient Name: Jane Smith
        MRN: 87654321
        Date of Birth: 05/20/1975
        Date of Service: 11/15/2023
        Diagnosis: Asthma
        Medications: Albuterol inhaler
        """
        result = self.parser.parse(text)
        
        assert 'patient_info' in result
        assert 'clinical_info' in result
        assert 'parsed_at' in result
        assert result['raw_text'] == text
    
    def test_extract_phi_fields(self):
        """Test PHI field extraction"""
        text = """
        Patient Name: John Doe
        MRN: 12345
        Phone: 555-1234
        """
        phi_fields = self.parser.extract_phi_fields(text)
        assert len(phi_fields) > 0
