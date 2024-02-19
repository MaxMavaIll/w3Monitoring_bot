from aiogram import Router
from tgbot.filters.for_all.filters import ChatTypeFilter
from tgbot.filters.for_all.filters import AdminFilter 


user_router = Router()
user_router.message.filter(
    ChatTypeFilter(chat_type='private')
)

user_router_admin = Router()
user_router_admin.message.filter(
    AdminFilter()
)