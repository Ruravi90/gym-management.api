from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date, datetime

# Usamos float en los schemas para que el JSON use números (el modelo guarda Decimal).


def _cm():
    return Field(default=None, ge=0)


class BodyMeasurementBase(BaseModel):
    date: date
    weight_kg: Optional[float] = _cm()
    waist_cm: Optional[float] = _cm()
    abdomen_low_cm: Optional[float] = _cm()
    thigh_cm: Optional[float] = _cm()
    arm_relaxed_cm: Optional[float] = _cm()
    arm_flexed_cm: Optional[float] = _cm()
    notes: Optional[str] = None


class BodyMeasurementCreate(BodyMeasurementBase):
    pass


class BodyMeasurementUpdate(BaseModel):
    weight_kg: Optional[float] = _cm()
    waist_cm: Optional[float] = _cm()
    abdomen_low_cm: Optional[float] = _cm()
    thigh_cm: Optional[float] = _cm()
    arm_relaxed_cm: Optional[float] = _cm()
    arm_flexed_cm: Optional[float] = _cm()
    notes: Optional[str] = None


class BodyMeasurementResponse(BodyMeasurementBase):
    id: int
    client_id: int
    created_at: datetime
    updated_at: datetime
    # Deltas vs el registro anterior (None si no hay registro previo)
    delta_weight_kg: Optional[float] = None
    delta_waist_cm: Optional[float] = None
    delta_abdomen_low_cm: Optional[float] = None
    delta_thigh_cm: Optional[float] = None
    delta_arm_relaxed_cm: Optional[float] = None
    delta_arm_flexed_cm: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
