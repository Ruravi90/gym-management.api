from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `kaizen_habits` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `reflection` LONGTEXT,
    `goal` LONGTEXT,
    `month` INT NOT NULL,
    `year` INT NOT NULL,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `client_id` INT NOT NULL,
    CONSTRAINT `fk_kaizen_h_clients_2f75f157` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`) ON DELETE CASCADE,
    KEY `idx_kaizen_habi_client__eadff8` (`client_id`, `month`, `year`)
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `kaizen_logs` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `date` DATE NOT NULL,
    `status` VARCHAR(7) NOT NULL COMMENT 'PENDING: pending\nVICTORY: victory\nDEFEAT: defeat' DEFAULT 'pending',
    `reflection` LONGTEXT,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `habit_id` INT NOT NULL,
    UNIQUE KEY `uid_kaizen_logs_habit_i_7d0f3a` (`habit_id`, `date`),
    CONSTRAINT `fk_kaizen_l_kaizen_h_fb41ef63` FOREIGN KEY (`habit_id`) REFERENCES `kaizen_habits` (`id`) ON DELETE CASCADE,
    KEY `idx_kaizen_logs_habit_i_7d0f3a` (`habit_id`, `date`)
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `kaizen_medals` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `type` VARCHAR(7) NOT NULL COMMENT 'DAILY: daily\nWEEKLY: weekly\nMONTHLY: monthly\nYEARLY: yearly',
    `description` VARCHAR(255) NOT NULL,
    `earned_date` DATE NOT NULL,
    `client_id` INT NOT NULL,
    CONSTRAINT `fk_kaizen_m_clients_c4db3ec6` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`) ON DELETE CASCADE,
    KEY `idx_kaizen_meda_client__23271a` (`client_id`, `type`)
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `kaizen_medals`;
        DROP TABLE IF EXISTS `kaizen_habits`;
        DROP TABLE IF EXISTS `kaizen_logs`;"""


MODELS_STATE = (
    "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"
)
