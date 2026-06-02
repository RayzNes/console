# console.py

class Console:
    def __init__(self, name: str, launch_year: int, price: float,
                 hardware_power: float, library_size: int,
                 library_quality: float, marketing_budget: float,
                 color: tuple, spec_info: dict = None):
        self.name = name
        self.launch_year = launch_year
        self.price = price                      # Номинальная цена продажи ($)
        self.hardware_power = hardware_power    # Мощность железа
        self.library_size = library_size        # Начальное кол-во игр
        self.library_quality = library_quality  # Качество игр (0.1 - 1.0)
        self.marketing_budget = marketing_budget # Номинальный маркетинг ($)
        self.color = color
        self.spec_info = spec_info or {}        # Техническая спецификация консоли (Имена чипов)

        self.sales_history = {}
        self.revenue_history = {}

    def get_real_price(self, inflation_factor: float) -> float:
        return self.price / inflation_factor

    def get_real_marketing(self, inflation_factor: float) -> float:
        return self.marketing_budget / inflation_factor

    def update_library(self, games_added: int):
        self.library_size += games_added