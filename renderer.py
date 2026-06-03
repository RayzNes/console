# renderer.py

import pygame

pygame.font.init()
font_large = pygame.font.Font(None, 32)
font_title = pygame.font.Font(None, 24)
font_body = pygame.font.Font(None, 18)

BG_COLOR = (12, 14, 20)
PANEL_COLOR = (18, 21, 32)
BORDER_COLOR = (32, 38, 58)
TEXT_WHITE = (235, 240, 250)
TEXT_MUTED = (115, 128, 142)
GREEN = (46, 204, 113)
BLUE = (52, 152, 219)
RED = (231, 76, 60)
AMBER = (241, 196, 15)

tab_rects = {
    "market": pygame.Rect(10, 10, 110, 30),
    "rd": pygame.Rect(130, 10, 220, 30),
    "factory": pygame.Rect(360, 10, 110, 30),
    "finance": pygame.Rect(480, 10, 110, 30),
    "licenses": pygame.Rect(600, 10, 150, 30)
}

btn_step = pygame.Rect(45, 465, 250, 40)
btn_auto = pygame.Rect(45, 515, 250, 40)
btn_reset = pygame.Rect(45, 565, 250, 40)

# R&D Кадры
btn_hire = pygame.Rect(800, 150, 160, 35)
btn_fire = pygame.Rect(800, 200, 160, 35)

# Координаты кнопок подвкладок R&D
btn_sub_res = pygame.Rect(45, 110, 180, 30)
btn_sub_design = pygame.Rect(235, 110, 220, 30)
btn_sub_console = pygame.Rect(465, 110, 180, 30)

# Конструктор чипов
btn_chip_type = pygame.Rect(45, 200, 250, 35)
btn_chip_name = pygame.Rect(45, 250, 250, 35)
btn_chip_core = pygame.Rect(45, 300, 250, 35)
btn_chip_cache = pygame.Rect(45, 350, 250, 35)
btn_chip_process = pygame.Rect(45, 400, 250, 35)
btn_chip_package = pygame.Rect(45, 450, 250, 35)
btn_chip_build = pygame.Rect(45, 510, 250, 45)

btn_chip_license_cpu = pygame.Rect(320, 200, 250, 35)
btn_chip_license_gpu = pygame.Rect(320, 250, 250, 35)

# Сборщик Консолей
btn_console_name = pygame.Rect(45, 440, 350, 35)
btn_console_launch = pygame.Rect(45, 500, 350, 45)
btn_fp_game_create = pygame.Rect(45, 560, 350, 40)

# Заказы логистики
btn_order_10k = pygame.Rect(45, 500, 250, 40)
btn_order_50k = pygame.Rect(310, 500, 250, 40)
btn_order_100k = pygame.Rect(575, 500, 250, 40)


def draw_text(surface, text, font, color, x, y):
    img = font.render(text, True, color)
    surface.blit(img, (x, y))


def draw_button(surface, rect, text, font, bg_color, border_color, text_color):
    pygame.draw.rect(surface, bg_color, rect, border_radius=4)
    pygame.draw.rect(surface, border_color, rect, width=1, border_radius=4)
    img = font.render(text, True, text_color)
    img_rect = img.get_rect(center=rect.center)
    surface.blit(img, img_rect)


def draw_notifications(screen, player):
    offset_y = 70
    for text, frames in player.notifications:
        alpha = min(255, int(frames * 4.25)) if frames < 60 else 255
        s = pygame.Surface((350, 45), pygame.SRCALPHA)
        s.fill((18, 21, 32, alpha))
        pygame.draw.rect(s, (241, 196, 15, alpha), (0, 0, 350, 45), 1, border_radius=4)
        screen.blit(s, (850, offset_y))

        img = font_body.render(text, True, (235, 240, 250))
        img.set_alpha(alpha)
        screen.blit(img, (865, offset_y + 15))
        offset_y += 55


def draw_chart(surface, x, y, w, h, market_history, consoles):
    chart_rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, PANEL_COLOR, chart_rect)
    pygame.draw.rect(surface, BORDER_COLOR, chart_rect, 1)

    if not market_history:
        draw_text(surface, "Начало симуляции. Ожидание хода...", font_body, TEXT_MUTED, x + 20, y + 20)
        return

    max_capacity = max(entry["capacity"] for entry in market_history) if market_history else 1
    max_sales = max(entry["total_sold"] for entry in market_history) if market_history else 1
    max_value = max(max_capacity, max_sales, 1)

    graph_rect = pygame.Rect(x + 40, y + 20, w - 60, h - 60)
    pygame.draw.line(surface, TEXT_WHITE, (graph_rect.x, graph_rect.y), (graph_rect.x, graph_rect.bottom), 1)
    pygame.draw.line(surface, TEXT_WHITE, (graph_rect.x, graph_rect.bottom), (graph_rect.right, graph_rect.bottom), 1)

    colors = {}
    for console in consoles:
        colors[console.name] = AMBER if console.is_player else TEXT_MUTED

    months_data = {}
    for i, entry in enumerate(market_history):
        month_key = f"{entry['year']}_{entry['month']}"
        months_data[month_key] = {
            "index": i,
            "capacity": entry["capacity"],
            "sales": entry["console_sales"]
        }

    max_index = len(market_history) - 1

    if max_index == 0:
        data = list(months_data.values())[0]
        x_pos = graph_rect.x + graph_rect.width / 2
        y_pos = graph_rect.bottom - (data["capacity"] / max_value) * graph_rect.height
        pygame.draw.circle(surface, AMBER, (int(x_pos), int(y_pos)), 4)
        draw_text(surface, f"Емкость: {data['capacity']:,}", font_body, TEXT_WHITE, int(x_pos) + 10, int(y_pos) - 10)
        return

    prev_point = None
    for month_key, data in months_data.items():
        x_pos = graph_rect.x + (data["index"] / max_index) * graph_rect.width
        y_pos = graph_rect.bottom - (data["capacity"] / max_value) * graph_rect.height
        point = (int(x_pos), int(y_pos))
        if prev_point:
            draw_dashed_line(surface, prev_point, point, TEXT_MUTED, 2)
        prev_point = point

    console_data = {}
    for console in consoles:
        console_data[console.name] = []

    for month_key, data in months_data.items():
        for console_name, sales in data["sales"].items():
            if console_name not in console_data:
                console_data[console_name] = []
            console_data[console_name].append(sales)

    for console_name, sales_list in console_data.items():
        if not sales_list:
            continue
        color = colors.get(console_name, TEXT_MUTED)
        prev_point = None
        for i, sales in enumerate(sales_list):
            x_pos = graph_rect.x + (i / max_index) * graph_rect.width
            y_pos = graph_rect.bottom - (sales / max_value) * graph_rect.height
            point = (int(x_pos), int(y_pos))
            if prev_point:
                pygame.draw.line(surface, color, prev_point, point, 2)
            prev_point = point

    draw_text(surface, "Продажи", font_body, TEXT_MUTED, x + 5, y + 10)


