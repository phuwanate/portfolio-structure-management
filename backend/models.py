from sqlalchemy import Column, Integer, String, Float, Boolean
from backend.database import Base


class Port(Base):
    __tablename__ = "ports"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    invested = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)
    arrow_white = Column(Boolean, default=False)   # Cash → Port (เงินลงทุนตั้งต้น)
    arrow_green = Column(Boolean, default=False)   # Profit → Port (เติมเงินจาก Profit)
    arrow_orange = Column(Boolean, default=False)  # Port → Profit (โอนกำไรออก)


class CashFlow(Base):
    __tablename__ = "cashflow"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # "cash" or "profit"
    amount = Column(Float, default=0.0)
