from fastapi import APIRouter, Depends, HTTPException
from app import crud, schemas
from app.utils.auth import get_current_user
from app.models.user import User
from app.models.client import Client
from app.services import mentor as mentor_service

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
    return mentor_service.build_client_context(
        client, routines, recent_sessions, measurements, body_type=current_user.body_type
    )


@router.post("/chat", response_model=schemas.routine.MentorResponse)
async def mentor_chat(
    request: schemas.routine.MentorRequest,
    current_user: User = Depends(get_current_user),
):
    """Chatea con el mentor IA. Usa la rutina, el progreso y las medidas del cliente como contexto."""
    client = await get_current_client(current_user)
    context = await _build_context(client, current_user)
    result = await mentor_service.mentor_chat(request.message, context)
    return schemas.routine.MentorResponse(**result)


@router.post("/weekly-checkin", response_model=schemas.routine.MentorResponse)
async def weekly_checkin(
    current_user: User = Depends(get_current_user),
):
    """Genera el reporte semanal: medidas vs semana anterior + adherencia a la rutina + recomendaciones."""
    client = await get_current_client(current_user)
    context = await _build_context(client, current_user)
    result = await mentor_service.weekly_checkin(context)
    return schemas.routine.MentorResponse(**result)


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

    # Guardar el tipo de cuerpo para futuras rutinas/reportes
    if current_user.body_type != body_type:
        current_user.body_type = body_type
        await current_user.save(update_fields=["body_type", "updated_at"])

    catalog = await crud.routine.list_exercises()
    if not catalog:
        return schemas.routine.RoutineGenerationResponse(
            ok=False,
            reply="Aún no hay ejercicios en el catálogo. Pide al administrador que ejecute el seeder.",
        )

    result = await mentor_service.generate_routine_plan(
        body_type=body_type,
        goal=request.goal,
        days_per_week=request.days_per_week,
        equipment=request.equipment,
        experience=request.experience,
        duration_minutes=request.duration_minutes,
        catalog=catalog,
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
