from __future__ import annotations

class ConfigHolder:
    def __init__(self, config:Config):
        self.current = config
        self.previous = config.copy(deep)

    def __enter__(self)->ConfigHolder:
        return self

    def __exit__(self, *args):
        

class Config:
    history:dict[str, Config] = {}
