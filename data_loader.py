# data_loader.py

import json
import os

COMPONENTS_FILE = "components.json"
EVENTS_FILE = "events.json"

def init_data_files():
    """Создает файлы данных по умолчанию, если они отсутствуют"""
    if not os.path.exists(COMPONENTS_FILE):
        components_data = {
            "cpus": [
                {"name": "Discrete Logic Gate", "year": 1972, "cost": 15.0, "power": 1.0},
                {"name": "Intel 8080", "year": 1974, "cost": 40.0, "power": 6.0},
                {"name": "MOS 6502", "year": 1975, "cost": 25.0, "power": 9.0},
                {"name": "Signetics 2650", "year": 1975, "cost": 20.0, "power": 5.0},
                {"name": "Zilog Z80", "year": 1976, "cost": 30.0, "power": 11.0},
                {"name": "GI CP1600 (16-bit)", "year": 1978, "cost": 50.0, "power": 22.0}
            ],
            "gpus": [
                {"name": "B&W RF Generator", "year": 1972, "cost": 10.0, "power": 1.0},
                {"name": "Color Sync Chip", "year": 1975, "cost": 18.0, "power": 4.0},
                {"name": "Atari TIA", "year": 1977, "cost": 22.0, "power": 10.0},
                {"name": "GI AY-3-8900 (STIC)", "year": 1979, "cost": 38.0, "power": 24.0},
                {"name": "TI TMS9918", "year": 1981, "cost": 45.0, "power": 45.0}
            ],
            "media": [
                {"name": "Built-in Board", "year": 1972, "cost": 5.0, "power_mult": 1.0},
                {"name": "Early ROM Cartridge (2KB)", "year": 1976, "cost": 12.0, "power_mult": 1.3},
                {"name": "Standard ROM Cartridge (4KB)", "year": 1977, "cost": 18.0, "power_mult": 1.6},
                {"name": "Advanced ROM Cartridge (16KB)", "year": 1981, "cost": 28.0, "power_mult": 2.4}
            ]
        }
        with open(COMPONENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(components_data, f, indent=4, ensure_ascii=False)

    if not os.path.exists(EVENTS_FILE):
        events_data = [
            {
                "year": 1972,
                "name": "Рождение индустрии",
                "desc": "Выход Magnavox Odyssey. Видеоигры официально пришли в дома простых обывателей.",
                "effect_type": "market_capacity_multiplier",
                "effect_value": 1.0
            },
            {
                "year": 1975,
                "name": "Бум домашних Pong-систем",
                "desc": "Интерес к домашним играм взлетает благодаря Pong от Atari. Базовая емкость рынка удваивается.",
                "effect_type": "market_capacity_multiplier",
                "effect_value": 2.0
            },
            {
                "year": 1977,
                "name": "Эра картриджей",
                "desc": "Появление сменных игр меняет правила игры. Важность библиотеки игр удваивается.",
                "effect_type": "library_weight_multiplier",
                "effect_value": 2.0
            },
            {
                "year": 1980,
                "name": "Лихорадка Space Invaders",
                "desc": "Безумный успех аркадных портов дома. Доля людей, отказывающихся от покупки консоли, снижается.",
                "effect_type": "no_buy_penalty",
                "effect_value": -5.0
            },
            {
                "year": 1982,
                "name": "Кризис перенасыщения",
                "desc": "Рынок забит плохими играми сторонних студий. Среднее качество библиотек снижается на 15%.",
                "effect_type": "library_quality_penalty",
                "effect_value": -0.15
            },
            {
                "year": 1983,
                "name": "Великий Крах Видеоигр 1983",
                "desc": "Крах доверия к индустрии. Емкость рынка катастрофически обваливается на 85%!",
                "effect_type": "market_capacity_multiplier",
                "effect_value": 0.15
            }
        ]
        with open(EVENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(events_data, f, indent=4, ensure_ascii=False)

def load_data():
    """Загружает файлы конфигурации в память"""
    init_data_files()
    with open(COMPONENTS_FILE, "r", encoding="utf-8") as f:
        components = json.load(f)
    with open(EVENTS_FILE, "r", encoding="utf-8") as f:
        events = json.load(f)
    return components, events