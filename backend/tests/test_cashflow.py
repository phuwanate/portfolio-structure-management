def test_get_cashflow_initial(client):
    resp = client.get("/cashflow")
    assert resp.status_code == 200
    data = resp.json()
    types = {cf["type"] for cf in data}
    assert "cash" in types
    assert "profit" in types


def test_update_cashflow(client):
    resp = client.put("/cashflow/cash", params={"amount": 50000})
    assert resp.status_code == 200
    assert resp.json()["amount"] == 50000


def test_update_cashflow_not_found(client):
    resp = client.put("/cashflow/invalid", params={"amount": 100})
    assert resp.status_code == 404
