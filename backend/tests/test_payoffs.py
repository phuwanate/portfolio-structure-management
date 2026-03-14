def test_get_payoffs_empty(client):
    resp = client.get("/payoffs")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_payoff(client):
    client.put("/cashflow/profit", params={"amount": 5000})
    resp = client.post("/payoffs", json={"amount": 1000, "comment": "withdraw"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["amount"] == 1000
    assert data["comment"] == "withdraw"
    # CF Profit should be reduced
    cf = {c["type"]: c["amount"] for c in client.get("/cashflow").json()}
    assert cf["profit"] == 4000


def test_create_payoff_not_enough(client):
    resp = client.post("/payoffs", json={"amount": 99999})
    assert resp.status_code == 400


def test_create_payoff_zero(client):
    resp = client.post("/payoffs", json={"amount": 0})
    assert resp.status_code == 400


def test_delete_payoff(client):
    client.put("/cashflow/profit", params={"amount": 3000})
    client.post("/payoffs", json={"amount": 500})
    payoffs = client.get("/payoffs").json()
    resp = client.delete(f"/payoffs/{payoffs[0]['id']}")
    assert resp.status_code == 200
    assert client.get("/payoffs").json() == []


def test_delete_payoff_not_found(client):
    resp = client.delete("/payoffs/9999")
    assert resp.status_code == 404
