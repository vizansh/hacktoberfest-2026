from fastapi.testclient import TestClient

from server import app


client = TestClient(app)


def test_pages_load():
    for path in ("/", "/word", "/phrases", "/time"):
        response = client.get(path)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")


def test_empty_inputs_are_rejected():
    assert client.get("/api/word", params={"word": ""}).status_code == 400
    assert client.get("/api/phrase", params={"sentence": ""}).status_code == 400
    assert client.get("/api/time", params={"text": ""}).status_code == 400


def test_time_input_limit():
    response = client.get("/api/time", params={"text": "x" * 501})
    assert response.status_code == 413
