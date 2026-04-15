"""Tests for the Food Calories Calculator API."""

from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ─── Helpers ────────────────────────────────────────────────────
def _dummy_image() -> BytesIO:
    """Create a minimal valid JPEG image for testing."""
    # 1x1 white JPEG
    from PIL import Image

    buf = BytesIO()
    img = Image.new("RGB", (1, 1), color="white")
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf


# ─── Health ─────────────────────────────────────────────────────
def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


# ─── Single Photo – Local Model ────────────────────────────────
def test_recognize_local_model():
    """The local model should always return a demo result."""
    img = _dummy_image()
    response = client.post(
        "/api/food/recognize",
        files={"image": ("test.jpg", img, "image/jpeg")},
        data={"model": "local"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "foods" in data
    assert len(data["foods"]) > 0
    assert data["total_calories"] > 0
    assert data["model_used"] == "local-demo"


# ─── Comparison – Local Model ──────────────────────────────────
def test_compare_local_model():
    """The local model comparison should return before/after/consumed."""
    before = _dummy_image()
    after = _dummy_image()
    response = client.post(
        "/api/food/compare",
        files={
            "before_image": ("before.jpg", before, "image/jpeg"),
            "after_image": ("after.jpg", after, "image/jpeg"),
        },
        data={"model": "local"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "before_foods" in data
    assert "after_foods" in data
    assert "consumed_foods" in data
    assert data["total_consumed_calories"] > 0
    assert data["model_used"] == "local-demo"


# ─── Validation ─────────────────────────────────────────────────
def test_recognize_unknown_model():
    """Requesting an unknown model should return 400."""
    img = _dummy_image()
    response = client.post(
        "/api/food/recognize",
        files={"image": ("test.jpg", img, "image/jpeg")},
        data={"model": "nonexistent"},
    )
    assert response.status_code == 400


def test_recognize_openrouter_without_key():
    """OpenRouter without an API key should return 400."""
    img = _dummy_image()
    response = client.post(
        "/api/food/recognize",
        files={"image": ("test.jpg", img, "image/jpeg")},
        data={"model": "openrouter"},
    )
    # Should fail because no API key is set in the test environment
    assert response.status_code == 400
    data = response.json()
    assert "API key" in data["detail"]


def test_compare_openrouter_without_key():
    """OpenRouter comparison without an API key should return 400."""
    before = _dummy_image()
    after = _dummy_image()
    response = client.post(
        "/api/food/compare",
        files={
            "before_image": ("before.jpg", before, "image/jpeg"),
            "after_image": ("after.jpg", after, "image/jpeg"),
        },
        data={"model": "openrouter"},
    )
    assert response.status_code == 400
    data = response.json()
    assert "API key" in data["detail"]


# ─── Frontend ───────────────────────────────────────────────────
def test_frontend_served():
    """The root path should serve the frontend HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "食物热量计算器" in response.text
