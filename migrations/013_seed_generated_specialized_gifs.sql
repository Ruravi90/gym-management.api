-- GIFs propios generados para el catálogo especializado.
-- La ruta es relativa al frontend para que funcione en cualquier dominio.
UPDATE exercises SET gif_url = '/assets/exercises/gifs/australian-pull-up.gif', gif_urls = JSON_ARRAY('/assets/exercises/gifs/australian-pull-up.gif') WHERE name = 'Australian pull-up' AND training_type = 'calisthenics';
UPDATE exercises SET gif_url = '/assets/exercises/gifs/chin-up.gif', gif_urls = JSON_ARRAY('/assets/exercises/gifs/chin-up.gif') WHERE name = 'Chin-up' AND training_type = 'calisthenics';
UPDATE exercises SET gif_url = '/assets/exercises/gifs/pike-push-up.gif', gif_urls = JSON_ARRAY('/assets/exercises/gifs/pike-push-up.gif') WHERE name = 'Pike push-up' AND training_type = 'calisthenics';
UPDATE exercises SET gif_url = '/assets/exercises/gifs/pistol-squat.gif', gif_urls = JSON_ARRAY('/assets/exercises/gifs/pistol-squat.gif') WHERE name = 'Pistol squat' AND training_type = 'calisthenics';
UPDATE exercises SET gif_url = '/assets/exercises/gifs/l-sit-hold.gif', gif_urls = JSON_ARRAY('/assets/exercises/gifs/l-sit-hold.gif') WHERE name = 'L-sit hold' AND training_type = 'calisthenics';
UPDATE exercises SET gif_url = '/assets/exercises/gifs/hollow-body-hold.gif', gif_urls = JSON_ARRAY('/assets/exercises/gifs/hollow-body-hold.gif') WHERE name = 'Hollow body hold' AND training_type = 'calisthenics';
UPDATE exercises SET gif_url = '/assets/exercises/gifs/box-jump.gif', gif_urls = JSON_ARRAY('/assets/exercises/gifs/box-jump.gif') WHERE name = 'Box jump' AND training_type = 'crossfit';
UPDATE exercises SET gif_url = '/assets/exercises/gifs/kettlebell-swing.gif', gif_urls = JSON_ARRAY('/assets/exercises/gifs/kettlebell-swing.gif') WHERE name = 'Kettlebell swing' AND training_type = 'crossfit';
UPDATE exercises SET gif_url = '/assets/exercises/gifs/thruster.gif', gif_urls = JSON_ARRAY('/assets/exercises/gifs/thruster.gif') WHERE name = 'Thruster' AND training_type = 'crossfit';
UPDATE exercises SET gif_url = '/assets/exercises/gifs/power-clean.gif', gif_urls = JSON_ARRAY('/assets/exercises/gifs/power-clean.gif') WHERE name = 'Power clean' AND training_type = 'crossfit';
UPDATE exercises SET gif_url = '/assets/exercises/gifs/dumbbell-snatch.gif', gif_urls = JSON_ARRAY('/assets/exercises/gifs/dumbbell-snatch.gif') WHERE name = 'Dumbbell snatch' AND training_type = 'crossfit';
UPDATE exercises SET gif_url = '/assets/exercises/gifs/double-unders.gif', gif_urls = JSON_ARRAY('/assets/exercises/gifs/double-unders.gif') WHERE name = 'Double unders' AND training_type = 'crossfit';
