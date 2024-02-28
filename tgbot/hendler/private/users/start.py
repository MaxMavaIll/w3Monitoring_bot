from aiogram import Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.filters import Command, Text, StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, ContentType

from tgbot.keyboard.user.inline import menu
from tgbot.keyboard.user.reply import validators_reply
from tgbot.keyboard.user.inline import already

from tgbot.hendler.private.users.router import user_router
from tgbot.state.user.state import GetValidators
from tgbot.function import get_active_validators, get_name_validators
#from tgbot.state.user.state import 
#from tgbot.keyboard.user.inline import 

import logging as log


@user_router.message(Command(commands="start"))
async def Choose_Network( message: Message, state: FSMContext):
    log.info("Function Choose_Network")

    data = await state.get_data()
    if not data.get(message.from_user.id):
        log.info(f"Add new user {message.from_user.id} | {message.from_user.first_name}")
        data[message.from_user.id] = {}
    
    data[message.from_user.id]['buffer_validator'] = []
    data[message.from_user.id]['network'] = None

    bot_msg = await message.answer(f"Hallo user {message.from_user.first_name}!!\nChoose a network ↓", reply_markup=await menu())
    data[message.from_user.id]["bot_msg_id"] = bot_msg.message_id

    await state.update_data(data)
    await state.set_state(GetValidators.get)

    

@user_router.callback_query(state=GetValidators.get)
async def Choose_Validator(callback: CallbackQuery, state: FSMContext):
    log.info("Function Choose_Validator")

    data = await state.get_data()
    network = callback.data.split("&")[-1]
    data[callback.from_user.id]['network'] = network

    if not data[callback.from_user.id].get(network):
        log.info(f"Add new network {callback.from_user.id} | {network}")
        data[callback.from_user.id][network] = {}
    
    await callback.message.delete()

    validators_data = await get_active_validators(name_network=network)
    validators = await get_name_validators(validators_data=validators_data)
    log.info(validators)
    
    bot_msg = await callback.message.answer(f"choose the validator you want to follow ↓",
                                            reply_markup=await validators_reply(validators=validators))
    
    data[callback.from_user.id]["bot_msg_id"] = bot_msg.message_id

    await state.set_state(GetValidators.get_val)
    await state.update_data(data)
    


@user_router.message(state=GetValidators.get_val)
async def Choose_Validator(message: Message, state: FSMContext, bot: Bot):
    log.info("Function Choose_Validator")
    data = await state.get_data()
    choose_validators = data[message.from_user.id]['buffer_validator']
    network = data[message.from_user.id]['network']
    moniker = message.text.split('. ')[1]
    bot_msg_id = data[message.from_user.id]["bot_msg_id"]

    validators_data = await get_active_validators(name_network=network)
    validators = await get_name_validators(validators_data=validators_data)
    log.info(message.text)
    log.info(choose_validators)

    if message.text == "Next":
        log.info(f"User: {message.from_user.id} enter Next")
        await message.answer(f"You chose such validators: {choose_validators}",
                                    reply_markup= await already())
        # data[message.from_user.id][network]
        await state.set_state()
        
    elif message.text == "Bacck":
        log.info(f"User: {message.from_user.id} enter Back")
        bot_msg = await message.answer(f"Maybe you want to choose another network?\nChoose a network ↓", 
                                                reply_markup=await menu())
        await state.set_state()
    
    elif moniker in list(validators.keys()) and moniker not in choose_validators:
        log.info(f"User: {message.from_user.id} want to add new moniker {message.text}")
        
        choose_validators.append(moniker)

        await bot.delete_message(message_id=bot_msg_id, chat_id=message.from_user.id)
        await message.delete()
        bot_msg = await message.answer(f"Choose validators: {*choose_validators,}", reply_markup=await validators_reply(validators=validators, get_list=choose_validators))
        data[message.from_user.id]["bot_msg_id"] = bot_msg.message_id

    elif moniker in choose_validators:
        choose_validators.remove(moniker)

        await bot.delete_message(message_id=bot_msg_id, chat_id=message.from_user.id)
        await message.delete()
        bot_msg = await message.answer(f"Choose validators: {*choose_validators,}", reply_markup=await validators_reply(validators=validators, get_list=choose_validators))
        data[message.from_user.id]["bot_msg_id"] = bot_msg.message_id

    await state.update_data(data)