#!/usr/bin/env python3
"""
Verification script to test core functionality without full dependencies
"""

def test_config():
    """Test configuration module"""
    try:
        from config import get_config
        config = get_config()
        print("✓ Config module loaded")
        print(f"  - App Name: {config.APP_NAME}")
        print(f"  - App Version: {config.APP_VERSION}")
        return True
    except Exception as e:
        print(f"✗ Config module failed: {e}")
        return False


def test_parser():
    """Test medical data parser"""
    try:
        from src.parser.medical_parser import MedicalDataParser
        parser = MedicalDataParser()
        
        test_text = """
        Patient Name: John Doe
        MRN: 12345678
        Date of Birth: 01/15/1980
        Diagnosis: Hypertension
        """
        
        result = parser.parse(test_text)
        print("✓ Parser module working")
        print(f"  - Extracted patient name: {result['patient_info'].get('patient_name', 'N/A')}")
        print(f"  - Extracted MRN: {result['patient_info'].get('mrn', 'N/A')}")
        return True
    except Exception as e:
        print(f"✗ Parser module failed: {e}")
        return False


def test_validator():
    """Test HIPAA validator"""
    try:
        from src.validation.validator import HIPAAValidator
        validator = HIPAAValidator()
        
        text = 'Patient: John Smith, Phone: 555-1234, Email: test@example.com'
        phi = validator.detect_phi(text)
        
        print("✓ Validator module working")
        print(f"  - PHI types detected: {list(phi.keys())}")
        return True
    except Exception as e:
        print(f"✗ Validator module failed: {e}")
        return False


def test_database_models():
    """Test database models"""
    try:
        from src.database.models import Document, Patient, ClinicalRecord
        print("✓ Database models loaded")
        print(f"  - Document table: {Document.__tablename__}")
        print(f"  - Patient table: {Patient.__tablename__}")
        print(f"  - Clinical records table: {ClinicalRecord.__tablename__}")
        return True
    except Exception as e:
        print(f"✗ Database models failed: {e}")
        return False


def test_database_connection():
    """Test database connection"""
    try:
        from src.database.connection import DatabaseManager
        db = DatabaseManager('sqlite:///test_verify.db')
        db.create_tables()
        print("✓ Database connection and table creation working")
        
        # Cleanup
        import os
        if os.path.exists('test_verify.db'):
            os.remove('test_verify.db')
        
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


def test_utils():
    """Test utility functions"""
    try:
        from src.utils.file_utils import allowed_file, get_file_extension
        
        assert allowed_file("test.pdf") == True
        assert allowed_file("test.txt") == False
        assert get_file_extension("test.pdf") == "pdf"
        
        print("✓ Utility functions working")
        return True
    except Exception as e:
        print(f"✗ Utility functions failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Medical Data Extraction Project - Verification")
    print("=" * 60)
    print()
    
    tests = [
        ("Configuration", test_config),
        ("Medical Parser", test_parser),
        ("HIPAA Validator", test_validator),
        ("Database Models", test_database_models),
        ("Database Connection", test_database_connection),
        ("Utility Functions", test_utils),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"Testing {name}...")
        result = test_func()
        results.append(result)
        print()
    
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n✓ All core modules verified successfully!")
        print("\nNote: Full API testing requires installing all dependencies:")
        print("  pip install -r requirements.txt")
    else:
        print("\n✗ Some tests failed. Please review errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
