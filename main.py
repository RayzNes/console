# main.py

import pygame
import sys
from config import DIFFICULTIES, START_YEAR, END_YEAR, PRODUCTION_LEAD_TIME, SEASONAL_FACTORS
from data_loader import load_data
from ai_competitor import AICompany
from market import Market
from player import PlayerCompany, ConsoleProject
from console import Console
from games_db import get_historical_games, GameLicense
import renderer

# Инициализация графики
pygame.init()
WIDTH, HEIGHT = 1224, 1024
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Console Tycoon: Silicon Race - Interactive Control Panel")
clock = pygame.time.Clock()

# Глобальные состояния
current_difficulty = None
current_tab = "market"
rd_sub_tab = "research"

# Списки выбора компонентов для кастомного конструирования
selected_cpu_idx = 0
selected_gpu_idx = 0
selected_media_idx = 0
margin_value = 1.5

# Описание интерактивных кнопок подвкладок R&D
btn_sub_res = pygame.Rect(45, 110, 180, 30)
btn_sub_design = pygame.Rect(235, 110, 210, 30)
btn_sub_console = pygame.Rect(455, 110, 180, 30)


def draw_chart(surface, x, y, w, h, market_history, consoles):
    renderer.draw_chart(surface, x, y, w, h, market_history, consoles)


