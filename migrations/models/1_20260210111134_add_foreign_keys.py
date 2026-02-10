from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `facial_encodings` ADD CONSTRAINT `fk_facial_e_clients_3a7d0063` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`) ON DELETE CASCADE;
        ALTER TABLE `memberships` ADD CONSTRAINT `fk_membersh_clients_23275b71` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`) ON DELETE CASCADE;
        ALTER TABLE `memberships` ADD CONSTRAINT `fk_membersh_membersh_37ad3859` FOREIGN KEY (`membership_type_id`) REFERENCES `membership_types` (`id`) ON DELETE SET NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `memberships` DROP FOREIGN KEY `fk_membersh_membersh_37ad3859`;
        ALTER TABLE `memberships` DROP FOREIGN KEY `fk_membersh_clients_23275b71`;
        ALTER TABLE `facial_encodings` DROP FOREIGN KEY `fk_facial_e_clients_3a7d0063`;"""


MODELS_STATE = (
    "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"
    "MK/Q"
)
