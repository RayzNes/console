# main.py

import pygame
import sys
import random
from config import (DIFFICULTIES, START_YEAR, END_YEAR, PRODUCTION_LEAD_TIME,
                    HISTORICAL_CPUS, HISTORICAL_GPUS, HISTORICAL_MEDIA,
                    PRESET_NAMES, CHIP_PRESET_NAMES, MARKETING_TYPES, STUDIO_CONTRACTS)
from ai_competitor import AICompany
from market import Market
from player import PlayerCompany, ConsoleProject, CustomChipProject, FirstPartyGameProject, PortingProject
from console import Console
from games_db import get_historical_games, GameLicense
from sound import SoundFX
from data_loader import load_data
import renderer

pygame.init()
WIDTH, HEIGHT = 1224, 1024
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Console Tycoon: Silicon Race")
clock = pygame.time.Clock()

sound_fx = SoundFX()

# Селекторы параметров R&D кастомных чипов
active_designer_type = "cpu"
designer_core_idx = 0
designer_cache_idx = 0
designer_process_idx = 0
designer_package_idx = 0

# Состояние интерактивного выбора лицензии на чип
licensing_selector_type = None

# Текстовые переменные для имен
selected_console_name_idx = 0
selected_chip_name_idx = 0

# Логика табов и подвкладок
current_tab = "market"
rd_sub_tab = "research"
licenses_sub_tab = "games"

# Drag-and-drop менеджер
drag_manager = {
    "active": False,
    "type": None,  # "cpu", "gpu", "media"
    "index": 0,
    "name": "",
    "cost": 0.0
}


def draw_chart(surface, x, y, w, h, market_history, consoles):
    renderer.draw_chart(surface, x, y, w, h, market_history, consoles)


