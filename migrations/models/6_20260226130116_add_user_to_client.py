from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `clients` ADD `user_id` INT;
        ALTER TABLE `clients` ADD CONSTRAINT `fk_clients_users_888199a9` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `clients` DROP FOREIGN KEY `fk_clients_users_888199a9`;
        ALTER TABLE `clients` DROP COLUMN `user_id`;"""


MODELS_STATE = (
    "eJztXVtzmzgU/isentqZbqf1Jm0nb45DWm8dO+PLbqdNh1FAsZmCoCCaejr57ytxRwgKFF"
    "+w9WQj6cjoOwfpfOcI+ZdkWho03JcDjCHSAFKhdNH7JSFg0i+c2hc9Cdh2UkcLMLg3/OYg"
    "2+7exQ5QMal5AIYLSZEGXdXRbaxbiJQizzBooaWShjpaJUUe0r97UMHWCuI1dEjFl6+kWE"
    "ca/AldevlFUtdQ/aboSME6uVlSHRVZHg7LqIz9TXnQoaFlxqVr9Ab9cgVvbL9shPC135De"
    "0r2iWoZnoqSxvcFrC8WtdYRp6Qoi6AAMtdQg6RhCRKKiYDykADsejAeiJQUafACegVOgVE"
    "RKtRBFmdyO649wRX/lr/7rs7dn7/5+c/aONPHvJC55+xSMLxl8IOhDMFlIT349wCBo4YOd"
    "AJcFPYfhFYGC1vCBzAkzmGqh9MvoSxOEo4IE4sT4WsLYgUCbImMTqq8E0MXoRp4vBje3dC"
    "Sm6343fJQGC5nW9P3SDVP67M1zWm6RRyd4quJOev+NFh969LL3eTqRfQQtF68c/xeTdovP"
    "Er0n4GFLQdajArSUpUWlETCkJave+AFqpN+0dAsKDm97h/rtiD6jYZcqVIM/dBUqvPluuA"
    "YOX48ZIUaFBKiDVJpkgp+KAdEKr8nl61evSrT472A2/DCYPSOtnvvzXYIXsjB062AVC3QS"
    "p/75eQWcSCsWJ9XQIcJcuypcRzMy7SynO8CrhQWVuiEP3/jrqY9JHsRry4H6Cn2EGx/LEb"
    "mnyK1ikAtdtGHc0eFh+BRZQlSaWL4DHmP3LGsgZIhkYBAHz99gPhxcyZIP5T1Qvz0CR1My"
    "mNIaq28xJXHbfJXZN9kSgMDKR4COg9515P96mo7H1kri+cZRXblnTFsphrVyd+AZ05WV2I"
    "tpB14xwVTHm8BgSNPwkqDs13oudOILck96ZFvCe27de07Dy11jZOSZuQc+AyfTRaNVp70p"
    "QBrOZOLmXPSCzzu0vL3yr4PPO3Qlj2V6HXxKjZbySis5u0BFZl3dUFMSjax1D2t5K+aaYM"
    "ZMFFVdIEZszybZ0BM6r2Jm5zkzSybT6oaWkTklPygNnEXa/ACGx/O2/5lPJ3zoslIMdktE"
    "xvRF01X8omfoLv56kA9tCUp03BliOYkM72bwiSGRk+F4eskyRtrBJcto4GMDoLNSAugKQC"
    "deVw7n8rBJRlCExA4sJKbbtDHpr1ZYICvVydjAWZXQwFkuMuC7UYRG8VhtMV5ZqU7idV4p"
    "5nQexJxyIYH9ENswasChtUk8oZjUBnx9F4wWmkA3AopKZkrsuWG+h0w7xB4UgINrE5r30H"
    "HX5OkTFHY7FNb/rPFgR+27yQoax5EDg62BUyzQybmvMU42GWste4oFOolTvwpM/RxK7LxW"
    "Ay+OaCeRa8jPw9UiB9ilZRkQID5miRAD1T2R2ta0Fa8DbZOdy+l0nPG1L0cLhuIsby5l8n"
    "j6TjZppAdB9zxpT623OUR/kxrOSAqSc2Akx7O1horNSgrF7lWx4c2LKHiLGVoKSAv52WXY"
    "zcHBVzU5mzKMTGp2Li96k+V4XJabTWXA4h2CvEU5FL7+OIMG8AdSiGd2S+LhzSlFsGYezw"
    "eg6sBQIFItjXT2h5Bc+73JYWcdhiXxWf8QkZu4o46hsc2YD2MmnNhP3pCKY0A8E972xt9U"
    "1EcEeNoO8ESaVGiLPIYL+LMwrckIdiXkU+buyZ8W5Ymi2NsbTyfvo+Zs9ijLonSTPJiKDQ"
    "ivzcFbklHISHWSwzffbSh45zHQE8E7j1SxOQ9ObA8W24NPZ3vw+405NIDrShxfOq4r9aJV"
    "2gTuwnlOp0/JdwenXp8jhFq8OCfypvvMB6Z/PYdWMfdgxDriHe+ceNBf91RscQKaJcQjI3"
    "Vi9qgCG6g63tTxY1Iip+TGMGlXp9k7pFnJbvr1HfHjo2GXMrTYJ6ipx7Sc0OK+tVi0DaJ4"
    "1i/cA7HFGV9y1TXUPAMGt7PHDTci4HQUcQkRcDpSxcZJsgPYQ51KMnL4fzYFWRwBYHKeO4"
    "wC2GBj0rhKPjJAjTmJDARXIjLQdmSg7o7O3b9nSR4UV1dbW5Obb+WMbLIRp4gkxdR9YGty"
    "PLk0oBjdVmpHlFiJYtiOrnJUeG1YoGARiCUY5T1Qkc4p7Gq6vBzLvduZPBzNR+H7pbGG/E"
    "palGyvnsmDMfs2BEVEsQFvLf0dkLFYQzQPKvzZBpgd4bz0QI8fcN+El3ECa4CWl9wheDZZ"
    "A8ItaoeAnkk8bqvWUWt5yY7kLlpx6YCqQpr3VDwX1qEPObndxdlf7ZtIiLPqxO6xWiAeL3"
    "EQwbyjUKzYPdbWisC87FsPQb6weAkssS4OKRP78Lj78Gq9vF4bxCSmvgg7PDh7rIol/6Gr"
    "/YLdbvIbi0ANJTmOSB9V8hzhM/hi68kO3VVCkv2VPTRGZDOOa5/j1tFrg/VqnuO/t6hoYM"
    "Phb4VmlpM7obWZGzUAhmE9NgscpERPFEURr//zEHPpbuWy/1fo4m7llqIxyWqcQ6z0UJ6M"
    "nDiXR0S4ji8QIiJcR6rYutvV9n0UxuHw5a2ehOGfycPhs9FZPcUslh6Gs+NzTx2yNgoCe+"
    "wEdtduXFcPON0t0RfHm251+4Q/tXFB+v3/4USyO9x0Ep0Ix/wVzuDqZjS56AHN1NEduhlM"
    "Bu/l2UUvWH2cO0SIpny7IExzNF9c9ByoQl9Ud/EdWs5pU9rxHZovb+WZEvbmejY9GJ32KT"
    "Ux3H4Vu+2zClkDd00WGBu47qPl1NrQwhE9sZlRHDkrqK1gQILanoZim1PbMI1sO9aDzlv/"
    "67Dbymn1o2a2T/8DADCYHg=="
)
