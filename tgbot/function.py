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
        rez[validator["description"]["moniker"]] = validator["operator_address"]
    
    return rez

def send_buffer_to_data(user_buffer: list = [], user_network_data: dict = {}, name_network: str = None ):
    tmp = {}

    for moniker in user_buffer:
        tmp[moniker] = {'status': 'BOND_STATUS_BONDED', 'jailed': False}

    user_network_data[name_network] = tmp