def main():
    global current_tab, current_difficulty, rd_sub_tab
    global selected_cpu_idx, selected_gpu_idx, selected_media_idx, margin_value

    components_db, events_db = load_data()
    player = None
    market = None
    ai_companies = []

    # Каталог игр для лицензирования [2]
    games_list = get_historical_games()

    btn_easy = pygame.Rect(462, 350, 300, 50)
    btn_medium = pygame.Rect(462, 420, 300, 50)
    btn_hard = pygame.Rect(462, 490, 300, 50)

    auto_play = False
    auto_tick_cooldown = 0

    while True:
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

        # ИИ-соперники забирают игры на аукционе, если у игрока нет лицензии [2]
        for ai in ai_companies:
            if not ai.launched and market.current_year >= ai.launch_year:
                console = ai.design_console(components_db)
                market.add_console(console)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = event.pos

                    # Навигация
                    for t_key, rect in renderer.tab_rects.items():
                        if rect.collidepoint(mouse_pos):
                            current_tab = t_key

                    # События: РЫНОК
                    if current_tab == "market":
                        if renderer.btn_step.collidepoint(mouse_pos):
                            simulate_one_month(market, player, components_db, games_list)
                        elif renderer.btn_auto.collidepoint(mouse_pos):
                            auto_play = not auto_play
                        elif renderer.btn_reset.collidepoint(mouse_pos):
                            current_difficulty = None
                            main()
                            return

                    # События: R&D (Исследования)
                    elif current_tab == "rd":
                        if btn_sub_res.collidepoint(mouse_pos):
                            rd_sub_tab = "research"
                        elif btn_sub_design.collidepoint(mouse_pos):
                            rd_sub_tab = "designer"
                        elif btn_sub_console.collidepoint(mouse_pos):
                            rd_sub_tab = "console"

                        # 1. Исследования
                        if rd_sub_tab == "research":
                            # Передан текущий год из симуляции (Исправлен критический баг №1) [1]
                            avail_nodes = player.tech_tree.get_available_research(market.current_year)
                            offset_y = 205
                            for node in avail_nodes[:10]:
                                click_rect = pygame.Rect(45, offset_y, 450, 25)
                                if click_rect.collidepoint(mouse_pos):
                                    player.active_research = node
                                offset_y += 30

                        # 2. Конструктор Чипов
                        elif rd_sub_tab == "designer":
                            if renderer.btn_cpu_select.collidepoint(mouse_pos):
                                cpu_core = \
                                [n for n in player.tech_tree.nodes.values() if n.category == "cpu" and n.researched][-1]
                                cpu_cache_nodes = [n for n in player.tech_tree.nodes.values() if
                                                   n.category == "memory" and n.researched and "cache" in n.node_id]
                                cache = cpu_cache_nodes[-1] if cpu_cache_nodes else None
                                process = [n for n in player.tech_tree.nodes.values() if
                                           n.category == "manufacturing" and n.researched][-1]
                                package = [n for n in player.tech_tree.nodes.values() if
                                           n.category == "manufacturing" and n.researched and "package" in n.node_id][
                                    -1]

                                power, cost = player.tech_tree.calculate_custom_cpu(cpu_core, cache, process, package)
                                player.custom_cpus.append({
                                    "name": f"MyCPU-{len(player.custom_cpus) + 1}",
                                    "power": power, "cost": cost
                                })
                                player.add_notification("СКОНСТРУИРОВАН CPU")

                            elif renderer.btn_gpu_select.collidepoint(mouse_pos):
                                gpu_core = \
                                [n for n in player.tech_tree.nodes.values() if n.category == "gpu" and n.researched][-1]
                                memory = [n for n in player.tech_tree.nodes.values() if
                                          n.category == "memory" and n.researched and "mem" in n.node_id][-1]
                                process = [n for n in player.tech_tree.nodes.values() if
                                           n.category == "manufacturing" and n.researched][-1]
                                package = [n for n in player.tech_tree.nodes.values() if
                                           n.category == "manufacturing" and n.researched and "package" in n.node_id][
                                    -1]

                                power, cost = player.tech_tree.calculate_custom_gpu(gpu_core, memory, process, package)
                                player.custom_gpus.append({
                                    "name": f"MyGPU-{len(player.custom_gpus) + 1}",
                                    "power": power, "cost": cost
                                })
                                player.add_notification("СКОНСТРУИРОВАН GPU")

                        # 3. Сборка консолей из чипов
                        elif rd_sub_tab == "console":
                            if renderer.btn_hire.collidepoint(mouse_pos):
                                player.engineers += 1
                            elif renderer.btn_fire.collidepoint(mouse_pos):
                                player.engineers = max(1, player.engineers - 1)

                            if not player.active_project and player.custom_cpus and player.custom_gpus:
                                if renderer.btn_cpu_select.collidepoint(mouse_pos):
                                    selected_cpu_idx = (selected_cpu_idx + 1) % len(player.custom_cpus)
                                elif renderer.btn_gpu_select.collidepoint(mouse_pos):
                                    selected_gpu_idx = (selected_gpu_idx + 1) % len(player.custom_gpus)
                                elif renderer.btn_media_select.collidepoint(mouse_pos):
                                    selected_media_idx = (selected_media_idx + 1) % len(components_db["media"])
                                elif renderer.btn_margin_dec.collidepoint(mouse_pos):
                                    margin_value = max(1.1, margin_value - 0.1)
                                elif renderer.btn_margin_inc.collidepoint(mouse_pos):
                                    margin_value = min(3.0, margin_value + 0.1)
                                elif renderer.btn_launch_project.collidepoint(mouse_pos):
                                    cpu = player.custom_cpus[selected_cpu_idx % len(player.custom_cpus)]
                                    gpu = player.custom_gpus[selected_gpu_idx % len(player.custom_gpus)]
                                    med = components_db["media"][selected_media_idx]
                                    player.active_project = ConsoleProject("MyConsole v1", cpu, gpu, med, margin_value)

                    # События: ФАБРИКА
                    elif current_tab == "factory" and player.released_consoles:
                        p_console = player.released_consoles[0]

                        # Месяцы доставки рассчитываются из Lead Time [1]
                        if renderer.btn_order_10k.collidepoint(mouse_pos) and player.cash >= (
                                10000 * p_console.unit_cost):
                            order_silicon(player, p_console, 10_000, PRODUCTION_LEAD_TIME["small"])
                        elif renderer.btn_order_50k.collidepoint(mouse_pos) and player.cash >= (
                                50000 * p_console.unit_cost):
                            order_silicon(player, p_console, 50_000, PRODUCTION_LEAD_TIME["medium"])
                        elif renderer.btn_order_100k.collidepoint(mouse_pos) and player.cash >= (
                                100000 * p_console.unit_cost):
                            order_silicon(player, p_console, 100_000, PRODUCTION_LEAD_TIME["large"])

                    # События: ЛИЦЕНЗИИ [2]
                    elif current_tab == "licenses":
                        year_games = [g for g in games_list if g.year_available == market.current_year]
                        offset_y = 130
                        for g in year_games:
                            btn_rect = pygame.Rect(950, offset_y + 20, 220, 40)
                            if btn_rect.collidepoint(mouse_pos) and g.acquired_by is None:
                                if player.cash >= g.license_cost:
                                    player.cash -= g.license_cost
                                    g.acquired_by = 'player'
                                    player.licensed_games.append(g)

                                    # Роялти выросло + увеличиваем размер библиотеки активной консоли [2]
                                    if player.released_consoles:
                                        p_console = player.released_consoles[0]
                                        p_console.library_size += 1

                                        # Проверка мощности консоли: слабая консоль ухудшает качество софта [1]
                                        if p_console.hardware_power < g.min_power:
                                            p_console.library_quality = max(0.1, p_console.library_quality - 0.15)
                                            player.add_notification(f"СЛАБОЕ ЖЕЛЕЗО: Качество {g.name} урезано!")
                                        else:
                                            player.add_notification(f"ЛИЦЕНЗИРОВАНО: {g.name}")
                                offset_y += 95

            # Дублирующее клавиатурное управление
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

        # Шаг автоматической прокрутки
        if auto_play:
            auto_tick_cooldown += 1
            if auto_tick_cooldown >= 30:
                simulate_one_month(market, player, components_db, games_list)
                auto_tick_cooldown = 0

        # Анимация и удаление всплывающих сообщений
        player.update_notifications()

        # Рендеринг кадра
        screen.fill(renderer.BG_COLOR)
        pygame.draw.rect(screen, renderer.PANEL_COLOR, (0, 0, WIDTH, 50))
        pygame.draw.line(screen, renderer.BORDER_COLOR, (0, 50), (WIDTH, 50), 2)

        # Вывод кнопок вкладок
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

        # Отрисовка активных экранов
        if current_tab == "market":
            renderer.render_market_tab(screen, market, auto_play, renderer.font_title, renderer.font_body,
                                       renderer.btn_step, renderer.btn_auto, renderer.btn_reset, player)
        elif current_tab == "rd":
            renderer.render_rd_tab(screen, player, components_db, selected_cpu_idx, selected_gpu_idx,
                                   selected_media_idx, margin_value,
                                   renderer.font_title, renderer.font_body, renderer.font_large, rd_sub_tab,
                                   renderer.btn_hire, renderer.btn_fire, renderer.btn_cpu_select,
                                   renderer.btn_gpu_select, renderer.btn_media_select,
                                   renderer.btn_margin_dec, renderer.btn_margin_inc, renderer.btn_launch_project,
                                   btn_sub_res, btn_sub_design, btn_sub_console, None, None)
        elif current_tab == "factory":
            renderer.render_factory_tab(screen, player, renderer.font_title, renderer.font_body, renderer.font_large,
                                        renderer.btn_order_10k, renderer.btn_order_50k, renderer.btn_order_100k)
        elif current_tab == "finance":
            renderer.render_finance_tab(screen, player, renderer.font_title, renderer.font_body, renderer.font_large)
        elif current_tab == "licenses":
            renderer.render_licenses_tab(screen, player, games_list, market.current_year, renderer.font_title,
                                         renderer.font_body)

        # Вывод всплывающих уведомлений [1]
        renderer.draw_notifications(screen, player)

        pygame.display.flip()
        clock.tick(60)


