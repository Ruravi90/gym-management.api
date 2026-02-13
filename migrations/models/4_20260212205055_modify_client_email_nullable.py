from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `clients` MODIFY COLUMN `email` VARCHAR(100);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `clients` MODIFY COLUMN `email` VARCHAR(100) NOT NULL;"""


MODELS_STATE = (
    "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"
    "XUVjAgQW1PQ7H7fxPr+X/rOXVu"
)
