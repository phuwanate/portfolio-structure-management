def _create_port(client, name="TestPort", invested=1000, profit=500):
    client.put("/cashflow/cash", params={"amount": 100000})
    return client.post("/ports", json={"name": name, "invested": invested, "profit": profit}).json()


def test_get_snapshots_empty(client):
    resp = client.get("/asset-snapshots")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_snapshot(client):
    port = _create_port(client)
    resp = client.post("/asset-snapshots", json={"port_id": port["id"], "comment": "initial"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["port_id"] == port["id"]
    assert data["port_name"] == "TestPort"
    assert data["invested"] == 1000
    assert data["profit"] == 500
    assert data["total"] == 1500
    assert data["comment"] == "initial"
    assert "date" in data


def test_create_snapshot_port_not_found(client):
    resp = client.post("/asset-snapshots", json={"port_id": 9999})
    assert resp.status_code == 404


def test_create_snapshot_default_comment(client):
    port = _create_port(client)
    resp = client.post("/asset-snapshots", json={"port_id": port["id"]})
    assert resp.status_code == 200
    assert resp.json()["comment"] == ""


def test_delete_snapshot(client):
    port = _create_port(client)
    client.post("/asset-snapshots", json={"port_id": port["id"]})
    snapshots = client.get("/asset-snapshots").json()
    resp = client.delete(f"/asset-snapshots/{snapshots[0]['id']}")
    assert resp.status_code == 200
    assert client.get("/asset-snapshots").json() == []


def test_delete_snapshot_not_found(client):
    resp = client.delete("/asset-snapshots/9999")
    assert resp.status_code == 404


def test_snapshots_multiple_ports(client):
    p1 = _create_port(client, name="PortA", invested=2000, profit=100)
    p2 = _create_port(client, name="PortB", invested=3000, profit=200)
    client.post("/asset-snapshots", json={"port_id": p1["id"], "comment": "a"})
    client.post("/asset-snapshots", json={"port_id": p2["id"], "comment": "b"})
    snapshots = client.get("/asset-snapshots").json()
    # 2 port snapshots + 2 auto Total Asset snapshots
    assert len(snapshots) == 4
    names = {s["port_name"] for s in snapshots}
    assert names == {"PortA", "PortB", "Total Asset"}


def test_snapshot_reflects_current_values(client):
    port = _create_port(client, invested=1000, profit=0)
    # Update profit then snapshot
    client.put(f"/ports/{port['id']}/profit", params={"amount": 750})
    resp = client.post("/asset-snapshots", json={"port_id": port["id"]})
    data = resp.json()
    assert data["profit"] == 750
    assert data["total"] == 1750
