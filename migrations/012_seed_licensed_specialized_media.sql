-- Recurso verificado en Wikimedia Commons, CC BY-SA 4.0.
-- Debe conservarse la atribución: Taco Fleur, https://commons.wikimedia.org/wiki/File:Kettlebell_Swings_AKA_Conventional_Swings.webm
UPDATE exercises
SET video_url = 'https://commons.wikimedia.org/wiki/Special:FilePath/Kettlebell%20Swings%20AKA%20Conventional%20Swings.webm'
WHERE name = 'Kettlebell swing' AND training_type = 'crossfit';
