# -*- coding: utf-8 -*-
"""Catálogo de GIFs: un solo GIF por ejercicio.

Fuente única: exercise_data.py (hasaneyldrm/exercises-dataset, raw GitHub),
el mismo GIF que se usa al sembrar los ejercicios. GIF_CATALOG permite que
update_gifs() refresque gif_url/gif_urls sin re-sembrar, y garantiza que el
GIF guardado siempre coincida con el del seeder.
"""

from app.seeders.exercise_data import EXERCISES

GIF_CATALOG = {
    ex["name"].lower().strip(): ex["gif_url"]
    for ex in EXERCISES
}