def draw_dashed_line(surface, start_pos, end_pos, color, width=1, dash_length=5):
    x1, y1 = start_pos
    x2, y2 = end_pos
    length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    if length == 0: return
    dash_count = int(length / dash_length)
    for i in range(dash_count):
        t1 = i / dash_count
        t2 = (i + 0.5) / dash_count
        start = (int(x1 + (x2 - x1) * t1), int(y1 + (y2 - y1) * t1))
        end = (int(x1 + (x2 - x1) * t2), int(y1 + (y2 - y1) * t2))
        pygame.draw.line(surface, color, start, end, width)


def render_difficulty_screen(screen, font_large, font_title, font_body):
    screen.fill(BG_COLOR)
    draw_text(screen, "CHOOSE YOUR DIFFICULTY / ВЫБЕРИТЕ СЛОЖНОСТЬ", font_large, AMBER, 300, 250)
    draw_button(screen, pygame.Rect(462, 350, 300, 50), "EASY (ЛЕГКО)", font_title, PANEL_COLOR, GREEN, GREEN)
    draw_button(screen, pygame.Rect(462, 420, 300, 50), "MEDIUM (СРЕДНЕ)", font_title, PANEL_COLOR, BLUE, BLUE)
    draw_button(screen, pygame.Rect(462, 490, 300, 50), "HARD (ТЯЖЕЛО)", font_title, PANEL_COLOR, RED, RED)


def render_bankruptcy_screen(screen, font_large, font_title):
    screen.fill((20, 5, 5))
    draw_text(screen, "BANKRUPTCY - GAME OVER / БАНКРОТСТВО", font_large, RED, 350, 350)
    draw_text(screen, "Компания ликвидирована за долги.", font_title, TEXT_WHITE, 440, 410)
    draw_button(screen, pygame.Rect(462, 480, 300, 50), "ПЕРЕЗАПУСТИТЬ ИГРУ [R]", font_title, PANEL_COLOR, AMBER, AMBER)


