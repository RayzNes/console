import pygame

# Initialize fonts
pygame.font.init()
font_large = pygame.font.Font(None, 32)
font_title = pygame.font.Font(None, 24)
font_body = pygame.font.Font(None, 18)

# Constants
BG_COLOR = (12, 14, 20)
PANEL_COLOR = (18, 21, 32)
BORDER_COLOR = (32, 38, 58)
TEXT_WHITE = (235, 240, 250)
TEXT_MUTED = (115, 128, 142)
GREEN = (46, 204, 113)
BLUE = (52, 152, 219)
RED = (231, 76, 60)
AMBER = (241, 196, 15)

# Tab rectangles for navigation
tab_rects = {
    "market": pygame.Rect(10, 10, 100, 30),
    "rd": pygame.Rect(120, 10, 100, 30),
    "factory": pygame.Rect(230, 10, 100, 30),
    "finance": pygame.Rect(340, 10, 100, 30)
}

# Button rectangles (define all the buttons used in main.py)
btn_step = pygame.Rect(45, 465, 250, 40)
btn_auto = pygame.Rect(45, 515, 250, 40)
btn_reset = pygame.Rect(45, 565, 250, 40)

btn_hire = pygame.Rect(665, 240, 100, 30)
btn_fire = pygame.Rect(775, 240, 100, 30)

btn_cpu_select = pygame.Rect(45, 260, 250, 30)
btn_gpu_select = pygame.Rect(45, 350, 250, 30)
btn_media_select = pygame.Rect(45, 280, 250, 30)

btn_margin_dec = pygame.Rect(45, 340, 40, 30)
btn_margin_inc = pygame.Rect(95, 340, 40, 30)
btn_launch_project = pygame.Rect(45, 390, 300, 40)

btn_order_10k = pygame.Rect(45, 500, 250, 40)
btn_order_50k = pygame.Rect(310, 500, 250, 40)
btn_order_100k = pygame.Rect(575, 500, 250, 40)


