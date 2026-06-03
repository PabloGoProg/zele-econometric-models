"""API tests for authentication and model metadata schemas."""

from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_logout_and_login_with_case_insensitive_email(client: TestClient) -> None:
    password = "StrongPassword123!"
    register = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Case User",
            "email": "Case.User@Example.com",
            "password": password,
        },
    )

    assert register.status_code == 201
    assert register.json()["email"] == "case.user@example.com"
    assert "access_token" in register.cookies

    logout = client.post("/api/v1/auth/logout")
    assert logout.status_code == 204

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "case.user@example.com", "password": password},
    )
    assert login.status_code == 200
    assert login.json()["email"] == "case.user@example.com"


def test_login_rejects_invalid_password(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "name": "Invalid Password",
            "email": "invalid@example.com",
            "password": "StrongPassword123!",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "invalid@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Credenciales inválidas"}


def test_models_list_returns_seeded_catalog(client: TestClient) -> None:
    response = client.get("/api/v1/models")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3
    assert {model["name"] for model in body} == {
        "econ_growth",
        "unemployment",
        "business_growth",
    }
    assert all(len(model["description"]) > 150 for model in body)


def test_model_schema_returns_enriched_variable_metadata(client: TestClient) -> None:
    response = client.get("/api/v1/models/1/schema")

    assert response.status_code == 200
    body = response.json()
    first_variable = body["variables"][0]
    assert body["r_squared"] >= 0
    assert {
        "name",
        "display_name",
        "description",
        "meaning",
        "value_type",
        "default_value",
        "min",
        "max",
        "step",
    }.issubset(first_variable)
    assert first_variable["display_name"]
    assert first_variable["value_type"] in {
        "log_change_rate",
        "percentage",
        "normalized_index",
    }


def test_model_variables_endpoint_returns_only_variables(client: TestClient) -> None:
    response = client.get("/api/v1/models/1/variables")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 5
    assert all("display_name" in variable for variable in body)
    assert all("value_type" in variable for variable in body)


def test_unknown_model_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/models/999/schema")

    assert response.status_code == 404
    assert response.json() == {"detail": "Modelo no encontrado"}
