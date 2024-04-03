from aiogram import Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.filters import Command, Text, StateFilter
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, ContentType
from aiogram.types import ReplyKeyboardRemove


from tgbot.keyboard.user.inline import inl_menu, inl_to_menu
from tgbot.keyboard.user.reply import validators_reply

from tgbot.hendler.private.users.router import user_router
from tgbot.state.user.state import GetValidators
from tgbot.function import get_active_validators, get_name_validators, send_buffer_to_data, form_answer
#from tgbot.state.user.state import 
#from tgbot.keyboard.user.inline import 

import logging as log
import asyncio

@user_router.message(Command(commands="start"))
async def Start( message: Message, state: FSMContext):
    log.info("Function Start")

    data = await state.get_data()
    
    if not data.get('networks'):
        data['networks'] = {}

    data['buffer_validator'] = []
    data['network'] = None

    bot_msg = await message.answer(f"Hello {message.from_user.first_name}!!\nSelect a network ↓", reply_markup=await inl_menu())
    data["bot_msg_id"] = bot_msg.message_id
    log.info(f"Data: {data}")


    await state.update_data(data)
    # await state.set_state(GetValidators.get)

    
@user_router.callback_query(Text(text_startswith='network&'))
async def Choose_Network(callback: CallbackQuery, state: FSMContext, bot: Bot):
    log.info("Function Choose_Network")

    user_id = str(callback.from_user.id)
    data = await state.get_data()
    network = callback.data.split("&")[-1]
    data['network'] = network

    if not data['networks'].get(network):
        log.info(f"Add new network {user_id} | {network}")
        data['networks'][network] = {}
    
    if  data['networks'][network] != {}:
        for val_addr in data['networks'][network]:
            data['buffer_validator'].append(data['networks'][network][val_addr]['moniker'])

    choose_validators = data['buffer_validator']

    await callback.message.delete()

    bot_msg = await callback.message.answer("Wait a moment, I'm getting the data")
    validators_data = await get_active_validators(name_network=network)
    validators = await get_name_validators(validators_data=validators_data)
    await bot.delete_message(message_id=bot_msg.message_id, chat_id=callback.from_user.id)

    if validators == {}:
        bot_msg = await callback.message.answer("I didn't receive data from the API", reply_markup=await inl_to_menu())
        data["bot_msg_id"] = bot_msg.message_id
        await state.update_data(data)
        return
    
    bot_msg = await callback.message.answer(f"Select the validator you'd like to monitor.\nYou can do it by either:"
                                            f"\n  * <b>Typing the moniker of your validator</b>"
                                            f"\n  * <b>Finding it on the keyboard (active set only)</b>",
                                            reply_markup=await validators_reply(validators=validators, get_list=choose_validators))
    
    data["bot_msg_id"] = bot_msg.message_id

    await state.set_state(GetValidators.get_val)
    await state.update_data(data)
    

@user_router.message(state=GetValidators.get_val)
async def Choose_Validator(message: Message, state: FSMContext, bot: Bot):
    log.info("Function Choose_Validator")

    user_id = str(message.from_user.id)
    data = await state.get_data()
    network = data['network']
    choose_validators = data['buffer_validator']

    if '.' in message.text:
        moniker = message.text.split('. ')[1]
    else:
        moniker = message.text
    bot_msg_id = data["bot_msg_id"]

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
            message_form_answer = await form_answer(choosed_validators=choose_validators, get_valAddr=validators)
            bot_msg = await message.answer(f"Great I will monitor your validators if you are outside the active set and in jail I will let you know:\n<b>{network}</b>:{message_form_answer}",
                                        reply_markup= await inl_to_menu())

        send_buffer_to_data(choose_validators, validators, data['networks'], network)

        choose_validators.clear()
        data["bot_msg_id"] = bot_msg.message_id
        
        await state.set_state()
        
    elif message.text == "Back":
        log.info(f"User: {message.from_user.id} enter Back")
        choose_validators.clear()
        
        bot_msg = await message.answer(f"Maybe you want to choose another network?\nChoose a network ↓", 
                                                reply_markup=await inl_menu())
        
        data["bot_msg_id"] = bot_msg.message_id
        
        await message.delete()
        await bot.delete_message(message_id=bot_msg_id, chat_id=message.from_user.id)
        
        await state.set_state()
    
    elif message.text == "Clear All":
        log.info(f"User: {message.from_user.id} want to delete all with buffer")
        choose_validators.clear()

        await message.delete()
        bot_msg = await message.answer(f"Choose validators: {*choose_validators,}", reply_markup=await validators_reply(validators=validators, get_list=choose_validators))
        await bot.delete_message(message_id=bot_msg_id, chat_id=message.from_user.id)
        data["bot_msg_id"] = bot_msg.message_id
        


    elif moniker in list(validators.keys()) and moniker not in choose_validators:
        log.info(f"User: {message.from_user.id} want to add new moniker {message.text} to buffer")
        
        choose_validators.append(moniker)

        await message.delete()
        bot_msg = await message.answer(f"Choose validators: {*choose_validators,}", reply_markup=await validators_reply(validators=validators, get_list=choose_validators))
        await bot.delete_message(message_id=bot_msg_id, chat_id=message.from_user.id)
        data["bot_msg_id"] = bot_msg.message_id
        log.info(f"bot_msg_id: {bot_msg.message_id}")

    elif moniker in choose_validators:
        log.info(f"User: {message.from_user.id} want to delete new moniker {message.text} with buffer")
        choose_validators.remove(moniker)

        await message.delete()
        bot_msg = await message.answer(f"Choose validators: {*choose_validators,}", reply_markup=await validators_reply(validators=validators, get_list=choose_validators))
        await bot.delete_message(message_id=bot_msg_id, chat_id=message.from_user.id)
        data["bot_msg_id"] = bot_msg.message_id

    else:
        await bot.delete_message(message_id=bot_msg_id, chat_id=message.from_user.id)
        await message.delete()
        bot_msg = await message.answer(f"I did not find this validator, please try again")
        await asyncio.sleep(1)
        await bot.delete_message(message_id=bot_msg.message_id, chat_id=message.from_user.id)
        bot_msg = await message.answer(f"Choose validators: {*choose_validators,}", reply_markup=await validators_reply(validators=validators, get_list=choose_validators))
        data["bot_msg_id"] = bot_msg.message_id

    await state.update_data(data)


@user_router.callback_query(Text(text_startswith='menu&'))
async def Menu(callback: CallbackQuery, state: FSMContext, bot: Bot):
    log.info("Function Menu")
    data = await state.get_data()
    user_id = str(callback.from_user.id)
    
    data['buffer_validator'] = []
    data['network'] = None

    await callback.message.delete()
    bot_msg = await callback.message.answer(f"{callback.from_user.first_name}, Perhaps you'd like to monitor validators in other networks as well?", 
                                   reply_markup=await inl_menu())
    data["bot_msg_id"] = bot_msg.message_id

    await state.update_data(data)