def draw_chart(surface, x, y, w, h, market_history, consoles):
    """Рисует график продаж и емкости рынка"""
    if not market_history:
        draw_text(surface, "Нет данных для отображения", font_body, TEXT_MUTED, x + 10, y + 10)
        return

    # Настройки графика
    chart_rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, PANEL_COLOR, chart_rect)
    pygame.draw.rect(surface, BORDER_COLOR, chart_rect, 1)

    # Находим максимальные значения для масштабирования
    max_capacity = max(entry["capacity"] for entry in market_history) if market_history else 1
    max_sales = max(entry["total_sold"] for entry in market_history) if market_history else 1
    max_value = max(max_capacity, max_sales)

    if max_value == 0:
        max_value = 1

    # Оси графика
    graph_rect = pygame.Rect(x + 40, y + 20, w - 60, h - 60)
    pygame.draw.line(surface, TEXT_WHITE, (graph_rect.x, graph_rect.y), (graph_rect.x, graph_rect.bottom), 1)
    pygame.draw.line(surface, TEXT_WHITE, (graph_rect.x, graph_rect.bottom), (graph_rect.right, graph_rect.bottom), 1)

    # Рисуем линии продаж для каждой консоли
    colors = {}
    for console in consoles:
        if console.is_player:
            colors[console.name] = AMBER
        elif "Atari" in console.name:
            colors[console.name] = (230, 126, 34)
        elif "Magnavox" in console.name:
            colors[console.name] = (200, 200, 200)
        elif "Mattel" in console.name:
            colors[console.name] = (52, 152, 219)
        elif "Coleco" in console.name:
            colors[console.name] = (46, 204, 113)
        else:
            colors[console.name] = TEXT_MUTED

    # Собираем данные по месяцам
    months_data = {}
    for i, entry in enumerate(market_history):
        month_key = f"{entry['year']}_{entry['month']}"
        months_data[month_key] = {
            "index": i,
            "capacity": entry["capacity"],
            "sales": entry["console_sales"]
        }

    if not months_data:
        return

    max_index = len(market_history) - 1

    # If only one data point, just draw a point
    if max_index == 0:
        # Draw capacity point
        data = list(months_data.values())[0]
        x_pos = graph_rect.x + graph_rect.width / 2
        y_pos = graph_rect.bottom - (data["capacity"] / max_value) * graph_rect.height
        pygame.draw.circle(surface, TEXT_MUTED, (int(x_pos), int(y_pos)), 3)

        # Draw sales points for each console
        for console_name, sales in data["sales"].items():
            if console_name in colors:
                y_pos = graph_rect.bottom - (sales / max_value) * graph_rect.height
                pygame.draw.circle(surface, colors[console_name], (int(x_pos), int(y_pos)), 3)

        # Подписи осей
        draw_text(surface, "Продажи", font_body, TEXT_MUTED, x + 5, y + 10)
        draw_text(surface, "Время", font_body, TEXT_MUTED, x + w - 40, graph_rect.bottom + 5)
        return

    # Рисуем линию емкости рынка (пунктирная)
    prev_point = None
    for month_key, data in months_data.items():
        x_pos = graph_rect.x + (data["index"] / max_index) * graph_rect.width
        y_pos = graph_rect.bottom - (data["capacity"] / max_value) * graph_rect.height

        point = (int(x_pos), int(y_pos))

        if prev_point:
            # Рисуем пунктирную линию
            draw_dashed_line(surface, prev_point, point, TEXT_MUTED, 2)
        prev_point = point

    # Рисуем линии продаж для каждой консоли
    console_data = {}
    for console in consoles:
        console_data[console.name] = []

    for month_key, data in months_data.items():
        for console_name, sales in data["sales"].items():
            console_data[console_name].append(sales)

    for console_name, sales_list in console_data.items():
        if not sales_list or console_name not in colors:
            continue

        color = colors.get(console_name, TEXT_MUTED)
        prev_point = None

        for i, sales in enumerate(sales_list):
            if i > max_index:
                continue

            x_pos = graph_rect.x + (i / max_index) * graph_rect.width
            y_pos = graph_rect.bottom - (sales / max_value) * graph_rect.height

            point = (int(x_pos), int(y_pos))

            if prev_point:
                pygame.draw.line(surface, color, prev_point, point, 2)
            prev_point = point

    # Подписи осей
    draw_text(surface, "Продажи", font_body, TEXT_MUTED, x + 5, y + 10)
    draw_text(surface, "Время", font_body, TEXT_MUTED, x + w - 40, graph_rect.bottom + 5)

    # Легенда
    legend_x = x + 10
    legend_y = y + h - 80
    draw_text(surface, "Легенда:", font_body, TEXT_WHITE, legend_x, legend_y)

    legend_y += 20
    for console in consoles[:5]:  # Показываем до 5 консолей в легенде
        color = colors.get(console.name, TEXT_MUTED)
        pygame.draw.rect(surface, color, (legend_x, legend_y, 12, 12))
        name = console.name[:20]  # Обрезаем длинные имена
        draw_text(surface, name, font_body, TEXT_WHITE, legend_x + 18, legend_y - 2)
        legend_y += 18


def draw_dashed_line(surface, start_pos, end_pos, color, width=1, dash_length=5):
    """Рисует пунктирную линию"""
    x1, y1 = start_pos
    x2, y2 = end_pos

    length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    if length == 0:
        return

    dash_count = int(length / dash_length)

    for i in range(dash_count):
        t1 = i / dash_count
        t2 = (i + 0.5) / dash_count

        start = (int(x1 + (x2 - x1) * t1), int(y1 + (y2 - y1) * t1))
        end = (int(x1 + (x2 - x1) * t2), int(y1 + (y2 - y1) * t2))

        pygame.draw.line(surface, color, start, end, width)

def draw_text(surface, text, font, color, x, y):
    img = font.render(text, True, color)
    surface.blit(img, (x, y))


def draw_button(surface, rect, text, font, bg_color, border_color, text_color):
    pygame.draw.rect(surface, bg_color, rect, border_radius=4)
    pygame.draw.rect(surface, border_color, rect, width=1, border_radius=4)
    img = font.render(text, True, text_color)
    img_rect = img.get_rect(center=rect.center)
    surface.blit(img, img_rect)


