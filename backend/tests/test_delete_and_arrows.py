def _create_port(client, name="X"):
    client.put("/cashflow/cash", params={"amount": 100000})
    return client.post("/ports", json={"name": name}).json()


def test_delete_port(client):
    port = _create_port(client)
    resp = client.delete(f"/ports/{port['id']}")
    assert resp.status_code == 200
    assert client.get("/ports").json() == []


def test_delete_port_not_found(client):
    resp = client.delete("/ports/9999")
    assert resp.status_code == 404


def test_update_arrows(client):
    port = _create_port(client)
    resp = client.put(f"/ports/{port['id']}/arrows", json={
        "arrow_white": True, "arrow_green": False, "arrow_orange": True
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["arrow_white"] is True
    assert data["arrow_green"] is False
    assert data["arrow_orange"] is True


def test_update_arrows_not_found(client):
    resp = client.put("/ports/9999/arrows", json={
        "arrow_white": True, "arrow_green": False, "arrow_orange": False
    })
    assert resp.status_code == 404
