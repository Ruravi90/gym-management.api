from pydantic import BaseModel
from typing import Optional, List

class PreferenceItem(BaseModel):
    title: str
    quantity: int
    unit_price: float
    currency_id: str = "MXN"

class PreferenceCreate(BaseModel):
    membership_type_id: int

class PreferenceResponse(BaseModel):
    preference_id: str
    init_point: str
    sandbox_init_point: str

class PaymentWebhook(BaseModel):
    action: str
    api_version: str
    data: dict
    date_created: str
    id: int
    live_mode: bool
    type: str
    user_id: str
