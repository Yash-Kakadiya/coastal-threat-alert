import pytest
from httpx import AsyncClient
from backend.app import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Health check should return message."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Coastal Threat Alert API" in response.json()["message"]


@pytest.mark.asyncio
async def test_threat_score_endpoint():
    """POST /threat/score should return a valid threat score."""
    payload = {
        "wind_speed": 10,
        "maximum_wind_speed": 15,
        "humidity": 70,
        "rain_intensity": 2,
        "barometric_pressure": 1000,
    }
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/threat/score", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "level" in data
    assert "parameters" in data


@pytest.mark.asyncio
async def test_threat_from_csv_endpoint(tmp_path):
    """GET /threat/from_csv should return threat for latest row in CSV."""
    # create a fake CSV in processed dir
    processed_dir = tmp_path / "processed"
    processed_dir.mkdir()
    fake_csv = processed_dir / "cleaned_weather.csv"
    fake_csv.write_text(
        "Wind Speed,Maximum Wind Speed,Humidity,Rain Intensity,Barometric Pressure\n"
        "5,8,60,1,1012\n"
    )

    # monkeypatch Path so app reads our fake CSV
    import backend.app as app_module

    app_module.Path = lambda _: fake_csv

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/threat/from_csv")

    assert response.status_code == 200
    data = response.json()
    assert "latest_reading" in data
    assert "threat" in data
    assert "score" in data["threat"]
