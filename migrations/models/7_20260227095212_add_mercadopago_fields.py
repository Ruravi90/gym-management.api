from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `memberships` ADD `mp_payment_status` VARCHAR(50);
        ALTER TABLE `memberships` ADD `mp_payment_id` VARCHAR(100);
        ALTER TABLE `memberships` ADD `mp_preference_id` VARCHAR(100);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `memberships` DROP COLUMN `mp_payment_status`;
        ALTER TABLE `memberships` DROP COLUMN `mp_payment_id`;
        ALTER TABLE `memberships` DROP COLUMN `mp_preference_id`;"""


MODELS_STATE = (
    "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"
    "41nv+vQm5LF9WPmtg+/Q9Cbc2g"
)
