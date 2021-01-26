import json


class FileMgmt:
    @classmethod
    def save_json(cls, fp: str, data):
        with open(fp, mode='w', encoding='utf-8') as file:
            json.dump(data, file)

    @classmethod
    def load_json(cls, fp: str):
        with open(fp, mode='r', encoding='utf-8') as file:
            return json.load(file)
