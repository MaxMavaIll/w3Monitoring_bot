from aiogram import Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.filters import Command, Text, StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, ContentType
from aiogram.types import ReplyKeyboardRemove


from tgbot.keyboard.user.inline import inl_menu, inl_to_menu
from tgbot.keyboard.user.reply import validators_reply

from tgbot.hendler.private.users.router import user_router
from tgbot.state.user.state import GetValidators
from tgbot.function import get_active_validators, get_name_validators, send_buffer_to_data
#from tgbot.state.user.state import 
#from tgbot.keyboard.user.inline import 

import logging as log


@user_router.message(Command(commands="start"))
async def Start( message: Message, state: FSMContext):
    log.info("Function Start")

    data = await state.get_data()
    user_id = str(message.from_user.id)
    if not data.get(user_id):
        log.info(f"Add new user {message.from_user.id} | {message.from_user.first_name}")
        data[user_id] = {}
    
    if not data[user_id].get('networks'):
        data[user_id]['networks'] = {}

    data[user_id]['buffer_validator'] = []
    data[user_id]['network'] = None

    bot_msg = await message.answer(f"Hallo user {message.from_user.first_name}!!\nChoose a network ↓", reply_markup=await inl_menu())
    data[user_id]["bot_msg_id"] = bot_msg.message_id
    log.info(f"Data: {data}")


    await state.update_data(data)
    # await state.set_state(GetValidators.get)

    

@user_router.callback_query(Text(text_startswith='network&'))
async def Choose_Network(callback: CallbackQuery, state: FSMContext):
    log.info("Function Choose_Network")

    user_id = str(callback.from_user.id)
    data = await state.get_data()
    network = callback.data.split("&")[-1]
    data[user_id]['network'] = network

    if not data[user_id]['networks'].get(network):
        log.info(f"Add new network {user_id} | {network}")
        data[user_id]['networks'][network] = {}
    
    if  data[user_id]['networks'][network] != {}:
        data[user_id]['buffer_validator'] = list(data[user_id]['networks'][network].keys())

    choose_validators = data[user_id]['buffer_validator']

    await callback.message.delete()

    validators_data = await get_active_validators(name_network=network)
    validators = await get_name_validators(validators_data=validators_data)
    log.info(validators)
    
    bot_msg = await callback.message.answer(f"Choose the validator you want to monitor ↓",
                                            reply_markup=await validators_reply(validators=validators, get_list=choose_validators))
    
    data[user_id]["bot_msg_id"] = bot_msg.message_id

    await state.set_state(GetValidators.get_val)
    await state.update_data(data)
    


@user_router.message(state=GetValidators.get_val)
async def Choose_Validator(message: Message, state: FSMContext, bot: Bot):
    log.info("Function Choose_Validator")

    user_id = str(message.from_user.id)
    data = await state.get_data()
    network = data[user_id]['network']
    choose_validators = data[user_id]['buffer_validator']

    if '.' in message.text:
        moniker = message.text.split('. ')[1]
    bot_msg_id = data[user_id]["bot_msg_id"]

    validators_data = await get_active_validators(name_network=network)
    validators = await get_name_validators(validators_data=validators_data)
    log.info(message.text)
    log.info(choose_validators)

    if message.text == "Save":
        log.info(f"User: {message.from_user.id} enter Save")

        await message.delete()
        await bot.delete_message(message_id=bot_msg_id, chat_id=message.from_user.id)
        
        if choose_validators == []:
            bot_msg = await message.answer(f"I saved your changes.",
                                        reply_markup= await inl_to_menu())
        else:
            bot_msg = await message.answer(f"Great I will monitor your validators if you are outside the active set and in jail I will let you know:\nValidators:\n\t{*choose_validators,}",
                                        reply_markup= await inl_to_menu())

        send_buffer_to_data(choose_validators, data[user_id]['networks'], network)

        choose_validators.clear()
        data[user_id]["bot_msg_id"] = bot_msg.message_id
        
        await state.set_state()
        
    elif message.text == "Back":
        log.info(f"User: {message.from_user.id} enter Back")
        choose_validators.clear()
        
        bot_msg = await message.answer(f"Maybe you want to choose another network?\nChoose a network ↓", 
                                                reply_markup=await inl_menu())
        
        data[user_id]["bot_msg_id"] = bot_msg.message_id
        
        await message.delete()
        await bot.delete_message(message_id=bot_msg_id, chat_id=message.from_user.id)
        
        
        
        await state.set_state()
    
    elif message.text == "Clear All":
        log.info(f"User: {message.from_user.id} want to delete all with buffer")
        choose_validators.clear()

        await message.delete()
        bot_msg = await message.answer(f"Choose validators: {*choose_validators,}", reply_markup=await validators_reply(validators=validators, get_list=choose_validators))
        await bot.delete_message(message_id=bot_msg_id, chat_id=message.from_user.id)
        data[user_id]["bot_msg_id"] = bot_msg.message_id
        


    elif moniker in list(validators.keys()) and moniker not in choose_validators:
        log.info(f"User: {message.from_user.id} want to add new moniker {message.text} to buffer")
        
        choose_validators.append(moniker)

        await message.delete()
        bot_msg = await message.answer(f"Choose validators: {*choose_validators,}", reply_markup=await validators_reply(validators=validators, get_list=choose_validators))
        await bot.delete_message(message_id=bot_msg_id, chat_id=message.from_user.id)
        data[user_id]["bot_msg_id"] = bot_msg.message_id
        log.info(f"bot_msg_id: {bot_msg.message_id}")

    elif moniker in choose_validators:
        log.info(f"User: {message.from_user.id} want to delete new moniker {message.text} with buffer")
        choose_validators.remove(moniker)

        await message.delete()
        bot_msg = await message.answer(f"Choose validators: {*choose_validators,}", reply_markup=await validators_reply(validators=validators, get_list=choose_validators))
        await bot.delete_message(message_id=bot_msg_id, chat_id=message.from_user.id)
        data[user_id]["bot_msg_id"] = bot_msg.message_id

    await state.update_data(data)


@user_router.callback_query(Text(text_startswith='menu&'))
async def Menu(callback: CallbackQuery, state: FSMContext, bot: Bot):
    log.info("Function Menu")
    data = await state.get_data()
    user_id = str(callback.from_user.id)
    
    data[user_id]['buffer_validator'] = []
    data[user_id]['network'] = None

    await callback.message.delete()
    bot_msg = await callback.message.answer(f"{callback.from_user.first_name}, Perhaps you'd like to monitor validators in other networks as well?", 
                                   reply_markup=await inl_menu())
    data[user_id]["bot_msg_id"] = bot_msg.message_id

    await state.update_data(data)