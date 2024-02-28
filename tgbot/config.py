
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
    port: str
    database: str
    def dsn(self):
        return f"redis://:{self.password}@{self.host}:{self.port}/{self.database}"

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
            database=config["db"]["DB"],
            port=config["db"]["DB_PORT"],
            password=config["db"]["DB_PASS"]
        ),
        misc=Miscellaneus()
    )