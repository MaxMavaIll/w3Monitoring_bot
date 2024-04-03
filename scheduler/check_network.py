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
        validator_addr = validator['operator_address']

        if validator_addr in users_data:
            commission_now = validator['commission']['commission_rates']['rate']
            status_now = validator['status']
            jailed_now = validator['jailed']
            status_old = users_data[validator_addr]['info']['status']
            commission_old = users_data[validator_addr]['info']['commission']

            if status_now != status_old:
                
                if jailed_now == True:
                    log.info(f"Jailed: {jailed_now}")

                    await send_message_bot(f"Validator <b>{users_data[validator_addr]['info']['moniker']}</b> landed in jail"
                                           f"\n<b>{network.title()}</b>:"
                                           f"\n    val_addr: <code>{validator_addr}</code>"
                                           f"\n    jailed: <b>{jailed_now}</b>"
                                           f"\n    status: <b>{status_now}</b>", 
                                           [ids['user_id'] for ids in users_data[validator_addr]['user_ids'] ])
                    
                else:
                    
                    await send_message_bot(f"Validator <b>{users_data[validator_addr]['info']['moniker']}</b> received a new status"
                                           f"\n<b>{network.title()}</b>:"
                                           f"\n    val_addr: <code>{validator_addr}</code>"
                                           f"\n    jailed: <b>{jailed_now}</b>"
                                           f"\n    status: <b>{status_now}</b>", 
                                           [ids['user_id'] for ids in users_data[validator_addr]['user_ids'] ])
                
                users_data[validator_addr]['info']['status'] = status_now
                users_data[validator_addr]['info']['jailed'] = jailed_now
                changed_validators.append(validator_addr)
            
            if commission_now != commission_old:
                await send_message_bot(f"Validator <b>{users_data[validator_addr]['info']['moniker']}</b> changed the commission"
                                           f"\n<b>{network.title()}</b>:"
                                           f"\n    val_addr: <code>{validator_addr}</code>"
                                           f"\n    commission: <b>{int(float(commission_old) * 100)}% -> {int(float(commission_now) * 100)}</b>% ",
                                           [ids['user_id'] for ids in users_data[validator_addr]['user_ids'] ])

                users_data[validator_addr]['info']['commission'] = commission_now
                changed_validators.append(validator_addr)

    return changed_validators


async def main():
    while True:
        
        keys = get_keys_redis()
        data = get_data_with_keys(keys=keys)

        for network in data:
            try: 
                validators_data = await get_validators_all(network)
            
                changed_validators = await check_validators_status(validators_data=validators_data,
                                                                users_data=data[network], 
                                                                network=network)
            
                log.info(f"List changed validators: {changed_validators}")

                if changed_validators:
                    log.info("Data update redis")
                    update_data(update_data=data[network], network=network, changed_validators=changed_validators)
                    
            except:
                log.exception(f"Network {network}:")

        log.info(f"Sleep {config['time_sleep']} min")
        time.sleep(config["time_sleep"] * 60)

if __name__ == "__main__":
    asyncio.run(main())