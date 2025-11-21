"""
Medical Data Parser
Extracts structured medical information from OCR text
"""
import re
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)


class MedicalDataParser:
    """Parser for extracting structured medical data from text"""
    
    # Common medical document patterns
    PATIENT_NAME_PATTERNS = [
        r"patient\s*name[:\s]+([A-Za-z\s,]+)",
        r"name[:\s]+([A-Za-z\s,]+)",
    ]
    
    DATE_OF_BIRTH_PATTERNS = [
        r"(?:date of birth|dob|birth date)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"(?:date of birth|dob|birth date)[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
    ]
    
    MRN_PATTERNS = [
        r"(?:mrn|medical record number|medical record no\.?|record number)[:\s]+(\d+)",
        r"(?:patient id|patient no\.?)[:\s]+(\d+)",
    ]
    
    DATE_OF_SERVICE_PATTERNS = [
        r"(?:date of service|service date|visit date|date)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"(?:date of service|service date|visit date|date)[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
    ]
    
    DIAGNOSIS_PATTERNS = [
        r"(?:diagnosis|diagnoses)[:\s]+([A-Za-z0-9\s,\.\-;]+)",
        r"(?:icd-?10|icd-?9)[:\s]+([A-Z0-9\.\s,]+)",
    ]
    
    MEDICATION_PATTERNS = [
        r"(?:medication|medications|prescription|prescriptions|rx)[:\s]+([A-Za-z0-9\s,\.\-;()]+)",
    ]
    
    PROCEDURE_PATTERNS = [
        r"(?:procedure|procedures)[:\s]+([A-Za-z0-9\s,\.\-;]+)",
        r"(?:cpt|cpt code)[:\s]+(\d{5})",
    ]
    
    INSURANCE_PATTERNS = [
        r"(?:insurance|insurance company|payer)[:\s]+([A-Za-z0-9\s,\.]+)",
        r"(?:policy number|policy no\.?|member id)[:\s]+([A-Z0-9\-]+)",
    ]
    
    PHONE_PATTERNS = [
        r"(?:phone|telephone|tel|mobile|cell)[:\s]+([\d\-\(\)\s]+)",
    ]
    
    EMAIL_PATTERNS = [
        r"(?:email|e-mail)[:\s]+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
    ]
    
    ADDRESS_PATTERNS = [
        r"(?:address)[:\s]+([A-Za-z0-9\s,\.\-#]+(?:street|st|avenue|ave|road|rd|boulevard|blvd|drive|dr|lane|ln)[A-Za-z0-9\s,\.\-]*)",
    ]
    
    def __init__(self):
        """Initialize the medical data parser"""
        pass
    
    def extract_field(
        self, text: str, patterns: List[str], flags=re.IGNORECASE
    ) -> Optional[str]:
        """
        Extract a field from text using regex patterns
        
        Args:
            text: Input text
            patterns: List of regex patterns to try
            flags: Regex flags
            
        Returns:
            Extracted field value or None
        """
        for pattern in patterns:
            match = re.search(pattern, text, flags)
            if match:
                return match.group(1).strip()
        return None
    
    def extract_all_matches(
        self, text: str, patterns: List[str], flags=re.IGNORECASE
    ) -> List[str]:
        """
        Extract all matches from text using regex patterns
        
        Args:
            text: Input text
            patterns: List of regex patterns to try
            flags: Regex flags
            
        Returns:
            List of extracted values
        """
        results = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, flags)
            for match in matches:
                results.append(match.group(1).strip())
        return results
    
    def parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse date string to ISO format
        
        Args:
            date_str: Date string
            
        Returns:
            ISO formatted date string or None
        """
        try:
            parsed_date = date_parser.parse(date_str)
            return parsed_date.strftime("%Y-%m-%d")
        except Exception as e:
            logger.warning(f"Failed to parse date '{date_str}': {e}")
            return None
    
    def extract_patient_info(self, text: str) -> Dict[str, any]:
        """
        Extract patient information from text
        
        Args:
            text: OCR extracted text
            
        Returns:
            Dictionary with patient information
        """
        patient_info = {}
        
        # Extract patient name
        name = self.extract_field(text, self.PATIENT_NAME_PATTERNS)
        if name:
            patient_info['patient_name'] = name
        
        # Extract date of birth
        dob = self.extract_field(text, self.DATE_OF_BIRTH_PATTERNS)
        if dob:
            parsed_dob = self.parse_date(dob)
            if parsed_dob:
                patient_info['date_of_birth'] = parsed_dob
        
        # Extract MRN
        mrn = self.extract_field(text, self.MRN_PATTERNS)
        if mrn:
            patient_info['mrn'] = mrn
        
        # Extract phone
        phone = self.extract_field(text, self.PHONE_PATTERNS)
        if phone:
            patient_info['phone'] = phone
        
        # Extract email
        email = self.extract_field(text, self.EMAIL_PATTERNS)
        if email:
            patient_info['email'] = email
        
        # Extract address
        address = self.extract_field(text, self.ADDRESS_PATTERNS)
        if address:
            patient_info['address'] = address
        
        return patient_info
    
    def extract_clinical_info(self, text: str) -> Dict[str, any]:
        """
        Extract clinical information from text
        
        Args:
            text: OCR extracted text
            
        Returns:
            Dictionary with clinical information
        """
        clinical_info = {}
        
        # Extract date of service
        dos = self.extract_field(text, self.DATE_OF_SERVICE_PATTERNS)
        if dos:
            parsed_dos = self.parse_date(dos)
            if parsed_dos:
                clinical_info['date_of_service'] = parsed_dos
        
        # Extract diagnoses
        diagnoses = self.extract_all_matches(text, self.DIAGNOSIS_PATTERNS)
        if diagnoses:
            clinical_info['diagnoses'] = diagnoses
        
        # Extract medications
        medications = self.extract_all_matches(text, self.MEDICATION_PATTERNS)
        if medications:
            clinical_info['medications'] = medications
        
        # Extract procedures
        procedures = self.extract_all_matches(text, self.PROCEDURE_PATTERNS)
        if procedures:
            clinical_info['procedures'] = procedures
        
        return clinical_info
    
    def extract_insurance_info(self, text: str) -> Dict[str, any]:
        """
        Extract insurance information from text
        
        Args:
            text: OCR extracted text
            
        Returns:
            Dictionary with insurance information
        """
        insurance_info = {}
        
        # Extract insurance company
        insurance = self.extract_field(text, self.INSURANCE_PATTERNS)
        if insurance:
            insurance_info['insurance_company'] = insurance
        
        return insurance_info
    
    def parse(self, text: str) -> Dict[str, any]:
        """
        Parse medical document text and extract structured data
        
        Args:
            text: OCR extracted text
            
        Returns:
            Dictionary with all extracted medical data
        """
        try:
            result = {
                "patient_info": self.extract_patient_info(text),
                "clinical_info": self.extract_clinical_info(text),
                "insurance_info": self.extract_insurance_info(text),
                "raw_text": text,
                "parsed_at": datetime.utcnow().isoformat()
            }
            
            logger.info("Successfully parsed medical document")
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse medical document: {e}")
            raise
    
    def extract_phi_fields(self, text: str) -> List[str]:
        """
        Extract Protected Health Information (PHI) fields for redaction
        
        Args:
            text: Input text
            
        Returns:
            List of PHI strings found in text
        """
        phi_fields = []
        
        # Extract all PHI patterns
        phi_fields.extend(self.extract_all_matches(text, self.PATIENT_NAME_PATTERNS))
        phi_fields.extend(self.extract_all_matches(text, self.DATE_OF_BIRTH_PATTERNS))
        phi_fields.extend(self.extract_all_matches(text, self.MRN_PATTERNS))
        phi_fields.extend(self.extract_all_matches(text, self.PHONE_PATTERNS))
        phi_fields.extend(self.extract_all_matches(text, self.EMAIL_PATTERNS))
        phi_fields.extend(self.extract_all_matches(text, self.ADDRESS_PATTERNS))
        
        return phi_fields
