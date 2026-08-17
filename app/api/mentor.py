import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from app import crud, schemas
from app.utils.auth import get_current_user
from app.models.user import User
from app.models.client import Client
from app.services import mentor as mentor_service

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_current_client(current_user: User = Depends(get_current_user)):
    client = await Client.get_or_none(user_id=current_user.id)
    if not client:
        client = await Client.create(
            name=current_user.name,
            email=current_user.email,
            phone=current_user.phone,
            user_id=current_user.id,
        )
    return client


async def _build_context(client: Client, current_user: User) -> str:
    routines = await crud.routine.get_client_routines(client_id=client.id, active_only=False)
    recent_sessions = await crud.routine.get_client_sessions(client_id=client.id, limit=10)
    measurements = await crud.measurement.list_measurements(client_id=client.id, limit=4)
    latest_weight = measurements[0].weight_kg if measurements else None
    return mentor_service.build_client_context(
        client,
        routines,
        recent_sessions,
        measurements,
        body_type=current_user.body_type,
        height_cm=current_user.height_cm,
        age=current_user.age,
        weight_kg=latest_weight,
    )


async def _save_profile(current_user: User, data: dict) -> None:
    """Guarda los campos de perfil físico enviados (solo los que vienen)."""
    allowed = ("body_type", "height_cm", "age", "sex", "daily_activity", "injuries")
    update = {k: v for k, v in data.items() if k in allowed and v is not None}
    if update:
        await current_user.update_from_dict(update)
        await current_user.save()


async def _profile_response(client: Client, current_user: User):
    """Perfil físico + peso actual (última medición) + IMC."""
    measurements = await crud.measurement.list_measurements(client_id=client.id, limit=1)
    weight = float(measurements[0].weight_kg) if measurements and measurements[0].weight_kg is not None else None
    bmi = None
    if current_user.height_cm and weight:
        m = current_user.height_cm / 100.0
        bmi = round(weight / (m * m), 1)
    return schemas.routine.ProfileResponse(
        body_type=current_user.body_type,
        height_cm=current_user.height_cm,
        age=current_user.age,
        sex=current_user.sex,
        daily_activity=current_user.daily_activity,
        injuries=current_user.injuries,
        weight_kg=weight,
        bmi=bmi,
    )


@router.post("/weekly-checkin", response_model=schemas.routine.MentorResponse)
async def weekly_checkin(
    current_user: User = Depends(get_current_user),
):
    """Genera el reporte semanal: medidas vs semana anterior + adherencia a la rutina + recomendaciones."""
    try:
        client = await get_current_client(current_user)

        # Rate limit: 1 reporte por semana
        now = datetime.now()
        if client.last_weekly_checkin_at:
            days_since = (now - client.last_weekly_checkin_at).days
            if days_since < 7:
                days_left = 7 - days_since
                return schemas.routine.MentorResponse(
                    reply=(
                        f"📋 Ya generaste tu reporte semanal esta semana. "
                        f"Volvé a generarlo en {days_left} día(s). "
                        f"Un reporte por semana es suficiente para medir tu progreso. 💪"
                    ),
                    provider=None,
                )

        context = await _build_context(client, current_user)
        result = await mentor_service.weekly_checkin(context)

        # Registrar la fecha del checkin
        client.last_weekly_checkin_at = now
        await client.save(update_fields=["last_weekly_checkin_at"])

        return schemas.routine.MentorResponse(**result)
    except Exception as e:
        logger.exception("Error in /mentor/weekly-checkin")
        return schemas.routine.MentorResponse(
            reply="No pude generar tu reporte semanal en este momento. Inténtalo de nuevo en unos segundos. 💪",
            provider=None,
        )


@router.get("/body-type", response_model=schemas.routine.BodyTypeResponse)
async def get_body_type(
    current_user: User = Depends(get_current_user),
):
    """Devuelve el tipo de cuerpo guardado del cliente (si lo tiene)."""
    if current_user.body_type:
        return schemas.routine.BodyTypeResponse(
            body_type=current_user.body_type,
            reply=f"Tu tipo de cuerpo guardado es: {current_user.body_type}.",
        )
    return schemas.routine.BodyTypeResponse(
        body_type=None,
        reply="Todavía no has indicado tu tipo de cuerpo.",
    )


@router.post("/body-type", response_model=schemas.routine.BodyTypeResponse)
async def save_body_type(
    request: schemas.routine.BodyTypeRequest,
    current_user: User = Depends(get_current_user),
):
    """Guarda el tipo de cuerpo del cliente (ectomorph, mesomorph o endomorph)."""
    body_type = request.body_type.strip().lower()
    if body_type not in schemas.routine.BODY_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Tipo de cuerpo inválido. Usa: ectomorph, mesomorph o endomorph.",
        )
    current_user.body_type = body_type
    await current_user.save(update_fields=["body_type", "updated_at"])
    info = mentor_service.BODY_TYPE_INFO.get(body_type, "")
    return schemas.routine.BodyTypeResponse(
        body_type=body_type,
        reply=(
            f"¡Listo! Guardé tu tipo de cuerpo: {body_type}. "
            f"{info} Lo tendré en cuenta en tus rutinas y reportes. 💪"
        ),
    )


