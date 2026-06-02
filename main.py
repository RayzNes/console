# main.py

import pygame
import sys
from config import (DIFFICULTIES, START_YEAR, END_YEAR, PRODUCTION_LEAD_TIME,
                    HISTORICAL_CPUS, HISTORICAL_GPUS, HISTORICAL_MEDIA,
                    PRESET_NAMES, CHIP_PRESET_NAMES)
from data_loader import load_data
from ai_competitor import AICompany
from market import Market
from player import PlayerCompany, ConsoleProject, CustomChipProject, FirstPartyGameProject, PortingProject
from console import Console
from games_db import get_historical_games, GameLicense
import renderer

# Настройки Pygame
pygame.init()
WIDTH, HEIGHT = 1224, 1024
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Console Tycoon: Silicon Race")
clock = pygame.time.Clock()

# Селекторы параметров R&D кастомных чипов
active_designer_type = "cpu"  # "cpu" или "gpu"
designer_core_idx = 0
designer_cache_idx = 0
designer_process_idx = 0
designer_package_idx = 0

# Текстовые переменные для имен
selected_console_name_idx = 0
selected_chip_name_idx = 0


def draw_chart(surface, x, y, w, h, market_history, consoles):
    renderer.draw_chart(surface, x, y, w, h, market_history, consoles)

