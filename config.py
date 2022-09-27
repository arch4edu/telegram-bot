import json
from pathlib import Path


class Config:
    def __init__(self, path="config.json"):
        self.path = Path(path)
        if self.path.exists():
            self.dict = json.load(open(self.path))
        else:
            self.dict = {}
            self.save()

    def get(self, chat, key):
        if not chat in self.dict:
            return None
        return None if not key in self.dict[chat] else self.dict[chat][key]

    def set(self, chat, key, value):
        if not chat in self.dict:
            self.dict[chat] = {}
        self.dict[chat][key] = value
        self.save()

    def save(self):
        json.dump(self.dict, open(self.path, "w"), sort_keys=True, indent=2)
