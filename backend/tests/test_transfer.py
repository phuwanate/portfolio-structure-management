def _setup_port_with_profit(client, profit=1000):
    client.put("/cashflow/cash", params={"amount": 100000})
    port = client.post("/ports", json={"name": "T", "invested": 0, "profit": profit}).json()
    return port


def test_transfer_profit(client):
    port = _setup_port_with_profit(client, profit=1000)
    resp = client.post(f"/ports/{port['id']}/transfer-to-profit", params={"amount": 400})
    assert resp.status_code == 200
    assert resp.json()["port_profit"] == 600
    assert resp.json()["cashflow_profit"] == 400


def test_transfer_more_than_available(client):
    port = _setup_port_with_profit(client, profit=100)
    resp = client.post(f"/ports/{port['id']}/transfer-to-profit", params={"amount": 500})
    assert resp.status_code == 400


def test_transfer_zero(client):
    port = _setup_port_with_profit(client)
    resp = client.post(f"/ports/{port['id']}/transfer-to-profit", params={"amount": 0})
    assert resp.status_code == 400


def test_transfer_not_found(client):
    resp = client.post("/ports/9999/transfer-to-profit", params={"amount": 100})
    assert resp.status_code == 404
