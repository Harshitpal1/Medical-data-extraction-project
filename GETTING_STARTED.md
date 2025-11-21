# Getting Started Guide

Quick start guide for the Medical Data Extraction Project.

## Prerequisites

Before you begin, ensure you have:

- Python 3.11 or higher
- pip (Python package manager)
- Git
- 4GB RAM minimum
- 10GB free disk space

## Quick Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Harshitpal1/Medical-data-extraction-project.git
cd Medical-data-extraction-project
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** Some dependencies like `easyocr` and `opencv-python` are large and may take several minutes to download.

### 4. Verify Installation

Run the verification script to ensure core modules work:

```bash
python verify_setup.py
```

You should see:
```
✓ All core modules verified successfully!
```

### 5. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings (optional for development)
nano .env  # or use your preferred editor
```

### 6. Initialize Database

The database will be automatically initialized on first run. For manual initialization:

```bash
python -c "from src.database.connection import init_db; init_db()"
```

### 7. Start the API Server

```bash
# Development mode with auto-reload
uvicorn src.api.main:app --reload

# Or using Python directly
python -m src.api.main
```

The API will be available at: `http://localhost:8000`

### 8. Access API Documentation

Open your browser and visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Using Docker (Alternative)

If you prefer Docker:

### 1. Install Docker

Download and install Docker Desktop from: https://www.docker.com/products/docker-desktop

### 2. Start Services

```bash
docker-compose up --build
```

This starts:
- FastAPI application on port 8000
- PostgreSQL database on port 5432
- Redis on port 6379

### 3. Access the Application

- API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## First API Request

### Upload a Document

Using cURL:
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data/samples/sample_medical_record.txt"
```

Using Python:
```python
import requests

url = "http://localhost:8000/api/v1/documents/upload"
files = {"file": open("data/samples/sample_medical_record.txt", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

### Check Document Status

```bash
# Replace {id} with the ID from upload response
curl "http://localhost:8000/api/v1/documents/{id}"
```

## Testing the Installation

### Run Tests

```bash
# Install test dependencies (if not already installed)
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Ensure you're in the virtual environment
which python  # Should show path to venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 2. Database Connection Errors

```bash
# For SQLite (development)
# No setup needed, database created automatically

# For PostgreSQL (production)
# Ensure PostgreSQL is running
pg_isready -h localhost -p 5432
```

#### 3. Port Already in Use

```bash
# Use a different port
uvicorn src.api.main:app --reload --port 8001
```

#### 4. OCR Dependencies

If you encounter issues with OCR libraries:

```bash
# For Tesseract (optional)
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

#### 5. Memory Issues with EasyOCR

EasyOCR downloads large model files. If you have limited disk space:

```bash
# Use Tesseract instead
# Edit .env and set:
OCR_ENGINE=tesseract
```

## Next Steps

Now that you're set up:

1. **Explore the API**: Visit `http://localhost:8000/docs` for interactive API documentation
2. **Read Documentation**: Check out the `docs/` directory for detailed guides
3. **Run Tests**: Execute `pytest` to ensure everything works
4. **Try Examples**: Process the sample medical record in `data/samples/`
5. **Develop Features**: See `docs/DEVELOPMENT.md` for development guidelines

## Configuration Options

Key environment variables to configure (in `.env`):

```bash
# OCR Engine
OCR_ENGINE=easyocr  # or 'tesseract'

# Database
DATABASE_URL=sqlite:///medical_data.db  # or PostgreSQL URL

# API
DEBUG=True
PORT=8000

# HIPAA Compliance
ENABLE_AUDIT_LOG=True
PHI_REDACTION_ENABLED=True
```

See `.env.example` for all available options.

## Learning Resources

- [API Documentation](docs/API.md) - Complete API reference
- [Database Schema](docs/DATABASE.md) - Database structure
- [Development Guide](docs/DEVELOPMENT.md) - Development best practices
- [FastAPI Docs](https://fastapi.tiangolo.com/) - FastAPI framework
- [HIPAA Compliance](https://www.hhs.gov/hipaa) - HIPAA regulations

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review documentation in the `docs/` directory
3. Search existing GitHub issues
4. Create a new issue on GitHub with:
   - Error message
   - Steps to reproduce
   - Your environment (OS, Python version)

## What's Next?

After getting started:

- **Process Documents**: Upload medical documents via the API
- **Extract Data**: Use the parser to extract structured information
- **Validate Compliance**: Check HIPAA compliance with built-in validators
- **Explore Endpoints**: Try different API endpoints
- **Customize**: Modify parsers and validators for your specific needs

## Production Deployment

For production deployment:

1. Use PostgreSQL instead of SQLite
2. Set `DEBUG=False` in environment
3. Configure proper secrets in `.env`
4. Enable HTTPS/TLS
5. Set up proper authentication
6. Configure backup strategy
7. Enable monitoring and logging
8. Review HIPAA compliance requirements

See deployment guides in production documentation (to be added).

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For questions or issues:
- GitHub Issues: https://github.com/Harshitpal1/Medical-data-extraction-project/issues
- Documentation: See `docs/` directory

---

**Ready to start building?** Begin by uploading your first medical document! 🚀
