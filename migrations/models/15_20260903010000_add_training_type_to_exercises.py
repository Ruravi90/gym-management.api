from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `exercises` ADD COLUMN `training_type` VARCHAR(20) NOT NULL DEFAULT 'gym';
        CREATE INDEX `idx_exercises_training_type` ON `exercises` (`training_type`);
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX `idx_exercises_training_type` ON `exercises`;
        ALTER TABLE `exercises` DROP COLUMN `training_type`;
        """
