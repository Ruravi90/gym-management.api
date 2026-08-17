# -*- coding: utf-8 -*-
"""Catálogo de GIFs de múltiples fuentes para carrusel.

Fuentes:
1. hasaneyldrm/exercises-dataset (Raw GitHub) - GIFs animados
2. JahelCuadrado/ExerciseGymGifsDB (jsDelivr CDN) - GIFs animados

Mapping: exercise_name -> [gif_url_1, gif_url_2]
Nombres deben coincidir EXACTAMENTE con exercise_data.py
"""

GIF_CATALOG = {
    # ===== Pecho =====
    "barbell bench press": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/chest/barbell-bench-press.gif",
    "dumbbell incline bench press": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/chest/incline-dumbbell-bench-press.gif",
    "push-up": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/chest/push-up.gif",
    "dumbbell fly": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/chest/dumbbell-fly.gif",
    "cable cross-over variation": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/chest/cable-crossover.gif",
    "barbell decline bench press": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/chest/decline-barbell-bench-press.gif",
    "dumbbell bench press": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/chest/dumbbell-bench-press.gif",
    "chest dip": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/chest/chest-dip.gif",

    # ===== Espalda =====
    "barbell deadlift": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/back/barbell-deadlift.gif",
    "pull-up": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/back/pull-up.gif",
    "barbell bent over row": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/back/bent-over-barbell-row.gif",
    "cable lat pulldown full range of motion": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/back/lat-pulldown.gif",
    "cable seated row": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/back/seated-cable-row.gif",
    "lever t bar row": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/back/t-bar-row.gif",
    "lever back extension": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/back/back-extension.gif",

    # ===== Hombros =====
    "barbell seated overhead press": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/shoulders/barbell-shoulder-press.gif",
    "dumbbell lateral raise": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/shoulders/lateral-raise.gif",
    "dumbbell front raise": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/shoulders/front-raise.gif",
    "dumbbell reverse fly": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/shoulders/reverse-fly.gif",
    "dumbbell arnold press": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/shoulders/arnold-press.gif",
    "barbell upright row": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/shoulders/upright-row.gif",
    "barbell shrug": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/shoulders/barbell-shrug.gif",

    # ===== Bíceps =====
    "barbell curl": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/barbell-curl.gif",
    "dumbbell biceps curl": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/dumbbell-bicep-curl.gif",
    "dumbbell hammer curl": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/hammer-curl.gif",
    "lever preacher curl": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/preacher-curl.gif",
    "cable concentration curl": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/concentration-curl.gif",
    "cable curl": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/cable-curl.gif",

    # ===== Tríceps =====
    "cable pushdown": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/tricep-pushdown.gif",
    "barbell lying triceps extension skull crusher": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/skull-crusher.gif",
    "barbell standing overhead triceps extension": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/overhead-tricep-extension.gif",
    "smith close-grip bench press": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/close-grip-bench-press.gif",
    "three bench dip": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/bench-dip.gif",

    # ===== Piernas =====
    "barbell squat (on knees)": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/barbell-squat.gif",
    "barbell front squat": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/front-squat.gif",
    "smith leg press": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/leg-press.gif",
    "dumbbell lunge": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/dumbbell-lunge.gif",
    "lever leg extension": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/leg-extension.gif",
    "lever lying leg curl": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/leg-curl.gif",
    "barbell standing calf raise": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/lower-legs/standing-calf-raise.gif",
    "barbell romanian deadlift": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/romanian-deadlift.gif",
    "dumbbell goblet squat": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/goblet-squat.gif",
    "barbell glute bridge": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/glute-bridge.gif",
    "cable kickback": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/cable-kickback.gif",

    # ===== Core =====
    "front plank with twist": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/waist/plank.gif",
    "tuck crunch": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/waist/crunch.gif",
    "3/4 sit-up": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/waist/sit-up.gif",
    "hanging leg raise": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/waist/hanging-leg-raise.gif",
    "russian twist": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/waist/russian-twist.gif",
    "band bicycle crunch": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/waist/bicycle-crunch.gif",

    # ===== Cardio =====
    "mountain climber": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/cardio/mountain-climber.gif",
    "captains chair straight leg raise": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/waist/leg-raise.gif",
    "burpee": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/cardio/burpee.gif",
    "high knee against wall": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/cardio/high-knees.gif",
    "astride jumps (male)": "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/cardio/jumping-jacks.gif",
}