def main():
    global current_tab, current_difficulty, rd_sub_tab
    global selected_cpu_idx, selected_gpu_idx, selected_media_idx, margin_value
    global active_designer_type, designer_core_idx, designer_cache_idx, designer_process_idx, designer_package_idx
    global selected_console_name_idx, selected_chip_name_idx

    # Initialize these variables before using them
    current_difficulty = None  # Add this line
    current_tab = "market"  # Add this line (or set a default)
    rd_sub_tab = "research"  # Add this line (or set a default)
    selected_cpu_idx = 0  # Add this line
    selected_gpu_idx = 0  # Add this line
    selected_media_idx = 0  # Add this line
    margin_value = 1.45  # Add this line (default margin)

    components_db, events_db = load_data()
    player = None
    market = None
    ai_companies = []
    games_list = get_historical_games()

    btn_easy = pygame.Rect(462, 350, 300, 50)
    btn_medium = pygame.Rect(462, 420, 300, 50)
    btn_hard = pygame.Rect(462, 490, 300, 50)

    auto_play = False
    auto_tick_cooldown = 0

    while True:
        # Выбор сложности
        if not current_difficulty:
            renderer.render_difficulty_screen(screen, renderer.font_large, renderer.font_title, renderer.font_body)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if btn_easy.collidepoint(event.pos):
                            current_difficulty = "easy"
                        elif btn_medium.collidepoint(event.pos):
                            current_difficulty = "medium"
                        elif btn_hard.collidepoint(event.pos):
                            current_difficulty = "hard"

                        if current_difficulty:
                            settings = DIFFICULTIES[current_difficulty]
                            player = PlayerCompany("PlayerCorp", current_difficulty, settings)
                            market = Market(events_db, settings["demand_multiplier"])

                            ai_companies = [
                                AICompany("Magnavox", "budget", 1972, (200, 200, 200)),
                                AICompany("Atari Inc.", "balanced", 1977, (230, 126, 34)),
                                AICompany("Mattel Electronics", "premium", 1979, (52, 152, 219)),
                                AICompany("Coleco Industries", "premium", 1982, (46, 204, 113))
                            ]
            continue

        if player.bankruptcy_months >= 3:
            renderer.render_bankruptcy_screen(screen, renderer.font_large, renderer.font_title)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    current_difficulty = None
                    main()
                    return
            continue

        # Запуск ИИ
        for ai in ai_companies:
            if not ai.launched and market.current_year >= ai.launch_year:
                console = ai.design_console(components_db)
                market.add_console(console)

        # Локальные селекторы имен на основе пресетов из config.py
        console_name = PRESET_NAMES[selected_console_name_idx % len(PRESET_NAMES)]
        chip_name = CHIP_PRESET_NAMES[selected_chip_name_idx % len(CHIP_PRESET_NAMES)]

        # Обработка мыши
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = event.pos

                    # Глобальные табы
                    for t_key, rect in renderer.tab_rects.items():
                        if rect.collidepoint(mouse_pos):
                            current_tab = t_key

                    # Таб: РЫНОК
                    if current_tab == "market":
                        if renderer.btn_step.collidepoint(mouse_pos):
                            simulate_one_month(market, player, components_db, games_list)
                        elif renderer.btn_auto.collidepoint(mouse_pos):
                            auto_play = not auto_play
                        elif renderer.btn_reset.collidepoint(mouse_pos):
                            current_difficulty = None
                            main()
                            return

                    # Таб: R&D (РАЗРАБОТКА)
                    elif current_tab == "rd":
                        if renderer.btn_sub_res.collidepoint(mouse_pos):
                            rd_sub_tab = "research"
                        elif renderer.btn_sub_design.collidepoint(mouse_pos):
                            rd_sub_tab = "designer"
                        elif renderer.btn_sub_console.collidepoint(mouse_pos):
                            rd_sub_tab = "console"

                        # Кадры
                        if renderer.btn_hire.collidepoint(mouse_pos):
                            player.engineers += 1
                        elif renderer.btn_fire.collidepoint(mouse_pos):
                            player.engineers = max(1, player.engineers - 1)

                        # Подтаб 1: Исследования
                        if rd_sub_tab == "research":
                            avail_nodes = player.tech_tree.get_available_research(market.current_year)
                            offset_y = 205
                            for node in avail_nodes[:10]:
                                click_rect = pygame.Rect(45, offset_y, 500, 25)
                                if click_rect.collidepoint(mouse_pos):
                                    player.active_research = node
                                offset_y += 30

                        # Подтаб 2: Конструктор чипов и Лицензирование сторонних чипов [2, 3]
                        elif rd_sub_tab == "designer":
                            if not player.active_chip_project:
                                if renderer.btn_chip_type.collidepoint(mouse_pos):
                                    active_designer_type = "gpu" if active_designer_type == "cpu" else "cpu"
                                elif renderer.btn_chip_name.collidepoint(mouse_pos):
                                    selected_chip_name_idx += 1
                                elif renderer.btn_chip_core.collidepoint(mouse_pos):
                                    designer_core_idx += 1
                                elif renderer.btn_chip_cache.collidepoint(mouse_pos):
                                    designer_cache_idx += 1
                                elif renderer.btn_chip_process.collidepoint(mouse_pos):
                                    designer_process_idx += 1
                                elif renderer.btn_chip_package.collidepoint(mouse_pos):
                                    designer_package_idx += 1

                                # Клик по сборке собственного кастомного чипа
                                elif renderer.btn_chip_build.collidepoint(mouse_pos):
                                    cores = [n for n in player.tech_tree.nodes.values() if
                                             n.category == active_designer_type and n.researched]
                                    processes = [n for n in player.tech_tree.nodes.values() if
                                                 n.category == "manufacturing" and "tech_" in n.node_id and n.researched]
                                    packages = [n for n in player.tech_tree.nodes.values() if
                                                n.category == "manufacturing" and "package_" in n.node_id and n.researched]
                                    core = cores[designer_core_idx % len(cores)] if cores else None
                                    process = processes[designer_process_idx % len(processes)] if processes else None
                                    package = packages[designer_package_idx % len(packages)] if packages else None

                                    if active_designer_type == "cpu":
                                        caches = [n for n in player.tech_tree.nodes.values() if
                                                  n.category == "memory" and "l1_" in n.node_id and n.researched]
                                        cache = caches[designer_cache_idx % len(caches)] if caches else None
                                        p, c = player.tech_tree.calculate_custom_cpu(core, cache, process, package)
                                        rd_cost = 50000.0 + (core.base_cost * 0.5)
                                    else:
                                        mems = [n for n in player.tech_tree.nodes.values() if
                                                n.category == "memory" and "mem_" in n.node_id and n.researched]
                                        mem = mems[designer_cache_idx % len(mems)] if mems else None
                                        p, c = player.tech_tree.calculate_custom_gpu(core, mem, process, package)
                                        rd_cost = 40000.0 + (core.base_cost * 0.5)

                                    if player.cash >= rd_cost:
                                        player.cash -= rd_cost
                                        player.active_chip_project = CustomChipProject(chip_name, active_designer_type,
                                                                                       p, c, rd_cost, 4)
                                        player.add_notification(f"ЗАПУЩЕН R&D ЧИПА: {chip_name}")

                                # Покупка готовой сторонней лицензии (быстро и сразу!) [2]
                                elif renderer.btn_chip_license_cpu.collidepoint(mouse_pos):
                                    avail_lic = [c for c in HISTORICAL_CPUS if c["year"] <= market.current_year]
                                    if avail_lic:
                                        # Берем последний доступный сторонний CPU
                                        target_lic = avail_lic[-1]
                                        if player.cash >= target_lic["license_fee"] and target_lic["name"] not in [
                                            x["name"] for x in player.licensed_cpus]:
                                            player.cash -= target_lic["license_fee"]
                                            player.licensed_cpus.append(
                                                {"name": target_lic["name"], "power": target_lic["power"],
                                                 "cost": target_lic["cost"]})
                                            player.add_notification(f"КУПЛЕНА ЛИЦЕНЗИЯ: {target_lic['name']}")

                                elif renderer.btn_chip_license_gpu.collidepoint(mouse_pos):
                                    avail_lic = [g for g in HISTORICAL_GPUS if g["year"] <= market.current_year]
                                    if avail_lic:
                                        target_lic = avail_lic[-1]
                                        if player.cash >= target_lic["license_fee"] and target_lic["name"] not in [
                                            x["name"] for x in player.licensed_gpus]:
                                            player.cash -= target_lic["license_fee"]
                                            player.licensed_gpus.append(
                                                {"name": target_lic["name"], "power": target_lic["power"],
                                                 "cost": target_lic["cost"]})
                                            player.add_notification(f"КУПЛЕНА ЛИЦЕНЗИЯ: {target_lic['name']}")

                        # Подтаб 3: Сборка Консолей
                        elif rd_sub_tab == "console":
                            all_cpus = player.custom_cpus + player.licensed_cpus
                            all_gpus = player.custom_gpus + player.licensed_gpus
                            all_media = HISTORICAL_MEDIA  # Используем новый справочник носителей [2]

                            if not player.active_project and all_cpus and all_gpus:
                                if renderer.btn_console_cpu.collidepoint(mouse_pos):
                                    selected_cpu_idx = (selected_cpu_idx + 1) % len(all_cpus)
                                elif renderer.btn_console_gpu.collidepoint(mouse_pos):
                                    selected_gpu_idx = (selected_gpu_idx + 1) % len(all_gpus)
                                elif renderer.btn_console_media.collidepoint(mouse_pos):
                                    selected_media_idx = (selected_media_idx + 1) % len(all_media)
                                elif renderer.btn_console_margin_dec.collidepoint(mouse_pos):
                                    margin_value = max(1.1, margin_value - 0.1)
                                elif renderer.btn_console_margin_inc.collidepoint(mouse_pos):
                                    margin_value = min(3.0, margin_value + 0.1)
                                elif renderer.btn_console_name.collidepoint(mouse_pos):
                                    selected_console_name_idx += 1
                                elif renderer.btn_console_launch.collidepoint(mouse_pos):
                                    cpu = all_cpus[selected_cpu_idx % len(all_cpus)]
                                    gpu = all_gpus[selected_gpu_idx % len(all_gpus)]
                                    med = all_media[selected_media_idx % len(all_media)]

                                    player.active_project = ConsoleProject(console_name, cpu, gpu, med, margin_value)
                                    player.add_notification(f"R&D КОНСОЛИ НАЧАТО: {console_name}")

                            elif player.active_project:
                                # Кнопка создания собственной First-Party игры во время R&D консоли [2]
                                if renderer.btn_fp_game_create.collidepoint(mouse_pos):
                                    cost_fp = 15000.0
                                    if player.cash >= cost_fp and len(player.active_game_projects) < 3:
                                        player.cash -= cost_fp
                                        g_name = f"Launch Hit #{len(player.active_game_projects) + 1}"
                                        player.active_game_projects.append(FirstPartyGameProject(g_name, cost_fp, 3))
                                        player.add_notification(f"РАЗРАБОТКА ИГРЫ: {g_name}")

                    # Таб: ФАБРИКА
                    elif current_tab == "factory" and player.released_consoles:
                        p_console = player.released_consoles[0]
                        if renderer.btn_order_10k.collidepoint(mouse_pos) and player.cash >= (
                                10000 * p_console.unit_cost):
                            order_silicon(player, p_console, 10_000, PRODUCTION_LEAD_TIME["small"])
                        elif renderer.btn_order_50k.collidepoint(mouse_pos) and player.cash >= (
                                50000 * p_console.unit_cost):
                            order_silicon(player, p_console, 50_000, PRODUCTION_LEAD_TIME["medium"])
                        elif renderer.btn_order_100k.collidepoint(mouse_pos) and player.cash >= (
                                100000 * p_console.unit_cost):
                            order_silicon(player, p_console, 100_000, PRODUCTION_LEAD_TIME["large"])

                    # Таб: ЛИЦЕНЗИИ [2]
                    elif current_tab == "licenses" and player.released_consoles:
                        target_console = player.released_consoles[0]
                        is_programmable = target_console.spec_info.get("is_programmable", False)

                        if is_programmable:
                            year_games = [g for g in games_list if g.year_available == market.current_year]
                            offset_y = 130
                            for g in year_games:
                                btn_rect = pygame.Rect(540, offset_y + 20, 180, 40)
                                is_porting = any(p.game.name == g.name for p in player.active_ports)
                                is_acquired = g.acquired_by == 'player' or any(
                                    l_game.name == g.name for l_game in player.licensed_games)

                                if btn_rect.collidepoint(
                                        mouse_pos) and not is_acquired and not is_porting and g.acquired_by is None:
                                    cost_total = g.license_cost
                                    double_cost = target_console.hardware_power < g.min_power
                                    if double_cost:
                                        cost_total *= 2.0  # Удвоение цены за слабое железо [1]

                                    if player.cash >= cost_total:
                                        player.cash -= cost_total
                                        # Отправка на портирование (займет 2 месяца) [2]
                                        player.active_ports.append(PortingProject(g, target_console, double_cost))
                                        player.add_notification(f"НАЧАТО ПОРТИРОВАНИЕ: {g.name}")
                                offset_y += 95

            # Кнопочные дубликаторы горячих клавиш
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    current_tab = "market"
                elif event.key == pygame.K_F2:
                    current_tab = "rd"
                elif event.key == pygame.K_F3:
                    current_tab = "factory"
                elif event.key == pygame.K_F4:
                    current_tab = "finance"
                elif event.key == pygame.K_F5:
                    current_tab = "licenses"
                elif event.key == pygame.K_s:
                    simulate_one_month(market, player, components_db, games_list)
                elif event.key == pygame.K_SPACE:
                    auto_play = not auto_play
                elif event.key == pygame.K_r:
                    current_difficulty = None
                    main()
                    return

        if auto_play:
            auto_tick_cooldown += 1
            if auto_tick_cooldown >= 30:
                simulate_one_month(market, player, components_db, games_list)
                auto_tick_cooldown = 0

        player.update_notifications()

        # Вызовы рендеринга из renderer.py
        screen.fill(renderer.BG_COLOR)
        pygame.draw.rect(screen, renderer.PANEL_COLOR, (0, 0, WIDTH, 50))
        pygame.draw.line(screen, renderer.BORDER_COLOR, (0, 50), (WIDTH, 50), 2)

        for t_key, rect in renderer.tab_rects.items():
            is_active = (current_tab == t_key)
            bg = renderer.AMBER if is_active else renderer.PANEL_COLOR
            border = renderer.AMBER if is_active else renderer.BORDER_COLOR
            text_col = renderer.BG_COLOR if is_active else renderer.TEXT_WHITE
            label = {"market": "РЫНОК", "rd": "РАЗРАБОТКА (R&D)", "factory": "ФАБРИКА", "finance": "ФИНАНСЫ",
                     "licenses": "ЛИЦЕНЗИИ"}[t_key]
            renderer.draw_button(screen, rect, label, renderer.font_title, bg, border, text_col)

        renderer.draw_text(screen, f"Год: {market.current_year} | Месяц: {market.current_month}", renderer.font_title,
                           renderer.AMBER, 1020, 15)
        cash_color = renderer.GREEN if player.cash >= 0 else renderer.RED
        renderer.draw_text(screen, f"Баланс: ${player.cash:,.0f}", renderer.font_title, cash_color, 820, 15)

        if current_tab == "market":
            renderer.render_market_tab(screen, market, auto_play, renderer.font_title, renderer.font_body,
                                       renderer.btn_step, renderer.btn_auto, renderer.btn_reset, player)
        elif current_tab == "rd":
            renderer.render_rd_tab(screen, player, components_db, selected_cpu_idx, selected_gpu_idx,
                                   selected_media_idx, margin_value,
                                   renderer.font_title, renderer.font_body, renderer.font_large, rd_sub_tab,
                                   active_designer_type, chip_name, designer_core_idx, designer_cache_idx,
                                   designer_process_idx, designer_package_idx,
                                   player.active_chip_project, player.active_game_projects, console_name)
        elif current_tab == "factory":
            renderer.render_factory_tab(screen, player, renderer.font_title, renderer.font_body, renderer.font_large,
                                        renderer.btn_order_10k, renderer.btn_order_50k, renderer.btn_order_100k)
        elif current_tab == "finance":
            renderer.render_finance_tab(screen, player, renderer.font_title, renderer.font_body, renderer.font_large)
        elif current_tab == "licenses":
            renderer.render_licenses_tab(screen, player, games_list, market.current_year, renderer.font_title,
                                         renderer.font_body)

        renderer.draw_notifications(screen, player)

        pygame.display.flip()
        clock.tick(60)


