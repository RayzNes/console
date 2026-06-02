# ai_competitor.py

from console import Console


class AICompany:
    def __init__(self, name: str, strategy: str, launch_year: int, color: tuple):
        self.name = name
        self.strategy = strategy
        self.launch_year = launch_year
        self.color = color
        self.launched = False

    def design_console(self, components_db: dict) -> Console:
        cpus = [c for c in components_db["cpus"] if c["year"] <= self.launch_year]
        gpus = [g for g in components_db["gpus"] if g["year"] <= self.launch_year]
        media = [m for m in components_db["media"] if m["year"] <= self.launch_year]

        # Защита от пустых массивов
        if not cpus: cpus = [components_db["cpus"][0]]
        if not gpus: gpus = [components_db["gpus"][0]]
        if not media: media = [components_db["media"][0]]

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
            # Безопасный выбор медианы без деления на ноль
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
            "cost": unit_cost
        }

        self.launched = True
        return Console(
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