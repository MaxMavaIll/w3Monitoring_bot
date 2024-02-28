import toml

from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

#EXEMPLE
# def exemple():
#     builder = ReplyKeyboardBuilder()

#     builder.add(
#         KeyboardButton(
#             text="stop",
#             callback_data="delete"
#         ), 
#         KeyboardButton(
#             text="start",
#             callback_data="start"
#         )
#     )

#     return builder.as_markup()

async def validators_reply(validators: list, get_list: list = []):
    builder = ReplyKeyboardBuilder()
    i = 1


    builder.row(
        KeyboardButton(
                text=f"Back"
            ),
        KeyboardButton(
                text=f"Clear All"
            ),
        KeyboardButton(
                text=f"Next"
        )
    )

    mass = []
    for moniker in validators:
        if moniker in get_list:

            mass.append(KeyboardButton(
                    text=f"✅ {i}. {moniker} "
                    # text=f"{moniker}"
                ))
        else:
            mass.append(KeyboardButton(
                text=f"{i}. {moniker}"
                # text=f"{moniker}"
            ))
        
        if len(mass) == 2:
            builder.row(#text=f"{moniker}"
                * mass
            )
            mass = []
        i += 1
        # builder.adjust(2)
    # builder.row(width=2)
    return builder.as_markup()