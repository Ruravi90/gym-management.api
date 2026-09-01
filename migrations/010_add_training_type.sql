-- Modalidad del ejercicio para filtros y generación especializada.
ALTER TABLE exercises ADD COLUMN training_type VARCHAR(20) NOT NULL DEFAULT 'gym';
CREATE INDEX idx_exercises_training_type ON exercises (training_type);
