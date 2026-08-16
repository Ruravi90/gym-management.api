from typing import List, Optional
from fastapi import HTTPException
from app.models.measurement import BodyMeasurement
from app.schemas.measurement import BodyMeasurementCreate, BodyMeasurementUpdate

DELTA_FIELDS = (
    "weight_kg",
    "waist_cm",
    "abdomen_low_cm",
    "thigh_cm",
    "arm_relaxed_cm",
    "arm_flexed_cm",
)


async def list_measurements(client_id: int, limit: int = 100) -> List[BodyMeasurement]:
    """Lista las medidas del cliente de más reciente a más antigua, con deltas vs la anterior."""
    measurements = await BodyMeasurement.filter(client_id=client_id).order_by("-date", "-id").limit(limit)
    # Como vienen en orden descendente, el "anterior" en el tiempo es el siguiente de la lista
    for i, m in enumerate(measurements):
        prev = measurements[i + 1] if i + 1 < len(measurements) else None
        for field in DELTA_FIELDS:
            current = getattr(m, field)
            previous = getattr(prev, field) if prev else None
            delta = None
            if current is not None and previous is not None:
                delta = round(current - previous, 2)
            setattr(m, f"delta_{field}", delta)
    return measurements


async def get_latest_measurements(client_id: int, limit: int = 4) -> List[BodyMeasurement]:
    return await BodyMeasurement.filter(client_id=client_id).order_by("-date", "-id").limit(limit)


async def get_measurement(measurement_id: int) -> Optional[BodyMeasurement]:
    return await BodyMeasurement.get_or_none(id=measurement_id)


async def upsert_measurement(client_id: int, data: BodyMeasurementCreate) -> BodyMeasurement:
    """Crea o actualiza la medición de una fecha concreta (una por fecha).

    Usa exclude_unset para que al actualizar solo cambien los campos enviados
    (no se borran los no enviados).
    """
    payload = data.model_dump(exclude_unset=True)
    measurement, created = await BodyMeasurement.update_or_create(
        client_id=client_id,
        date=data.date,
        defaults={k: v for k, v in payload.items() if k != "date"},
    )
    return measurement


async def update_measurement(measurement_id: int, data: BodyMeasurementUpdate) -> Optional[BodyMeasurement]:
    measurement = await BodyMeasurement.get_or_none(id=measurement_id)
    if not measurement:
        return None
    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        await measurement.update_from_dict(update_data)
        await measurement.save()
    return measurement


async def delete_measurement(measurement_id: int) -> bool:
    measurement = await BodyMeasurement.get_or_none(id=measurement_id)
    if not measurement:
        return False
    await measurement.delete()
    return True
