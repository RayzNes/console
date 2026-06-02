# player.py

from tech_tree import TechTree

class CustomChipProject:
    """Проект разработки собственного чипа (CPU или GPU) в R&D"""
    def __init__(self, name: str, category: str, power: float, cost: float, rd_cost: float, dev_months: int):
        self.name = name
        self.category = category
        self.power = power
        self.cost = cost
        self.rd_cost = rd_cost
        self.dev_months = dev_months
        self.progress = 0.0

    def advance(self, engineer_points: float):
        self.progress += engineer_points


class FirstPartyGameProject:
    """Проект собственной игры во время R&D консоли"""
    def __init__(self, name: str, cost: float, dev_months: int):
        self.name = name
        self.cost = cost
        self.dev_months = dev_months
        self.progress = 0.0

    def advance(self, engineer_points: float):
        self.progress += engineer_points


class PortingProject:
    """Проект портирования сторонней игры на конкретную консоль"""
    def __init__(self, game, console, double_cost: bool):
        self.game = game
        self.console = console
        self.double_cost = double_cost
        self.months_left = 2


class BrandReputation:
    def __init__(self):
        self.quality_perception = 0.5
        self.innovation_score = 0.5
        self.customer_loyalty = 0.3

    def update(self, console_quality: float, marketing_spend: float, shortage_ratio: float):
        self.quality_perception = max(0.1, min(1.0, self.quality_perception * 0.95 + console_quality * 0.05))
        marketing_bonus = min(0.02, marketing_spend / 1_000_000.0)
        self.innovation_score = max(0.1, min(1.0, self.innovation_score * 0.98 + marketing_bonus))
        loyalty_penalty = 0.1 * shortage_ratio
        self.customer_loyalty = max(0.1, min(1.0, self.customer_loyalty * 0.97 + (0.01 - loyalty_penalty)))

    def get_market_multiplier(self) -> float:
        return 1.0 + (self.quality_perception * 0.2) + (self.customer_loyalty * 0.15)


class ConsoleProject:
    def __init__(self, name: str, cpu: dict, gpu: dict, media: dict, margin: float):
        self.name = name
        self.cpu = cpu
        self.gpu = gpu
        self.media = media
        self.margin = margin

        floppy_overhead = 80.0 if "Floppy" in media["name"] else 0.0
        self.unit_cost = cpu["cost"] + gpu["cost"] + media["cost"] + floppy_overhead
        self.retail_price = int(self.unit_cost * margin)
        self.hardware_power = (cpu["power"] + gpu["power"]) * media["power_mult"]

        self.phase = "design"
        self.progress = 0.0
        self.quality = 0.50
        self.phase_thresholds = {
            "design": 30.0,
            "prototype": 70.0,
            "testing": 100.0
        }

    def advance_development(self, engineer_points: float):
        self.progress += engineer_points * 0.5
        if self.phase == "design" and self.progress >= self.phase_thresholds["design"]:
            self.phase = "prototype"
            self.quality = 0.65
        elif self.phase == "prototype" and self.progress >= self.phase_thresholds["prototype"]:
            self.phase = "testing"
            self.quality = 0.80
        elif self.phase == "testing" and self.progress >= self.phase_thresholds["testing"]:
            self.phase = "ready"
            self.quality = 0.95
        self.progress = min(100.0, self.progress)


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

        self.bankruptcy_months = 0
        self.reputation = BrandReputation()

        # Режим ручного ввода клавиатуры для кастомизации названий
        self.naming_mode = None  # None, "chip", "console"
        self.input_buffer = ""

        self.active_chip_project = None
        self.active_game_projects = []
        self.active_ports = []
        self.licensed_games = []

        self.licensed_cpus = []
        self.licensed_gpus = []

        self.custom_cpus = []
        self.custom_gpus = []

        self.notifications = []
        self.tech_tree = TechTree()
        self.active_research = None

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

    def add_notification(self, text: str):
        self.notifications.append([text, 240])

    def update_notifications(self):
        self.notifications = [[text, f - 1] for text, f in self.notifications if f > 1]

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
        if not self.active_research:
            return 0.0

        node = self.active_research
        points_generated = self.engineers * 4.0 * self.diff_settings["research_speed_multiplier"]
        total_points_needed = max(10, node.base_months * 10)
        monthly_cost = node.base_cost / node.base_months if node.base_months > 0 else 0.0

        node.progress_points += points_generated
        percent = (node.progress_points / total_points_needed) * 100.0
        if percent >= 100.0:
            node.researched = True
            self.add_notification(f"ИССЛЕДОВАНО: {node.name}")
            self.active_research = None

        return monthly_cost