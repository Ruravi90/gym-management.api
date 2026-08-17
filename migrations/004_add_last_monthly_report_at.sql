-- Agregar campo last_monthly_report_at a la tabla clients
-- para el rate limit de reportes mensuales (1 por mes)
ALTER TABLE clients ADD COLUMN last_monthly_report_at DATETIME NULL;
