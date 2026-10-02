from copy import deepcopy

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def ordered_use_case(monkeypatch):
    from app.sample_data import USE_CASE_SOURCES

    monkeypatch.setitem(
        USE_CASE_SOURCES,
        "ordered-use-case",
        [
            {"source_id": "source-z", "title": 'Café "Guide"'},
            {"source_id": "source-a", "title": "Another source"},
        ],
    )
    return USE_CASE_SOURCES


def test_health_reports_ready_without_modifying_configuration():
    from app.main import app
    from app.sample_data import USE_CASE_SOURCES

    original_configuration = deepcopy(USE_CASE_SOURCES)
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert USE_CASE_SOURCES == original_configuration


def test_configured_use_case_returns_its_sources():
    from app.main import app

    with TestClient(app) as client:
        response = client.get("/v1/use-cases/sample-use-case/sources")

    assert response.status_code == 200
    assert response.json() == {
        "use_case_id": "sample-use-case",
        "sources": [
            {"source_id": "sample-source-1", "title": "Sample source"},
        ],
    }


def test_configured_use_case_preserves_source_order_and_titles(ordered_use_case):
    from app.main import app

    with TestClient(app) as client:
        response = client.get("/v1/use-cases/ordered-use-case/sources")

    assert response.status_code == 200
    assert response.json() == {
        "use_case_id": "ordered-use-case",
        "sources": [
            {"source_id": "source-z", "title": 'Café "Guide"'},
            {"source_id": "source-a", "title": "Another source"},
        ],
    }


def test_configured_use_case_returns_json(ordered_use_case):
    from app.main import app

    with TestClient(app) as client:
        response = client.get("/v1/use-cases/ordered-use-case/sources")

    assert response.status_code == 200
    assert response.headers["content-type"].split(";")[0] == "application/json"


def test_configured_requests_do_not_modify_configuration(ordered_use_case):
    from app.main import app

    original_configuration = deepcopy(ordered_use_case)
    with TestClient(app) as client:
        first = client.get("/v1/use-cases/ordered-use-case/sources")
        second = client.get("/v1/use-cases/ordered-use-case/sources")

    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    assert ordered_use_case == original_configuration


def test_empty_use_case_returns_empty_sources_without_modifying_configuration():
    from app.main import app
    from app.sample_data import USE_CASE_SOURCES

    original_configuration = deepcopy(USE_CASE_SOURCES)
    with TestClient(app) as client:
        first = client.get("/v1/use-cases/empty-use-case/sources")
        second = client.get("/v1/use-cases/empty-use-case/sources")

    for response in (first, second):
        assert response.status_code == 200
        assert response.json() == {"use_case_id": "empty-use-case", "sources": []}
        assert response.headers["content-type"].split(";")[0] == "application/json"

    assert USE_CASE_SOURCES == original_configuration


def test_mixed_requests_preserve_configuration():
    from app.main import app
    from app.sample_data import USE_CASE_SOURCES

    original_configuration = deepcopy(USE_CASE_SOURCES)
    scenarios = [
        (
            "sample-use-case",
            200,
            {
                "use_case_id": "sample-use-case",
                "sources": [
                    {"source_id": "sample-source-1", "title": "Sample source"},
                ],
            },
        ),
        ("empty-use-case", 200, {"use_case_id": "empty-use-case", "sources": []}),
        ("missing-use-case", 404, {"detail": {"code": "unknown_use_case"}}),
    ]

    with TestClient(app) as client:
        for _ in range(2):
            for use_case_id, status_code, body in scenarios:
                response = client.get(f"/v1/use-cases/{use_case_id}/sources")
                assert response.status_code == status_code
                assert response.json() == body
                assert USE_CASE_SOURCES == original_configuration

            response = client.post("/v1/use-cases/sample-use-case/sources")
            assert response.status_code == 405
            assert USE_CASE_SOURCES == original_configuration


def test_openapi_documents_success_and_amended_unknown_use_case_error():
    from app.main import app

    with TestClient(app) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    operation = schema["paths"]["/v1/use-cases/{use_case_id}/sources"]["get"]
    schemas = schema["components"]["schemas"]
    responses = operation["responses"]

    success_ref = responses["200"]["content"]["application/json"]["schema"]["$ref"]
    success = schemas[success_ref.rsplit("/", 1)[-1]]
    assert set(success["properties"]) == {"use_case_id", "sources"}
    assert set(success["required"]) == {"use_case_id", "sources"}
    assert success["properties"]["use_case_id"]["type"] == "string"
    assert success["properties"]["sources"]["type"] == "array"
    source_ref = success["properties"]["sources"]["items"]["$ref"]
    source = schemas[source_ref.rsplit("/", 1)[-1]]
    assert set(source["properties"]) == {"source_id", "title"}
    assert set(source["required"]) == {"source_id", "title"}
    assert source["properties"]["source_id"]["type"] == "string"
    assert source["properties"]["title"]["type"] == "string"

    error_ref = responses["404"]["content"]["application/json"]["schema"]["$ref"]
    error = schemas[error_ref.rsplit("/", 1)[-1]]
    assert set(error["properties"]) == {"detail"}
    assert error["required"] == ["detail"]
    detail_ref = error["properties"]["detail"]["$ref"]
    detail = schemas[detail_ref.rsplit("/", 1)[-1]]
    assert set(detail["properties"]) == {"code"}
    assert detail["required"] == ["code"]
    assert detail["properties"]["code"]["const"] == "unknown_use_case"


@pytest.mark.parametrize(
    "requested_id",
    [
        "missing-use-case",
        "Sample-use-case",
        "%20sample-use-case",
        "sample-use-case%20",
    ],
)
def test_unknown_use_case_returns_404_with_unknown_use_case_code(requested_id):
    from app.main import app
    from app.sample_data import USE_CASE_SOURCES

    original_configuration = deepcopy(USE_CASE_SOURCES)
    with TestClient(app) as client:
        first = client.get(f"/v1/use-cases/{requested_id}/sources")
        second = client.get(f"/v1/use-cases/{requested_id}/sources")

    for response in (first, second):
        assert response.status_code == 404
        assert response.json() == {"detail": {"code": "unknown_use_case"}}
        assert response.headers["content-type"].split(";")[0] == "application/json"

    assert USE_CASE_SOURCES == original_configuration
