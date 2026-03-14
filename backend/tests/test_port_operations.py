def _create_port(client, name="Test", invested=0, profit=0):
    client.put("/cashflow/cash", params={"amount": 100000})
    resp = client.post("/ports", json={"name": name, "invested": invested, "profit": profit})
    return resp.json()


def test_update_invested(client):
    port = _create_port(client, invested=1000)
    resp = client.put(f"/ports/{port['id']}/invested", params={"amount": 2000})
    assert resp.status_code == 200
    assert resp.json()["invested"] == 2000


def test_update_invested_not_enough_cash(client):
    port = _create_port(client, invested=1000)
    resp = client.put(f"/ports/{port['id']}/invested", params={"amount": 999999})
    assert resp.status_code == 400


def test_update_invested_decrease_returns_cash(client):
    port = _create_port(client, invested=5000)
    client.put(f"/ports/{port['id']}/invested", params={"amount": 2000})
    cf = {c["type"]: c["amount"] for c in client.get("/cashflow").json()}
    assert cf["cash"] == 98000  # 100000 - 5000 + 3000


def test_update_invested_not_found(client):
    resp = client.put("/ports/9999/invested", params={"amount": 100})
    assert resp.status_code == 404


def test_update_profit(client):
    port = _create_port(client)
    resp = client.put(f"/ports/{port['id']}/profit", params={"amount": 500})
    assert resp.status_code == 200
    assert resp.json()["profit"] == 500


def test_update_profit_not_found(client):
    resp = client.put("/ports/9999/profit", params={"amount": 100})
    assert resp.status_code == 404
