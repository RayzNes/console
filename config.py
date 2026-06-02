# config.py

START_YEAR = 1972
END_YEAR = 1983  # Расширено до 1983 года для демонстрации Великого Краха

# Коэффициенты инфляции (база 1972 год = 1.0)
INFLATION_FACTORS = {
    1972: 1.00, 1973: 1.06, 1974: 1.18, 1975: 1.29,
    1976: 1.36, 1977: 1.45, 1978: 1.56, 1979: 1.74,
    1980: 1.97, 1981: 2.18, 1982: 2.31, 1983: 2.40
}

# Потенциальная емкость рынка (без учета эффектов от событий)
MARKET_CAPACITY = {
    1972: 150_000,
    1973: 300_000,
    1974: 500_000,
    1975: 800_000,
    1976: 1_200_000,
    1977: 2_500_000,
    1978: 4_500_000,
    1979: 7_000_000,
    1980: 10_000_000,
    1981: 13_000_000,
    1982: 16_000_000,
    1983: 18_000_000
}

# Настройки уровней сложности
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