from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        UPDATE `clients` c
        INNER JOIN `users` u ON u.`id` = c.`user_id`
        SET c.`body_type` = u.`body_type`, c.`height_cm` = u.`height_cm`,
            c.`age` = u.`age`, c.`sex` = u.`sex`,
            c.`daily_activity` = u.`daily_activity`, c.`injuries` = u.`injuries`,
            c.`birth_date` = u.`birth_date`, c.`goal` = u.`goal`,
            c.`restrictions` = u.`restrictions`, c.`emergency_contact` = u.`emergency_contact`
        WHERE c.`user_id` IS NOT NULL;
        ALTER TABLE `users` DROP COLUMN `daily_activity`;
        ALTER TABLE `users` DROP COLUMN `sex`;
        ALTER TABLE `users` DROP COLUMN `age`;
        ALTER TABLE `users` DROP COLUMN `height_cm`;
        ALTER TABLE `users` DROP COLUMN `restrictions`;
        ALTER TABLE `users` DROP COLUMN `goal`;
        ALTER TABLE `users` DROP COLUMN `birth_date`;
        ALTER TABLE `users` DROP COLUMN `emergency_contact`;
        ALTER TABLE `users` DROP COLUMN `injuries`;
        ALTER TABLE `users` DROP COLUMN `body_type`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` ADD `daily_activity` VARCHAR(20);
        ALTER TABLE `users` ADD `sex` VARCHAR(10);
        ALTER TABLE `users` ADD `age` INT;
        ALTER TABLE `users` ADD `height_cm` DOUBLE;
        ALTER TABLE `users` ADD `restrictions` LONGTEXT;
        ALTER TABLE `users` ADD `goal` VARCHAR(30);
        ALTER TABLE `users` ADD `birth_date` DATE;
        ALTER TABLE `users` ADD `emergency_contact` VARCHAR(150);
        ALTER TABLE `users` ADD `injuries` LONGTEXT;
        ALTER TABLE `users` ADD `body_type` VARCHAR(20);"""


MODELS_STATE = (
    "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"
)
