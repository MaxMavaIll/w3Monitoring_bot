
from dataclasses import dataclass
from typing import List
import toml

@dataclass
class Tg_bot:
    token: str
    admin_ids: List[int]
    user_redis: bool

@dataclass
class DBConfig:
    host: str
    password: str
    user: str
    database: str

@dataclass
class Miscellaneus:
    other_params: str = None

@dataclass
class Config:
    tg_bot: Tg_bot
    db: DBConfig
    misc: Miscellaneus

def load_config(path_config: str = 'config.toml'):
    config = toml.load(path_config)

    return Config(
        tg_bot=Tg_bot(
            token=config["Bot_Token"],
            admin_ids=config["Admins"],
            user_redis=config["USE_REDIS"]
        ), 
        db=DBConfig(
            host=config["db"]["DB_HOST"],
            password=config["db"]["DB_PASS"],
            user=config["db"]["DB_USER"],
            database=config["db"]["DB_NAME"]
        ),
        misc=Miscellaneus()
    )