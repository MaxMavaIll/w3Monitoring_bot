import toml

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from tgbot.function import get_active_validators, get_name_validators



async def menu():
    config = toml.load('config.toml')
    builder = InlineKeyboardBuilder()
    
    for network_name in config["network"]:
        builder.add(
            InlineKeyboardButton(
                text=network_name,
                callback_data=f"network&{network_name}"
            )
        )
    builder.adjust(5)
    return builder.as_markup()

async def already():
    builder = InlineKeyboardBuilder()
    builder.add(
            InlineKeyboardButton(
                text="Next",
                callback_data=f"validator&next"
            ),
            InlineKeyboardButton(
                text="Back",
                callback_data=f"validator&back"
            )
        )

    builder.adjust(3)
    return builder.as_markup()


# async def validators(network: str ):
#     builder = InlineKeyboardBuilder()

#     validators_data = await get_active_validators(name_network=network)
#     validators = await get_name_validators(validators_data=validators_data)
    
#     for moniker in validators:
#         builder.add(
#             InlineKeyboardButton(
#                 text=moniker,
#                 callback_data=f"validator&{validators[moniker]}"
#             )
#         )

#     builder.adjust(3)
#     return builder.as_markup()