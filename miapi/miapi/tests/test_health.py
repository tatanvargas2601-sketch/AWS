from app import create_app


def test_health():
    # init_db=False: la prueba no necesita MySQL
    client = create_app(init_db=False).test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
