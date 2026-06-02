# ai_competitor.py

from config import HISTORICAL_CPUS, HISTORICAL_GPUS, HISTORICAL_MEDIA
from console import Console


class AICompany:
    def __init__(self, name: str, strategy: str, launch_year: int, color: tuple):
        self.name = name
        self.strategy = strategy
        self.launch_year = launch_year
        self.color = color
        self.launched = False
        self.active_console = None

    def design_console(self, current_month: int) -> Console:
        cpus = [c for c in HISTORICAL_CPUS if c["year"] <= self.launch_year]
        gpus = [g for g in HISTORICAL_GPUS if g["year"] <= self.launch_year]
        media = [m for m in HISTORICAL_MEDIA if m["year"] <= self.launch_year]

        if not cpus: cpus = [HISTORICAL_CPUS[0]]
        if not gpus: gpus = [HISTORICAL_GPUS[0]]
        if not media: media = [HISTORICAL_MEDIA[0]]

        if self.strategy == "budget":
            cpu = min(cpus, key=lambda x: x["cost"])
            gpu = min(gpus, key=lambda x: x["cost"])
            med = min(media, key=lambda x: x["cost"])
            margin = 1.25
            marketing = 75_000
            start_games = 4
            quality = 0.50
        elif self.strategy == "premium":
            cpu = max(cpus, key=lambda x: x["power"])
            gpu = max(gpus, key=lambda x: x["power"])
            med = max(media, key=lambda x: x["power_mult"])
            margin = 1.70
            marketing = 500_000
            start_games = 10
            quality = 0.85
        else:
            sorted_cpus = sorted(cpus, key=lambda x: x["power"])
            cpu = sorted_cpus[len(sorted_cpus) // 2] if sorted_cpus else cpus[0]

            sorted_gpus = sorted(gpus, key=lambda x: x["power"])
            gpu = sorted_gpus[len(sorted_gpus) // 2] if sorted_gpus else gpus[0]

            sorted_media = sorted(media, key=lambda x: x["power_mult"])
            med = sorted_media[len(sorted_media) // 2] if sorted_media else media[0]

            margin = 1.45
            marketing = 250_000
            start_games = 7
            quality = 0.70

        unit_cost = cpu["cost"] + gpu["cost"] + med["cost"]
        retail_price = int(unit_cost * margin)
        hardware_power = (cpu["power"] + gpu["power"]) * med["power_mult"]

        spec_info = {
            "cpu_name": cpu["name"],
            "gpu_name": gpu["name"],
            "media_name": med["name"],
            "cost": unit_cost,
            "is_programmable": med["is_programmable"]
        }

        self.launched = True
        console = Console(
            name=f"{self.name} System",
            launch_year=self.launch_year,
            price=retail_price,
            hardware_power=hardware_power,
            library_size=start_games,
            library_quality=quality,
            marketing_budget=marketing,
            color=self.color,
            spec_info=spec_info
        )
        # Передаем реальный динамический месяц запуска [7]
        console.launch_month = current_month
        self.active_console = console
        return console