def simulate_one_month(market, player: PlayerCompany, components_db, games_list):
    """Экономический расчет с репутацией и роялти за лицензии"""
    if player.cash < 0:
        player.bankruptcy_months += 1
    else:
        player.bankruptcy_months = 0

    # Прогресс исследований и R&D консоли
    rd_expense = 0.0
    research_cost = player.advance_research()
    rd_expense += research_cost

    if player.active_project:
        eng_points = player.engineers * 5.0
        project = player.active_project
        project.advance_development(eng_points)
        rd_expense += player.engineers * 500.0

        if project.phase == "ready":
            player_console = Console(
                name=project.name,
                launch_year=market.current_year,
                price=project.retail_price,
                hardware_power=project.hardware_power,
                library_size=5 + len(player.licensed_games),
                library_quality=project.quality,
                marketing_budget=50_000,
                color=(241, 196, 15),
                spec_info={"cost": project.unit_cost, "cpu_name": project.cpu["name"], "gpu_name": project.gpu["name"]},
                is_player=True
            )
            player_console.launch_month = market.current_month
            market.add_console(player_console)
            player.released_consoles.append(player_console)
            player.active_project = None

    arrived_stock = player.process_monthly_logistics()
    if arrived_stock > 0:
        player.add_notification(f"ПОСТАВКА: +{arrived_stock:,} кремниевых плат!")

    if player.released_consoles:
        player.released_consoles[0].inventory += arrived_stock

    salaries = player.get_monthly_salaries()

    # Запуск ежемесячной симуляции рынка
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

        # Расчет доли упущенных из-за дефицита продаж
        if units_sold > 0:
            shortage_ratio = max(0.0, 1.0 - (p_console.inventory / float(units_sold + p_console.inventory + 1)))

        hw_revenue = units_sold * p_console.price

        # Динамические роялти за каждую выкупленную лицензию [1, 2]
        if p_console.installed_base > 0:
            base_royalty_payout = 0.15  # Базовая ставка
            for game in player.licensed_games:
                base_royalty_payout += game.base_royalty
            royalty_revenue = p_console.installed_base * base_royalty_payout

        marketing_expenses = p_console.marketing_budget
        warehouse_cost = p_console.inventory * 1.0

        # Обновление репутации бренда на базе качества и дефицита [2]
        player.reputation.update(p_console.library_quality, p_console.marketing_budget, shortage_ratio)

    # ИИ выкупает оставшиеся игры на аукционе в конце месяца [2]
    unowned_games = [g for g in games_list if g.year_available == market.current_year and g.acquired_by is None]
    for game in unowned_games:
        # Простой случайный выкуп ИИ
        import random
        if random.random() < 0.15 and market.consoles:
            ai_choice = random.choice([c for c in market.consoles if not c.is_player])
            game.acquired_by = ai_choice.name
            ai_choice.library_size += 1

    # Изъятие денег на закупку при финальной доставке
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
    """Метод заказа с предоплатой (исправлен баг №2)"""
    cost_total = qty * console.unit_cost * player.diff_settings["manufacturing_cost_multiplier"]
    player.cash -= cost_total
    player.production_orders.append({
        "months_left": lead_time,
        "quantity": qty,
        "unit_cost": console.unit_cost
    })
    player.add_notification("ЗАКАЗ РАЗМЕЩЕН НА ФАБРИКЕ")


if __name__ == "__main__":
    main()