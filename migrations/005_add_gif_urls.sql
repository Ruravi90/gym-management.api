-- Agregar campo gif_urls a la tabla exercises para carrusel de GIFs
-- gif_url sigue siendo el GIF principal, gif_urls almacena la lista completa
ALTER TABLE exercises ADD COLUMN gif_urls JSON NULL;
