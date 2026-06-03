# market.py

import math
from config import INFLATION_FACTORS, SEASONAL_FACTORS, HISTORICAL_EVENTS, MARKETING_TYPES
from console import Console


class Market:
    def __init__(self, difficulty_multiplier: float = 1.0):
        self.current_year = 1972
        self.current_month = 1
        self.consoles = []
        self.history = []
        self.active_event_info = None
        self.difficulty_multiplier = difficulty_multiplier

    def add_console(self, console: Console):
        self.consoles.append(console)

    def get_inflation_factor(self) -> float:
        return INFLATION_FACTORS.get(self.current_year, 2.40)

    def get_market_capacity(self) -> int:
        from config import MARKET_CAPACITY
        annual_cap = MARKET_CAPACITY.get(self.current_year, 18_000_000)
        monthly_base = int(annual_cap / 12)
        season_mod = SEASONAL_FACTORS.get(self.current_month, 1.0)
        return int(monthly_base * self.difficulty_multiplier * season_mod)

    def get_event_for_year(self, year: int):
        for event in HISTORICAL_EVENTS:
            if event["year"] == year:
                return event
        return None

    def simulate_month(self, player_reputation=None) -> dict:
        if self.current_year > 1983:
            return None

        inflation = self.get_inflation_factor()
        capacity = self.get_market_capacity()

        capacity_multiplier = 1.0
        library_weight_multiplier = 1.0
        no_buy_utility_modifier = 0.0
        quality_modifier = 0.0

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

        capacity = int(capacity * capacity_multiplier)

        active_consoles = []
        for c in self.consoles:
            if c.launch_year < self.current_year:
                active_consoles.append(c)
            elif c.launch_year == self.current_year and c.launch_month <= self.current_month:
                active_consoles.append(c)

        for console in active_consoles:
            new_games = max(1, int(console.hardware_power * 0.03))
            console.update_library(new_games)
            if quality_modifier != 0.0:
                console.library_quality = max(0.1, min(1.0, console.library_quality + (quality_modifier / 12.0)))

        if not active_consoles:
            self._record_step(0, {}, capacity)
            self._advance_date()
            return {}

        max_power = max(c.hardware_power for c in active_consoles)

        utilities = {}
        total_utility = 0.0
        no_buy_utility = max(2.0, 10.0 + no_buy_utility_modifier)

        for console in active_consoles:
            # Ценовая война: если текущая цена ниже исходной, повышается ценовая лояльность
            real_price = console.get_real_price(inflation)
            price_factor = math.exp(-0.0075 * real_price)

            power_ratio = console.hardware_power / max_power
            tech_factor = math.log1p(console.hardware_power) * math.sqrt(power_ratio)

            library_factor = math.log1p(console.library_size) * console.library_quality * library_weight_multiplier

            # Динамический маркетинг
            m_type = getattr(console, "marketing_type", "print")
            m_info = MARKETING_TYPES.get(m_type, MARKETING_TYPES["none"])
            real_marketing = m_info["cost"] / inflation
            marketing_factor = math.log1p((real_marketing * m_info["multiplier"]) / 3000.0)

            utility = (tech_factor * 2.0 + library_factor * 2.5 + marketing_factor * 1.5) * price_factor

            if console.is_player and player_reputation:
                utility *= player_reputation.get_market_multiplier()

            utility = max(0.01, utility)
            utilities[console] = utility
            total_utility += utility

        total_pool = total_utility + no_buy_utility
        monthly_sales = {}
        total_sold = 0

        # Пополнение ИИ
        for console in active_consoles:
            if not console.is_player:
                if console.inventory < capacity * 0.2:
                    console.inventory += int(capacity * 0.3)

        for console in active_consoles:
            share = utilities[console] / total_pool
            demand = int(capacity * share)

            actual_sales = min(demand, console.inventory)
            console.inventory -= actual_sales
            console.installed_base += actual_sales

            time_key = f"{self.current_year}_{self.current_month}"
            console.sales_history[time_key] = actual_sales
            console.revenue_history[time_key] = actual_sales * console.price

            monthly_sales[console] = actual_sales
            total_sold += actual_sales

        self._record_step(total_sold, {c.name: sales for c, sales in monthly_sales.items()}, capacity)
        self._advance_date()
        return monthly_sales

    def _advance_date(self):
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1

    def _record_step(self, total_sold: int, console_sales: dict, actual_capacity: int):
        self.history.append({
            "year": self.current_year,
            "month": self.current_month,
            "capacity": actual_capacity,
            "inflation": self.get_inflation_factor(),
            "total_sold": total_sold,
            "console_sales": console_sales
        })