import toml
import aiohttp
import logging as log

async def get_active_validators(
          name_network: str
    ):
    config = toml.load("config.toml")

    log.info(f"Config: {config} | {name_network}")
    url = f"{config['network'][name_network]['api']}/cosmos/staking/v1beta1/validators?status=BOND_STATUS_BONDED&pagination.limit=1000"

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
                
async def get_name_validators(
          validators_data: dict
    ) -> dict:
    rez = {}

    for validator in validators_data["validators"]:
        moniker = validator["description"]["moniker"]
        validator_addr = validator["operator_address"]
        commission = validator['commission']['commission_rates']['rate']
        status = validator['status']
        jailed = validator['jailed']

        rez[moniker] = {'val_addr':  validator_addr, 'commission': commission, 'status': status, 'jailed': jailed}
    
    return rez

def send_buffer_to_data(user_buffer: list = [], get_valAddr: dict = {},  user_network_data: dict = {}, name_network: str = None ):
    tmp = {}

    for moniker in user_buffer:
        validator_addr = get_valAddr[moniker]['val_addr']
        status = get_valAddr[moniker]['status']
        jailed = get_valAddr[moniker]['jailed']
        commission = get_valAddr[moniker]['commission']

        tmp[validator_addr] = {'status': status, 'jailed': jailed, 'moniker': moniker, 'commission': commission}

    user_network_data[name_network] = tmp