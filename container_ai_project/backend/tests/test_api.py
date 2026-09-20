"""
Basic tests for the Flask API.
Run with: pytest backend/tests/
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["LLM_BACKEND"] = "template"


@pytest.fixture
def client():
    from app import create_app
    from services.db_manager import init_db
    init_db()
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_containers_empty(client):
    r = client.get("/containers")
    assert r.status_code == 200
    assert "containers" in r.get_json()


def test_stats_empty(client):
    r = client.get("/stats")
    j = r.get_json()
    assert r.status_code == 200
    assert "total" in j
