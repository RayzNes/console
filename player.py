# player.py

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
        """Прогресс проекта в зависимости от усилий инженеров"""
        if self.phase == "design":
            self.progress += engineer_points * 0.8  # Проектирование идет быстро
            if self.progress >= 100.0:
                self.phase = "prototype"
                self.progress = 0.0
        elif self.phase == "prototype":
            self.progress += engineer_points * 0.5  # Отладка прототипа и плат
            if self.progress >= 100.0:
                self.phase = "testing"
                self.progress = 0.0
        elif self.phase == "testing":
            # На этапе тестирования полируется качество ПО и игр
            self.progress += engineer_points * 0.3
            self.quality = min(1.0, self.quality + 0.02)
            if self.progress >= 100.0:
                self.phase = "ready"
                self.progress = 100.0


class PlayerCompany:
    def __init__(self, name: str, start_cash: float):
        self.name = name
        self.cash = start_cash

        # Штат инженеров R&D
        self.engineers = 5
        self.engineer_salary = 1500.0  # Зарплата одного инженера в месяц

        # Активная разработка
        self.active_project = None
        self.released_consoles = []

        # Заказы на производство (очередь поставок с фабрик)
        # Хранит кортежи: {"months_left": int, "quantity": int, "unit_cost": float}
        self.production_orders = []

        # Финансовый отчет за прошедший месяц
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
        """Обрабатывает поставки готовых партий кремниевых пластин/консолей"""
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