def render_difficulty_screen(screen, font_large, font_title, font_body):
    """Экран выбора сложности перед началом игры"""
    screen.fill(BG_COLOR)
    draw_text(screen, "CHOOSE YOUR DIFFICULTY / ВЫБЕРИТЕ СЛОЖНОСТЬ", font_large, AMBER, 300, 250)

    # Кнопки выбора
    draw_button(screen, pygame.Rect(462, 350, 300, 50), "EASY (ЛЕГКО)", font_title, PANEL_COLOR, GREEN, GREEN)
    draw_button(screen, pygame.Rect(462, 420, 300, 50), "MEDIUM (СРЕДНЕ)", font_title, PANEL_COLOR, BLUE, BLUE)
    draw_button(screen, pygame.Rect(462, 490, 300, 50), "HARD (ТЯЖЕЛО)", font_title, PANEL_COLOR, RED, RED)

    draw_text(screen, "Easy: $2M cash, x1.3 demand | Medium: $1.2M, x1.0 demand | Hard: $0.6M, x0.7 demand", font_body,
              TEXT_MUTED, 330, 580)


def render_bankruptcy_screen(screen, font_large, font_title):
    """Экран банкротства при полном выгорании бюджета"""
    screen.fill((20, 5, 5))
    draw_text(screen, "BANKRUPTCY - GAME OVER / БАНКРОТСТВО", font_large, RED, 350, 350)
    draw_text(screen, "Компания ликвидирована за долги.", font_title, TEXT_WHITE, 440, 410)
    draw_button(screen, pygame.Rect(462, 480, 300, 50), "ПЕРЕЗАПУСТИТЬ ИГРУ [R]", font_title, PANEL_COLOR, AMBER, AMBER)


def render_market_tab(screen, market, auto_play, font_title, font_body, btn_step, btn_auto, btn_reset, player):
    draw_text(screen, "МАРКЕТИНГОВАЯ ОБСТАНОВКА И ПРОДАЖИ", font_title, AMBER, 30, 70)
    draw_text(screen, "Легенда: Серый пунктир - емкость рынка | Желтый - Ваша система | Другие - ИИ", font_body,
              TEXT_MUTED, 30, 95)

    # Сетка графиков
    from main import draw_chart
    draw_chart(screen, 30, 120, 1164, 300, market.history, market.consoles)

    # Панель управления временем
    pygame.draw.rect(screen, PANEL_COLOR, (30, 440, 280, 280))
    pygame.draw.rect(screen, BORDER_COLOR, (30, 440, 280, 280), 1)
    draw_text(screen, "СЕНСОРНЫЙ КОНТРОЛЬ", font_title, TEXT_WHITE, 45, 455)

    draw_button(screen, btn_step, "ШАГ ХОДА (+1 Месяц)", font_body, PANEL_COLOR, BORDER_COLOR, AMBER)
    auto_color = GREEN if auto_play else RED
    auto_text = "АВТО-СИМУЛЯЦИЯ: ВКЛ" if auto_play else "АВТО-СИМУЛЯЦИЯ: ВЫКЛ"
    draw_button(screen, btn_auto, auto_text, font_body, PANEL_COLOR, BORDER_COLOR, auto_color)
    draw_button(screen, btn_reset, "СБРОСИТЬ ИГРУ", font_body, PANEL_COLOR, RED, TEXT_WHITE)

    # Проверка на банкротство
    if player.bankruptcy_months > 0:
        draw_text(screen, f"КРИЗИС! БАЛАНС < 0!", font_body, RED, 45, 680)
        draw_text(screen, f"Банкротство через {4 - player.bankruptcy_months} мес.", font_body, RED, 45, 695)

    # Список консолей
    pygame.draw.rect(screen, PANEL_COLOR, (330, 440, 864, 280))
    pygame.draw.rect(screen, BORDER_COLOR, (330, 440, 864, 280), 1)
    draw_text(screen, "АКТИВНЫЕ СИСТЕМЫ НА РЫНКЕ", font_title, TEXT_WHITE, 345, 455)
    pygame.draw.line(screen, BORDER_COLOR, (345, 480), (1180, 480), 1)

    col_offset_x = 345
    for console in market.consoles:
        is_active = console.launch_year < market.current_year or (
                console.launch_year == market.current_year and console.launch_month <= market.current_month)
        if is_active:
            name_label = f"{console.name} [ИГРОК]" if console.is_player else console.name
            draw_text(screen, name_label, font_title, console.color, col_offset_x, 500)
            draw_text(screen, f"Инсталл-база: {console.installed_base:,}", font_body, TEXT_WHITE, col_offset_x, 530)
            draw_text(screen, f"На складе: {console.inventory:,} шт.", font_body, TEXT_WHITE, col_offset_x, 555)
            draw_text(screen, f"Сила чипов: {console.hardware_power:.1f} HW", font_body, TEXT_MUTED, col_offset_x, 580)
            col_offset_x += 210
            if col_offset_x > 1100:
                break


