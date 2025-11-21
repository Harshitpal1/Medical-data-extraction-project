# Development Guidelines

Guidelines and best practices for developing the Medical Data Extraction project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Git Workflow](#git-workflow)
- [Documentation](#documentation)
- [Security](#security)
- [Performance](#performance)

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ or SQLite for local development
- Git
- Docker & Docker Compose (optional)

### Setting Up Development Environment

1. **Clone and setup:**

```bash
git clone https://github.com/Harshitpal1/Medical-data-extraction-project.git
cd Medical-data-extraction-project
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment:**

```bash
cp .env.example .env
# Edit .env with your local settings
```

3. **Initialize database:**

```bash
python -c "from src.database.connection import init_db; init_db()"
```

4. **Run the application:**

```bash
uvicorn src.api.main:app --reload
```

## Development Workflow

### 1. Feature Development

1. Create a new branch from `main`
2. Implement feature with tests
3. Run tests and linting
4. Submit pull request
5. Code review
6. Merge to main

### 2. Running the Application

**Development mode with auto-reload:**
```bash
uvicorn src.api.main:app --reload --log-level debug
```

**Production mode:**
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

**With Docker:**
```bash
docker-compose up --build
```

### 3. Database Migrations

Currently, schema changes are made directly to models.py. Future: Alembic migrations.

```python
# Reset database (development only)
from src.database.connection import db_manager
db_manager.drop_tables()
db_manager.create_tables()
```

## Code Style

### Python Style Guide

Follow PEP 8 and use these tools:

**Black (formatting):**
```bash
black src/ tests/
```

**Flake8 (linting):**
```bash
flake8 src/ tests/ --max-line-length=100
```

**isort (import sorting):**
```bash
isort src/ tests/
```

**mypy (type checking):**
```bash
mypy src/
```

### Code Conventions

1. **Imports:**
```python
# Standard library
import os
from typing import List, Dict

# Third-party
import numpy as np
from fastapi import FastAPI

# Local
from config import get_config
from src.utils import helpers
```

2. **Type Hints:**
```python
def process_document(doc_id: int, options: Dict[str, Any]) -> Dict[str, Any]:
    """Always use type hints for function parameters and returns."""
    pass
```

3. **Docstrings:**
```python
def extract_patient_info(text: str) -> Dict[str, Any]:
    """
    Extract patient information from medical text.
    
    Args:
        text: Raw text extracted from document
        
    Returns:
        Dictionary containing patient information fields
        
    Raises:
        ValueError: If text is empty or invalid
    """
    pass
```

4. **Constants:**
```python
# Use uppercase for constants
MAX_FILE_SIZE = 10485760  # 10MB
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
```

5. **Error Handling:**
```python
try:
    result = process_document(doc_id)
except DocumentNotFoundError as e:
    logger.error(f"Document not found: {e}")
    raise
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    raise
```

## Testing

### Writing Tests

1. **Test Structure:**
```python
import pytest
from src.module import function

class TestFeature:
    """Test cases for feature."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.test_data = {}
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        result = function(self.test_data)
        assert result is not None
    
    def test_edge_case(self):
        """Test edge case."""
        with pytest.raises(ValueError):
            function(None)
```

2. **Test Markers:**
```python
@pytest.mark.unit
def test_unit():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass
```

3. **Running Tests:**
```bash
# All tests
pytest

# Specific category
pytest -m unit
pytest -m integration

# With coverage
pytest --cov=src --cov-report=html

# Specific file
pytest tests/unit/test_parser.py
```

### Test Coverage

Maintain minimum 80% code coverage:

```bash
pytest --cov=src --cov-report=term-missing
```

## Git Workflow

### Branch Naming

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### Commit Messages

Follow conventional commits:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```
feat(ocr): add support for TIFF images

fix(parser): correct date parsing for international formats

docs(api): update endpoint documentation
```

### Pull Requests

1. Update from main before submitting
2. Include tests for new features
3. Update documentation
4. Add description of changes
5. Reference related issues

**PR Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests passing

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
```

## Documentation

### Code Documentation

1. **Module docstrings:**
```python
"""
Module for OCR text extraction.

This module provides OCR capabilities using both Tesseract and EasyOCR
engines for extracting text from medical documents.
"""
```

2. **Class docstrings:**
```python
class OCREngine:
    """
    OCR Engine for medical document processing.
    
    Supports multiple OCR backends and provides preprocessing
    capabilities for improved accuracy.
    
    Attributes:
        engine: OCR engine name ('tesseract' or 'easyocr')
        languages: List of language codes
    """
```

3. **Function docstrings:**
```python
def extract_from_pdf(self, pdf_path: str) -> List[Dict]:
    """
    Extract text from PDF file.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        List of dictionaries with extracted text per page
        
    Raises:
        ValueError: If file doesn't exist
        PDFError: If PDF is corrupted
    """
```

### API Documentation

Update OpenAPI documentation in route docstrings:

```python
@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a medical document for processing.
    
    - **file**: Medical document (PDF, PNG, JPG, JPEG, TIFF)
    
    Returns document ID and processing status.
    """
```

## Security

### HIPAA Compliance

1. **PHI Handling:**
   - Never log PHI data
   - Always use audit logging
   - Implement data minimization
   - Use encryption for storage and transmission

2. **Example:**
```python
# BAD - logs PHI
logger.info(f"Processing patient: {patient_name}")

# GOOD - logs non-PHI
logger.info(f"Processing document ID: {doc_id}")
audit_log.create(action="READ", document_id=doc_id, phi_accessed=True)
```

### Input Validation

Always validate user inputs:

```python
from pydantic import BaseModel, validator

class DocumentUpload(BaseModel):
    filename: str
    
    @validator('filename')
    def validate_filename(cls, v):
        if not allowed_file(v):
            raise ValueError("Invalid file type")
        return v
```

### Secrets Management

Never commit secrets:

```python
# Use environment variables
SECRET_KEY = os.getenv("SECRET_KEY")

# NOT hardcoded values
SECRET_KEY = "hardcoded-secret"  # NEVER DO THIS
```

## Performance

### Optimization Guidelines

1. **Database Queries:**
```python
# BAD - N+1 queries
for doc in documents:
    patient = db.query(Patient).filter_by(document_id=doc.id).first()

# GOOD - Single query with join
documents = db.query(Document).join(Patient).all()
```

2. **Caching:**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_config_value(key: str) -> str:
    return config.get(key)
```

3. **Async Operations:**
```python
# Use background tasks for long operations
@router.post("/documents/upload")
async def upload_document(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_document, doc_id)
```

### Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile
process_document(doc_id)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Pylance
- Python Test Explorer
- GitLens
- Docker

**.vscode/settings.json:**
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "editor.formatOnSave": true
}
```

### PyCharm

1. Enable PEP 8 checks
2. Configure Black as formatter
3. Set up pytest as test runner
4. Enable type checking

## Troubleshooting

### Common Issues

1. **Import errors:**
```bash
# Ensure src is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

2. **Database connection:**
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Reset database
python -c "from src.database.connection import init_db; init_db()"
```

3. **OCR issues:**
```bash
# Verify Tesseract installation
tesseract --version

# Test EasyOCR
python -c "import easyocr; print('EasyOCR OK')"
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pytest Documentation](https://docs.pytest.org/)

## Support

For development questions or issues:
1. Check existing issues on GitHub
2. Review documentation
3. Ask in discussions
4. Create new issue if needed
