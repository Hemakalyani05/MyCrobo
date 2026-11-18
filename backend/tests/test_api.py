import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_samples_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/samples")
        assert res.status_code == 200
        samples = res.json()
        assert len(samples) >= 3
        ids = [s["id"] for s in samples]
        assert "vulnerable-python" in ids
        assert "vulnerable-node" in ids
        assert "vulnerable-go" in ids

@pytest.mark.asyncio
async def test_scan_and_export():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Run scan
        payload = {"source_type": "sample", "target": "vulnerable-python"}
        scan_res = await client.post("/api/scan", json=payload)
        assert scan_res.status_code == 200
        report = scan_res.json()
        scan_id = report["scan_id"]

        # Fetch scan
        get_res = await client.get(f"/api/scan/{scan_id}")
        assert get_res.status_code == 200
        assert get_res.json()["scan_id"] == scan_id

        # Check history
        hist_res = await client.get("/api/history")
        assert hist_res.status_code == 200
        assert len(hist_res.json()) >= 1

        # Export markdown
        md_res = await client.get(f"/api/export/{scan_id}?format=markdown")
        assert md_res.status_code == 200
        assert "CodeSentinel AI Audit Report" in md_res.text

        # Export HTML
        html_res = await client.get(f"/api/export/{scan_id}?format=html")
        assert html_res.status_code == 200
        assert "CodeSentinel AI Audit" in html_res.text

        # Test frontend index serve
        fe_res = await client.get("/")
        assert fe_res.status_code == 200
        assert "CodeSentinel" in fe_res.text
