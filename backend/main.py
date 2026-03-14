from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import engine, get_db, Base
from backend.models import Port, CashFlow, AssetSnapshot, PayoffRecord
from backend.schemas import PortCreate, PortResponse, PortUpdateArrows, CashFlowResponse, AssetSnapshotCreate, AssetSnapshotResponse, PayoffCreate, PayoffResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Portfolio Structure API")


def _init_cashflow(db: Session):
    """สร้าง Cash และ Profit ถ้ายังไม่มี"""
    for t in ["cash", "profit"]:
        if not db.query(CashFlow).filter(CashFlow.type == t).first():
            db.add(CashFlow(type=t, amount=0.0))
    db.commit()


@app.on_event("startup")
def startup():
    db = next(get_db())
    _init_cashflow(db)
    db.close()


# --- Cash & Profit ---
@app.get("/cashflow", response_model=list[CashFlowResponse])
def get_cashflow(db: Session = Depends(get_db)):
    return db.query(CashFlow).all()


@app.put("/cashflow/{cf_type}")
def update_cashflow(cf_type: str, amount: float, db: Session = Depends(get_db)):
    cf = db.query(CashFlow).filter(CashFlow.type == cf_type).first()
    if not cf:
        raise HTTPException(404, "CashFlow type not found")
    cf.amount = amount
    db.commit()
    return {"type": cf.type, "amount": cf.amount}


# --- Ports ---
@app.get("/ports", response_model=list[PortResponse])
def get_ports(db: Session = Depends(get_db)):
    return db.query(Port).all()


@app.post("/ports", response_model=PortResponse)
def create_port(port: PortCreate, db: Session = Depends(get_db)):
    # ห้ามชื่อซ้ำ
    existing = db.query(Port).filter(Port.name == port.name).first()
    if existing:
        raise HTTPException(400, f"Port '{port.name}' already exists")
    # หัก Invested จาก Cash
    if port.invested > 0:
        cash = db.query(CashFlow).filter(CashFlow.type == "cash").first()
        if cash.amount < port.invested:
            raise HTTPException(400, f"Not enough Cash (available: {cash.amount})")
        cash.amount -= port.invested
    db_port = Port(**port.model_dump())
    db.add(db_port)
    db.commit()
    db.refresh(db_port)
    return db_port


@app.put("/ports/{port_id}/invested", response_model=PortResponse)
def update_port_invested(port_id: int, amount: float, db: Session = Depends(get_db)):
    port = db.query(Port).filter(Port.id == port_id).first()
    if not port:
        raise HTTPException(404, "Port not found")
    diff = amount - port.invested
    if diff > 0:
        cash = db.query(CashFlow).filter(CashFlow.type == "cash").first()
        if cash.amount < diff:
            raise HTTPException(400, f"Not enough Cash (available: {cash.amount})")
        cash.amount -= diff
    elif diff < 0:
        cash = db.query(CashFlow).filter(CashFlow.type == "cash").first()
        cash.amount += abs(diff)
    port.invested = amount
    db.commit()
    db.refresh(port)
    return port


@app.put("/ports/{port_id}/profit", response_model=PortResponse)
def update_port_profit(port_id: int, amount: float, db: Session = Depends(get_db)):
    port = db.query(Port).filter(Port.id == port_id).first()
    if not port:
        raise HTTPException(404, "Port not found")
    port.profit = amount
    db.commit()
    db.refresh(port)
    return port


@app.post("/ports/{port_id}/transfer-to-profit")
def transfer_profit_to_cashflow(port_id: int, amount: float, db: Session = Depends(get_db)):
    port = db.query(Port).filter(Port.id == port_id).first()
    if not port:
        raise HTTPException(404, "Port not found")
    if amount <= 0:
        raise HTTPException(400, "Amount must be positive")
    if amount > port.profit:
        raise HTTPException(400, f"Not enough profit (available: {port.profit})")
    port.profit -= amount
    profit_cf = db.query(CashFlow).filter(CashFlow.type == "profit").first()
    profit_cf.amount += amount
    db.commit()
    return {"message": f"Transferred {amount} from '{port.name}' to Cash Flow (Profit)", "port_profit": port.profit, "cashflow_profit": profit_cf.amount}


@app.delete("/ports/{port_id}")
def delete_port(port_id: int, db: Session = Depends(get_db)):
    port = db.query(Port).filter(Port.id == port_id).first()
    if not port:
        raise HTTPException(404, "Port not found")
    db.delete(port)
    db.commit()
    return {"message": f"Port '{port.name}' deleted"}


@app.put("/ports/{port_id}/arrows", response_model=PortResponse)
def update_port_arrows(port_id: int, arrows: PortUpdateArrows, db: Session = Depends(get_db)):
    port = db.query(Port).filter(Port.id == port_id).first()
    if not port:
        raise HTTPException(404, "Port not found")
    port.arrow_white = arrows.arrow_white
    port.arrow_green = arrows.arrow_green
    port.arrow_orange = arrows.arrow_orange
    db.commit()
    db.refresh(port)
    return port


