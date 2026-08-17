-- Agregar campo last_weekly_checkin_at a la tabla clients
-- para el rate limit de reportes semanales (1 por semana)
ALTER TABLE clients ADD COLUMN last_weekly_checkin_at DATETIME NULL;
