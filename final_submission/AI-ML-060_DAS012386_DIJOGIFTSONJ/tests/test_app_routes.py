"""
Pytest unit tests for Flask Web Application Routes and File Generation (AI-ML-060)
"""

import io
import pytest
from pathlib import Path
import config
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_route(client):
    """Verify that home dashboard route returns HTTP 200."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Intelligent Air Quality" in response.data
    assert b"Test Accuracy" in response.data


def test_predict_get(client):
    """Verify that single predict form returns HTTP 200."""
    response = client.get("/predict")
    assert response.status_code == 200
    assert b"Single Environmental Sample Inference" in response.data


def test_predict_post_valid(client):
    """Verify POST request to /predict returns prediction and probability."""
    form_data = {
        "PT08.S1(CO)": "1360.0",
        "NMHC(GT)": "150.0",
        "C6H6(GT)": "11.9",
        "PT08.S2(NMHC)": "1046.0",
        "NOx(GT)": "166.0",
        "PT08.S3(NOx)": "1056.0",
        "NO2(GT)": "113.0",
        "PT08.S4(NO2)": "1692.0",
        "PT08.S5(O3)": "1268.0",
        "T": "13.6",
        "RH": "48.9",
        "AH": "0.7578",
        "hour": "18",
        "month": "3",
        "day_of_week": "2",
    }
    response = client.post("/predict", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Prediction Result" in response.data


def test_batch_get(client):
    """Verify that batch upload route returns HTTP 200."""
    response = client.get("/batch")
    assert response.status_code == 200
    assert b"Batch Air Quality Prediction" in response.data


def test_batch_post_sample(client):
    """Verify batch upload and CSV processing."""
    sample_csv = config.DATA_DIR / "sample_batch_test.csv"
    assert sample_csv.exists(), "Sample batch CSV must exist"
    
    with open(sample_csv, "rb") as f:
        file_bytes = io.BytesIO(f.read())
        
    data = {
        "file": (file_bytes, "test_batch.csv")
    }
    response = client.post("/batch", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert response.status_code == 200
    assert b"Batch Processing Completed" in response.data
    assert b"Download Output CSV" in response.data


def test_reports_exist():
    """Verify that reports and diagrams exist."""
    assert (config.REPORT_OUTPUT_DIR / "AI_ML_060_Project_Report.docx").exists()
    assert (config.REPORT_OUTPUT_DIR / "AI_ML_060_Project_Report.pdf").exists()
    assert (config.DOCS_DIR / "flowchart.png").exists()
    assert (config.DOCS_DIR / "architecture.png").exists()