def simulate_one_month(market, player: PlayerCompany, components_db, games_list):
    if player.cash < 0:
        player.bankruptcy_months += 1
    else:
        player.bankruptcy_months = 0

    rd_expense = 0.0

    # Прогресс исследований тех-древа
    research_cost = player.advance_research()
    rd_expense += research_cost

    # Прогресс активной разработки собственного CPU/GPU в R&D [3]
    if player.active_chip_project:
        proj = player.active_chip_project
        points_generated = player.engineers * 4.0 * player.diff_settings["research_speed_multiplier"]
        proj.advance(points_generated)

        rd_expense += player.engineers * 400.0  # амортизация оборудования R&D

        points_needed = max(10, proj.dev_months * 10)
        if proj.progress >= points_needed:
            # Чип готов! Добавляем в локальную базу
            if proj.category == "cpu":
                player.custom_cpus.append({"name": proj.name, "power": proj.power, "cost": proj.cost})
            else:
                player.custom_gpus.append({"name": proj.name, "power": proj.power, "cost": proj.cost})

            player.add_notification(f"ЧИП ГОТОВ К ПРОИЗВОДСТВУ: {proj.name}")
            player.active_chip_project = None

    # Прогресс собственных 1st Party игр во время R&D консоли [2]
    if player.active_project:
        points_generated = player.engineers * 3.0
        for fp_game in player.active_game_projects:
            if fp_game.progress < 30.0:  # Каждая игра требует 30 очков
                fp_game.advance(points_generated)
                rd_expense += 200.0  # Месячные затраты на дизайн игры

    # Прогресс сторонних портов/лицензий (портирование занимает 2 месяца) [2]
    remaining_ports = []
    for port in player.active_ports:
        port.months_left -= 1
        if port.months_left <= 0:
            # Порт завершен! Игра официально выходит на консоли
            player.licensed_games.append(port.game)
            port.console.library_size += 1

            # Если железо консоли слабее игры, ее качество ухудшается на 15% [1]
            if port.double_cost:
                port.console.library_quality = max(0.1, port.console.library_quality - 0.15)
                player.add_notification(f"ПОРТ ЗАВЕРШЕН: {port.game.name} (Ухудшен из-за ТТХ)")
            else:
                player.add_notification(f"ПОРТ ЗАВЕРШЕН: {port.game.name}!")
        else:
            remaining_ports.append(port)
    player.active_ports = remaining_ports

    # Прогресс разработки консоли
    if player.active_project:
        eng_points = player.engineers * 5.0
        project = player.active_project
        project.advance_development(eng_points)
        rd_expense += player.engineers * 500.0

        if project.phase == "ready":
            # Считаем количество готовых 1st party игр в стартовой линейке [2]
            completed_fp_games = [g for g in player.active_game_projects if g.progress >= 30.0]
            start_library_size = 5 + len(completed_fp_games)

            # Рассчитываем стартовый буст качества от проработанности игр
            quality_boost = sum(0.04 for g in completed_fp_games)
            final_quality = min(1.0, project.quality + quality_boost)

            player_console = Console(
                name=project.name,
                launch_year=market.current_year,
                price=project.retail_price,
                hardware_power=project.hardware_power,
                library_size=start_library_size,
                library_quality=final_quality,
                marketing_budget=50_000,
                color=(241, 196, 15),
                spec_info={
                    "cost": project.unit_cost,
                    "cpu_name": project.cpu["name"],
                    "gpu_name": project.gpu["name"],
                    "is_programmable": project.media.get("is_programmable", False)  # Сохраняем тип картриджа [1]
                },
                is_player=True
            )
            player_console.launch_month = market.current_month
            market.add_console(player_console)
            player.released_consoles.append(player_console)

            player.active_project = None
            player.active_game_projects = []  # Очищаем очередь игр
            player.add_notification(f"УСПЕШНЫЙ ЗАПУСК КОНСОЛИ: {player_console.name}!")

    arrived_stock = player.process_monthly_logistics()
    if arrived_stock > 0:
        player.add_notification(f"ПОСТАВКА ПЛАТ: +{arrived_stock:,} шт.")

    if player.released_consoles:
        player.released_consoles[0].inventory += arrived_stock

    salaries = player.get_monthly_salaries()
    monthly_sales = market.simulate_month(player.reputation)

    hw_revenue = 0.0
    royalty_revenue = 0.0
    manufacturing_cost = 0.0
    warehouse_cost = 0.0
    marketing_expenses = 0.0
    shortage_ratio = 0.0

    if player.released_consoles:
        p_console = player.released_consoles[0]
        units_sold = monthly_sales.get(p_console, 0)
        if units_sold > 0:
            shortage_ratio = max(0.0, 1.0 - (p_console.inventory / float(units_sold + p_console.inventory + 1)))

        hw_revenue = units_sold * p_console.price

        if p_console.installed_base > 0:
            base_royalty_payout = 0.15
            # Каждая полностью портированная игра добавляет свой буст к роялти-прибыли [1, 2]
            for game in player.licensed_games:
                base_royalty_payout += game.base_royalty
            royalty_revenue = p_console.installed_base * base_royalty_payout

        marketing_expenses = p_console.marketing_budget
        warehouse_cost = p_console.inventory * 1.0
        player.reputation.update(p_console.library_quality, p_console.marketing_budget, shortage_ratio)

    # ИИ выкупает оставшиеся лицензии в конце месяца
    unowned_games = [g for g in games_list if g.year_available == market.current_year and g.acquired_by is None]
    for game in unowned_games:
        import random
        if random.random() < 0.12 and market.consoles:
            ai_choice = random.choice([c for c in market.consoles if not c.is_player])
            game.acquired_by = ai_choice.name
            ai_choice.library_size += 1

    # Закупка у подрядчиков
    for order in player.production_orders:
        if order["months_left"] == 1:
            manufacturing_cost += order["quantity"] * order["unit_cost"] * player.diff_settings[
                "manufacturing_cost_multiplier"]

    total_revenue = hw_revenue + royalty_revenue
    total_expenses = manufacturing_cost + rd_expense + salaries + warehouse_cost + marketing_expenses
    net_profit = total_revenue - total_expenses

    player.cash += net_profit
    player.financials_last_month = {
        "hw_revenue": hw_revenue,
        "royalty_revenue": royalty_revenue,
        "manufacturing_cost": manufacturing_cost,
        "rd_expenses": rd_expense,
        "marketing_expenses": marketing_expenses,
        "salaries": salaries,
        "warehouse_cost": warehouse_cost,
        "net_profit": net_profit
    }


def order_silicon(player: PlayerCompany, console: Console, qty: int, lead_time: int):
    cost_total = qty * console.unit_cost * player.diff_settings["manufacturing_cost_multiplier"]
    player.cash -= cost_total
    player.production_orders.append({
        "months_left": lead_time,
        "quantity": qty,
        "unit_cost": console.unit_cost
    })
    player.add_notification("ЗАКАЗ ОПЛАЧЕН И НАПРАВЛЕН В СБОРКУ")


if __name__ == "__main__":
    main()