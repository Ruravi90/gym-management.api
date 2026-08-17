# -*- coding: utf-8 -*-
"""Catálogo de GIFs de múltiples fuentes para carrusel.

Fuentes:
1. hasaneyldrm/exercises-dataset (Raw GitHub) - GIFs animados
2. JahelCuadrado/ExerciseGymGifsDB (jsDelivr CDN) - GIFs animados

Mapping: exercise_name -> [gif_url_1, gif_url_2]
"""

GIF_CATALOG = {
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
    "dumbbell bench press": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0289-SpYC0Kp.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/chest/dumbbell-bench-press.gif",
    ],
    "barbell deadlift": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0032-ila4NZS.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/barbell-deadlift.gif",
    ],
    "pull-up": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0652-lBDjFxJ.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/back/pull-up.gif",
    ],
    "barbell bent over row": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0251-9WTm7dq.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/back/bent-over-barbell-row.gif",
    ],
    "dumbbell one arm row": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0027-eZyBC3j.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/back/dumbbell-one-arm-row.gif",
    ],
    "barbell shoulder press": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/2330-LEprlgG.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/shoulders/barbell-shoulder-press.gif",
    ],
    "dumbbell shoulder press": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0861-fUBheHs.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/shoulders/dumbbell-shoulder-press.gif",
    ],
    "lateral raise": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0606-aaXr7ld.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/shoulders/lateral-raise.gif",
    ],
    "front raise": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0573-rUXfn3R.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/shoulders/front-raise.gif",
    ],
    "barbell curl": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0091-kTbSH9h.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/barbell-curl.gif",
    ],
    "dumbbell curl": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0334-DsgkuIt.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/dumbbell-bicep-curl.gif",
    ],
    "tricep pushdown": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0310-3eGE2JC.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/tricep-pushdown.gif",
    ],
    "tricep dip": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0383-EAs3xL9.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-arm/tricep-dip.gif",
    ],
    "barbell squat": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/2137-Xy4jlWA.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/barbell-squat.gif",
    ],
    "leg press": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0120-UDlhcO8.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/leg-press.gif",
    ],
    "leg extension": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0095-dG7tG5y.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/leg-extension.gif",
    ],
    "leg curl": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0031-25GPyDY.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/leg-curl.gif",
    ],
    "calf raise": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0294-NbVPDMW.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/lower-legs/standing-calf-raise.gif",
    ],
    "dumbbell lunges": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0313-slDvUAU.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/upper-legs/dumbbell-lunge.gif",
    ],
    "plank": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0592-b6hQYMb.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/waist/plank.gif",
    ],
    "crunch": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/1631-NvfE43H.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/waist/crunch.gif",
    ],
    "russian twist": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0868-G08RZcQ.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/waist/russian-twist.gif",
    ],
    "hanging leg raise": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0201-3ZflifB.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/waist/hanging-leg-raise.gif",
    ],
    "face pull": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0060-h8LFzo9.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/shoulders/face-pull.gif",
    ],
    "shrugs": [
        "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/videos/0109-dZl9Q27.gif",
        "https://cdn.jsdelivr.net/gh/JahelCuadrado/ExerciseGymGifsDB@v1.1.0/shoulders/barbell-shrug.gif",
    ],
}
