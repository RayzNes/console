# console.py

class Console:
    def __init__(self, name: str, launch_year: int, price: float,
                 hardware_power: float, library_size: int,
                 library_quality: float, marketing_budget: float,
                 color: tuple, spec_info: dict = None, is_player: bool = False):
        self.name = name
        self.launch_year = launch_year
        self.launch_month = 1  # Месяц старта продаж (1-12)
        self.price = price  # Розничная цена ($)
        self.hardware_power = hardware_power  # Индекс мощности
        self.library_size = library_size  # Размер библиотеки игр
        self.library_quality = library_quality  # Среднее качество игр
        self.marketing_budget = marketing_budget  # Ежемесячный (!) бюджет на рекламу
        self.color = color
        self.spec_info = spec_info or {}

        # Новые поля Менеджмента (Stage 3)
        self.is_player = is_player
        self.inventory = 0  # Готовая продукция на складе
        self.installed_base = 0  # Установленная база у игроков
        self.unit_cost = self.spec_info.get("cost", price * 0.45)  # Себестоимость

        self.sales_history = {}  # Будет хранить историю в формате "ГОД_МЕСЯЦ"
        self.revenue_history = {}

    def get_real_price(self, inflation_factor: float) -> float:
        return self.price / inflation_factor

    def get_real_marketing(self, inflation_factor: float) -> float:
        return self.marketing_budget / inflation_factor

    def update_library(self, games_added: int):
        self.library_size += games_added