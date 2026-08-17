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
    "barbell bench press": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0025-EIeI8Vf.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/chest/barbell-bench-press.gif",
    ],
    "dumbbell incline bench press": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0314-ns0SIbU.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/chest/incline-dumbbell-bench-press.gif",
    ],
    "push-up": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0662-I4hDWkc.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/chest/push-up.gif",
    ],
    "dumbbell fly": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0308-yz9nUhF.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/chest/dumbbell-fly.gif",
    ],
    "cable cross-over variation": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0155-0CXGHya.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/chest/cable-crossover.gif",
    ],
    "barbell decline bench press": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0033-GrO65fd.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/chest/decline-barbell-bench-press.gif",
    ],
    "dumbbell bench press": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0289-SpYC0Kp.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/chest/dumbbell-bench-press.gif",
    ],
    "chest dip": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0251-9WTm7dq.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/chest/chest-dip.gif",
    ],

    # ===== Espalda =====
    "barbell deadlift": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0032-ila4NZS.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/back/barbell-deadlift.gif",
    ],
    "pull-up": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0652-lBDjFxJ.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/back/pull-up.gif",
    ],
    "barbell bent over row": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0251-9WTm7dq.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/back/bent-over-barbell-row.gif",
    ],
    "cable lat pulldown full range of motion": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0027-eZyBC3j.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/back/lat-pulldown.gif",
    ],
    "cable seated row": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/2330-LEprlgG.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/back/seated-cable-row.gif",
    ],
    "lever t bar row": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0861-fUBheHs.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/back/t-bar-row.gif",
    ],
    "lever back extension": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0606-aaXr7ld.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/back/back-extension.gif",
    ],

    # ===== Hombros =====
    "barbell seated overhead press": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0573-rUXfn3R.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/shoulders/barbell-shoulder-press.gif",
    ],
    "dumbbell lateral raise": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0606-aaXr7ld.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/shoulders/lateral-raise.gif",
    ],
    "dumbbell front raise": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0573-rUXfn3R.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/shoulders/front-raise.gif",
    ],
    "dumbbell reverse fly": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0334-DsgkuIt.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/shoulders/reverse-fly.gif",
    ],
    "dumbbell arnold press": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0310-3eGE2JC.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/shoulders/arnold-press.gif",
    ],
    "barbell upright row": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0383-EAs3xL9.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/shoulders/upright-row.gif",
    ],
    "barbell shrug": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0109-dZl9Q27.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/shoulders/barbell-shrug.gif",
    ],

    # ===== Bíceps =====
    "barbell curl": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0091-kTbSH9h.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/barbell-curl.gif",
    ],
    "dumbbell biceps curl": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0334-DsgkuIt.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/dumbbell-bicep-curl.gif",
    ],
    "dumbbell hammer curl": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0289-SpYC0Kp.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/hammer-curl.gif",
    ],
    "lever preacher curl": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0027-eZyBC3j.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/preacher-curl.gif",
    ],
    "cable concentration curl": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/2330-LEprlgG.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/concentration-curl.gif",
    ],
    "cable curl": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0861-fUBheHs.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/cable-curl.gif",
    ],

    # ===== Tríceps =====
    "cable pushdown": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0310-3eGE2JC.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/tricep-pushdown.gif",
    ],
    "barbell lying triceps extension skull crusher": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0383-EAs3xL9.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/skull-crusher.gif",
    ],
    "barbell standing overhead triceps extension": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0120-UDlhcO8.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/overhead-tricep-extension.gif",
    ],
    "smith close-grip bench press": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0095-dG7tG5y.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/close-grip-bench-press.gif",
    ],
    "three bench dip": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0031-25GPyDY.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/bench-dip.gif",
    ],

    # ===== Piernas =====
    "barbell squat (on knees)": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/2137-Xy4jlWA.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/barbell-squat.gif",
    ],
    "barbell front squat": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0294-NbVPDMW.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/front-squat.gif",
    ],
    "smith leg press": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0120-UDlhcO8.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/leg-press.gif",
    ],
    "dumbbell lunge": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0313-slDvUAU.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/dumbbell-lunge.gif",
    ],
    "lever leg extension": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0095-dG7tG5y.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/leg-extension.gif",
    ],
    "lever lying leg curl": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0031-25GPyDY.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/leg-curl.gif",
    ],
    "barbell standing calf raise": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0294-NbVPDMW.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/lower-legs/standing-calf-raise.gif",
    ],
    "barbell romanian deadlift": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0032-ila4NZS.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/romanian-deadlift.gif",
    ],
    "dumbbell goblet squat": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0313-slDvUAU.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/goblet-squat.gif",
    ],
    "barbell glute bridge": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0201-3ZflifB.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/glute-bridge.gif",
    ],
    "cable kickback": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0060-h8LFzo9.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/cable-kickback.gif",
    ],

    # ===== Core =====
    "front plank with twist": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0592-b6hQYMb.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/waist/plank.gif",
    ],
    "tuck crunch": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/1631-NvfE43H.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/waist/crunch.gif",
    ],
    "3/4 sit-up": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0868-G08RZcQ.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/waist/sit-up.gif",
    ],
    "hanging leg raise": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0201-3ZflifB.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/waist/hanging-leg-raise.gif",
    ],
    "russian twist": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0868-G08RZcQ.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/waist/russian-twist.gif",
    ],
    "band bicycle crunch": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/1631-NvfE43H.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/waist/bicycle-crunch.gif",
    ],

    # ===== Cardio =====
    "mountain climber": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0592-b6hQYMb.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/cardio/mountain-climber.gif",
    ],
    "captains chair straight leg raise": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0201-3ZflifB.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/waist/leg-raise.gif",
    ],
    "burpee": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0662-I4hDWkc.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/cardio/burpee.gif",
    ],
    "high knee against wall": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0868-G08RZcQ.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/cardio/high-knees.gif",
    ],
    "astride jumps (male)": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0060-h8LFzo9.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/cardio/jumping-jacks.gif",
    ],
}