@router.get("/profile", response_model=schemas.routine.ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    """Perfil físico del cliente: tipo de cuerpo, altura, edad, sexo, actividad y lesiones."""
    client = await get_current_client(current_user)
    return await _profile_response(client, current_user)


@router.post("/profile", response_model=schemas.routine.ProfileResponse)
async def save_profile(
    request: schemas.routine.ProfileUpdate,
    current_user: User = Depends(get_current_user),
):
    """Guarda (parcialmente) el perfil físico del cliente."""
    data = request.model_dump(exclude_unset=True)
    if data.get("body_type"):
        data["body_type"] = data["body_type"].strip().lower()
        if data["body_type"] not in schemas.routine.BODY_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Tipo de cuerpo inválido. Usa: ectomorph, mesomorph o endomorph.",
            )
    await _save_profile(current_user, data)
    client = await get_current_client(current_user)
    return await _profile_response(client, current_user)


@router.post("/generate-routine", response_model=schemas.routine.RoutineGenerationResponse)
async def generate_routine(
    request: schemas.routine.RoutineGenerationRequest,
    current_user: User = Depends(get_current_user),
):
    """Genera una rutina personalizada con IA y la crea en la BD (con ejercicios del catálogo).

    Si el cliente aún no tiene tipo de cuerpo y no lo envía, el mentor responde
    pidiéndole que elija uno (ask_body_type=True).
    """
    client = await get_current_client(current_user)

    # Límite: máximo 2 rutinas generadas por IA al mes
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    routines_this_month = await crud.routine.Routine.filter(
        client_id=client.id,
        created_at__gte=month_start,
    ).count()
    if routines_this_month >= 2:
        return schemas.routine.RoutineGenerationResponse(
            ok=False,
            reply=(
                "📋 Este mes ya generaste 2 rutinas con IA. "
                "Un buen plan necesita al menos 4 semanas para ver resultados. "
                "Seguí con tu rutina actual y volvé a generar una nueva el próximo mes. 💪"
            ),
        )

    body_type = request.body_type.strip().lower() if request.body_type else (current_user.body_type or "")
    if body_type and body_type not in schemas.routine.BODY_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Tipo de cuerpo inválido. Usa: ectomorph, mesomorph o endomorph.",
        )

    if not body_type:
        return schemas.routine.RoutineGenerationResponse(
            ok=False,
            ask_body_type=True,
            reply=(
                "Para diseñar tu rutina ideal, primero dime: 🤔 "
                "¿qué tipo de cuerpo tienes? Elige una de estas tres opciones:\n\n"
                "• **Ectomorfo** — complexión delgada, te cuesta subir de peso.\n"
                "• **Mesomorfo** — complexión atlética, ganas músculo con facilidad.\n"
                "• **Endomorfo** — tendencia a acumular grasa, ganas peso fácil.\n\n"
                "Con eso adapto series, repeticiones y descansos a tu metabolismo."
            ),
        )

    # Guardar el intake del instructor en el perfil
    profile_data = request.model_dump(exclude_unset=True)
    profile_data["body_type"] = body_type
    await _save_profile(current_user, profile_data)

    # Guardar el peso del intake como medición de hoy (si se indicó) para el IMC
    if request.weight_kg is not None:
        from datetime import date as date_cls
        await crud.measurement.upsert_measurement(
            client_id=client.id,
            data=schemas.measurement.BodyMeasurementCreate(date=date_cls.today(), weight_kg=request.weight_kg),
        )

    catalog = await crud.routine.list_exercises()
    if not catalog:
        return schemas.routine.RoutineGenerationResponse(
            ok=False,
            reply="Aún no hay ejercicios en el catálogo. Pide al administrador que ejecute el seeder.",
        )

    # Peso actual: el del intake o la última medición registrada
    latest = await crud.measurement.list_measurements(client_id=client.id, limit=1)
    weight_kg = request.weight_kg if request.weight_kg is not None else (latest[0].weight_kg if latest else None)

    result = await mentor_service.generate_routine_plan(
        body_type=body_type,
        goal=request.goal,
        days_per_week=request.days_per_week,
        equipment=request.equipment,
        experience=request.experience,
        duration_minutes=request.duration_minutes,
        catalog=catalog,
        height_cm=request.height_cm or current_user.height_cm,
        weight_kg=weight_kg,
        age=request.age or current_user.age,
        sex=request.sex or current_user.sex,
        daily_activity=request.daily_activity or current_user.daily_activity,
        injuries=request.injuries or current_user.injuries,
    )

    if not result.get("ok"):
        return schemas.routine.RoutineGenerationResponse(
            ok=False,
            reply=result.get("reply", "No pude generar la rutina."),
        )

    plan = result["plan"]
    routine_data = schemas.routine.RoutineCreate(
        name=plan["name"],
        description=plan.get("description"),
        is_active=True,
        days=[schemas.routine.RoutineDayCreate(**d) for d in plan["days"]],
    )

    # Al generar una rutina nueva, desactivar las anteriores para no mezclar planes
    await crud.routine.Routine.filter(client_id=client.id, is_active=True).update(is_active=False)

    routine = await crud.routine.create_routine(
        client_id=client.id,
        created_by_id=current_user.id,
        data=routine_data,
    )

    total_exercises = sum(len(d.exercises) for d in routine.days)
    return schemas.routine.RoutineGenerationResponse(
        ok=True,
        reply=(
            f"🎉 ¡Listo! Creé tu rutina **\"{routine.name}\"** con {len(routine.days)} día(s) "
            f"y {total_exercises} ejercicios, adaptada a tu tipo de cuerpo ({body_type}) "
            f"y tu objetivo ({request.goal}). Ya puedes abrirla y empezar a entrenar con "
            f"los GIFs de cada ejercicio. ¡A darle! 💪🔥"
        ),
        provider=result.get("provider"),
        routine_id=routine.id,
        routine_name=routine.name,
    )