def render_market_tab(screen, market, auto_play, font_title, font_body, btn_step, btn_auto, btn_reset, player):
    draw_text(screen, "МАРКЕТИНГОВАЯ ОБСТАНОВКА И ПРОДАЖИ", font_title, AMBER, 30, 70)
    pygame.draw.rect(screen, PANEL_COLOR, (730, 60, 464, 50))
    pygame.draw.rect(screen, BORDER_COLOR, (730, 60, 464, 50), 1)
    rep = player.reputation
    draw_text(screen,
              f"Бренд: Качество: {rep.quality_perception:.2f} | Сила: {rep.innovation_score:.2f} | Лояльность: {rep.customer_loyalty:.2f}",
              font_body, TEXT_WHITE, 745, 78)

    draw_chart(screen, 30, 120, 1164, 300, market.history, market.consoles)

    # Левая интерактивная панель управления ценой и маркетингом
    pygame.draw.rect(screen, PANEL_COLOR, (30, 440, 280, 280))
    pygame.draw.rect(screen, BORDER_COLOR, (30, 440, 280, 280), 1)
    draw_text(screen, "ПАНЕЛЬ УПРАВЛЕНИЯ", font_title, TEXT_WHITE, 45, 455)

    draw_button(screen, btn_step, "ШАГ ХОДА (+1 Месяц)", font_body, PANEL_COLOR, BORDER_COLOR, AMBER)
    auto_color = GREEN if auto_play else RED
    auto_text = "АВТО-СИМУЛЯЦИЯ: ВКЛ" if auto_play else "АВТО-СИМУЛЯЦИЯ: ВЫКЛ"
    draw_button(screen, btn_auto, auto_text, font_body, PANEL_COLOR, BORDER_COLOR, auto_color)
    draw_button(screen, btn_reset, "СБРОСИТЬ ИГРУ", font_body, PANEL_COLOR, RED, TEXT_WHITE)

    # Ценовые войны и Смена маркетинга (если у игрока выпущена консоль)
    if player.released_consoles:
        p_con = player.released_consoles[0]
        # Изменение цены (Ценовые войны)
        draw_text(screen, f"Цена: ${p_con.price} (Баз: ${p_con.original_price})", font_body, AMBER, 45, 620)
        pygame.draw.rect(screen, PANEL_COLOR, (45, 640, 110, 30))
        draw_button(screen, pygame.Rect(45, 640, 50, 30), "-$10", font_body, PANEL_COLOR, RED, RED)
        draw_button(screen, pygame.Rect(105, 640, 50, 30), "+$10", font_body, PANEL_COLOR, GREEN, GREEN)

        # Тип маркетинга
        m_modes = ["none", "guerrilla", "print", "tv"]
        curr_idx = m_modes.index(getattr(p_con, "marketing_type", "print"))
        next_mode = m_modes[(curr_idx + 1) % len(m_modes)]
        from config import MARKETING_TYPES
        m_info = MARKETING_TYPES.get(p_con.marketing_type, {"name": "Нет"})
        draw_text(screen, f"Маркетинг: {m_info['name']}", font_body, TEXT_WHITE, 165, 620)
        draw_button(screen, pygame.Rect(165, 640, 130, 30), "Сменить рекламу", font_body, PANEL_COLOR, BORDER_COLOR,
                    AMBER)

    if player.bankruptcy_months > 0:
        draw_text(screen, f"КРИЗИС! БАЛАНС < 0!", font_body, RED, 45, 680)
        draw_text(screen, f"Банкротство через {4 - player.bankruptcy_months} мес.", font_body, RED, 45, 695)

    # СРАВНИТЕЛЬНАЯ ТАБЛИЦА ХАРАКТЕРИСТИК КОНСОЛЕЙ
    pygame.draw.rect(screen, PANEL_COLOR, (330, 440, 864, 280))
    pygame.draw.rect(screen, BORDER_COLOR, (330, 440, 864, 280), 1)
    draw_text(screen, "СРАВНИТЕЛЬНАЯ ТАБЛИЦА КОНСОЛЕЙ НА РЫНКЕ", font_title, AMBER, 345, 455)

    # Заголовки колонок
    col_headers = [
        ("Название", 345),
        ("Цена", 540),
        ("Мощность", 620),
        ("Игр в либ.", 710),
        ("Качество", 800),
        ("Реклама", 880),
        ("Инсталл-База", 1000),
        ("Склад", 1110)
    ]
    for header, x_pos in col_headers:
        draw_text(screen, header, font_body, TEXT_MUTED, x_pos, 485)

    pygame.draw.line(screen, BORDER_COLOR, (345, 502), (1180, 502), 1)

    # Вывод строк таблицы
    active_consoles = []
    for c in market.consoles:
        is_active = c.launch_year < market.current_year or (
                c.launch_year == market.current_year and c.launch_month <= market.current_month)
        if is_active:
            active_consoles.append(c)

    offset_y = 510
    for con in active_consoles[:5]:  # Вывод до 5 систем
        row_color = con.color if con.is_player else TEXT_WHITE
        bg_highlight = (24, 28, 40) if con.is_player else PANEL_COLOR

        # Подложка под строку игрока
        if con.is_player:
            pygame.draw.rect(screen, bg_highlight, (340, offset_y - 2, 844, 22))

        from config import MARKETING_TYPES
        m_name = MARKETING_TYPES.get(con.marketing_type, {"name": "Нет"})["name"]

        draw_text(screen, con.name[:18], font_body, row_color, 345, offset_y)
        draw_text(screen, f"${con.price}", font_body, TEXT_WHITE, 540, offset_y)
        draw_text(screen, f"{con.hardware_power:.1f} HW", font_body, TEXT_WHITE, 620, offset_y)
        draw_text(screen, f"{con.library_size}", font_body, TEXT_WHITE, 710, offset_y)
        draw_text(screen, f"{con.library_quality * 100:.0f}%", font_body, TEXT_WHITE, 800, offset_y)
        draw_text(screen, m_name, font_body, TEXT_MUTED, 880, offset_y)
        draw_text(screen, f"{con.installed_base:,}", font_body, TEXT_WHITE, 1000, offset_y)
        draw_text(screen, f"{con.inventory:,} шт.", font_body, row_color, 1110, offset_y)

        offset_y += 24


