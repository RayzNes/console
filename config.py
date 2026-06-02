# config.py

START_YEAR = 1972
END_YEAR = 1983

INFLATION_FACTORS = {
    1972: 1.00, 1973: 1.06, 1974: 1.18, 1975: 1.29,
    1976: 1.36, 1977: 1.45, 1978: 1.56, 1979: 1.74,
    1980: 1.97, 1981: 2.18, 1982: 2.31, 1983: 2.40
}

MARKET_CAPACITY = {
    1972: 150_000, 1973: 300_000, 1974: 500_000, 1975: 800_000,
    1976: 1_200_000, 1977: 2_500_000, 1978: 4_500_000, 1979: 7_000_000,
    1980: 10_000_000, 1981: 13_000_000, 1982: 16_000_000, 1983: 18_000_000
}

DIFFICULTIES = {
    "easy": {
        "start_cash": 2_000_000.0,
        "demand_multiplier": 1.3,
        "research_speed_multiplier": 1.5,
        "manufacturing_cost_multiplier": 0.8
    },
    "medium": {
        "start_cash": 1_200_000.0,
        "demand_multiplier": 1.0,
        "research_speed_multiplier": 1.0,
        "manufacturing_cost_multiplier": 1.0
    },
    "hard": {
        "start_cash": 600_000.0,
        "demand_multiplier": 0.7,
        "research_speed_multiplier": 0.7,
        "manufacturing_cost_multiplier": 1.3
    }
}

PRODUCTION_LEAD_TIME = {
    "small": 1,
    "medium": 2,
    "large": 3
}

ROYALTY_RATES = {
    "weak_bargaining": 0.10,
    "normal": 0.15,
    "strong_bargaining": 0.22,
    "exclusive": 0.30
}

SEASONAL_FACTORS = {
    1: 0.6, 2: 0.7, 3: 0.8, 4: 0.9, 5: 1.0, 6: 1.1,
    7: 1.0, 8: 0.9, 9: 1.0, 10: 1.2, 11: 1.5, 12: 1.8
}

# --- ИСТОРИЧЕСКИЙ СПРАВОЧНИК КОМПЛЕКТУЮЩИХ (1972-1983) ---
HISTORICAL_CPUS = [
    {
        "id": "cpu_discrete_1972", "name": "Discrete Logic Circuit", "year": 1972,
        "power": 1.0, "cost": 15.00, "license_fee": 0,
        "desc": "Набор транзисторов. Нет программируемости, игры жестко вшиты."
    },
    {
        "id": "cpu_mos_6502_1975", "name": "MOS Technology 6502", "year": 1975,
        "power": 8.0, "cost": 25.00, "license_fee": 1500,
        "desc": "Сердце Atari 2600. Самый дешевый и эффективный процессор эпохи."
    },
    {
        "id": "cpu_zilog_z80_1976", "name": "Zilog Z80", "year": 1976,
        "power": 10.0, "cost": 40.00, "license_fee": 3000,
        "desc": "Конкурент 6502. Более сложная архитектура, дороже."
    },
    {
        "id": "cpu_intel_8086_1978", "name": "Intel 8086", "year": 1978,
        "power": 18.0, "cost": 85.00, "license_fee": 8000,
        "desc": "Мощный 16-битный монстр. Дорогой, но дает колоссальный скачок ТТХ."
    },
    {
        "id": "cpu_motorola_68000_1979", "name": "Motorola 68000", "year": 1979,
        "power": 25.0, "cost": 120.00, "license_fee": 15000,
        "desc": "Техническая элита. Основа будущей Sega Genesis."
    },
    {
        "id": "cpu_ricoh_2a03_1982", "name": "Ricoh 2A03", "year": 1982,
        "power": 15.0, "cost": 30.00, "license_fee": 5000,
        "desc": "Кастомный 6502 со встроенным звуковым чипом под NES (Famicom)."
    }
]

