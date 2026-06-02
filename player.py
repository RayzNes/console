# player.py

from tech_tree import TechTree


class ConsoleProject:
    def __init__(self, name: str, cpu: dict, gpu: dict, media: dict, margin: float):
        self.name = name
        self.cpu = cpu
        self.gpu = gpu
        self.media = media
        self.margin = margin

        # Расчет базовых ТТХ
        self.unit_cost = cpu["cost"] + gpu["cost"] + media["cost"]
        self.retail_price = int(self.unit_cost * margin)
        self.hardware_power = (cpu["power"] + gpu["power"]) * media["power_mult"]

        # Фазы R&D pipeline
        self.phase = "design"  # "design" -> "prototype" -> "testing" -> "ready"
        self.progress = 0.0  # 0.0 - 100.0%
        self.quality = 0.50  # Стартовое качество софта (растет на фазе тестирования)

    def advance_development(self, engineer_points: float):
        if self.phase == "design":
            self.progress += engineer_points * 0.8
            if self.progress >= 100.0:
                self.phase = "prototype"
                self.progress = 0.0
        elif self.phase == "prototype":
            self.progress += engineer_points * 0.5
            if self.progress >= 100.0:
                self.phase = "testing"
                self.progress = 0.0
        elif self.phase == "testing":
            self.progress += engineer_points * 0.3
            self.quality = min(1.0, self.quality + 0.02)
            if self.progress >= 100.0:
                self.phase = "ready"
                self.progress = 100.0


class PlayerCompany:
    def __init__(self, name: str, difficulty: str, diff_settings: dict):
        self.name = name
        self.difficulty = difficulty
        self.cash = diff_settings["start_cash"]
        self.diff_settings = diff_settings

        self.engineers = 5
        self.engineer_salary = 1500.0

        self.active_project = None
        self.released_consoles = []
        self.production_orders = []

        # Система предупреждения банкротства
        self.bankruptcy_months = 0

        # Технологический стек игрока
        self.tech_tree = TechTree()
        self.active_research = None  # Выбранный на данный момент узел ResearchNode

        # Собственная база созданных чипов (изначально пустая)
        self.custom_cpus = []
        self.custom_gpus = []

        self.financials_last_month = {
            "hw_revenue": 0.0,
            "royalty_revenue": 0.0,
            "manufacturing_cost": 0.0,
            "rd_expenses": 0.0,
            "marketing_expenses": 0.0,
            "salaries": 0.0,
            "warehouse_cost": 0.0,
            "net_profit": 0.0
        }

    def process_monthly_logistics(self):
        arrived_units = 0
        remaining_orders = []
        for order in self.production_orders:
            order["months_left"] -= 1
            if order["months_left"] <= 0:
                arrived_units += order["quantity"]
            else:
                remaining_orders.append(order)
        self.production_orders = remaining_orders
        return arrived_units

    def get_monthly_salaries(self) -> float:
        return self.engineers * self.engineer_salary

    def advance_research(self) -> float:
        """Продвигает активное исследование. Возвращает стоимость за ход."""
        if not self.active_research:
            return 0.0

        node = self.active_research
        # Суммарная мощность очков науки
        points_generated = self.engineers * 4.0 * self.diff_settings["research_speed_multiplier"]

        # Необходимое количество очков = месяцы * 10
        total_points_needed = max(10, node.base_months * 10)

        # Ежемесячная стоимость исследования = общая стоимость / месяцы
        monthly_cost = node.base_cost / node.base_months if node.base_months > 0 else 0.0

        node.progress_points += points_generated

        # Прогресс в процентах
        percent = (node.progress_points / total_points_needed) * 100.0
        if percent >= 100.0:
            node.researched = True
            self.active_research = None

        return monthly_cost