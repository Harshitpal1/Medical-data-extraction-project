"""
Integration tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import io

from src.api.main import app
from src.database.connection import init_db

# Initialize test database
init_db("sqlite:///test.db")

client = TestClient(app)


class TestHealthEndpoints:
    """Test cases for health endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_readiness_check(self):
        """Test readiness check endpoint"""
        response = client.get("/api/v1/readiness")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"


class TestRootEndpoint:
    """Test cases for root endpoint"""
    
    def test_root(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data


class TestDocumentEndpoints:
    """Test cases for document endpoints"""
    
    def test_list_documents(self):
        """Test list documents endpoint"""
        response = client.get("/api/v1/documents")
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "total" in data
    
    def test_upload_document_invalid_type(self):
        """Test upload with invalid file type"""
        file_content = b"test content"
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
        
        response = client.post("/api/v1/documents/upload", files=files)
        assert response.status_code == 400
    
    def test_get_document_not_found(self):
        """Test get non-existent document"""
        response = client.get("/api/v1/documents/99999")
        assert response.status_code == 404