def render_rd_tab(screen, player, components_db, sel_cpu, sel_gpu, sel_media, margin,
                  font_title, font_body, font_large, sub_tab,
                  active_designer_type, chip_name, designer_core_idx, designer_cache_idx, designer_process_idx,
                  designer_package_idx,
                  active_chip_project, active_game_projects, console_name,
                  licensing_selector_type, current_year, drag_manager=None):
    draw_text(screen, "ОТДЕЛ ИССЛЕДОВАНИЙ И РАЗРАБОТОК (R&D)", font_title, AMBER, 30, 70)

    # Вкладки R&D
    draw_button(screen, btn_sub_res, "1. ИССЛЕДОВАНИЯ", font_body, AMBER if sub_tab == "research" else PANEL_COLOR,
                BORDER_COLOR, TEXT_WHITE)
    draw_button(screen, btn_sub_design, "2. КОНСТРУКТОР ЧИПОВ", font_body,
                AMBER if sub_tab == "designer" else PANEL_COLOR, BORDER_COLOR, TEXT_WHITE)
    draw_button(screen, btn_sub_console, "3. СБОРКА СИСТЕМ", font_body, AMBER if sub_tab == "console" else PANEL_COLOR,
                BORDER_COLOR, TEXT_WHITE)

    # Кадровый штаб
    pygame.draw.rect(screen, PANEL_COLOR, (800, 250, 394, 440))
    pygame.draw.rect(screen, BORDER_COLOR, (800, 250, 394, 440), 1)
    draw_text(screen, "ШТАТ ИНЖЕНЕРОВ R&D", font_title, TEXT_WHITE, 815, 270)
    draw_text(screen, f"Активные инженеры: {player.engineers}", font_large, AMBER, 815, 300)
    draw_text(screen, f"Фонд з/п (в месяц): ${player.get_monthly_salaries():,.0f}", font_body, TEXT_WHITE, 815, 335)

    draw_button(screen, btn_hire, "НАНЯТЬ (+1)", font_body, PANEL_COLOR, GREEN, GREEN)
    draw_button(screen, btn_fire, "УВОЛИТЬ (-1)", font_body, PANEL_COLOR, RED, RED)

    # 1. ТЕХНОЛОГИЧЕСКИЕ ИССЛЕДОВАНИЯ (ВИЗУАЛЬНОЕ ДЕРЕВО)
    if sub_tab == "research":
        pygame.draw.rect(screen, PANEL_COLOR, (30, 150, 750, 540))
        pygame.draw.rect(screen, BORDER_COLOR, (30, 150, 750, 540), 1)
        draw_text(screen, "ВИЗУАЛЬНАЯ СЕТКА ТЕХНОЛОГИЙ (КЛИК ДЛЯ ИЗУЧЕНИЯ)", font_title, AMBER, 45, 165)

        # Отрисовка связей векторов
        for node in player.tech_tree.nodes.values():
            start_pos = (30 + node.coords[0] + 55, 150 + node.coords[1] + 15)
            for prereq_id in node.prerequisites:
                prereq_node = player.tech_tree.nodes[prereq_id]
                end_pos = (30 + prereq_node.coords[0] + 55, 150 + prereq_node.coords[1] + 15)
                line_color = GREEN if prereq_node.researched else TEXT_MUTED
                pygame.draw.line(screen, line_color, start_pos, end_pos, 2)

        # Отрисовка нод (кнопок)
        for node in player.tech_tree.nodes.values():
            x, y = 30 + node.coords[0], 150 + node.coords[1]
            node_rect = pygame.Rect(x, y, 110, 35)

            is_active = (player.active_research == node)
            if node.researched:
                bg = GREEN
                txt_col = BG_COLOR
            elif is_active:
                bg = BLUE
                txt_col = TEXT_WHITE
            elif node.year_available > current_year:
                bg = (10, 12, 16)
                txt_col = RED
            else:
                # Проверим, открыты ли пререквизиты
                unlocked = all(player.tech_tree.nodes[p].researched for p in node.prerequisites)
                bg = AMBER if unlocked else (25, 25, 30)
                txt_col = BG_COLOR if unlocked else TEXT_MUTED

            draw_button(screen, node_rect, node.name[:14], font_body, bg, BORDER_COLOR, txt_col)

        if player.active_research:
            node = player.active_research
            draw_text(screen, f"Изучается: {node.name}", font_large, AMBER, 45, 620)
            pts_needed = max(10, node.base_months * 10)
            percent = min(100.0, (node.progress_points / pts_needed) * 100.0)
            pygame.draw.rect(screen, BG_COLOR, (45, 650, 500, 20))
            pygame.draw.rect(screen, GREEN, (45, 650, int(500 * (percent / 100.0)), 20))
            draw_text(screen, f"Прогресс: {percent:.1f}%", font_body, TEXT_WHITE, 560, 650)

    # 2. КОНСТРУКТОР ЧИПОВ И ЛИЦЕНЗИРОВАНИЕ
    elif sub_tab == "designer":
        pygame.draw.rect(screen, PANEL_COLOR, (30, 150, 750, 540))
        pygame.draw.rect(screen, BORDER_COLOR, (30, 150, 750, 540), 1)
        draw_text(screen, "ИНЖЕНЕРНЫЙ СИНТЕЗ ЧИПОВ И ЛИЦЕНЗИИ", font_large, AMBER, 45, 165)

        if player.active_chip_project:
            proj = player.active_chip_project
            draw_text(screen, f"Идет R&D чипа: {proj.name} ({proj.category.upper()})", font_title, TEXT_WHITE, 45, 230)
            pts_needed = max(10, proj.dev_months * 10)
            percent = min(100.0, (proj.progress / pts_needed) * 100.0)
            pygame.draw.rect(screen, BG_COLOR, (45, 270, 500, 25))
            pygame.draw.rect(screen, GREEN, (45, 270, int(500 * (percent / 100.0)), 25))
            draw_text(screen, f"Прогресс: {percent:.1f}%", font_body, TEXT_WHITE, 45, 310)
        else:
            draw_text(screen, "СОБСТВЕННЫЙ R&D ЧИПА (ДОРОГО И ДОЛГО)", font_title, AMBER, 45, 210)

            type_label = f"Тип чипа: {active_designer_type.upper()}"
            draw_button(screen, btn_chip_type, type_label, font_body, PANEL_COLOR, BORDER_COLOR, TEXT_WHITE)

            border_color = AMBER if player.naming_mode == "chip" else BORDER_COLOR
            name_label = f"Имя чипа: {chip_name}" if player.naming_mode != "chip" else f"Ввод: {player.input_buffer}_"
            draw_button(screen, btn_chip_name, name_label, font_body, PANEL_COLOR, border_color, TEXT_WHITE)

            draw_text(screen, "Транзисторы и упаковка:", font_body, TEXT_MUTED, 45, 300)

            cores = [n for n in player.tech_tree.nodes.values() if n.category == active_designer_type and n.researched]
            processes = [n for n in player.tech_tree.nodes.values() if
                         n.category == "manufacturing" and "tech_" in n.node_id and n.researched]
            packages = [n for n in player.tech_tree.nodes.values() if
                        n.category == "manufacturing" and "package_" in n.node_id and n.researched]

            core = cores[designer_core_idx % len(cores)] if cores else None
            process = processes[designer_process_idx % len(processes)] if processes else None
            package = packages[designer_package_idx % len(packages)] if packages else None

            core_name = f"Ядро: {core.name}" if core else "Ядро: нет"
            draw_button(screen, btn_chip_core, core_name, font_body, PANEL_COLOR, BORDER_COLOR, TEXT_WHITE)

            proc_name = f"Техпроцесс: {process.name}" if process else "Техпроцесс: нет"
            draw_button(screen, btn_chip_process, proc_name, font_body, PANEL_COLOR, BORDER_COLOR, TEXT_WHITE)

            pack_name = f"Корпус: {package.name}" if package else "Корпус: нет"
            draw_button(screen, btn_chip_package, pack_name, font_body, PANEL_COLOR, BORDER_COLOR, TEXT_WHITE)

            if active_designer_type == "cpu":
                caches = [n for n in player.tech_tree.nodes.values() if
                          n.category == "memory" and "l1_" in n.node_id and n.researched]
                cache = caches[designer_cache_idx % len(caches)] if caches else None
                cache_name = f"Кэш: {cache.name}" if cache else "Кэш: нет"
                draw_button(screen, btn_chip_cache, cache_name, font_body, PANEL_COLOR, BORDER_COLOR, TEXT_WHITE)

                p, c = player.tech_tree.calculate_custom_cpu(core, cache, process, package)
                rd_cost = 50000.0 + (core.base_cost * 0.5)
                dev_months = 4
            else:
                mems = [n for n in player.tech_tree.nodes.values() if
                        n.category == "memory" and "mem_" in n.node_id and n.researched]
                mem = mems[designer_cache_idx % len(mems)] if mems else None
                mem_name = f"Память: {mem.name}" if mem else "Память: нет"
                draw_button(screen, btn_chip_cache, mem_name, font_body, PANEL_COLOR, BORDER_COLOR, TEXT_WHITE)

                p, c = player.tech_tree.calculate_custom_gpu(core, mem, process, package)
                rd_cost = 40000.0 + (core.base_cost * 0.5)
                dev_months = 4

            draw_text(screen, f"ТТХ: {p} HW | Себест: ${c} | R&D: ${rd_cost:,.0f} | Срок: {dev_months} мес.", font_body,
                      AMBER, 45, 490)

            b_color = AMBER if player.cash >= rd_cost else RED
            draw_button(screen, btn_chip_build, "НАЧАТЬ РАЗРАБОТКУ ЧИПА (R&D)", font_body, PANEL_COLOR, b_color,
                        TEXT_WHITE)

            draw_text(screen, "ЛИЦЕНЗИРОВАНИЕ СТОРОННИХ ЧИПОВ", font_title, GREEN, 350, 165)
            draw_button(screen, btn_chip_license_cpu, "Выбрать CPU для лицензии", font_body, PANEL_COLOR, BORDER_COLOR,
                        TEXT_WHITE)
            draw_button(screen, btn_chip_license_gpu, "Выбрать GPU для лицензии", font_body, PANEL_COLOR, BORDER_COLOR,
                        TEXT_WHITE)

            if licensing_selector_type:
                from config import HISTORICAL_CPUS, HISTORICAL_GPUS
                list_chips = HISTORICAL_CPUS if licensing_selector_type == "cpu" else HISTORICAL_GPUS
                avail_lic = [c for c in list_chips if c["year"] <= current_year]

                pygame.draw.rect(screen, PANEL_COLOR, (650, 250, 544, 440))
                pygame.draw.rect(screen, BORDER_COLOR, (650, 250, 544, 440), 1)
                draw_text(screen, f"ДОСТУПНЫЕ {licensing_selector_type.upper()} ДЛЯ ЛИЦЕНЗИРОВАНИЯ:", font_title, AMBER,
                          665, 270)

                lic_offset_y = 310
                for item in avail_lic[:4]:
                    draw_text(screen, f"{item['name']} ({item['power']} HW)", font_body, TEXT_WHITE, 665, lic_offset_y)
                    draw_text(screen, f"Цена: ${item['license_fee']:,} | Unit: ${item['cost']}", font_body, TEXT_MUTED,
                              665, lic_offset_y + 15)

                    buy_rect = pygame.Rect(1020, lic_offset_y, 150, 30)
                    already_bought = item["name"] in [x["name"] for x in (
                        player.licensed_cpus if licensing_selector_type == "cpu" else player.licensed_gpus)]

                    if already_bought:
                        draw_button(screen, buy_rect, "КУПЛЕНО", font_body, GREEN, GREEN, BG_COLOR)
                    else:
                        b_col = GREEN if player.cash >= item["license_fee"] else RED
                        draw_button(screen, buy_rect, "ЛИЦЕНЗИРОВАТЬ", font_body, PANEL_COLOR, b_col, TEXT_WHITE)

                    lic_offset_y += 50

    # 3. СБОРКА СИСТЕМ (DRAG AND DROP КОНСТРУКТОР)
    elif sub_tab == "console":
        pygame.draw.rect(screen, PANEL_COLOR, (30, 150, 750, 540))
        pygame.draw.rect(screen, BORDER_COLOR, (30, 150, 750, 540), 1)

        if not player.active_project:
            draw_text(screen, "ПЕРЕТАЩИТЕ (DRAG-AND-DROP) КОМПОНЕНТЫ В ГНЕЗДА", font_large, AMBER, 45, 165)

            all_cpus = player.custom_cpus + player.licensed_cpus
            all_gpus = player.custom_gpus + player.licensed_gpus
            all_media = components_db["media"]

            # Гнезда (Targets) для дропа
            slot_cpu_rect = pygame.Rect(45, 210, 320, 60)
            slot_gpu_rect = pygame.Rect(45, 285, 320, 60)
            slot_media_rect = pygame.Rect(45, 360, 320, 60)

            # Получение текущих выбранных компонентов по индексам
            cpu = all_cpus[sel_cpu % len(all_cpus)] if all_cpus else None
            gpu = all_gpus[sel_gpu % len(all_gpus)] if all_gpus else None
            med = all_media[sel_media % len(all_media)] if all_media else None

            # Прорисовка гнезд
            cpu_border = AMBER if (drag_manager and drag_manager.get('type') == 'cpu') else BORDER_COLOR
            pygame.draw.rect(screen, (22, 26, 40), slot_cpu_rect, border_radius=4)
            pygame.draw.rect(screen, cpu_border, slot_cpu_rect, width=2, border_radius=4)
            cpu_lbl = f"CPU: {cpu['name']} ({cpu['power']} HW)" if cpu else "Перетащите CPU сюда"
            draw_text(screen, cpu_lbl, font_body, TEXT_WHITE, 60, 230)

            gpu_border = AMBER if (drag_manager and drag_manager.get('type') == 'gpu') else BORDER_COLOR
            pygame.draw.rect(screen, (22, 26, 40), slot_gpu_rect, border_radius=4)
            pygame.draw.rect(screen, gpu_border, slot_gpu_rect, width=2, border_radius=4)
            gpu_lbl = f"GPU: {gpu['name']} ({gpu['power']} HW)" if gpu else "Перетащите GPU сюда"
            draw_text(screen, gpu_lbl, font_body, TEXT_WHITE, 60, 305)

            med_border = AMBER if (drag_manager and drag_manager.get('type') == 'media') else BORDER_COLOR
            pygame.draw.rect(screen, (22, 26, 40), slot_media_rect, border_radius=4)
            pygame.draw.rect(screen, med_border, slot_media_rect, width=2, border_radius=4)
            med_lbl = f"Носитель: {med['name']}" if med else "Перетащите Носитель сюда"
            draw_text(screen, med_lbl, font_body, TEXT_WHITE, 60, 380)

            # Пул доступных компонентов для перетаскивания (справа)
            pygame.draw.rect(screen, (10, 12, 18), (400, 210, 350, 310))
            pygame.draw.rect(screen, BORDER_COLOR, (400, 210, 350, 310), 1)
            draw_text(screen, "ДОСТУПНЫЕ ПЛАТЫ ДЛЯ ПЕРЕНОСА:", font_body, AMBER, 415, 220)

            # Создадим список элементов для отрисовки в пуле
            items_to_render = []
            for idx, c in enumerate(all_cpus):
                items_to_render.append(
                    {"type": "cpu", "name": f"CPU: {c['name'][:14]}", "index": idx, "cost": c["cost"]})
            for idx, g in enumerate(all_gpus):
                items_to_render.append(
                    {"type": "gpu", "name": f"GPU: {g['name'][:14]}", "index": idx, "cost": g["cost"]})
            for idx, m in enumerate(all_media):
                items_to_render.append(
                    {"type": "media", "name": f"Media: {m['name'][:14]}", "index": idx, "cost": m["cost"]})

            offset_card_y = 245
            for item in items_to_render[:6]:  # Ограничиваем список
                card_rect = pygame.Rect(415, offset_card_y, 320, 35)
                pygame.draw.rect(screen, PANEL_COLOR, card_rect, border_radius=4)
                pygame.draw.rect(screen, BORDER_COLOR, card_rect, width=1, border_radius=4)
                draw_text(screen, f"{item['name']} | ${item['cost']}", font_body, TEXT_WHITE, 430, offset_card_y + 10)
                offset_card_y += 42

            # Наценка и выпуск
            if cpu and gpu and med:
                unit_cost = cpu["cost"] + gpu["cost"] + med["cost"]
                if "Floppy" in med["name"]: unit_cost += 80.0
                retail_p = int(unit_cost * margin)
                power = (cpu["power"] + gpu["power"]) * med["power_mult"]

                draw_text(screen, f"Текущая Наценка: {margin:.1f}x  |  Розничная цена: ${retail_p}", font_body,
                          TEXT_WHITE, 45, 435)
                draw_button(screen, pygame.Rect(45, 455, 50, 30), "-", font_title, PANEL_COLOR, BORDER_COLOR, RED)
                draw_button(screen, pygame.Rect(110, 455, 50, 30), "+", font_title, PANEL_COLOR, BORDER_COLOR, GREEN)

                border_color = AMBER if player.naming_mode == "console" else BORDER_COLOR
                name_label = f"Имя консоли: {console_name}" if player.naming_mode != "console" else f"Ввод: {player.input_buffer}_"
                draw_button(screen, btn_console_name, name_label, font_body, PANEL_COLOR, border_color, TEXT_WHITE)

                draw_text(screen, f"Итоговая себестоимость: ${unit_cost:.1f} | Мощность: {power:.1f} HW", font_body,
                          TEXT_MUTED, 45, 520)
                draw_button(screen, btn_console_launch, "ЗАПУСТИТЬ КОНСОЛЬ В ПРОИЗВОДСТВО", font_title, PANEL_COLOR,
                            AMBER, AMBER)

            # Прорисовка тащащегося элемента поверх всего
            if drag_manager and drag_manager.get('active'):
                mx, my = pygame.mouse.get_pos()
                drag_rect = pygame.Rect(mx - 80, my - 15, 160, 30)
                pygame.draw.rect(screen, AMBER, drag_rect, border_radius=4)
                draw_text(screen, drag_manager['name'][:18], font_body, BG_COLOR, mx - 70, my - 7)

        else:
            project = player.active_project
            draw_text(screen, f"В РАЗРАБОТКЕ: {project.name}", font_large, AMBER, 45, 165)

            phase_titles = {
                "design": "ПРОЕКТИРОВАНИЕ ЧИПОВ И СХЕМ", "prototype": "СБОРКА РАБОЧЕГО ПРОТОТИПА",
                "testing": "ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ И ПОЛИРОВКА", "ready": "ГОТОВО К ВЫПУСКУ"
            }
            draw_text(screen, f"Фаза: {phase_titles[project.phase]}", font_title, TEXT_WHITE, 45, 210)

            pygame.draw.rect(screen, BG_COLOR, (45, 250, 500, 25))
            pygame.draw.rect(screen, GREEN, (45, 250, int(500 * (project.progress / 100.0)), 25))
            draw_text(screen, f"{project.progress:.1f}%", font_body, TEXT_WHITE, 260, 255)

            draw_text(screen, f"Стартовая линейка игр: {len(active_game_projects)} шт.", font_title, TEXT_WHITE, 45,
                      300)
            for i, fp_game in enumerate(active_game_projects):
                draw_text(screen, f"- {fp_game.name} (R&D: {min(100.0, fp_game.progress):.1f}%)", font_body, TEXT_MUTED,
                          45, 330 + i * 20)

            draw_button(screen, btn_fp_game_create, "Создать собственную Launch-игру (Стоимость R&D: $15,000)",
                        font_body, PANEL_COLOR, GREEN, TEXT_WHITE)


