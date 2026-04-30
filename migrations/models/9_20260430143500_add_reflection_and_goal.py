from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True

async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `kaizen_habits` ADD COLUMN `reflection` LONGTEXT;
        ALTER TABLE `kaizen_habits` ADD COLUMN `goal` LONGTEXT;
        ALTER TABLE `kaizen_logs` ADD COLUMN `reflection` LONGTEXT;"""

async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `kaizen_habits` DROP COLUMN `reflection`;
        ALTER TABLE `kaizen_habits` DROP COLUMN `goal`;
        ALTER TABLE `kaizen_logs` DROP COLUMN `reflection`;"""
