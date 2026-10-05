import httpx

def test_health_endpoint():
    r = httpx.get("http://localhost:8000/health", timeout=5)
    assert r.status_code == 200
