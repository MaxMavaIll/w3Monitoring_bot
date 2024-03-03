import redis
import logging
import toml
import time
import json
import aiohttp

from datetime import datetime, timedelta

from aiogram import Bot

config = toml.load('config.toml')

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

log_s = logging.StreamHandler()
log_s.setLevel(logging.INFO)
formatter2 = logging.Formatter(
    "%(name)s %(asctime)s %(levelname)s %(message)s")
log_s.setFormatter(formatter2)

log.addHandler(log_s)




TOKEN = config['Bot_Token']

def get_keys_redis() -> list:
    
    keys = []
    
    сonn_redis = redis.Redis(
        host=config['db']['DB_HOST'], 
        port=config['db']['DB_PORT'], 
        db=config['db']['DB'],
        password=config['db']['DB_PASS']
        )

    keys_list = сonn_redis.keys('*')

    log.debug(keys_list)

    for key in keys_list:
        if "data" in key.decode("utf-8"):
            keys.append(key.decode("utf-8"))

    log.info(f"Number of clients: {len(keys)}\n")


    return keys

def get_data_with_keys(keys: list) -> dict:
    сonn_redis = redis.Redis(
        host=config['db']['DB_HOST'], 
        port=config['db']['DB_PORT'], 
        db=config['db']['DB'],
        password=config['db']['DB_PASS']
        )
    
    data = dict()

    for key in keys:
        split_key = key.split(":")

        bot_id = str(split_key[1])
        chat_id = str(split_key[2])
        user_id = str(split_key[3])


        value = json.loads(сonn_redis.get(key).decode("utf-8"))
        log.info(f"{value}")
        for network in value["networks"]:
            if not data.get(network):
                    data[network] = {}

            for val_addr in value["networks"][network]:
                if not data[network].get(val_addr):
                    data[network][val_addr] = {'user_ids': []}

                data[network][val_addr]['info'] = value['networks'][network][val_addr]
                data[network][val_addr]['user_ids'].append({'bot_id': bot_id, 'chat_id': chat_id, 'user_id': user_id})
                
    log.info(f'Data: {data}')
    log.debug(value)
    return data



def update_data(update_data: dict, network: str, changed_validators: list):
    сonn_redis = redis.Redis(
        host=config['db']['DB_HOST'], 
        port=config['db']['DB_PORT'], 
        db=config['db']['DB'],
        password=config['db']['DB_PASS']
        )
    
    for changed_val_addr in changed_validators:
        for users_id in update_data[changed_val_addr]['user_ids']:
            key = (
                f"fsm:{users_id['bot_id']}" 
                f":{users_id['chat_id']}"
                f":{users_id['user_id']}:data")
            log.info(f"Get key -> {key}")
            
            updated_data = json.loads(сonn_redis.get(key))

            log.info(f"Updating status usr {users_id['user_id']}:\n"
                     f" {updated_data['networks'][network][changed_val_addr]['status']} "
                     f"-> {update_data[changed_val_addr]['info']['status']}")
            updated_data['networks'][network][changed_val_addr]['status'] = update_data[changed_val_addr]['info']['status']
            
            log.info(f"Updating jailed usr {users_id['user_id']}:\n"
                     f" {updated_data['networks'][network][changed_val_addr]['jailed']} "
                     f"-> {update_data[changed_val_addr]['info']['jailed']}")            
            updated_data['networks'][network][changed_val_addr]['jailed'] = update_data[changed_val_addr]['info']['jailed']

            
            сonn_redis.set(key, json.dumps(updated_data))
            log.info("Data updated in redis")
    

    
    


async def get_validators_all(
          name_network: str
    ):
    config = toml.load("config.toml")

    log.debug(f"Config: {config} | {name_network}")
    url = f"{config['network'][name_network]['api']}/cosmos/staking/v1beta1/validators?pagination.limit=10000"

    log.info(f"Network {name_network} -> I get validators")
    async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    log.debug(f"{name_network}  -> Success, I get 200")
                    data = await response.json()
                    return data 
                else:
                    log.error(f"{name_network}  -> Fail, I get {response.status}")
                    log.error(f"{name_network}  -> Answer with server: {await response.text()}")
                    return {}
                
async def send_message_bot(message: str, users: list):
        """
        type_bot_token | TOKEN_ERROR, TOKEN_PROPOSALS, TOKEN_SERVER, TOKEN_NODE
        """
        log.info(f"Users i will send message: {users}")

        for chat_id in users:
            log.info(f"Відправляю повідомлення -> {chat_id}")

            
            url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
            # url = url + f'/sendMessage?chat_id={chat_id}&text={message}'
            data = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, data=data) as response:

                    if response.status == 200:
                        log.info(f"Повідомлення було відправиленно успішно код {response.status}")
                        log.debug(f"Отримано через папит:\n{await response.text()}")
                        
                    else:
                        log.error(f"Повідомлення отримало код {response.status}")
                        log.error(await response.text())
                        log.debug(f"url: {url}")
                        log.debug(f"data: {data}")

                        