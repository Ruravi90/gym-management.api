-- Agregar campos de detalles de ejercicios
-- tips, common_mistakes, modifications para instrucciones detalladas
ALTER TABLE exercises ADD COLUMN tips TEXT NULL;
ALTER TABLE exercises ADD COLUMN common_mistakes TEXT NULL;
ALTER TABLE exercises ADD COLUMN modifications TEXT NULL;