def render_factory_tab(screen, player, font_title, font_body, font_large, btn_order_10k, btn_order_50k, btn_order_100k):
    draw_text(screen, "УПРАВЛЕНИЕ ЛОГИСТИКОЙ И ЗАКАЗОМ КРЕМНИЕВЫХ ПЛАСТИН", font_title, AMBER, 30, 70)

    if not player.released_consoles:
        draw_text(screen, "У вас нет запущенных на рынке систем. Сначала завершите R&D во вкладке [F2].", font_large,
                  TEXT_MUTED, 30, 150)
        return

    console = player.released_consoles[0]

    pygame.draw.rect(screen, PANEL_COLOR, (30, 110, 450, 300))
    pygame.draw.rect(screen, BORDER_COLOR, (30, 110, 450, 300), 1)
    draw_text(screen, f"ТЕКУЩИЕ ЗАПАСЫ: {console.name}", font_title, TEXT_WHITE, 45, 125)
    draw_text(screen, f"На складе: {console.inventory:,} шт.", font_large, AMBER, 45, 165)
    draw_text(screen, f"Себестоимость: ${console.unit_cost:.1f} / шт.", font_body, TEXT_WHITE, 45, 215)

    pygame.draw.rect(screen, PANEL_COLOR, (30, 430, 1104, 250))
    pygame.draw.rect(screen, BORDER_COLOR, (30, 430, 1104, 250), 1)
    draw_text(screen, "РАЗМЕСТИТЬ СЕНСОРНЫЙ ЗАКАЗ НА КРЕМНИЕВЫЕ ПЛАСТИНЫ (доставка 1 месяц)", font_title, AMBER, 45,
              450)

    cost_10k = 10000 * console.unit_cost
    b1_color = GREEN if player.cash >= cost_10k else RED
    draw_button(screen, btn_order_10k, f"Партия: 10k шт. (-${cost_10k:,.0f}) (1 мес.)", font_body, PANEL_COLOR,
                b1_color, TEXT_WHITE)

    cost_50k = 50000 * console.unit_cost
    b2_color = GREEN if player.cash >= cost_50k else RED
    draw_button(screen, btn_order_50k, f"Партия: 50k шт. (-${cost_50k:,.0f}) (2 мес.)", font_body, PANEL_COLOR,
                b2_color, TEXT_WHITE)

    cost_100k = 100000 * console.unit_cost
    b3_color = GREEN if player.cash >= cost_100k else RED
    draw_button(screen, btn_order_100k, f"Партия: 100k шт. (-${cost_100k:,.0f}) (3 мес.)", font_body, PANEL_COLOR,
                b3_color, TEXT_WHITE)


