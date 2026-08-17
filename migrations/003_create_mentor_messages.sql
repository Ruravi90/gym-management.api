-- Tabla para historial de mensajes del mentor IA
CREATE TABLE IF NOT EXISTS mentor_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    message_type VARCHAR(30) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    INDEX idx_mentor_messages_client_id (client_id),
    INDEX idx_mentor_messages_created_at (created_at)
);
