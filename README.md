# Medical Data Extraction Project

A comprehensive medical data extraction system with OCR capabilities, data parsing, HIPAA compliance validation, and REST API for processing medical documents.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 Features

- **OCR Engine**: Extract text from medical documents using Tesseract or EasyOCR
- **Medical Data Parser**: Intelligent parsing of patient information, clinical data, and insurance details
- **HIPAA Compliance**: Built-in validation and PHI detection/redaction capabilities
- **REST API**: FastAPI-based endpoints for document processing
- **Database**: PostgreSQL with SQLAlchemy ORM for data persistence
- **Audit Logging**: Comprehensive audit trails for compliance
- **Docker Support**: Easy deployment with Docker Compose

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Development](#-development)
- [Testing](#-testing)
- [HIPAA Compliance](#-hipaa-compliance)
- [Contributing](#-contributing)
- [License](#-license)

## 🔧 Installation

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 15 or higher (optional, can use SQLite for development)
- Tesseract OCR (optional, if using Tesseract engine)
- Docker and Docker Compose (optional, for containerized deployment)

### Local Setup

1. **Clone the repository**

```bash
git clone https://github.com/Harshitpal1/Medical-data-extraction-project.git
cd Medical-data-extraction-project
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Install Tesseract (Optional)**

For Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

For macOS:
```bash
brew install tesseract
```

For Windows:
Download from: https://github.com/UB-Mannheim/tesseract/wiki

5. **Configure environment variables**

```bash
cp .env.example .env
# Edit .env with your configuration
```

6. **Initialize database**

```bash
# The database will be initialized automatically on first run
# Or manually with:
python -c "from src.database.connection import init_db; init_db()"
```

### Docker Setup

1. **Build and run with Docker Compose**

```bash
docker-compose up --build
```

This will start:
- FastAPI application on port 8000
- PostgreSQL database on port 5432
- Redis on port 6379

## 🚀 Quick Start

### Starting the API Server

**Local:**
```bash
python -m src.api.main
# or
uvicorn src.api.main:app --reload
```

**Docker:**
```bash
docker-compose up
```

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Basic Usage Example

1. **Upload a medical document**

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/medical_document.pdf"
```

2. **Check processing status**

```bash
curl "http://localhost:8000/api/v1/documents/{document_id}"
```

3. **List all documents**

```bash
curl "http://localhost:8000/api/v1/documents"
```

## 📚 API Documentation

### Endpoints

#### Health Check
- `GET /api/v1/health` - Health check
- `GET /api/v1/readiness` - Readiness check

#### Documents
- `POST /api/v1/documents/upload` - Upload and process a medical document
- `GET /api/v1/documents` - List all documents
- `GET /api/v1/documents/{id}` - Get document details
- `DELETE /api/v1/documents/{id}` - Delete a document

### Request Examples

**Upload Document:**
```python
import requests

url = "http://localhost:8000/api/v1/documents/upload"
files = {"file": open("medical_record.pdf", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

**Get Document:**
```python
import requests

url = "http://localhost:8000/api/v1/documents/1"
response = requests.get(url)
print(response.json())
```

For detailed API documentation, visit: `http://localhost:8000/docs`

## 📁 Project Structure

```
Medical-data-extraction-project/
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── pytest.ini              # Pytest configuration
├── .env.example            # Example environment variables
├── .gitignore              # Git ignore rules
│
├── src/                    # Source code
│   ├── __init__.py
│   ├── ocr/               # OCR engine
│   │   ├── __init__.py
│   │   └── engine.py      # OCR implementation
│   ├── parser/            # Medical data parser
│   │   ├── __init__.py
│   │   └── medical_parser.py
│   ├── validation/        # Data validation
│   │   ├── __init__.py
│   │   └── validator.py   # HIPAA compliance validator
│   ├── database/          # Database models
│   │   ├── __init__.py
│   │   ├── models.py      # SQLAlchemy models
│   │   └── connection.py  # Database connection
│   ├── api/               # REST API
│   │   ├── __init__.py
│   │   ├── main.py        # FastAPI application
│   │   └── routes/        # API routes
│   │       ├── health.py
│   │       └── documents.py
│   └── utils/             # Utility functions
│       ├── __init__.py
│       ├── file_utils.py
│       └── logging_utils.py
│
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── unit/             # Unit tests
│   │   ├── test_ocr.py
│   │   ├── test_parser.py
│   │   └── test_validation.py
│   └── integration/       # Integration tests
│       └── test_api.py
│
├── data/                  # Data directory
│   ├── samples/          # Sample documents
│   ├── uploads/          # Uploaded files
│   └── processed/        # Processed files
│
└── docs/                 # Documentation
    ├── API.md           # API documentation
    ├── DATABASE.md      # Database schema
    └── DEVELOPMENT.md   # Development guidelines
```

## ⚙️ Configuration

Configuration is managed through environment variables. Key settings:

### Application Settings
- `APP_NAME`: Application name
- `APP_ENV`: Environment (development/production/testing)
- `DEBUG`: Debug mode (True/False)
- `SECRET_KEY`: Secret key for encryption

### OCR Settings
- `OCR_ENGINE`: OCR engine to use (tesseract/easyocr)
- `OCR_LANGUAGES`: Comma-separated language codes
- `OCR_CONFIDENCE_THRESHOLD`: Minimum confidence threshold (0.0-1.0)

### Database Settings
- `DATABASE_URL`: Database connection URL
- `DATABASE_POOL_SIZE`: Connection pool size
- `DATABASE_MAX_OVERFLOW`: Maximum overflow connections

### HIPAA Compliance
- `ENABLE_AUDIT_LOG`: Enable audit logging (True/False)
- `ENCRYPTION_ENABLED`: Enable data encryption (True/False)
- `DATA_RETENTION_DAYS`: Data retention period (default: 2555 days / 7 years)
- `PHI_REDACTION_ENABLED`: Enable PHI redaction (True/False)

See `.env.example` for all available configuration options.

## 💻 Development

### Setting Up Development Environment

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Install pre-commit hooks (optional):
```bash
pre-commit install
```

3. Run in development mode:
```bash
uvicorn src.api.main:app --reload --log-level debug
```

### Code Quality

**Format code with Black:**
```bash
black src/ tests/
```

**Lint with Flake8:**
```bash
flake8 src/ tests/
```

**Type checking with mypy:**
```bash
mypy src/
```

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With coverage report
pytest --cov=src --cov-report=html
```

### Run Specific Test Files

```bash
pytest tests/unit/test_ocr.py
pytest tests/unit/test_parser.py
pytest tests/unit/test_validation.py
```

### Test Markers

Tests are organized with markers:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.ocr` - OCR related tests
- `@pytest.mark.api` - API tests

Run specific markers:
```bash
pytest -m unit
pytest -m "not slow"
```

## 🔒 HIPAA Compliance

This project includes features to support HIPAA compliance:

### PHI Detection and Redaction
- Automatic detection of 18 HIPAA identifiers
- PHI redaction capabilities
- Data minimization checks

### Audit Logging
- Comprehensive audit trails for all document access
- User activity tracking
- Timestamp-based audit records

### Data Security
- Encrypted data storage support
- Secure file handling
- Access control mechanisms

### Retention Policies
- Configurable data retention periods
- Automatic retention period validation
- Default 7-year retention (2555 days)

### Best Practices
1. Always enable `ENABLE_AUDIT_LOG` in production
2. Use encrypted database connections
3. Regularly review audit logs
4. Implement proper access controls
5. Use HTTPS for all API communications
6. Regularly update dependencies for security patches

**Note:** This project provides tools to support HIPAA compliance but does not guarantee compliance. Organizations must conduct proper security assessments and implement additional controls as needed.

## 📖 Additional Documentation

- [API Documentation](docs/API.md) - Detailed API reference
- [Database Schema](docs/DATABASE.md) - Database structure and relationships
- [Development Guide](docs/DEVELOPMENT.md) - Development guidelines and best practices

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure:
- Code follows PEP 8 style guidelines
- All tests pass
- New features include tests
- Documentation is updated

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- EasyOCR for OCR capabilities
- Tesseract OCR
- FastAPI framework
- SQLAlchemy ORM
- The open-source community

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Disclaimer:** This software is provided for educational and development purposes. Users are responsible for ensuring their use of this software complies with all applicable regulations including HIPAA.