# console.py

class Console:
    def __init__(self, name: str, launch_year: int, price: float,
                 hardware_power: float, library_size: int,
                 library_quality: float, marketing_budget: float,
                 color: tuple, spec_info: dict = None, is_player: bool = False):
        self.name = name
        self.launch_year = launch_year
        self.launch_month = 1
        self.price = price  # Текущая розничная цена ($), может изменяться на лету
        self.original_price = price  # Исходно установленная цена
        self.hardware_power = hardware_power
        self.library_size = library_size
        self.library_quality = library_quality
        self.marketing_budget = marketing_budget  # Больше не используется, заменено на тип рекламы
        self.marketing_type = "print"  # Тип рекламы по умолчанию ("none", "guerrilla", "print", "tv")
        self.color = color
        self.spec_info = spec_info or {}

        # Менеджмент
        self.is_player = is_player
        self.inventory = 0
        self.installed_base = 0
        self.unit_cost = self.spec_info.get("cost", price * 0.45)

        self.sales_history = {}
        self.revenue_history = {}

    def get_real_price(self, inflation_factor: float) -> float:
        return self.price / inflation_factor

    def get_real_marketing(self, inflation_factor: float) -> float:
        from config import MARKETING_TYPES
        cost = MARKETING_TYPES.get(self.marketing_type, {"cost": 0})["cost"]
        return cost / inflation_factor

    def update_library(self, games_added: int):
        self.library_size += games_added