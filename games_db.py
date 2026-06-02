# games_db.py

class GameLicense:
    def __init__(self, name: str, year_available: int, min_power: float,
                 base_royalty: float, license_cost: float, desc: str):
        self.name = name
        self.year_available = year_available
        self.min_power = min_power  # Мин. мощность консоли
        self.base_royalty = base_royalty  # Буст роялти-ставки
        self.license_cost = license_cost  # Стоимость лицензии
        self.desc = desc
        self.acquired_by = None  # 'player' или имя консоли


def get_historical_games():
    """Справочник игр до 1977 года"""
    return [
        GameLicense("Table Tennis", 1972, 1.0, 0.02, 12000.0, "Первая в мире коммерческая видеоигра. Базовый интерес."),
        GameLicense("Shooting Gallery", 1972, 2.0, 0.03, 18000.0,
                    "Нишевый жанр, требует поддержки светового пистолета."),
        GameLicense("Submarines", 1972, 1.0, 0.02, 10000.0,
                    "Простая тактическая игра, низкая себестоимость адаптации."),

        GameLicense("Pong (Atari)", 1973, 2.0, 0.07, 45000.0,
                    "Главный хит года. Драка на аукционе, взрывает продажи железа!"),
        GameLicense("Space Race", 1973, 2.0, 0.03, 20000.0, "Первая игра про космос. Привлекает подростков."),
        GameLicense("Gotcha", 1973, 3.0, 0.04, 25000.0, "Первый лабиринт. Требует видеопамяти под отрисовку стен."),

        GameLicense("Gran Trak 10", 1974, 4.0, 0.05, 40000.0, "Первая гонка. На слабом чипе превратится в слайд-шоу."),
        GameLicense("Tank (Kee Games)", 1974, 3.0, 0.04, 30000.0,
                    "Хит для двоих игроков. Требует второго порта джойстика."),
        GameLicense("Sprakz", 1974, 2.0, 0.03, 15000.0, "Простой космический проект по недорогой лицензии."),

        GameLicense("Gun Fight", 1975, 6.0, 0.06, 55000.0, "Первая игра на базе реального процессора Intel 8080."),
        GameLicense("Steeplechase", 1975, 4.0, 0.03, 22000.0,
                    "Симулятор скачек, крайне популярный в Великобритании и США."),
        GameLicense("Shark Jaws", 1975, 5.0, 0.05, 35000.0, "Попытка сыграть на хайпе фильма 'Челюсти'."),

        GameLicense("Death Race", 1976, 5.0, 0.04, 30000.0,
                    "Первая игра, вызвавшая протесты из-за жестокости. Черный пиар."),
        GameLicense("Breakout", 1976, 6.0, 0.07, 70000.0, "Развитие идеи Pong. Бешеный спрос."),
        GameLicense("Heavyweight Champ", 1976, 6.0, 0.05, 40000.0,
                    "Первый файтинг (бокс) с использованием крупных спрайтов."),

        GameLicense("Space Wars", 1977, 10.0, 0.08, 85000.0,
                    "Первая векторная графика. Тяжело пойдет на слабом процессоре."),
        GameLicense("Combat", 1977, 8.0, 0.07, 75000.0,
                    "Главный хит для зарождающихся систем со сменными картриджами."),
        GameLicense("Circus", 1977, 7.0, 0.05, 45000.0, "Аркадная классика про прыжки на батуте. Понятна детям.")
    ]