def render_rd_tab(screen, player, components_db, sel_cpu, sel_gpu, sel_media, margin,
                  font_title, font_body, font_large, sub_tab,
                  btn_hire, btn_fire, btn_cpu_select, btn_gpu_select, btn_media_select,
                  btn_margin_dec, btn_margin_inc, btn_launch_project,
                  btn_sub_res, btn_sub_design, btn_sub_console, btn_research_action, btn_chip_build):
    """Многостраничный R&D модуль: Технологии, Конструктор, Сборка"""
    draw_text(screen, "ОТДЕЛ ИССЛЕДОВАНИЙ И РАЗРАБОТОК (R&D)", font_title, AMBER, 30, 70)

    # Сенсорные кнопки переключения подвкладок R&D [2]
    draw_button(screen, btn_sub_res, "1. ИССЛЕДОВАНИЯ", font_body, AMBER if sub_tab == "research" else PANEL_COLOR,
                BORDER_COLOR, TEXT_WHITE)
    draw_button(screen, btn_sub_design, "2. КОНСТРУКТОР ЧИПОВ", font_body,
                AMBER if sub_tab == "designer" else PANEL_COLOR, BORDER_COLOR, TEXT_WHITE)
    draw_button(screen, btn_sub_console, "3. СБОРКА СИСТЕМ", font_body, AMBER if sub_tab == "console" else PANEL_COLOR,
                BORDER_COLOR, TEXT_WHITE)

    # --- СТРАНИЦА 1: ДРЕВО ТЕХНОЛОГИЙ ---
    if sub_tab == "research":
        pygame.draw.rect(screen, PANEL_COLOR, (30, 150, 600, 540))
        pygame.draw.rect(screen, BORDER_COLOR, (30, 150, 600, 540), 1)
        draw_text(screen, "ДОСТУПНЫЕ ТЕХНОЛОГИИ ДЛЯ ИЗУЧЕНИЯ", font_title, TEXT_WHITE, 45, 165)

        avail_nodes = player.tech_tree.get_available_research(
            1972 + (player.bankruptcy_months // 12))  # симуляция текущего года
        offset_y = 205
        for i, node in enumerate(avail_nodes[:10]):
            btn_rect = pygame.Rect(45, offset_y, 450, 25)
            is_active = (player.active_research == node)
            bg = GREEN if is_active else PANEL_COLOR
            text_color = BG_COLOR if is_active else TEXT_WHITE
            draw_button(screen, btn_rect,
                        f"{node.name} ({node.category.upper()}) | Cost: ${node.base_cost:,} | {node.base_months} мес.",
                        font_body, bg, BORDER_COLOR, text_color)
            offset_y += 30

        # Справа информация по текущему исследованию
        pygame.draw.rect(screen, PANEL_COLOR, (650, 150, 544, 540))
        pygame.draw.rect(screen, BORDER_COLOR, (650, 150, 544, 540), 1)
        draw_text(screen, "СОСТОЯНИЕ ИССЛЕДОВАНИЯ", font_title, TEXT_WHITE, 665, 165)

        if player.active_research:
            node = player.active_research
            draw_text(screen, f"Изучается: {node.name}", font_large, AMBER, 665, 215)
            draw_text(screen, f"Категория: {node.category.upper()}", font_body, TEXT_WHITE, 665, 255)
            draw_text(screen, f"Требуемый срок: {node.base_months} мес.", font_body, TEXT_WHITE, 665, 275)

            # Прогресс бар технологии
            pts_needed = max(10, node.base_months * 10)
            percent = min(100.0, (node.progress_points / pts_needed) * 100.0)
            pygame.draw.rect(screen, BG_COLOR, (665, 315, 450, 25))
            pygame.draw.rect(screen, GREEN, (665, 315, int(450 * (percent / 100.0)), 25))
            draw_text(screen, f"{percent:.1f}%", font_body, TEXT_WHITE, 880, 320)
        else:
            draw_text(screen, "Нет активных разработок.", font_large, TEXT_MUTED, 665, 215)
            draw_text(screen, "Кликните по технологии слева для запуска.", font_body, TEXT_MUTED, 665, 255)

    # --- СТРАНИЦА 2: КОНСТРУКТОР ЧИПОВ ---
    elif sub_tab == "designer":
        pygame.draw.rect(screen, PANEL_COLOR, (30, 150, 1164, 540))
        pygame.draw.rect(screen, BORDER_COLOR, (30, 150, 1164, 540), 1)
        draw_text(screen, "ИНЖЕНЕРНЫЙ СИНТЕЗ МИКРОСХЕМ (CHIP DESIGNER)", font_large, AMBER, 45, 175)

        # Вывод имеющихся исследованных узлов для сборки
        researched_cpus = [n for n in player.tech_tree.nodes.values() if n.category == "cpu" and n.researched]
        researched_gpus = [n for n in player.tech_tree.nodes.values() if n.category == "gpu" and n.researched]
        researched_mems = [n for n in player.tech_tree.nodes.values() if n.category == "memory" and n.researched]
        researched_procs = [n for n in player.tech_tree.nodes.values() if
                            n.category == "manufacturing" and n.researched]
        researched_packs = [n for n in player.tech_tree.nodes.values() if
                            n.category == "manufacturing" and n.researched]  # пакетный корпус

        # Ограничения интерфейса: отображаем выбранный пресет для синтеза CPU
        draw_text(screen, "Сборка процессора (CPU Synthesis):", font_title, TEXT_WHITE, 45, 230)
        draw_button(screen, btn_cpu_select, "Собрать кастомный CPU", font_body, PANEL_COLOR, BORDER_COLOR, TEXT_WHITE)

        draw_text(screen, "Сборка видеочипа (GPU Synthesis):", font_title, TEXT_WHITE, 45, 320)
        draw_button(screen, btn_gpu_select, "Собрать кастомный GPU", font_body, PANEL_COLOR, BORDER_COLOR, TEXT_WHITE)

        # Выводим список уже построенных чипов
        draw_text(screen, "ВАША БАЗА ЗАПАТЕНТОВАННЫХ ЧИПОВ:", font_title, AMBER, 650, 230)
        offset_chips_y = 265
        for custom_cpu in player.custom_cpus:
            draw_text(screen,
                      f"CPU: {custom_cpu['name']} | HW Сила: {custom_cpu['power']} | Себест.: ${custom_cpu['cost']}",
                      font_body, TEXT_WHITE, 650, offset_chips_y)
            offset_chips_y += 20

        for custom_gpu in player.custom_gpus:
            draw_text(screen,
                      f"GPU: {custom_gpu['name']} | HW Сила: {custom_gpu['power']} | Себест.: ${custom_gpu['cost']}",
                      font_body, TEXT_WHITE, 650, offset_chips_y)
            offset_chips_y += 20

    # --- СТРАНИЦА 3: СБОРКА СИСТЕМ ---
    elif sub_tab == "console":
        # Управление кадрами (Правая панель)
        pygame.draw.rect(screen, PANEL_COLOR, (650, 150, 544, 320))
        pygame.draw.rect(screen, BORDER_COLOR, (650, 150, 544, 320), 1)
        draw_text(screen, "КОНТРОЛЬ ШТАТА", font_title, TEXT_WHITE, 665, 165)
        draw_text(screen, f"Инженеры: {player.engineers}", font_large, AMBER, 665, 200)
        draw_button(screen, btn_hire, "НАНЯТЬ (+1)", font_body, PANEL_COLOR, GREEN, GREEN)
        draw_button(screen, btn_fire, "УВОЛИТЬ (-1)", font_body, PANEL_COLOR, RED, RED)

        # Сборка консолей из созданных чипов
        pygame.draw.rect(screen, PANEL_COLOR, (30, 150, 600, 320))
        pygame.draw.rect(screen, BORDER_COLOR, (30, 150, 600, 320), 1)

        if not player.active_project:
            draw_text(screen, "КОНСТРУИРОВАНИЕ СИСТЕМЫ ИЗ ВАШИХ ЧИПОВ", font_title, TEXT_WHITE, 45, 165)

            # Если у игрока нет собственных чипов, он должен сначала их сконструировать
            if not player.custom_cpus or not player.custom_gpus:
                draw_text(screen, "Внимание! У вас нет сконструированных чипов.", font_body, RED, 45, 210)
                draw_text(screen, "Сначала соберите CPU и GPU на вкладке [2. КОНСТРУКТОР ЧИПОВ].", font_body,
                          TEXT_WHITE, 45, 230)
            else:
                cpu = player.custom_cpus[sel_cpu % len(player.custom_cpus)]
                gpu = player.custom_gpus[sel_gpu % len(player.custom_gpus)]
                med = components_db["media"][sel_media]

                unit_cost = cpu["cost"] + gpu["cost"] + med["cost"]
                retail_p = int(unit_cost * margin)
                power = cpu["power"] + gpu["power"]

                draw_button(screen, btn_cpu_select, f"Ваш CPU: {cpu['name']} (HW: {cpu['power']} | ${cpu['cost']})",
                            font_body, PANEL_COLOR, BORDER_COLOR, TEXT_WHITE)
                draw_button(screen, btn_gpu_select, f"Ваш GPU: {gpu['name']} (HW: {gpu['power']} | ${gpu['cost']})",
                            font_body, PANEL_COLOR, BORDER_COLOR, TEXT_WHITE)
                draw_button(screen, btn_media_select, f"Носитель: {med['name']} (${med['cost']})", font_body,
                            PANEL_COLOR, BORDER_COLOR, TEXT_WHITE)

                draw_text(screen, f"Наценка: {margin:.1f}x (Розничная цена: ${retail_p})", font_body, TEXT_WHITE, 45,
                          312)
                draw_button(screen, btn_margin_dec, "-", font_title, PANEL_COLOR, BORDER_COLOR, RED)
                draw_button(screen, btn_margin_inc, "+", font_title, PANEL_COLOR, BORDER_COLOR, GREEN)

                draw_button(screen, btn_launch_project, "ЗАПУСТИТЬ КОНСОЛЬ В ПРОИЗВОДСТВО", font_title, PANEL_COLOR,
                            AMBER, AMBER)
        else:
            project = player.active_project
            draw_text(screen, f"В РАЗРАБОТКЕ: {project.name}", font_large, AMBER, 45, 165)
            pygame.draw.rect(screen, BG_COLOR, (45, 240, 500, 25))
            pygame.draw.rect(screen, GREEN, (45, 240, int(500 * (project.progress / 100.0)), 25))
            draw_text(screen, f"{project.progress:.1f}%", font_body, TEXT_WHITE, 270, 245)


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

    # Размещение сенсорных заказов с учетом проверки кошелька [1]
    pygame.draw.rect(screen, PANEL_COLOR, (30, 430, 1104, 250))
    pygame.draw.rect(screen, BORDER_COLOR, (30, 430, 1104, 250), 1)
    draw_text(screen, "РАЗМЕСТИТЬ СЕНСОРНЫЙ ЗАКАЗ НА КРЕМНИЕВЫЕ ПЛАСТИНЫ (доставка 1 месяц)", font_title, AMBER, 45,
              450)

    # Деактивация (визуальное покраснение), если баланс не позволяет сделать заказ [1]
    cost_10k = 10000 * console.unit_cost
    b1_color = GREEN if player.cash >= cost_10k else RED
    draw_button(screen, btn_order_10k, f"Партия: 10k шт. (-${cost_10k:,.0f})", font_body, PANEL_COLOR, b1_color,
                TEXT_WHITE)

    cost_50k = 50000 * console.unit_cost
    b2_color = GREEN if player.cash >= cost_50k else RED
    draw_button(screen, btn_order_50k, f"Партия: 50k шт. (-${cost_50k:,.0f})", font_body, PANEL_COLOR, b2_color,
                TEXT_WHITE)

    cost_100k = 100000 * console.unit_cost
    b3_color = GREEN if player.cash >= cost_100k else RED
    draw_button(screen, btn_order_100k, f"Партия: 100k шт. (-${cost_100k:,.0f})", font_body, PANEL_COLOR, b3_color,
                TEXT_WHITE)


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