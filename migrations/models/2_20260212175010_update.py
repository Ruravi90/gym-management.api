from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `audit_logs` (
    `id` INT NOT NULL PRIMARY KEY,
    `action_type` VARCHAR(10) NOT NULL COMMENT 'CREATE: CREATE\nUPDATE: UPDATE\nDELETE: DELETE',
    `user_id` INT,
    `entity_type` VARCHAR(50) NOT NULL,
    `entity_id` INT NOT NULL,
    `old_values` JSON,
    `new_values` JSON,
    `timestamp` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `ip_address` VARCHAR(45),
    `user_agent` VARCHAR(500),
    KEY `idx_audit_logs_timesta_233d58` (`timestamp`),
    KEY `idx_audit_logs_entity__1b0d2b` (`entity_type`, `entity_id`),
    KEY `idx_audit_logs_user_id_f7db5c` (`user_id`),
    KEY `idx_audit_logs_action__9da40e` (`action_type`)
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `audit_logs`;"""


MODELS_STATE = (
    "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"
    "FtBQUS3PY0FLv/V7Ge/wfK2HYE"
)
