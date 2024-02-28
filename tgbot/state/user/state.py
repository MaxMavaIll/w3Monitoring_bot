from aiogram.dispatcher.filters.state import StatesGroup, State

#EXEMPLE
# class exemple(StatesGroup):
#     """States for checker creating form"""

#     get = State()
#     write = State()

class GetValidators(StatesGroup):
#     """States for checker creating form"""

    get = State()
    get_val = State()
    