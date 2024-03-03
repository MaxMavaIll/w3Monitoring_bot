import asyncio
import toml
import time
import logging 
import aiohttp

from function import *

config = toml.load('config.toml')

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

log_s = logging.StreamHandler()
log_s.setLevel(logging.INFO)
formatter2 = logging.Formatter(
    "%(name)s %(asctime)s %(levelname)s %(message)s")
log_s.setFormatter(formatter2)

log.addHandler(log_s)

async def check_validators_status(validators_data: dict, users_data: dict, network: str):
    changed_validators = list()
    
    for validator in validators_data['validators']:
        if validator['operator_address'] in users_data:

            if validator['status'] != users_data[validator['operator_address']]['info']['status']:
                log.info(f"Jailed: {validator['jailed']}")
                
                if validator['jailed'] == True:
                    await send_message_bot(f"Validator <b>{users_data[validator['operator_address']]['info']['moniker']}</b> landed in jail"
                                           f"\n<b>{network.title()}</b>:"
                                           f"\n    val_addr: <code>{validator['operator_address']}</code>"
                                           f"\n    jailed: <b>{validator['jailed']}</b>"
                                           f"\n    status: <b>{validator['status']}</b>", 
                                           [ids['user_id'] for ids in users_data[validator['operator_address']]['user_ids'] ])
                    
                else:
                    
                    await send_message_bot(f"Validator <b>{users_data[validator['operator_address']]['info']['moniker']}</b> received a new status"
                                           f"\n<b>{network.title()}</b>:"
                                           f"\n    val_addr: <code>{validator['operator_address']}</code>"
                                           f"\n    jailed: <b>{validator['jailed']}</b>"
                                           f"\n    status: <b>{validator['status']}</b>", 
                                           [ids['user_id'] for ids in users_data[validator['operator_address']]['user_ids'] ])
                
                users_data[validator['operator_address']]['info']['status'] = validator['status']
                users_data[validator['operator_address']]['info']['jailed'] = validator['jailed']
                changed_validators.append(validator['operator_address'])
                continue

            log.info(f"Status {users_data[validator['operator_address']]['info']['status']} не був змінений")

    return changed_validators


async def main():
    while True:
        
        keys = get_keys_redis()
        data = get_data_with_keys(keys=keys)

        # tasks = [ network for network in data]
        # await asyncio.gather(*tasks)
        for network in data:
            try: 
                validators_data = await get_validators_all(network)
            
            # log.info(f"Data: {data[network]}")
                changed_validators = await check_validators_status(validators_data=validators_data, users_data=data[network], network=network)
            
                log.info(f"Data: {changed_validators}")

                if changed_validators:
                    log.info("Data update redis")
                    update_data(update_data=data[network], network=network, changed_validators=changed_validators)
            except aiohttp.client_exceptions.ClientConnectorError:
                log.exception(f"Network {network}:")

        log.info(f"Sleep {config['time_sleep']} min")
        time.sleep(config["time_sleep"] * 60)

if __name__ == "__main__":
    asyncio.run(main())