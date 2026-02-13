from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `clients` DROP INDEX `email`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `clients` ADD UNIQUE INDEX `email` (`email`);"""


MODELS_STATE = (
    "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"
    "GABLU9DcXu/02s5/8BWw52BA=="
)