def render_finance_tab(screen, player, font_title, font_body, font_large):
    draw_text(screen, "ЕЖЕМЕСЯЧНЫЙ ФИНАНСОВЫЙ ОТЧЕТ КОМПАНИИ (ЗА ПРОШЛЫЙ ХОД)", font_title, AMBER, 30, 70)
    pygame.draw.rect(screen, PANEL_COLOR, (30, 110, 1164, 570))
    pygame.draw.rect(screen, BORDER_COLOR, (30, 110, 1164, 570), 1)

    fin = player.financials_last_month
    draw_text(screen, "ВЫРУЧКА (REVENUES)", font_title, GREEN, 60, 135)
    draw_text(screen, f"Продажи железа (Hardware Sales): ${fin['hw_revenue']:,.2f}", font_body, TEXT_WHITE, 60, 175)
    draw_text(screen, f"Роялти от стороннего софта (Royalty Revenue): ${fin['royalty_revenue']:,.2f}", font_body,
              TEXT_WHITE, 60, 205)

    draw_text(screen, "РАСХОДЫ (OPERATING EXPENSES)", font_title, RED, 60, 260)
    draw_text(screen, f"Производство (Manufacturing Cost): -${fin['manufacturing_cost']:,.2f}", font_body, TEXT_WHITE,
              60, 300)
    draw_text(screen, f"R&D и исследования: -${fin['rd_expenses']:,.2f}", font_body, TEXT_WHITE, 60, 330)
    draw_text(screen, f"Реклама (Marketing): -${fin['marketing_expenses']:,.2f}", font_body, TEXT_WHITE, 60, 360)
    draw_text(screen, f"Зарплаты: -${fin['salaries']:,.2f}", font_body, TEXT_WHITE, 60, 390)
    draw_text(screen, f"Складское хранение: -${fin['warehouse_cost']:,.2f}", font_body, TEXT_WHITE, 60, 420)

    pygame.draw.line(screen, BORDER_COLOR, (60, 470), (1130, 470), 2)
    draw_text(screen, "ЧИСТАЯ ПРИБЫЛЬ (NET INCOME)", font_title, AMBER, 60, 500)
    profit_color = GREEN if fin["net_profit"] >= 0 else RED
    draw_text(screen, f"${fin['net_profit']:,.2f}", font_large, profit_color, 400, 500)


