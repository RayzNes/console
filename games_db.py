# games_db.py

class GameLicense:
    def __init__(self, name: str, year_available: int, min_power: float,
                 base_royalty: float, license_cost: float, desc: str):
        self.name = name
        self.year_available = year_available
        self.min_power = min_power  # Мин. мощность консоли для запуска
        self.base_royalty = base_royalty  # Добавляется к роялти-ставке консоли (+$,$)
        self.license_cost = license_cost  # Цена выкупа лицензии
        self.desc = desc
        self.acquired_by = None  # 'player' или 'AI_Name'


def get_historical_games():
    """Каталог игр эпохи 1972-1977 гг."""
    return [
        # 1972
        GameLicense("Table Tennis", 1972, 1.0, 0.02, 15000.0, "Прообраз Pong. Запустится на простейшей логике."),
        GameLicense("Shooting Gallery", 1972, 2.0, 0.03, 20000.0, "Требует световой пистолет и чуть больше логики."),
        GameLicense("Submarines", 1972, 1.0, 0.02, 12000.0, "Простая тактическая игра с низкой ценой адаптации."),

        # 1973
        GameLicense("Pong (Atari)", 1973, 2.0, 0.06, 50000.0,
                    "Главный хит года. Гарантирует сильный взлет продаж железа!"),
        GameLicense("Space Race", 1973, 2.0, 0.03, 22000.0, "Первая игра про космос. Привлекает подростков."),
        GameLicense("Gotcha", 1973, 3.0, 0.04, 30000.0, "Первый лабиринт. Требует видеопамяти под отрисовку стен."),

        # 1974
        GameLicense("Gran Trak 10", 1974, 4.0, 0.05, 45000.0, "Первая гонка. На слабом чипе превратится в слайд-шоу."),
        GameLicense("Tank (Kee Games)", 1974, 3.0, 0.04, 35000.0,
                    "Хит для двоих игроков. Высокий интерес покупателей."),
        GameLicense("Sprakz", 1974, 2.0, 0.03, 18000.0, "Простой космический проект по недорогой лицензии."),

        # 1975
        GameLicense("Gun Fight (Intel 8080)", 1975, 6.0, 0.06, 60000.0,
                    "На жесткой логике без процессора адаптация стоит x2!"),
        GameLicense("Steeplechase", 1975, 4.0, 0.03, 25000.0, "Симулятор скачек, крайне популярный в США."),
        GameLicense("Shark Jaws", 1975, 5.0, 0.05, 40000.0, "Хайп на теме фильма 'Челюсти'. Высокие продажи."),

        # 1976
        GameLicense("Death Race", 1976, 5.0, 0.04, 35000.0, "Скандальный проект. Бесплатный черный пиар."),
        GameLicense("Breakout (Woz/Jobs)", 1976, 6.0, 0.07, 75000.0, "Развитие идеи Pong от легендарных инженеров."),
        GameLicense("Heavyweight Champ", 1976, 6.0, 0.05, 45000.0, "Первый бокс. Слабое железо размоет лица боксеров."),

        # 1977
        GameLicense("Space Wars", 1977, 10.0, 0.08, 90000.0, "Первая векторная графика. Сожрет ресурсы процессора."),
        GameLicense("Combat", 1977, 8.0, 0.07, 80000.0, "Главный хит для зарождающихся картриджных систем."),
        GameLicense("Circus", 1977, 7.0, 0.05, 50000.0, "Прыжки на батуте. Легко продается, понятна детям.")
    ]