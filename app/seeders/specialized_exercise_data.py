"""Catálogo inicial de calistenia y CrossFit."""

import re

def _ex(name, training_type, equipment, difficulty, target, instructions, modifications):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    media_url = f"/assets/exercises/gifs/{slug}.gif"
    return {
        "name": name, "training_type": training_type, "equipment": equipment,
        "difficulty": difficulty, "target": target, "body_part": "full body",
        "muscle_group": target, "instructions": instructions,
        "modifications": modifications, "gif_url": media_url, "gif_urls": [media_url], "video_url": None,
    }

SPECIALIZED_EXERCISES = [
    _ex("Australian pull-up", "calisthenics", "bar", "beginner", "back", "Cuelga bajo la barra, mantén el cuerpo alineado y acerca el pecho controladamente.", "Usa una barra más alta o flexiona las rodillas."),
    _ex("Chin-up", "calisthenics", "pull-up bar", "intermediate", "back", "Cuelga con palmas hacia ti, activa los hombros y lleva el pecho hacia la barra.", "Usa banda elástica o máquina asistida."),
    _ex("Pike push-up", "calisthenics", "body weight", "intermediate", "shoulders", "Forma una V invertida y baja la cabeza entre las manos manteniendo el core activo.", "Eleva las manos sobre una plataforma."),
    _ex("Pistol squat", "calisthenics", "body weight", "advanced", "legs", "Desciende sobre una pierna con el torso estable y extiende la cadera para subir.", "Sujétate a un soporte o usa una caja."),
    _ex("L-sit hold", "calisthenics", "parallettes", "advanced", "core", "Bloquea los brazos, deprime los hombros y mantén las piernas extendidas al frente.", "Mantén las rodillas flexionadas."),
    _ex("Hollow body hold", "calisthenics", "body weight", "beginner", "core", "Presiona la zona lumbar contra el suelo y mantén brazos y piernas extendidos.", "Acerca brazos y piernas al torso."),
    _ex("Box jump", "crossfit", "box", "beginner", "legs", "Salta a la caja con ambos pies, aterriza suave y baja con control.", "Usa una caja más baja o realiza step-up."),
    _ex("Kettlebell swing", "crossfit", "kettlebell", "beginner", "glutes", "Impulsa la pesa con la cadera, mantén la espalda neutra y no eleves con los brazos.", "Reduce el peso o practica el hip hinge."),
    _ex("Thruster", "crossfit", "barbell or dumbbell", "intermediate", "full body", "Realiza una sentadilla frontal y aprovecha la extensión de piernas para empujar sobre la cabeza.", "Usa una sola mancuerna o reduce la carga."),
    _ex("Power clean", "crossfit", "barbell", "advanced", "full body", "Lleva la barra desde el suelo y recíbela en posición de rack con codos altos.", "Practica hang clean con una carga ligera."),
    _ex("Dumbbell snatch", "crossfit", "dumbbell", "intermediate", "full body", "Extiende cadera y rodillas y recibe la mancuerna sobre la cabeza con control.", "Alterna desde una posición elevada."),
    _ex("Double unders", "crossfit", "jump rope", "advanced", "conditioning", "Salta bajo y gira la cuerda dos veces por salto manteniendo muñecas relajadas.", "Comienza con single unders o saltos sin cuerda."),
]

_EXTRA = [
    ("pull-up", "calisthenics", "pull-up bar", "intermediate", "back"), ("muscle-up", "calisthenics", "pull-up bar", "advanced", "full body"),
    ("ring-dip", "calisthenics", "gymnastic rings", "intermediate", "triceps"), ("archer-push-up", "calisthenics", "body weight", "advanced", "chest"),
    ("diamond-push-up", "calisthenics", "body weight", "intermediate", "triceps"), ("handstand-push-up", "calisthenics", "body weight", "advanced", "shoulders"),
    ("front-lever", "calisthenics", "pull-up bar", "advanced", "core"), ("back-lever", "calisthenics", "gymnastic rings", "advanced", "shoulders"),
    ("dragon-flag", "calisthenics", "bench", "advanced", "core"), ("toes-to-bar", "calisthenics", "pull-up bar", "intermediate", "core"),
    ("hanging-knee-raise", "calisthenics", "pull-up bar", "beginner", "core"), ("nordic-hamstring-curl", "calisthenics", "bench", "advanced", "hamstrings"),
    ("burpee", "crossfit", "body weight", "beginner", "conditioning"), ("wall-ball", "crossfit", "medicine ball", "beginner", "full body"),
    ("rowing-machine", "crossfit", "rowing machine", "beginner", "conditioning"), ("assault-bike", "crossfit", "assault bike", "beginner", "conditioning"),
    ("front-squat", "crossfit", "barbell", "intermediate", "legs"), ("overhead-squat", "crossfit", "barbell", "advanced", "full body"),
    ("clean-and-jerk", "crossfit", "barbell", "advanced", "full body"), ("barbell-snatch", "crossfit", "barbell", "advanced", "full body"),
    ("push-press", "crossfit", "barbell", "intermediate", "shoulders"), ("sumo-deadlift-high-pull", "crossfit", "barbell", "intermediate", "full body"),
    ("farmer-carry", "crossfit", "dumbbell", "beginner", "conditioning"), ("handstand-walk", "crossfit", "body weight", "advanced", "shoulders"),
]
SPECIALIZED_EXERCISES.extend(
    _ex(name.replace('-', ' ').title(), kind, equipment, level, target,
        f"Ejecuta {name.replace('-', ' ')} con control, postura estable y respiración coordinada.",
        "Reduce el rango, la carga o usa una progresión asistida.")
    for name, kind, equipment, level, target in _EXTRA
)