HISTORICAL_GPUS = [
    {
        "id": "gpu_discrete_1972", "name": "Spot Generator (Discrete)", "year": 1972,
        "power": 1.0, "cost": 10.00, "license_fee": 0,
        "desc": "Дискретная графика. Способен выводить лишь 2-3 белых квадрата."
    },
    {
        "id": "gpu_gi_ay3_1975", "name": "GI AY-3-8500", "year": 1975,
        "power": 3.0, "cost": 7.00, "license_fee": 500,
        "desc": "Чип Pong 'все-в-одном'. Генерирует графику и звук Pong-игр."
    },
    {
        "id": "gpu_atari_tia_1977", "name": "Atari TIA", "year": 1977,
        "power": 6.0, "cost": 20.00, "license_fee": 4000,
        "desc": "Супер-сложный чип, строящий изображение построчно на лету."
    },
    {
        "id": "gpu_gi_ay3_8910_1979", "name": "GI AY-3-8910", "year": 1979,
        "power": 8.0, "cost": 25.00, "license_fee": 2500,
        "desc": "Программируемый звукогенератор с базовой спрайтовой логикой."
    },
    {
        "id": "gpu_tms9918_1981", "name": "TMS9918 (Texas Instr.)", "year": 1981,
        "power": 16.0, "cost": 45.00, "license_fee": 6000,
        "desc": "Поддержка аппаратных спрайтов и 15 цветов одновременно."
    },
    {
        "id": "gpu_ricoh_ppu_1983", "name": "Ricoh PPU", "year": 1983,
        "power": 22.0, "cost": 35.00, "license_fee": 10000,
        "desc": "Вершина 8-битной графики. Плавный скроллинг во всех направлениях."
    }
]

HISTORICAL_MEDIA = [
    {
        "id": "media_built_in_1972", "name": "Printed Circuit Cards", "year": 1972,
        "power_mult": 1.0, "cost": 2.00, "license_fee": 0, "is_programmable": False,
        "desc": "Простые платы-перемычки. Не несут кода, лишь замыкают цепи."
    },
    {
        "id": "media_rom_cart_1_1976", "name": "ROM Cartridge (Gen 1)", "year": 1976,
        "power_mult": 1.3, "cost": 8.00, "license_fee": 1000, "is_programmable": True,
        "desc": "Картриджи со встроенными ПЗУ (ROM). Начало эры сменного ПО."
    },
    {
        "id": "media_cassette_1978", "name": "Magnetic Cassette", "year": 1978,
        "power_mult": 1.5, "cost": 1.50, "license_fee": 500, "is_programmable": True,
        "desc": "Дешевый носитель, медленная скорость загрузки, высокая емкость."
    },
    {
        "id": "media_rom_cart_2_1980", "name": "ROM Cartridge (Gen 2)", "year": 1980,
        "power_mult": 1.8, "cost": 12.00, "license_fee": 2000, "is_programmable": True,
        "desc": "Объем картриджей растет, позволяя делать комплексные игры."
    },
    {
        "id": "media_floppy_1982", "name": "Floppy Disk 5.25\"", "year": 1982,
        "power_mult": 2.1, "cost": 3.00, "license_fee": 3500, "is_programmable": True,
        "desc": "Огромный объем при дешевом диске, но дисковод добавляет +$80 к себестоимости."
    },
    {
        "id": "media_bank_cart_1983", "name": "Bank-Switching Cartridge", "year": 1983,
        "power_mult": 2.4, "cost": 18.00, "license_fee": 5000, "is_programmable": True,
        "desc": "Картриджи с мапперами обхода архитектурных лимитов ОЗУ."
    }
]

PRESET_NAMES = [
    "Nexus-8", "PicoEngine", "Nova-Station", "Sega-X", "Zephyr System",
    "Vortex-2000", "Aura Play", "Odyssey-Ultra", "Retro-Vector", "Horizon-8"
]

CHIP_PRESET_NAMES = [
    "Alpha-Chip", "Sledgehammer", "Razor-Z", "Blaze", "Omega-Core", "Cybertron"
]