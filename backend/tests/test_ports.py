def test_get_ports_empty(client):
    resp = client.get("/ports")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_port(client):
    resp = client.post("/ports", json={"name": "Port A", "invested": 0, "profit": 0})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Port A"
    assert data["id"] is not None


def test_create_port_duplicate(client):
    client.post("/ports", json={"name": "Port A"})
    resp = client.post("/ports", json={"name": "Port A"})
    assert resp.status_code == 400


def test_create_port_deducts_cash(client):
    client.put("/cashflow/cash", params={"amount": 10000})
    client.post("/ports", json={"name": "Port B", "invested": 3000})
    cf = {c["type"]: c["amount"] for c in client.get("/cashflow").json()}
    assert cf["cash"] == 7000


def test_create_port_not_enough_cash(client):
    resp = client.post("/ports", json={"name": "Port C", "invested": 99999})
    assert resp.status_code == 400