def main():
    global current_tab, current_difficulty, rd_sub_tab, licenses_sub_tab
    global selected_cpu_idx, selected_gpu_idx, selected_media_idx, margin_value
    global active_designer_type, designer_core_idx, designer_cache_idx, designer_process_idx, designer_package_idx
    global selected_console_name_idx, selected_chip_name_idx
    global licensing_selector_type
    global drag_manager

    components, events = load_data()

    current_difficulty = None
    current_tab = "market"
    rd_sub_tab = "research"
    licenses_sub_tab = "games"
    selected_cpu_idx = 0
    selected_gpu_idx = 0
    selected_media_idx = 0
    margin_value = 1.45

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
        # Экран сложности
        if not current_difficulty:
            renderer.render_difficulty_screen(screen, renderer.font_large, renderer.font_title, renderer.font_body)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if btn_easy.collidepoint(event.pos): current_difficulty = "easy"
                        elif btn_medium.collidepoint(event.pos): current_difficulty = "medium"
                        elif btn_hard.collidepoint(event.pos): current_difficulty = "hard"

                        if current_difficulty:
                            sound_fx.play_success()
                            settings = DIFFICULTIES[current_difficulty]
                            player = PlayerCompany("PlayerCorp", current_difficulty, settings)
                            market = Market(settings["demand_multiplier"])

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
                    sound_fx.play_success()
                    current_difficulty = None
                    main()
                    return
            continue

        for ai in ai_companies:
            if not ai.launched and market.current_year >= ai.launch_year:
                console = ai.design_console(market.current_month)
                market.add_console(console)

        console_name = PRESET_NAMES[selected_console_name_idx % len(PRESET_NAMES)] if not player.released_consoles else player.released_consoles[0].name
        chip_name = CHIP_PRESET_NAMES[selected_chip_name_idx % len(CHIP_PRESET_NAMES)]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Текстовый ввод
            elif event.type == pygame.KEYDOWN and player.naming_mode is not None:
                sound_fx.play_click()
                if event.key == pygame.K_RETURN:
                    if player.naming_mode == "chip":
                        CHIP_PRESET_NAMES[selected_chip_name_idx % len(CHIP_PRESET_NAMES)] = player.input_buffer
                    elif player.naming_mode == "console":
                        PRESET_NAMES[selected_console_name_idx % len(PRESET_NAMES)] = player.input_buffer
                    player.naming_mode = None
                    player.input_buffer = ""
                elif event.key == pygame.K_BACKSPACE:
                    player.input_buffer = player.input_buffer[:-1]
                else:
                    if len(player.input_buffer) < 14 and event.unicode.isalnum() or event.unicode in " -_":
                        player.input_buffer += event.unicode

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = event.pos

                    if player.naming_mode:
                        player.naming_mode = None
                        player.input_buffer = ""

                    old_tab = current_tab
                    for t_key, rect in renderer.tab_rects.items():
                        if rect.collidepoint(mouse_pos):
                            current_tab = t_key
                            licensing_selector_type = None
                    if current_tab != old_tab:
                        sound_fx.play_click()

                    # РЫНОК (События ценовых войн и смены рекламы)
                    if current_tab == "market":
                        if renderer.btn_step.collidepoint(mouse_pos):
                            sound_fx.play_click()
                            simulate_one_month(market, player, games_list)
                        elif renderer.btn_auto.collidepoint(mouse_pos):
                            sound_fx.play_click()
                            auto_play = not auto_play
                        elif renderer.btn_reset.collidepoint(mouse_pos):
                            sound_fx.play_error()
                            current_difficulty = None
                            main()
                            return
                        elif player.released_consoles:
                            # Кнопка снижения цены
                            if pygame.Rect(45, 640, 50, 30).collidepoint(mouse_pos):
                                sound_fx.play_click()
                                player.released_consoles[0].price = max(10, player.released_consoles[0].price - 10)
                                player.add_notification("Ценовые войны: Цена снижена!")
                            # Кнопка повышения цены
                            elif pygame.Rect(105, 640, 50, 30).collidepoint(mouse_pos):
                                sound_fx.play_click()
                                player.released_consoles[0].price += 10
                                player.add_notification("Ценовые войны: Цена повышена!")
                            # Кнопка ротации рекламы
                            elif pygame.Rect(165, 640, 130, 30).collidepoint(mouse_pos):
                                sound_fx.play_click()
                                modes = ["none", "guerrilla", "print", "tv"]
                                p_con = player.released_consoles[0]
                                curr_idx = modes.index(p_con.marketing_type)
                                p_con.marketing_type = modes[(curr_idx + 1) % len(modes)]
                                player.add_notification(f"Кампания изменена на: {MARKETING_TYPES[p_con.marketing_type]['name']}")

                    # РАЗРАБОТКА (R&D)
                    elif current_tab == "rd":
                        if renderer.btn_sub_res.collidepoint(mouse_pos):
                            sound_fx.play_click()
                            rd_sub_tab = "research"
                        elif renderer.btn_sub_design.collidepoint(mouse_pos):
                            sound_fx.play_click()
                            rd_sub_tab = "designer"
                            licensing_selector_type = None
                        elif renderer.btn_sub_console.collidepoint(mouse_pos):
                            sound_fx.play_click()
                            rd_sub_tab = "console"

                        if renderer.btn_hire.collidepoint(mouse_pos):
                            sound_fx.play_click()
                            player.engineers += 1
                        elif renderer.btn_fire.collidepoint(mouse_pos):
                            sound_fx.play_click()
                            player.engineers = max(1, player.engineers - 1)

                        # ИССЛЕДОВАНИЯ (Клик по 4X-сетке)
                        if rd_sub_tab == "research":
                            for node in player.tech_tree.nodes.values():
                                x, y = 30 + node.coords[0], 150 + node.coords[1]
                                node_rect = pygame.Rect(x, y, 110, 35)
                                if node_rect.collidepoint(mouse_pos):
                                    unlocked = all(player.tech_tree.nodes[p].researched for p in node.prerequisites)
                                    if unlocked and not node.researched and node.year_available <= market.current_year:
                                        if player.active_research:
                                            sound_fx.play_error()
                                            player.add_notification("Лаборатория уже занята!")
                                        else:
                                            sound_fx.play_success()
                                            player.active_research = node
                                            player.add_notification(f"Изучается: {node.name}")
                                    else:
                                        sound_fx.play_error()

                        # КОНСТРУКТОР ЧИПОВ
                        elif rd_sub_tab == "designer":
                            if not player.active_chip_project:
                                if renderer.btn_chip_type.collidepoint(mouse_pos):
                                    sound_fx.play_click()
                                    active_designer_type = "gpu" if active_designer_type == "cpu" else "cpu"
                                    designer_core_idx, designer_cache_idx, designer_process_idx, designer_package_idx = 0, 0, 0, 0
                                elif renderer.btn_chip_name.collidepoint(mouse_pos):
                                    sound_fx.play_click()
                                    player.naming_mode = "chip"
                                    player.input_buffer = chip_name
                                elif renderer.btn_chip_core.collidepoint(mouse_pos):
                                    sound_fx.play_click()
                                    designer_core_idx += 1
                                elif renderer.btn_chip_cache.collidepoint(mouse_pos):
                                    sound_fx.play_click()
                                    designer_cache_idx += 1
                                elif renderer.btn_chip_process.collidepoint(mouse_pos):
                                    sound_fx.play_click()
                                    designer_process_idx += 1
                                elif renderer.btn_chip_package.collidepoint(mouse_pos):
                                    sound_fx.play_click()
                                    designer_package_idx += 1

                                elif renderer.btn_chip_build.collidepoint(mouse_pos):
                                    cores = [n for n in player.tech_tree.nodes.values() if n.category == active_designer_type and n.researched]
                                    processes = [n for n in player.tech_tree.nodes.values() if n.category == "manufacturing" and "tech_" in n.node_id and n.researched]
                                    packages = [n for n in player.tech_tree.nodes.values() if n.category == "manufacturing" and "package_" in n.node_id and n.researched]
                                    core = cores[designer_core_idx % len(cores)] if cores else None
                                    process = processes[designer_process_idx % len(processes)] if processes else None
                                    package = packages[designer_package_idx % len(packages)] if packages else None

                                    if active_designer_type == "cpu":
                                        caches = [n for n in player.tech_tree.nodes.values() if n.category == "memory" and "l1_" in n.node_id and n.researched]
                                        cache = caches[designer_cache_idx % len(caches)] if caches else None
                                        p, c = player.tech_tree.calculate_custom_cpu(core, cache, process, package)
                                        rd_cost = 50000.0 + (core.base_cost * 0.5)
                                    else:
                                        mems = [n for n in player.tech_tree.nodes.values() if n.category == "memory" and "mem_" in n.node_id and n.researched]
                                        mem = mems[designer_cache_idx % len(mems)] if mems else None
                                        p, c = player.tech_tree.calculate_custom_gpu(core, mem, process, package)
                                        rd_cost = 40000.0 + (core.base_cost * 0.5)

                                    if player.cash >= rd_cost:
                                        sound_fx.play_success()
                                        player.cash -= rd_cost
                                        player.active_chip_project = CustomChipProject(chip_name, active_designer_type, p, c, rd_cost, 4)
                                        player.add_notification(f"ЗАПУЩЕН R&D ЧИПА: {chip_name}")
                                    else:
                                        sound_fx.play_error()

                                elif renderer.btn_chip_license_cpu.collidepoint(mouse_pos):
                                    sound_fx.play_click()
                                    licensing_selector_type = "cpu"
                                elif renderer.btn_chip_license_gpu.collidepoint(mouse_pos):
                                    sound_fx.play_click()
                                    licensing_selector_type = "gpu"

                                elif licensing_selector_type:
                                    avail_lic = [x for x in (HISTORICAL_CPUS if licensing_selector_type == "cpu" else HISTORICAL_GPUS) if x["year"] <= market.current_year]
                                    lic_offset_y = 310
                                    for item in avail_lic[:4]:
                                        buy_rect = pygame.Rect(1020, lic_offset_y, 150, 30)
                                        if buy_rect.collidepoint(mouse_pos):
                                            already_bought = item["name"] in [x["name"] for x in (player.licensed_cpus if licensing_selector_type == "cpu" else player.licensed_gpus)]
                                            if not already_bought and player.cash >= item["license_fee"]:
                                                sound_fx.play_success()
                                                player.cash -= item["license_fee"]
                                                if licensing_selector_type == "cpu":
                                                    player.licensed_cpus.append({"name": item["name"], "power": item["power"], "cost": item["cost"]})
                                                else:
                                                    player.licensed_gpus.append({"name": item["name"], "power": item["power"], "cost": item["cost"]})
                                                player.add_notification(f"КУПЛЕНА ЛИЦЕНЗИЯ: {item['name']}")
                                            elif not already_bought:
                                                sound_fx.play_error()
                                        lic_offset_y += 50

                        # СБОРКА СИСТЕМ (Drag-and-drop: Захват платы)
                        elif rd_sub_tab == "console" and not player.active_project:
                            all_cpus = player.custom_cpus + player.licensed_cpus
                            all_gpus = player.custom_gpus + player.licensed_gpus
                            all_media = components["media"]

                            items_to_render = []
                            for idx, c in enumerate(all_cpus):
                                items_to_render.append({"type": "cpu", "name": f"CPU: {c['name'][:14]}", "index": idx, "cost": c["cost"]})
                            for idx, g in enumerate(all_gpus):
                                items_to_render.append({"type": "gpu", "name": f"GPU: {g['name'][:14]}", "index": idx, "cost": g["cost"]})
                            for idx, m in enumerate(all_media):
                                items_to_render.append({"type": "media", "name": f"Media: {m['name'][:14]}", "index": idx, "cost": m["cost"]})

                            offset_card_y = 245
                            for item in items_to_render[:6]:
                                card_rect = pygame.Rect(415, offset_card_y, 320, 35)
                                if card_rect.collidepoint(mouse_pos):
                                    sound_fx.play_click()
                                    drag_manager["active"] = True
                                    drag_manager["type"] = item["type"]
                                    drag_manager["index"] = item["index"]
                                    drag_manager["name"] = item["name"]
                                    drag_manager["cost"] = item["cost"]
                                    break
                                offset_card_y += 42

                            # Обычные кнопки наценки и сборки консоли
                            if all_cpus and all_gpus:
                                if pygame.Rect(45, 455, 50, 30).collidepoint(mouse_pos):
                                    sound_fx.play_click()
                                    margin_value = max(1.1, margin_value - 0.1)
                                elif pygame.Rect(110, 455, 50, 30).collidepoint(mouse_pos):
                                    sound_fx.play_click()
                                    margin_value = min(3.0, margin_value + 0.1)
                                elif renderer.btn_console_name.collidepoint(mouse_pos):
                                    sound_fx.play_click()
                                    player.naming_mode = "console"
                                    player.input_buffer = console_name
                                elif renderer.btn_console_launch.collidepoint(mouse_pos):
                                    cpu = all_cpus[selected_cpu_idx % len(all_cpus)]
                                    gpu = all_gpus[selected_gpu_idx % len(all_gpus)]
                                    med = all_media[selected_media_idx % len(all_media)]

                                    sound_fx.play_success()
                                    player.active_project = ConsoleProject(console_name, cpu, gpu, med, margin_value)
                                    player.add_notification(f"R&D КОНСОЛИ НАЧАТО: {console_name}")

                            if player.active_project:
                                if renderer.btn_fp_game_create.collidepoint(mouse_pos):
                                    cost_fp = 15000.0
                                    if player.cash >= cost_fp and len(player.active_game_projects) < 3:
                                        sound_fx.play_success()
                                        player.cash -= cost_fp
                                        g_name = f"Launch Hit #{len(player.active_game_projects) + 1}"
                                        player.active_game_projects.append(FirstPartyGameProject(g_name, cost_fp, 3))
                                        player.add_notification(f"РАЗРАБОТКА ИГРЫ: {g_name}")
                                    else:
                                        sound_fx.play_error()

                    # ЛОГИСТИКА / ФАБРИКА
                    elif current_tab == "factory" and player.released_consoles:
                        p_console = player.released_consoles[0]
                        if renderer.btn_order_10k.collidepoint(mouse_pos) and player.cash >= (10000 * p_console.unit_cost):
                            sound_fx.play_success()
                            order_silicon(player, p_console, 10_000, PRODUCTION_LEAD_TIME["small"])
                        elif renderer.btn_order_50k.collidepoint(mouse_pos) and player.cash >= (50000 * p_console.unit_cost):
                            sound_fx.play_success()
                            order_silicon(player, p_console, 50_000, PRODUCTION_LEAD_TIME["medium"])
                        elif renderer.btn_order_100k.collidepoint(mouse_pos) and player.cash >= (100000 * p_console.unit_cost):
                            sound_fx.play_success()
                            order_silicon(player, p_console, 100_000, PRODUCTION_LEAD_TIME["large"])
                        else:
                            if any(x.collidepoint(mouse_pos) for x in [renderer.btn_order_10k, renderer.btn_order_50k, renderer.btn_order_100k]):
                                sound_fx.play_error()
                                player.add_notification("Ошибка: Недостаточно средств!")

                    # ЛИЦЕНЗИИ / ЭКСКЛЮЗИВНЫЕ КОНТРАКТЫ СО СТУДИЯМИ
                    elif current_tab == "licenses":
                        btn_games = pygame.Rect(30, 100, 200, 30)
                        btn_studios = pygame.Rect(240, 100, 200, 30)
                        if btn_games.collidepoint(mouse_pos):
                            sound_fx.play_click()
                            licenses_sub_tab = "games"
                        elif btn_studios.collidepoint(mouse_pos):
                            sound_fx.play_click()
                            licenses_sub_tab = "studios"

                        if licenses_sub_tab == "games" and player.released_consoles:
                            target_console = player.released_consoles[0]
                            is_programmable = target_console.spec_info.get("is_programmable", False)

                            if is_programmable:
                                year_games = [g for g in games_list if g.year_available == market.current_year]
                                offset_y = 145
                                for g in year_games:
                                    btn_rect = pygame.Rect(540, offset_y + 20, 180, 40)
                                    is_porting = any(p.game.name == g.name for p in player.active_ports)
                                    is_acquired = g.acquired_by == 'player' or any(l_game.name == g.name for l_game in player.licensed_games)

                                    if btn_rect.collidepoint(mouse_pos) and not is_acquired and not is_porting and g.acquired_by is None:
                                        cost_total = g.license_cost
                                        double_cost = target_console.hardware_power < g.min_power
                                        if double_cost:
                                            cost_total *= 2.0

                                        if player.cash >= cost_total:
                                            sound_fx.play_success()
                                            player.cash -= cost_total
                                            player.active_ports.append(PortingProject(g, target_console, double_cost))
                                            player.add_notification(f"НАЧАТО ПОРТИРОВАНИЕ: {g.name}")
                                        else:
                                            sound_fx.play_error()
                                            player.add_notification("Ошибка: Недостаточно средств!")
                                    offset_y += 95

                        elif licenses_sub_tab == "studios":
                            # Клик по кнопке подписания студии
                            avail_studios = [s for s in STUDIO_CONTRACTS if s["year"] <= market.current_year]
                            offset_y = 145
                            for s in avail_studios[:5]:
                                btn_rect = pygame.Rect(540, offset_y + 20, 180, 40)
                                if btn_rect.collidepoint(mouse_pos):
                                    already_signed = any(x["name"] == s["name"] for x in player.signed_studios)
                                    if not already_signed and player.cash >= s["cost"]:
                                        sound_fx.play_success()
                                        player.cash -= s["cost"]
                                        player.signed_studios.append(s)
                                        player.add_notification(f"Подписан эксклюзив: {s['name']}!")
                                    elif not already_signed:
                                        sound_fx.play_error()
                                offset_y += 100

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drag_manager["active"]:
                    # Дроп на слоты
                    mx, my = pygame.mouse.get_pos()
                    slot_cpu_rect = pygame.Rect(45, 210, 320, 60)
                    slot_gpu_rect = pygame.Rect(45, 285, 320, 60)
                    slot_media_rect = pygame.Rect(45, 360, 320, 60)

                    if slot_cpu_rect.collidepoint((mx, my)) and drag_manager["type"] == "cpu":
                        selected_cpu_idx = drag_manager["index"]
                        sound_fx.play_success()
                        player.add_notification("CPU успешно установлен в плату!")
                    elif slot_gpu_rect.collidepoint((mx, my)) and drag_manager["type"] == "gpu":
                        selected_gpu_idx = drag_manager["index"]
                        sound_fx.play_success()
                        player.add_notification("GPU успешно установлен в плату!")
                    elif slot_media_rect.collidepoint((mx, my)) and drag_manager["type"] == "media":
                        selected_media_idx = drag_manager["index"]
                        sound_fx.play_success()
                        player.add_notification("Интерфейс носителя выбран!")
                    else:
                        sound_fx.play_error()

                    # Сброс драга
                    drag_manager["active"] = False

            elif event.type == pygame.KEYDOWN and player.naming_mode is None:
                if event.key == pygame.K_F1: current_tab = "market"
                elif event.key == pygame.K_F2: current_tab = "rd"
                elif event.key == pygame.K_F3: current_tab = "factory"
                elif event.key == pygame.K_F4: current_tab = "finance"
                elif event.key == pygame.K_F5: current_tab = "licenses"
                elif event.key == pygame.K_s:
                    sound_fx.play_click()
                    simulate_one_month(market, player, games_list)
                elif event.key == pygame.K_SPACE:
                    sound_fx.play_click()
                    auto_play = not auto_play
                elif event.key == pygame.K_r:
                    sound_fx.play_error()
                    current_difficulty = None
                    main()
                    return

        if auto_play:
            auto_tick_cooldown += 1
            if auto_tick_cooldown >= 30:
                simulate_one_month(market, player, games_list)
                auto_tick_cooldown = 0

        player.update_notifications()

        screen.fill(renderer.BG_COLOR)
        pygame.draw.rect(screen, renderer.PANEL_COLOR, (0, 0, WIDTH, 50))
        pygame.draw.line(screen, renderer.BORDER_COLOR, (0, 50), (WIDTH, 50), 2)

        for t_key, rect in renderer.tab_rects.items():
            is_active = (current_tab == t_key)
            bg = renderer.AMBER if is_active else renderer.PANEL_COLOR
            border = renderer.AMBER if is_active else renderer.BORDER_COLOR
            text_col = renderer.BG_COLOR if is_active else renderer.TEXT_WHITE
            label = {"market": "РЫНОК", "rd": "РАЗРАБОТКА (R&D)", "factory": "ФАБРИКА", "finance": "ФИНАНСЫ", "licenses": "ЛИЦЕНЗИИ"}[t_key]
            renderer.draw_button(screen, rect, label, renderer.font_title, bg, border, text_col)

        renderer.draw_text(screen, f"Год: {market.current_year} | Месяц: {market.current_month}", renderer.font_title, renderer.AMBER, 1020, 15)
        cash_color = renderer.GREEN if player.cash >= 0 else renderer.RED
        renderer.draw_text(screen, f"Баланс: ${player.cash:,.0f}", renderer.font_title, cash_color, 820, 15)

        if current_tab == "market":
            renderer.render_market_tab(screen, market, auto_play, renderer.font_title, renderer.font_body, renderer.btn_step, renderer.btn_auto, renderer.btn_reset, player)
        elif current_tab == "rd":
            renderer.render_rd_tab(screen, player, components, selected_cpu_idx, selected_gpu_idx, selected_media_idx, margin_value,
                                   renderer.font_title, renderer.font_body, renderer.font_large, rd_sub_tab,
                                   active_designer_type, chip_name, designer_core_idx, designer_cache_idx, designer_process_idx, designer_package_idx,
                                   player.active_chip_project, player.active_game_projects, console_name,
                                   licensing_selector_type, market.current_year, drag_manager)
        elif current_tab == "factory":
            renderer.render_factory_tab(screen, player, renderer.font_title, renderer.font_body, renderer.font_large, renderer.btn_order_10k, renderer.btn_order_50k, renderer.btn_order_100k)
        elif current_tab == "finance":
            renderer.render_finance_tab(screen, player, renderer.font_title, renderer.font_body, renderer.font_large)
        elif current_tab == "licenses":
            renderer.render_licenses_tab(screen, player, games_list, market.current_year, renderer.font_large, renderer.font_title, renderer.font_body, licenses_sub_tab)

        renderer.draw_notifications(screen, player)

        pygame.display.flip()
        clock.tick(60)


