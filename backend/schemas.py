from pydantic import BaseModel


class PortCreate(BaseModel):
    name: str
    invested: float = 0.0
    profit: float = 0.0
    arrow_white: bool = False
    arrow_green: bool = False
    arrow_orange: bool = False


class PortResponse(BaseModel):
    id: int
    name: str
    invested: float
    profit: float
    arrow_white: bool
    arrow_green: bool
    arrow_orange: bool

    model_config = {"from_attributes": True}


class PortUpdateArrows(BaseModel):
    arrow_white: bool
    arrow_green: bool
    arrow_orange: bool


class CashFlowResponse(BaseModel):
    type: str
    amount: float

    model_config = {"from_attributes": True}
