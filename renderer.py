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

# 5 сенсорных вкладок (Добавлено F5: Лицензирование)
tab_rects = {
    "market": pygame.Rect(10, 10, 110, 30),
    "rd": pygame.Rect(130, 10, 210, 30),
    "factory": pygame.Rect(350, 10, 110, 30),
    "finance": pygame.Rect(470, 10, 110, 30),
    "licenses": pygame.Rect(590, 10, 150, 30)
}

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
    if not market_history:
        draw_text(surface, "Нет данных для отображения", font_body, TEXT_MUTED, x + 10, y + 10)
        return

    chart_rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, PANEL_COLOR, chart_rect)
    pygame.draw.rect(surface, BORDER_COLOR, chart_rect, 1)

    max_capacity = max(entry["capacity"] for entry in market_history) if market_history else 1
    max_sales = max(entry["total_sold"] for entry in market_history) if market_history else 1
    max_value = max(max_capacity, max_sales, 1)

    graph_rect = pygame.Rect(x + 40, y + 20, w - 60, h - 60)
    pygame.draw.line(surface, TEXT_WHITE, (graph_rect.x, graph_rect.y), (graph_rect.x, graph_rect.bottom), 1)
    pygame.draw.line(surface, TEXT_WHITE, (graph_rect.x, graph_rect.bottom), (graph_rect.right, graph_rect.bottom), 1)

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
        pygame.draw.circle(surface, TEXT_MUTED, (int(x_pos), int(y_pos)), 3)
        return

    # Емкость рынка (Серый пунктир)
    prev_point = None
    for month_key, data in months_data.items():
        x_pos = graph_rect.x + (data["index"] / max_index) * graph_rect.width
        y_pos = graph_rect.bottom - (data["capacity"] / max_value) * graph_rect.height
        point = (int(x_pos), int(y_pos))
        if prev_point:
            draw_dashed_line(surface, prev_point, point, TEXT_MUTED, 2)
        prev_point = point

    # Линии продаж консолей
    console_data = {}
    for console in consoles:
        console_data[console.name] = []

    for month_key, data in months_data.items():
        for console_name, sales in data["sales"].items():
            if console_name not in console_data:
                console_data[console_name] = []
            console_data[console_name].append(sales)

    for console_name, sales_list in console_data.items():
        if not sales_list or console_name not in colors:
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

    # Подписи и Легенда
    draw_text(surface, "Продажи", font_body, TEXT_MUTED, x + 5, y + 10)
    legend_x = x + 10
    legend_y = y + h - 80
    draw_text(surface, "Легенда:", font_body, TEXT_WHITE, legend_x, legend_y)
    legend_y += 20
    for console in consoles[:5]:
        color = colors.get(console.name, TEXT_MUTED)
        pygame.draw.rect(surface, color, (legend_x, legend_y, 12, 12))
        draw_text(surface, console.name[:20], font_body, TEXT_WHITE, legend_x + 18, legend_y - 2)
        legend_y += 18


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
    """Отрисовка всплывающих уведомлений в правом верхнем углу"""
    offset_y = 70
    for text, frames in player.notifications:
        # Плавное угасание в конце
        alpha = min(255, int(frames * 4.25)) if frames < 60 else 255
        box_rect = pygame.Rect(900, offset_y, 300, 45)

        # Полупрозрачная плашка сообщения
        s = pygame.Surface((300, 45), pygame.SRCALPHA)
        s.fill((18, 21, 32, alpha))
        pygame.draw.rect(s, (241, 196, 15, alpha), (0, 0, 300, 45), 1, border_radius=4)
        screen.blit(s, (900, offset_y))

        img = font_body.render(text, True, (235, 240, 250))
        img.set_alpha(alpha)
        screen.blit(img, (915, offset_y + 15))
        offset_y += 55


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

    # Визуализация бренда игрока
    pygame.draw.rect(screen, PANEL_COLOR, (730, 60, 464, 50))
    pygame.draw.rect(screen, BORDER_COLOR, (730, 60, 464, 50), 1)
    rep = player.reputation
    draw_text(screen,
              f"Репутация: Качество: {rep.quality_perception:.2f} | Инновации: {rep.innovation_score:.2f} | Лояльность: {rep.customer_loyalty:.2f}",
              font_body, TEXT_WHITE, 745, 78)

    draw_chart(screen, 30, 120, 1164, 300, market.history, market.consoles)

    pygame.draw.rect(screen, PANEL_COLOR, (30, 440, 280, 280))
    pygame.draw.rect(screen, BORDER_COLOR, (30, 440, 280, 280), 1)
    draw_text(screen, "СЕНСОРНЫЙ КОНТРОЛЬ", font_title, TEXT_WHITE, 45, 455)

    draw_button(screen, btn_step, "ШАГ ХОДА (+1 Месяц)", font_body, PANEL_COLOR, BORDER_COLOR, AMBER)
    auto_color = GREEN if auto_play else RED
    auto_text = "АВТО-СИМУЛЯЦИЯ: ВКЛ" if auto_play else "АВТО-СИМУЛЯЦИЯ: ВЫКЛ"
    draw_button(screen, btn_auto, auto_text, font_body, PANEL_COLOR, BORDER_COLOR, auto_color)
    draw_button(screen, btn_reset, "СБРОСИТЬ ИГРУ", font_body, PANEL_COLOR, RED, TEXT_WHITE)

    if player.bankruptcy_months > 0:
        draw_text(screen, f"КРИЗИС! БАЛАНС < 0!", font_body, RED, 45, 680)
        draw_text(screen, f"Банкротство через {4 - player.bankruptcy_months} мес.", font_body, RED, 45, 695)

    # Список систем
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
    draw_text(screen, "ОТДЕЛ ИССЛЕДОВАНИЙ И РАЗРАБОТОК (R&D)", font_title, AMBER, 30, 70)

    draw_button(screen, btn_sub_res, "1. ИССЛЕДОВАНИЯ", font_body, AMBER if sub_tab == "research" else PANEL_COLOR,
                BORDER_COLOR, TEXT_WHITE)
    draw_button(screen, btn_sub_design, "2. КОНСТРУКТОР ЧИПОВ", font_body,
                AMBER if sub_tab == "designer" else PANEL_COLOR, BORDER_COLOR, TEXT_WHITE)
    draw_button(screen, btn_sub_console, "3. СБОРКА СИСТЕМ", font_body, AMBER if sub_tab == "console" else PANEL_COLOR,
                BORDER_COLOR, TEXT_WHITE)

    if sub_tab == "research":
        pygame.draw.rect(screen, PANEL_COLOR, (30, 150, 600, 540))
        pygame.draw.rect(screen, BORDER_COLOR, (30, 150, 600, 540), 1)
        draw_text(screen, "ДОСТУПНЫЕ ТЕХНОЛОГИИ ДЛЯ ИЗУЧЕНИЯ", font_title, TEXT_WHITE, 45, 165)

        avail_nodes = player.tech_tree.get_available_research(1972)
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

        pygame.draw.rect(screen, PANEL_COLOR, (650, 150, 544, 540))
        pygame.draw.rect(screen, BORDER_COLOR, (650, 150, 544, 540), 1)
        draw_text(screen, "СОСТОЯНИЕ ИССЛЕДОВАНИЯ", font_title, TEXT_WHITE, 665, 165)

        if player.active_research:
            node = player.active_research
            draw_text(screen, f"Изучается: {node.name}", font_large, AMBER, 665, 215)
            draw_text(screen, f"Категория: {node.category.upper()}", font_body, TEXT_WHITE, 665, 255)
            draw_text(screen, f"Требуемый срок: {node.base_months} мес.", font_body, TEXT_WHITE, 665, 275)

            pts_needed = max(10, node.base_months * 10)
            percent = min(100.0, (node.progress_points / pts_needed) * 100.0)
            pygame.draw.rect(screen, BG_COLOR, (665, 315, 450, 25))
            pygame.draw.rect(screen, GREEN, (665, 315, int(450 * (percent / 100.0)), 25))
            draw_text(screen, f"{percent:.1f}%", font_body, TEXT_WHITE, 880, 320)
        else:
            draw_text(screen, "Нет активных разработок.", font_large, TEXT_MUTED, 665, 215)
            draw_text(screen, "Кликните по технологии слева для запуска.", font_body, TEXT_MUTED, 665, 255)

    elif sub_tab == "designer":
        pygame.draw.rect(screen, PANEL_COLOR, (30, 150, 1164, 540))
        pygame.draw.rect(screen, BORDER_COLOR, (30, 150, 1164, 540), 1)
        draw_text(screen, "ИНЖЕНЕРНЫЙ СИНТЕЗ МИКРОСХЕМ (CHIP DESIGNER)", font_large, AMBER, 45, 175)

        draw_text(screen, "Сборка процессора (CPU Synthesis):", font_title, TEXT_WHITE, 45, 230)
        draw_button(screen, btn_cpu_select, "Собрать кастомный CPU", font_body, PANEL_COLOR, BORDER_COLOR, TEXT_WHITE)

        draw_text(screen, "Сборка видеочипа (GPU Synthesis):", font_title, TEXT_WHITE, 45, 320)
        draw_button(screen, btn_gpu_select, "Собрать кастомный GPU", font_body, PANEL_COLOR, BORDER_COLOR, TEXT_WHITE)

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

    elif sub_tab == "console":
        pygame.draw.rect(screen, PANEL_COLOR, (650, 150, 544, 320))
        pygame.draw.rect(screen, BORDER_COLOR, (650, 150, 544, 320), 1)
        draw_text(screen, "КОНТРОЛЬ ШТАТА", font_title, TEXT_WHITE, 665, 165)
        draw_text(screen, f"Инженеры: {player.engineers}", font_large, AMBER, 665, 200)
        draw_button(screen, btn_hire, "НАНЯТЬ (+1)", font_body, PANEL_COLOR, GREEN, GREEN)
        draw_button(screen, btn_fire, "УВОЛИТЬ (-1)", font_body, PANEL_COLOR, RED, RED)

        pygame.draw.rect(screen, PANEL_COLOR, (30, 150, 600, 320))
        pygame.draw.rect(screen, BORDER_COLOR, (30, 150, 600, 320), 1)

        if not player.active_project:
            draw_text(screen, "КОНСТРУИРОВАНИЕ СИСТЕМЫ ИЗ ВАШИХ ЧИПОВ", font_title, TEXT_WHITE, 45, 165)

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

                draw_button(screen, btn_cpu_select, f"CPU: {cpu['name']} (HW: {cpu['power']} | ${cpu['cost']})",
                            font_body, PANEL_COLOR, BORDER_COLOR, TEXT_WHITE)
                draw_button(screen, btn_gpu_select, f"GPU: {gpu['name']} (HW: {gpu['power']} | ${gpu['cost']})",
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

    pygame.draw.rect(screen, PANEL_COLOR, (30, 430, 1104, 250))
    pygame.draw.rect(screen, BORDER_COLOR, (30, 430, 1104, 250), 1)
    draw_text(screen, "РАЗМЕСТИТЬ СЕНСОРНЫЙ ЗАКАЗ НА КРЕМНИЕВЫЕ ПЛАСТИНЫ (доставка 1 месяц)", font_title, AMBER, 45,
              450)

    cost_10k = 10000 * console.unit_cost
    b1_color = GREEN if player.cash >= cost_10k else RED
    draw_button(screen, btn_order_10k, f"Партия: 10k шт. (-${cost_10k:,.0f}) (1 мес.)", font_body, PANEL_COLOR,
                b1_color,
                TEXT_WHITE)

    cost_50k = 50000 * console.unit_cost
    b2_color = GREEN if player.cash >= cost_50k else RED
    draw_button(screen, btn_order_50k, f"Партия: 50k шт. (-${cost_50k:,.0f}) (2 мес.)", font_body, PANEL_COLOR,
                b2_color,
                TEXT_WHITE)

    cost_100k = 100000 * console.unit_cost
    b3_color = GREEN if player.cash >= cost_100k else RED
    draw_button(screen, btn_order_100k, f"Партия: 100k шт. (-${cost_100k:,.0f}) (3 мес.)", font_body, PANEL_COLOR,
                b3_color,
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


def render_licenses_tab(screen, player, games_list, current_year, font_title, font_body):
    """СТРАНИЦА 5: Игры и Лицензирование"""
    draw_text(screen, "ЛИЦЕНЗИРОВАНИЕ СТОРОННИХ ИГРОВЫХ ХИТОВ (GAME LICENSING)", font_title, AMBER, 30, 70)
    draw_text(screen, "Выкупайте эксклюзивные права, чтобы поднять уровень роялти и размер библиотеки!", font_body,
              TEXT_MUTED, 30, 95)

    offset_y = 130
    # Показываем только игры доступного года
    year_games = [g for g in games_list if g.year_available == current_year]

    if not year_games:
        draw_text(screen, "В этом году новых предложений от сторонних студий нет.", font_large, TEXT_MUTED, 45, 150)
        return

    for g in year_games:
        pygame.draw.rect(screen, PANEL_COLOR, (30, offset_y, 1164, 80))
        pygame.draw.rect(screen, BORDER_COLOR, (30, offset_y, 1164, 80), 1)

        draw_text(screen, f"{g.name} ({g.year_available} г.)", font_title, AMBER, 45, offset_y + 15)
        draw_text(screen, g.desc, font_body, TEXT_WHITE, 45, offset_y + 40)
        draw_text(screen, f"Мин. Мощность: {g.min_power} HW  |  Буст Роялти: +${g.base_royalty:.2f}/мес", font_body,
                  TEXT_MUTED, 45, offset_y + 58)

        # Кнопка покупки лицензии
        btn_rect = pygame.Rect(950, offset_y + 20, 220, 40)
        if g.acquired_by == 'player':
            draw_button(screen, btn_rect, "ВЫКУПЛЕНО", font_body, GREEN, GREEN, BG_COLOR)
        elif g.acquired_by is not None:
            draw_button(screen, btn_rect, f"У ИИ ({g.acquired_by})", font_body, PANEL_COLOR, RED, RED)
        else:
            cost_label = f"Выкупить: ${g.license_cost:,.0f}"
            b_color = GREEN if player.cash >= g.license_cost else RED
            draw_button(screen, btn_rect, cost_label, font_body, PANEL_COLOR, b_color, TEXT_WHITE)

        offset_y += 95