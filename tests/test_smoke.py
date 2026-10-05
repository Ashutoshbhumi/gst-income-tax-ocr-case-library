import os
os.environ["DATABASE_URL"]="sqlite:///./test_taxcase.db"
from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def login():
    r=client.post("/api/auth/login",data={"username":"admin@example.com","password":"Admin@123"})
    assert r.status_code==200
    return r.json()["access_token"]

def test_health():
    assert client.get("/health").json()["status"]=="ok"

def test_login_and_dashboard():
    t=login()
    r=client.get("/api/dashboard",headers={"Authorization":f"Bearer {t}"})
    assert r.status_code==200
    assert "active_cases" in r.json()