def simulate_one_month(market, player: PlayerCompany, games_list):
    if player.cash < 0:
        player.bankruptcy_months += 1
    else:
        player.bankruptcy_months = 0

    rd_expense = 0.0

    research_cost = player.advance_research()
    rd_expense += research_cost

    if player.active_chip_project:
        proj = player.active_chip_project
        points_generated = player.engineers * 4.0 * player.diff_settings["research_speed_multiplier"]
        proj.advance(points_generated)
        rd_expense += player.engineers * 400.0

        points_needed = max(10, proj.dev_months * 10)
        if proj.progress >= points_needed:
            sound_fx.play_success()
            if proj.category == "cpu":
                player.custom_cpus.append({"name": proj.name, "power": proj.power, "cost": proj.cost})
            else:
                player.custom_gpus.append({"name": proj.name, "power": proj.power, "cost": proj.cost})
            player.add_notification(f"ЧИП ГОТОВ К ПРОИЗВОДСТВУ: {proj.name}")
            player.active_chip_project = None

    if player.active_project:
        points_generated = player.engineers * 3.0
        for fp_game in player.active_game_projects:
            if fp_game.progress < 30.0:
                fp_game.advance(points_generated)
                rd_expense += 200.0

    remaining_ports = []
    for port in player.active_ports:
        port.months_left -= 1
        if port.months_left <= 0:
            sound_fx.play_success()
            player.licensed_games.append(port.game)
            port.console.library_size += 1
            if port.double_cost:
                port.console.library_quality = max(0.1, port.console.library_quality - 0.15)
                player.add_notification(f"ПОРТ ЗАВЕРШЕН: {port.game.name} (Ухудшен ТТХ)")
            else:
                player.add_notification(f"ПОРТ ЗАВЕРШЕН: {port.game.name}!")
        else:
            remaining_ports.append(port)
    player.active_ports = remaining_ports

    # Логика работы эксклюзивных контрактов (студии выпускают игры раз в 6 месяцев)
    if player.released_consoles and player.signed_studios:
        player.studio_exclusive_timer += 1
        if player.studio_exclusive_timer >= 6:
            player.studio_exclusive_timer = 0
            studio = random.choice(player.signed_studios)
            p_con = player.released_consoles[0]
            p_con.library_size += 1
            # Студия выпускает высококачественную игру (качество 0.85)
            p_con.library_quality = (p_con.library_quality * (p_con.library_size - 1) + 0.85) / p_con.library_size
            sound_fx.play_notify()
            player.add_notification(f"{studio['name']} выпустила эксклюзивный хит!")

    if player.active_project:
        eng_points = player.engineers * 5.0
        project = player.active_project
        project.advance_development(eng_points)
        rd_expense += player.engineers * 500.0

        if project.phase == "ready":
            sound_fx.play_success()
            completed_fp_games = [g for g in player.active_game_projects if g.progress >= 30.0]
            start_library_size = 5 + len(completed_fp_games)
            quality_boost = sum(0.04 for g in completed_fp_games)
            final_quality = min(1.0, project.quality + quality_boost)

            player_console = Console(
                name=project.name,
                launch_year=market.current_year,
                price=project.retail_price,
                hardware_power=project.hardware_power,
                library_size=start_library_size,
                library_quality=final_quality,
                marketing_budget=35_000,
                color=(241, 196, 15),
                spec_info={
                    "cost": project.unit_cost,
                    "cpu_name": project.cpu["name"],
                    "gpu_name": project.gpu["name"],
                    "is_programmable": project.media.get("is_programmable", False)
                },
                is_player=True
            )
            player_console.launch_month = market.current_month
            market.add_console(player_console)
            player.released_consoles.append(player_console)

            player.active_project = None
            player.active_game_projects = []
            player.add_notification(f"УСПЕШНЫЙ ЗАПУСК КОНСОЛИ: {player_console.name}!")

    arrived_stock = player.process_monthly_logistics()
    if arrived_stock > 0:
        sound_fx.play_notify()
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

        # Роялти + бонусы от эксклюзивных контрактов
        if p_console.installed_base > 0:
            base_royalty_payout = 0.15 + sum(s["royalty_bonus"] for s in player.signed_studios)
            for game in player.licensed_games:
                base_royalty_payout += game.base_royalty
            royalty_revenue = p_console.installed_base * base_royalty_payout

        # Динамический расчет стоимости маркетинга
        m_info = MARKETING_TYPES.get(p_console.marketing_type, {"cost": 0})
        marketing_expenses = m_info["cost"]
        warehouse_cost = p_console.inventory * 1.0
        player.reputation.update(p_console.library_quality, marketing_expenses, shortage_ratio)

    unowned_games = [g for g in games_list if g.year_available == market.current_year and g.acquired_by is None]
    for game in unowned_games:
        if random.random() < 0.12 and market.consoles:
            ai_choice = random.choice([c for c in market.consoles if not c.is_player])
            game.acquired_by = ai_choice.name
            ai_choice.library_size += 1

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