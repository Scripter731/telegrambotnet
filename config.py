import json
from pathlib import Path

CONFIG_PATH = Path("config.json")

def load_config():

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Файл конфигурации {CONFIG_PATH} не найден.")

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        config = json.load(file)

    required_keys = ["BOT_TOKEN", "API_ID", "API_HASH"]
    for key in required_keys:
        if key not in config:
            raise KeyError(f"В конфигурации отсутствует обязательный параметр: {key}")

    return config

try:
    config = load_config()
    BOT_TOKEN = config["BOT_TOKEN"]
    API_ID = config["API_ID"]
    API_HASH = config["API_HASH"]
    PROXIES = config.get("proxies", [])  # Proxy (if u want)
except Exception as e:
    print(f"Ошибка при загрузке конфигурации: {e}")
    raise