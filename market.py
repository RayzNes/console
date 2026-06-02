# market.py

import math
from config import INFLATION_FACTORS, MARKET_CAPACITY
from console import Console

class Market:
    def __init__(self, events_db: list):
        self.current_year = 1972
        self.consoles = []
        self.history = []
        self.events_db = events_db
        self.active_event_info = None

    def add_console(self, console: Console):
        self.consoles.append(console)

    def get_inflation_factor(self) -> float:
        return INFLATION_FACTORS.get(self.current_year, 2.40)

    def get_market_capacity(self) -> int:
        return MARKET_CAPACITY.get(self.current_year, 18_000_000)

    def get_event_for_year(self, year: int):
        """Находит событие текущего года"""
        for event in self.events_db:
            if event["year"] == year:
                return event
        return None

    def simulate_year(self) -> dict:
        if self.current_year > 1983:
            return None

        inflation = self.get_inflation_factor()
        base_capacity = self.get_market_capacity()

        # Настройки по умолчанию, которые могут измениться под влиянием событий
        capacity_multiplier = 1.0
        library_weight_multiplier = 1.0
        no_buy_utility_modifier = 0.0
        quality_modifier = 0.0

        # Считываем и применяем эффекты текущих событий
        current_event = self.get_event_for_year(self.current_year)
        if current_event:
            self.active_event_info = current_event
            eff_type = current_event.get("effect_type")
            eff_val = current_event.get("effect_value", 0.0)

            if eff_type == "market_capacity_multiplier":
                capacity_multiplier = eff_val
            elif eff_type == "library_weight_multiplier":
                library_weight_multiplier = eff_val
            elif eff_type == "no_buy_penalty":
                no_buy_utility_modifier = eff_val
            elif eff_type == "library_quality_penalty":
                quality_modifier = eff_val
        else:
            self.active_event_info = None

        # Финальная емкость рынка с учетом событий
        capacity = int(base_capacity * capacity_multiplier)

        active_consoles = [c for c in self.consoles if c.launch_year <= self.current_year]

        # Обновление библиотек игр на рынке
        for console in active_consoles:
            new_games = max(3, int(console.hardware_power * 0.3))
            console.update_library(new_games)
            if quality_modifier != 0.0:
                # Влияние кризисов на качество библиотек (например, наплыв дешевого софта в 1982)
                console.library_quality = max(0.1, min(1.0, console.library_quality + quality_modifier))

        if not active_consoles:
            self._record_step(0, {}, capacity)
            self.current_year += 1
            return {}

        max_power = max(c.hardware_power for c in active_consoles)

        utilities = {}
        total_utility = 0.0
        # Модифицируемая полезность отказа от покупки
        no_buy_utility = max(2.0, 10.0 + no_buy_utility_modifier)

        for console in active_consoles:
            # 1. Цена с учетом инфляции
            real_price = console.get_real_price(inflation)
            price_factor = math.exp(-0.0075 * real_price)

            # 2. Мощность железа с учетом технологического отставания
            power_ratio = console.hardware_power / max_power
            tech_factor = math.log1p(console.hardware_power) * math.sqrt(power_ratio)

            # 3. Игровая библиотека (коэффициент масштабируется макро-событиями картриджей)
            library_factor = math.log1p(console.library_size) * console.library_quality * library_weight_multiplier

            # 4. Реклама
            real_marketing = console.get_real_marketing(inflation)
            marketing_factor = math.log1p(real_marketing / 8000.0)

            # Расчет привлекательности
            utility = (tech_factor * 2.0 + library_factor * 2.5 + marketing_factor * 1.0) * price_factor
            utility = max(0.01, utility)

            utilities[console] = utility
            total_utility += utility

        total_pool = total_utility + no_buy_utility
        yearly_sales = {}
        total_sold = 0

        for console in active_consoles:
            share = utilities[console] / total_pool
            sales = int(capacity * share)

            console.sales_history[self.current_year] = sales
            console.revenue_history[self.current_year] = sales * console.price
            yearly_sales[console] = sales
            total_sold += sales

        self._record_step(total_sold, {c.name: sales for c, sales in yearly_sales.items()}, capacity)
        self.current_year += 1
        return yearly_sales

    def _record_step(self, total_sold: int, console_sales: dict, actual_capacity: int):
        self.history.append({
            "Год": self.current_year,
            "capacity": actual_capacity,
            "inflation": self.get_inflation_factor(),
            "total_sold": total_sold,
            "console_sales": console_sales
        })