# --- Asset Snapshots ---
@app.post("/asset-snapshots", response_model=AssetSnapshotResponse)
def create_asset_snapshot(body: AssetSnapshotCreate, db: Session = Depends(get_db)):
    from datetime import datetime
    port = db.query(Port).filter(Port.id == body.port_id).first()
    if not port:
        raise HTTPException(404, "Port not found")
    now = datetime.now()
    snapshot = AssetSnapshot(
        port_id=port.id,
        port_name=port.name,
        date=now,
        invested=port.invested,
        profit=port.profit,
        total=port.invested + port.profit,
        comment=body.comment,
    )
    db.add(snapshot)
    db.flush()

    # Auto-create Total Asset snapshot
    all_ports = db.query(Port).all()
    total_invested = sum(p.invested for p in all_ports)
    total_profit = sum(p.profit for p in all_ports)
    total_snapshot = AssetSnapshot(
        port_id=0,
        port_name="Total Asset",
        date=now,
        invested=total_invested,
        profit=total_profit,
        total=total_invested + total_profit,
        comment="auto",
    )
    db.add(total_snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


@app.get("/asset-snapshots", response_model=list[AssetSnapshotResponse])
def get_asset_snapshots(db: Session = Depends(get_db)):
    return db.query(AssetSnapshot).order_by(AssetSnapshot.date.asc()).all()


# --- Seed sample snapshots for testing chart ---
@app.post("/asset-snapshots/seed-sample")
def seed_sample_snapshots(db: Session = Depends(get_db)):
    from datetime import datetime, timedelta
    import random

    ports = db.query(Port).all()
    if not ports:
        raise HTTPException(400, "No ports found. Create ports first.")

    # ลบ sample เก่า (ถ้ามี)
    db.query(AssetSnapshot).filter(AssetSnapshot.comment == "[sample]").delete()
    db.commit()

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    records = []
    for days_ago in range(30, -1, -1):
        date = today - timedelta(days=days_ago)
        day_total_invested = 0
        day_total_profit = 0
        for port in ports:
            invested = port.invested * 0.6 * (1.02 ** (30 - days_ago)) * random.uniform(0.97, 1.03)
            profit = port.profit * 0.3 * (1.01 ** (30 - days_ago)) * random.uniform(0.95, 1.05)
            invested = round(invested, 2)
            profit = round(profit, 2)
            day_total_invested += invested
            day_total_profit += profit
            snap = AssetSnapshot(
                port_id=port.id,
                port_name=port.name,
                date=date,
                invested=invested,
                profit=profit,
                total=round(invested + profit, 2),
                comment="[sample]",
            )
            records.append(snap)
        # Total Asset row for this day
        total_snap = AssetSnapshot(
            port_id=0,
            port_name="Total Asset",
            date=date,
            invested=round(day_total_invested, 2),
            profit=round(day_total_profit, 2),
            total=round(day_total_invested + day_total_profit, 2),
            comment="[sample]",
        )
        records.append(total_snap)

    db.add_all(records)
    db.commit()
    return {"message": f"Seeded {len(records)} sample snapshots for {len(ports)} ports"}


@app.delete("/asset-snapshots/seed-sample")
def delete_sample_snapshots(db: Session = Depends(get_db)):
    count = db.query(AssetSnapshot).filter(AssetSnapshot.comment == "[sample]").delete()
    db.commit()
    return {"message": f"Deleted {count} sample snapshots"}


@app.delete("/asset-snapshots/{snapshot_id}")
def delete_asset_snapshot(snapshot_id: int, db: Session = Depends(get_db)):
    snapshot = db.query(AssetSnapshot).filter(AssetSnapshot.id == snapshot_id).first()
    if not snapshot:
        raise HTTPException(404, "Snapshot not found")
    # Also delete the auto-generated Total Asset snapshot with the same date
    if snapshot.port_name != "Total Asset":
        db.query(AssetSnapshot).filter(
            AssetSnapshot.port_name == "Total Asset",
            AssetSnapshot.date == snapshot.date,
            AssetSnapshot.comment == "auto",
        ).delete()
    db.delete(snapshot)
    db.commit()
    return {"message": "Snapshot deleted"}


# --- Payoff Records ---
@app.post("/payoffs", response_model=PayoffResponse)
def create_payoff(body: PayoffCreate, db: Session = Depends(get_db)):
    from datetime import datetime
    if body.amount <= 0:
        raise HTTPException(400, "Amount must be positive")
    profit_cf = db.query(CashFlow).filter(CashFlow.type == "profit").first()
    if profit_cf.amount < body.amount:
        raise HTTPException(400, f"Not enough CF Profit (available: {profit_cf.amount})")
    profit_cf.amount -= body.amount
    record = PayoffRecord(date=datetime.now(), amount=body.amount, comment=body.comment)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/payoffs", response_model=list[PayoffResponse])
def get_payoffs(db: Session = Depends(get_db)):
    return db.query(PayoffRecord).order_by(PayoffRecord.date.asc()).all()


@app.delete("/payoffs/{payoff_id}")
def delete_payoff(payoff_id: int, db: Session = Depends(get_db)):
    record = db.query(PayoffRecord).filter(PayoffRecord.id == payoff_id).first()
    if not record:
        raise HTTPException(404, "Payoff record not found")
    db.delete(record)
    db.commit()
    return {"message": "Payoff record deleted"}
