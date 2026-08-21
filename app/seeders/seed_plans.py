from app.models.billing import Plan


async def seed_plans() -> None:
    """Create the initial editable catalog without duplicating existing plans."""
    plans = [
        {
            "name": "Básico", "code": "basic",
            "description": "Para gimnasios que están comenzando.",
            "monthly_price": 499, "max_users": 5, "max_clients": 500,
            "support_level": "standard", "trial_days": 14,
        },
        {
            "name": "Profesional", "code": "professional",
            "description": "Para gimnasios en crecimiento.",
            "monthly_price": 999, "max_users": 15, "max_clients": 2000,
            "support_level": "priority", "trial_days": 14,
        },
        {
            "name": "Enterprise", "code": "enterprise",
            "description": "Para operaciones con necesidades avanzadas.",
            "monthly_price": 2499, "max_users": 50, "max_clients": 999999,
            "support_level": "dedicated", "trial_days": 14,
        },
    ]
    for plan_data in plans:
        # `code` es el criterio de búsqueda; no debe repetirse dentro de
        # `defaults`, porque Tortoise intenta extraerlo dos veces al crear.
        defaults = {key: value for key, value in plan_data.items() if key != "code"}
        await Plan.get_or_create(code=plan_data["code"], defaults=defaults)
