# tech_tree.py

class ResearchNode:
    def __init__(self, node_id, name, category, year_available, base_cost, base_months,
                 prerequisites=None, effects=None):
        self.node_id = node_id
        self.name = name
        self.category = category  # "cpu", "gpu", "memory", "manufacturing"
        self.year_available = year_available
        self.base_cost = base_cost  # общая стоимость исследования в $
        self.base_months = base_months
        self.prerequisites = prerequisites or []
        self.effects = effects or {}
        self.researched = False
        self.progress_points = 0.0


class TechTree:
    def __init__(self):
        self.nodes = self._build_tree()

    def _build_tree(self):
        nodes = {}

        # ========== CPU ВЕТКА ==========
        nodes["cpu_500khz"] = ResearchNode(
            "cpu_500khz", "500 КГц ядро", "cpu", 1970, 0, 0,
            effects={"clock_speed": 0.5, "cpu_power": 1.0}
        )
        nodes["cpu_750khz"] = ResearchNode(
            "cpu_750khz", "750 КГц ядро", "cpu", 1972, 30000, 3,
            prerequisites=["cpu_500khz"],
            effects={"clock_speed": 0.75, "cpu_power": 4.0}
        )
        nodes["cpu_1mhz"] = ResearchNode(
            "cpu_1mhz", "1 МГц ядро", "cpu", 1973, 50000, 4,
            prerequisites=["cpu_750khz"],
            effects={"clock_speed": 1.0, "cpu_power": 8.0}
        )
        nodes["cpu_3mhz"] = ResearchNode(
            "cpu_3mhz", "3 МГц ядро", "cpu", 1975, 90000, 6,
            prerequisites=["cpu_1mhz", "tech_3um"],
            effects={"clock_speed": 3.0, "cpu_power": 15.0}
        )
        nodes["cpu_7mhz"] = ResearchNode(
            "cpu_7mhz", "7 МГц ядро", "cpu", 1978, 150000, 8,
            prerequisites=["cpu_3mhz", "mem_dram"],
            effects={"clock_speed": 7.0, "cpu_power": 30.0}
        )
        nodes["cpu_10mhz"] = ResearchNode(
            "cpu_10mhz", "10 МГц ядро", "cpu", 1980, 250000, 10,
            prerequisites=["cpu_7mhz", "package_plcc"],
            effects={"clock_speed": 10.0, "cpu_power": 55.0}
        )

        # ========== GPU ВЕТКА ==========
        nodes["gpu_basic"] = ResearchNode(
            "gpu_basic", "Базовый видеочип", "gpu", 1970, 0, 0,
            effects={"gpu_power": 1.0, "sprite_limit": 4}
        )
        nodes["gpu_color"] = ResearchNode(
            "gpu_color", "Цветной видеочип", "gpu", 1975, 45000, 4,
            prerequisites=["gpu_basic"],
            effects={"gpu_power": 5.0, "sprite_limit": 8, "color_depth": 4}
        )
        nodes["gpu_sprite"] = ResearchNode(
            "gpu_sprite", "Аппаратные спрайты", "gpu", 1977, 85000, 5,
            prerequisites=["gpu_color"],
            effects={"gpu_power": 12.0, "sprite_limit": 32}
        )
        nodes["gpu_tilemap"] = ResearchNode(
            "gpu_tilemap", "Тайловая графика", "gpu", 1979, 140000, 6,
            prerequisites=["gpu_sprite"],
            effects={"gpu_power": 25.0, "tile_layers": 2}
        )
        nodes["gpu_copper"] = ResearchNode(
            "gpu_copper", "Сопроцессор дисплея", "gpu", 1982, 220000, 8,
            prerequisites=["gpu_tilemap", "package_plcc"],
            effects={"gpu_power": 50.0, "copper": True}
        )

        # ========== ПАМЯТЬ ==========
        nodes["mem_dip"] = ResearchNode(
            "mem_dip", "DIP SDRAM", "memory", 1970, 0, 0,
            effects={"memory_bandwidth": 1.0, "latency": 1.0}
        )
        nodes["mem_dram"] = ResearchNode(
            "mem_dram", "DRAM", "memory", 1976, 75000, 5,
            prerequisites=["mem_dip"],
            effects={"memory_bandwidth": 2.2, "latency": 0.8}
        )
        nodes["l1_8kb"] = ResearchNode(
            "l1_8kb", "L1 Кэш 8KB", "memory", 1970, 0, 0,
            effects={"cache_size": 8, "cpu_power_bonus": 0.0}
        )
        nodes["l1_16kb"] = ResearchNode(
            "l1_16kb", "L1 Кэш 16KB", "memory", 1975, 50000, 3,
            prerequisites=["l1_8kb"],
            effects={"cache_size": 16, "cpu_power_bonus": 5.0}
        )
        nodes["l1_32kb"] = ResearchNode(
            "l1_32kb", "L1 Кэш 32KB", "memory", 1980, 120000, 5,
            prerequisites=["l1_16kb", "tech_3um"],
            effects={"cache_size": 32, "cpu_power_bonus": 15.0}
        )

        # ========== ТЕХПРОЦЕСС (Manufacturing) ==========
        nodes["tech_10um"] = ResearchNode(
            "tech_10um", "10 μm техпроцесс", "manufacturing", 1970, 0, 0,
            effects={"transistor_density": 1.0, "cost_multiplier": 1.0}
        )
        nodes["tech_6um"] = ResearchNode(
            "tech_6um", "6 μm техпроцесс", "manufacturing", 1974, 90000, 5,
            prerequisites=["tech_10um"],
            effects={"transistor_density": 1.6, "cost_multiplier": 1.2}
        )
        nodes["tech_3um"] = ResearchNode(
            "tech_3um", "3 μm техпроцесс", "manufacturing", 1977, 180000, 7,
            prerequisites=["tech_6um"],
            effects={"transistor_density": 2.5, "cost_multiplier": 1.5}
        )
        nodes["tech_1_5um"] = ResearchNode(
            "tech_1_5um", "1.5 μm техпроцесс", "manufacturing", 1981, 280000, 9,
            prerequisites=["tech_3um"],
            effects={"transistor_density": 4.0, "cost_multiplier": 2.1}
        )

        # ========== КОРПУСА МИКРОСХЕМ ==========
        nodes["package_dip"] = ResearchNode(
            "package_dip", "DIP корпус", "manufacturing", 1970, 0, 0,
            effects={"size_reduction": 1.0, "yield_rate": 1.0}
        )
        nodes["package_dip74"] = ResearchNode(
            "package_dip74", "DIP-74 корпус", "manufacturing", 1975, 40000, 2,
            prerequisites=["package_dip"],
            effects={"size_reduction": 0.85, "yield_rate": 1.1}
        )
        nodes["package_plcc"] = ResearchNode(
            "package_plcc", "PLCC корпус", "manufacturing", 1980, 110000, 4,
            prerequisites=["package_dip74"],
            effects={"size_reduction": 0.65, "yield_rate": 1.3}
        )

        # Сразу отмечаем стартовые технологии как исследованные
        for node in nodes.values():
            if node.base_cost == 0:
                node.researched = True

        return nodes

    def get_available_research(self, current_year):
        """Возвращает узлы, доступные для изучения"""
        available = []
        for node in self.nodes.values():
            if not node.researched and node.year_available <= current_year:
                prereqs_met = all(self.nodes[p].researched for p in node.prerequisites)
                if prereqs_met:
                    available.append(node)
        return available

    def calculate_custom_cpu(self, core, cache, process, package):
        """Синтезирует CPU на основе выбранных технологий"""
        core_p = core.effects.get("cpu_power", 1.0)
        cache_p = cache.effects.get("cpu_power_bonus", 0.0) if cache else 0.0
        density = process.effects.get("transistor_density", 1.0) if process else 1.0
        yield_rate = package.effects.get("yield_rate", 1.0) if package else 1.0

        # Мощность CPU
        power = (core_p + cache_p) * density

        # Себестоимость
        base_cost = 10.0 + (core.base_cost * 0.0001) + ((cache.base_cost * 0.0001) if cache else 0.0)
        cost_mult = process.effects.get("cost_multiplier", 1.0) if process else 1.0
        size_red = package.effects.get("size_reduction", 1.0) if package else 1.0

        cost = (base_cost * cost_mult * size_red) / yield_rate
        return round(max(1.0, power), 1), round(max(3.0, cost), 1)

    def calculate_custom_gpu(self, core, memory, process, package):
        """Синтезирует GPU на основе выбранных технологий"""
        core_p = core.effects.get("gpu_power", 1.0)
        bandwidth = memory.effects.get("memory_bandwidth", 1.0) if memory else 1.0
        density = process.effects.get("transistor_density", 1.0) if process else 1.0
        yield_rate = package.effects.get("yield_rate", 1.0) if package else 1.0

        # Мощность GPU
        power = core_p * bandwidth * density

        # Себестоимость
        base_cost = 8.0 + (core.base_cost * 0.0001) + ((memory.base_cost * 0.0001) if memory else 0.0)
        cost_mult = process.effects.get("cost_multiplier", 1.0) if process else 1.0
        size_red = package.effects.get("size_reduction", 1.0) if package else 1.0

        cost = (base_cost * cost_mult * size_red) / yield_rate
        return round(max(1.0, power), 1), round(max(3.0, cost), 1)