def render_licenses_tab(screen, player, games_list, current_year, font_large, font_title, font_body, sub_tab="games"):
    draw_text(screen, "ЛИЦЕНЗИРОВАНИЕ И ЭКСКЛЮЗИВНЫЕ КОНТРАКТЫ", font_title, AMBER, 30, 70)

    # Кнопки переключения подвкладок
    btn_games = pygame.Rect(30, 100, 200, 30)
    btn_studios = pygame.Rect(240, 100, 200, 30)
    draw_button(screen, btn_games, "СТОРОННИЕ ИГРЫ", font_body, AMBER if sub_tab == "games" else PANEL_COLOR,
                BORDER_COLOR, TEXT_WHITE)
    draw_button(screen, btn_studios, "КОНТРАКТЫ СО СТУДИЯМИ", font_body, AMBER if sub_tab == "studios" else PANEL_COLOR,
                BORDER_COLOR, TEXT_WHITE)

    if sub_tab == "games":
        offset_y = 145
        year_games = [g for g in games_list if g.year_available == current_year]

        if player.active_ports:
            draw_text(screen, "АКТИВНЫЕ ПОРТЫ В РАЗРАБОТКЕ (2 МЕСЯЦА):", font_title, AMBER, 750, 145)
            port_offset_y = 175
            for p in player.active_ports:
                draw_text(screen, f"- {p.game.name} -> {p.console.name} (ост. {p.months_left} мес.)", font_body,
                          TEXT_WHITE, 750, port_offset_y)
                port_offset_y += 20

        if not year_games:
            draw_text(screen, "В этом году новых предложений от сторонних студий нет.", font_large, TEXT_MUTED, 45, 180)
            return

        if not player.released_consoles:
            draw_text(screen, "У вас нет запущенных на рынке систем. Лицензирование заблокировано.", font_large, RED,
                      45, 180)
            return

        target_console = player.released_consoles[0]
        is_programmable = target_console.spec_info.get("is_programmable", False)

        for g in year_games:
            pygame.draw.rect(screen, PANEL_COLOR, (30, offset_y, 700, 80))
            pygame.draw.rect(screen, BORDER_COLOR, (30, offset_y, 700, 80), 1)

            draw_text(screen, f"{g.name} ({g.year_available} г.)", font_title, AMBER, 45, offset_y + 10)
            draw_text(screen, g.desc, font_body, TEXT_WHITE, 45, offset_y + 30)
            draw_text(screen, f"Мин. Мощность: {g.min_power} HW  |  Буст Роялти: +${g.base_royalty:.2f}/мес", font_body,
                      TEXT_MUTED, 45, offset_y + 55)

            btn_rect = pygame.Rect(540, offset_y + 20, 180, 40)

            is_porting = any(p.game.name == g.name for p in player.active_ports)
            is_acquired = g.acquired_by == 'player' or any(l_game.name == g.name for l_game in player.licensed_games)

            if is_acquired:
                draw_button(screen, btn_rect, "ЛИЦЕНЗИРОВАНО", font_body, GREEN, GREEN, BG_COLOR)
            elif is_porting:
                draw_button(screen, btn_rect, "ПОРТИРУЕТСЯ...", font_body, PANEL_COLOR, BLUE, BLUE)
            elif g.acquired_by is not None:
                draw_button(screen, btn_rect, f"У ИИ ({g.acquired_by})", font_body, PANEL_COLOR, RED, RED)
            elif not is_programmable:
                draw_button(screen, btn_rect, "НЕТ КАРТРИДЖЕЙ!", font_body, PANEL_COLOR, RED, RED)
            else:
                cost_total = g.license_cost
                is_weak = target_console.hardware_power < g.min_power
                if is_weak:
                    cost_total *= 2.0

                cost_label = f"Выкупить: ${cost_total:,.0f}"
                if is_weak:
                    cost_label += " (x2 Слабое!)"

                b_color = GREEN if player.cash >= cost_total else RED
                draw_button(screen, btn_rect, cost_label, font_body, PANEL_COLOR, b_color, TEXT_WHITE)

            offset_y += 95

    elif sub_tab == "studios":
        # Студии для эксклюзивных контрактов
        from config import STUDIO_CONTRACTS
        offset_y = 145
        avail_studios = [s for s in STUDIO_CONTRACTS if s["year"] <= current_year]

        if not avail_studios:
            draw_text(screen, "В этом году новых студий для контрактов нет.", font_large, TEXT_MUTED, 45, 180)
            return

        draw_text(screen, "ПОДПИСАННЫЕ СТУДИИ-ПАРТНЕРЫ:", font_title, AMBER, 750, 145)
        sy = 175
        if not player.signed_studios:
            draw_text(screen, "Нет активных контрактов", font_body, TEXT_MUTED, 750, sy)
        for s in player.signed_studios:
            draw_text(screen, f"- {s['name']} (Роялти: +{s['royalty_bonus'] * 100:.1f}%)", font_body, GREEN, 750, sy)
            sy += 20

        for s in avail_studios[:5]:  # Вывод доступных на текущий год студий
            pygame.draw.rect(screen, PANEL_COLOR, (30, offset_y, 700, 85))
            pygame.draw.rect(screen, BORDER_COLOR, (30, offset_y, 700, 85), 1)

            draw_text(screen, f"{s['name']} (Основана: {s['year']} г.)", font_title, AMBER, 45, offset_y + 10)
            draw_text(screen, s["desc"], font_body, TEXT_WHITE, 45, offset_y + 35)
            draw_text(screen, f"Бонус роялти: +{s['royalty_bonus'] * 100:.1f}% | Буст эксклюзивных хитов", font_body,
                      TEXT_MUTED, 45, offset_y + 60)

            btn_rect = pygame.Rect(540, offset_y + 20, 180, 40)
            already_signed = any(x["name"] == s["name"] for x in player.signed_studios)

            if already_signed:
                draw_button(screen, btn_rect, "КОНТРАКТ ПОДПИСАН", font_body, GREEN, GREEN, BG_COLOR)
            else:
                b_color = GREEN if player.cash >= s["cost"] else RED
                draw_button(screen, btn_rect, f"Подписать: ${s['cost']:,}", font_body, PANEL_COLOR, b_color, TEXT_WHITE)

            offset_y += 100