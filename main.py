# main.py

import pygame
import sys
from config import START_YEAR, END_YEAR
from data_loader import load_data
from ai_competitor import AICompany
from market import Market
from player import PlayerCompany, ConsoleProject
from console import Console

# Инициализация графики
pygame.init()
WIDTH, HEIGHT = 1224, 1024
screen = pygame.display.get_surface() or pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Console Tycoon: Silicon Race - Interactive Control Panel")
clock = pygame.time.Clock()

# Палитра
BG_COLOR = (12, 14, 20)
PANEL_COLOR = (18, 21, 32)
BORDER_COLOR = (32, 38, 58)
TEXT_WHITE = (235, 240, 250)
TEXT_MUTED = (115, 128, 142)
GREEN = (46, 204, 113)
BLUE = (52, 152, 219)
RED = (231, 76, 60)
AMBER = (241, 196, 15)

# Шрифты
font_title = pygame.font.Font(None, 24)
font_body = pygame.font.Font(None, 18)
font_large = pygame.font.Font(None, 32)

# Глобальное состояние меню
current_tab = "market"

# ----------------------------------------------------
# Координационная сетка интерактивных сенсорных кнопок
# ----------------------------------------------------

# 1. Верхний бар навигации (Вкладки)
tab_rects = {
    "market": pygame.Rect(20, 10, 160, 30),
    "rd": pygame.Rect(190, 10, 240, 30),
    "factory": pygame.Rect(440, 10, 160, 30),
    "finance": pygame.Rect(610, 10, 160, 30)
}

# 2. Глобальные сенсорные кнопки времени (Вкладка Рынок, левая панель)
btn_step = pygame.Rect(45, 280, 250, 35)
btn_auto = pygame.Rect(45, 325, 250, 35)
btn_reset = pygame.Rect(45, 370, 250, 35)

# 3. Сенсорные кнопки управления R&D кадрами
btn_hire = pygame.Rect(665, 245, 140, 35)
btn_fire = pygame.Rect(825, 245, 140, 35)

# 4. Сенсорные кнопки проектирования новой консоли
btn_cpu_select = pygame.Rect(45, 155, 500, 35)
btn_gpu_select = pygame.Rect(45, 205, 500, 35)
btn_media_select = pygame.Rect(45, 255, 500, 35)
btn_margin_dec = pygame.Rect(45, 305, 50, 30)
btn_margin_inc = pygame.Rect(210, 305, 50, 30)
btn_launch_project = pygame.Rect(45, 360, 500, 45)

# 5. Сенсорные кнопки заказа партий на фабрике
btn_order_10k = pygame.Rect(45, 490, 270, 40)
btn_order_50k = pygame.Rect(335, 490, 270, 40)
btn_order_100k = pygame.Rect(625, 490, 270, 40)


def draw_text(surface, text, font, color, x, y):
    img = font.render(text, True, color)
    surface.blit(img, (x, y))


def draw_button(surface, rect, text, font, bg_color, border_color, text_color):
    """Вспомогательная функция отрисовки сенсорной кнопки"""
    pygame.draw.rect(surface, bg_color, rect, border_radius=4)
    pygame.draw.rect(surface, border_color, rect, width=1, border_radius=4)
    img = font.render(text, True, text_color)
    img_rect = img.get_rect(center=rect.center)
    surface.blit(img, img_rect)


def draw_chart(surface, x, y, w, h, market_history, consoles):
    pygame.draw.rect(surface, PANEL_COLOR, (x, y, w, h))
    pygame.draw.rect(surface, BORDER_COLOR, (x, y, w, h), 1)

    for i in range(1, 5):
        grid_y = y + int(h * (i / 5))
        pygame.draw.line(surface, BORDER_COLOR, (x, grid_y), (x + w, grid_y), 1)

    if not market_history:
        return

    # Динамический масштаб (для месяцев)
    max_val = 1_500_000
    steps_total = (END_YEAR - START_YEAR + 1) * 12
    step_x = w / steps_total

    # Отрисовка емкости рынка (Фактическая с учетом событий)
    points_capacity = []
    for idx, step in enumerate(market_history):
        px = x + int(idx * step_x)
        py = y + h - int((step["capacity"] / max_val) * h)
        points_capacity.append((px, py))
    if len(points_capacity) > 1:
        pygame.draw.lines(surface, TEXT_MUTED, False, points_capacity, 1)

    # Отрисовка линий продаж консолей
    for console in consoles:
        points_console = []
        for idx, step in enumerate(market_history):
            year_val = START_YEAR + (idx // 12)
            month_val = 1 + (idx % 12)
            time_key = f"{year_val}_{month_val}"
            sales = console.sales_history.get(time_key, 0)
            px = x + int(idx * step_x)
            py = y + h - int((sales / max_val) * h)
            points_console.append((px, py))
        if len(points_console) > 1:
            pygame.draw.lines(surface, console.color, False, points_console, 2)


def main():
    global current_tab
    components_db, events_db = load_data()
    market = Market(events_db)

    # Инициализация Игрока
    player = PlayerCompany("MySilicon Corp", start_cash=1_200_000.0)

    # Исторические ИИ-соперники
    ai_companies = [
        AICompany("Magnavox", "budget", 1972, (200, 200, 200)),
        AICompany("Atari Inc.", "balanced", 1977, (230, 126, 34)),
        AICompany("Mattel Electronics", "premium", 1979, (52, 152, 219)),
        AICompany("Coleco Industries", "premium", 1982, (46, 204, 113))
    ]

    # Списки выбора компонентов для R&D
    selected_cpu_idx = 0
    selected_gpu_idx = 0
    selected_media_idx = 0
    margin_value = 1.5

    auto_play = False
    auto_tick_cooldown = 0

    while True:
        # Спавн ИИ-конкурентов
        for ai in ai_companies:
            if not ai.launched and market.current_year >= ai.launch_year:
                console = ai.design_console(components_db)
                market.add_console(console)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Обработка кликов мыши (Интерактивные сенсорные кнопки) [1, 2]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # ЛКМ
                    mouse_pos = event.pos

                    # 1. Верхнее навигационное меню
                    for t_key, rect in tab_rects.items():
                        if rect.collidepoint(mouse_pos):
                            current_tab = t_key

                    # 2. Сенсорные элементы вкладки РЫНОК
                    if current_tab == "market":
                        if btn_step.collidepoint(mouse_pos):
                            simulate_one_month(market, player, components_db)
                        elif btn_auto.collidepoint(mouse_pos):
                            auto_play = not auto_play
                        elif btn_reset.collidepoint(mouse_pos):
                            main()
                            return

                    # 3. Сенсорные элементы вкладки R&D
                    elif current_tab == "rd":
                        # Кадровые кнопки доступны всегда во вкладке R&D
                        if btn_hire.collidepoint(mouse_pos):
                            player.engineers += 1
                        elif btn_fire.collidepoint(mouse_pos):
                            player.engineers = max(1, player.engineers - 1)

                        if not player.active_project:
                            # Изменение компонентов проекта
                            if btn_cpu_select.collidepoint(mouse_pos):
                                selected_cpu_idx = (selected_cpu_idx + 1) % len(components_db["cpus"])
                            elif btn_gpu_select.collidepoint(mouse_pos):
                                selected_gpu_idx = (selected_gpu_idx + 1) % len(components_db["gpus"])
                            elif btn_media_select.collidepoint(mouse_pos):
                                selected_media_idx = (selected_media_idx + 1) % len(components_db["media"])
                            elif btn_margin_dec.collidepoint(mouse_pos):
                                margin_value = max(1.1, margin_value - 0.1)
                            elif btn_margin_inc.collidepoint(mouse_pos):
                                margin_value = min(3.0, margin_value + 0.1)
                            elif btn_launch_project.collidepoint(mouse_pos):
                                cpu = components_db["cpus"][selected_cpu_idx]
                                gpu = components_db["gpus"][selected_gpu_idx]
                                med = components_db["media"][selected_media_idx]
                                player.active_project = ConsoleProject("MyConsole v1", cpu, gpu, med, margin_value)

                    # 4. Сенсорные элементы вкладки ФАБРИКА
                    elif current_tab == "factory" and player.released_consoles:
                        p_console = player.released_consoles[0]
                        if btn_order_10k.collidepoint(mouse_pos):
                            order_silicon(player, p_console, 10_000)
                        elif btn_order_50k.collidepoint(mouse_pos):
                            order_silicon(player, p_console, 50_000)
                        elif btn_order_100k.collidepoint(mouse_pos):
                            order_silicon(player, p_console, 100_000)

            # Дублирующие горячие клавиши (сохранено для опытных игроков)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    current_tab = "market"
                elif event.key == pygame.K_F2:
                    current_tab = "rd"
                elif event.key == pygame.K_F3:
                    current_tab = "factory"
                elif event.key == pygame.K_F4:
                    current_tab = "finance"
                elif event.key == pygame.K_s:
                    simulate_one_month(market, player, components_db)
                elif event.key == pygame.K_SPACE:
                    auto_play = not auto_play
                elif event.key == pygame.K_r:
                    main()
                    return

        # Логика автоматического шага
        if auto_play:
            auto_tick_cooldown += 1
            if auto_tick_cooldown >= 30:
                simulate_one_month(market, player, components_db)
                auto_tick_cooldown = 0

        # Рендеринг кадра
        screen.fill(BG_COLOR)

        # Отрисовка верхнего бара
        pygame.draw.rect(screen, PANEL_COLOR, (0, 0, WIDTH, 50))
        pygame.draw.line(screen, BORDER_COLOR, (0, 50), (WIDTH, 50), 2)

        # Отрисовка сенсорных вкладок
        for t_key, rect in tab_rects.items():
            is_active = (current_tab == t_key)
            bg = AMBER if is_active else PANEL_COLOR
            border = AMBER if is_active else BORDER_COLOR
            text_col = BG_COLOR if is_active else TEXT_WHITE

            label = {
                "market": "РЫНОК", "rd": "РАЗРАБОТКА (R&D)",
                "factory": "ФАБРИКА", "finance": "ФИНАНСЫ"
            }[t_key]

            draw_button(screen, rect, label, font_title, bg, border, text_col)

        # Статистика финансов и времени в шапке
        draw_text(screen, f"Год: {market.current_year} | Месяц: {market.current_month}", font_title, AMBER, 1020, 15)
        cash_color = GREEN if player.cash >= 0 else RED
        draw_text(screen, f"Баланс: ${player.cash:,.0f}", font_title, cash_color, 820, 15)

        # Рендеринг активной вкладки
        if current_tab == "market":
            render_market_tab(market, auto_play)
        elif current_tab == "rd":
            render_rd_tab(player, components_db, selected_cpu_idx, selected_gpu_idx, selected_media_idx, margin_value)
        elif current_tab == "factory":
            render_factory_tab(player)
        elif current_tab == "finance":
            render_finance_tab(player)

        pygame.display.flip()
        clock.tick(60)


def simulate_one_month(market, player: PlayerCompany, components_db):
    rd_expense = 0.0
    if player.active_project:
        eng_points = player.engineers * 5.0
        project = player.active_project
        project.advance_development(eng_points)
        rd_expense = player.engineers * 500.0

        if project.phase == "ready":
            player_console = Console(
                name=project.name,
                launch_year=market.current_year,
                price=project.retail_price,
                hardware_power=project.hardware_power,
                library_size=5,
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
    if player.released_consoles:
        player.released_consoles[0].inventory += arrived_stock

    salaries = player.get_monthly_salaries()
    monthly_sales = market.simulate_month()

    hw_revenue = 0.0
    royalty_revenue = 0.0
    manufacturing_cost = 0.0
    warehouse_cost = 0.0
    marketing_expenses = 0.0

    if player.released_consoles:
        p_console = player.released_consoles[0]
        units_sold = monthly_sales.get(p_console, 0)
        hw_revenue = units_sold * p_console.price
        royalty_revenue = p_console.installed_base * 0.15
        marketing_expenses = p_console.marketing_budget
        warehouse_cost = p_console.inventory * 1.0

    for order in player.production_orders:
        if order["months_left"] == 1:
            manufacturing_cost += order["quantity"] * order["unit_cost"]

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


def order_silicon(player: PlayerCompany, console: Console, qty: int):
    player.production_orders.append({
        "months_left": 1,
        "quantity": qty,
        "unit_cost": console.unit_cost
    })


# Вкладка РЫНОК
def render_market_tab(market, auto_play):
    draw_text(screen, "МАРКЕТИНГОВАЯ ОБСТАНОВКА И ПРОДАЖИ", font_title, AMBER, 30, 70)
    draw_text(screen, "Легенда: Серый пунктир - емкость рынка | Желтый - Ваша система | Другие - ИИ", font_body,
              TEXT_MUTED, 30, 95)

    # Большой график продаж (адаптирован под размер 1224x1024)
    draw_chart(screen, 30, 120, 1164, 300, market.history, market.consoles)

    # Левая панель управления симуляцией времени
    pygame.draw.rect(screen, PANEL_COLOR, (30, 440, 280, 280))
    pygame.draw.rect(screen, BORDER_COLOR, (30, 440, 280, 280), 1)
    draw_text(screen, "СЕНСОРНЫЙ КОНТРОЛЬ", font_title, TEXT_WHITE, 45, 455)

    # Отрисовка интерактивных кнопок времени
    draw_button(screen, btn_step, "ШАГ ХОДА (+1 Месяц)", font_body, PANEL_COLOR, BORDER_COLOR, AMBER)

    auto_color = GREEN if auto_play else RED
    auto_text = "АВТО-СИМУЛЯЦИЯ: ВКЛ" if auto_play else "АВТО-СИМУЛЯЦИЯ: ВЫКЛ"
    draw_button(screen, btn_auto, auto_text, font_body, PANEL_COLOR, BORDER_COLOR, auto_color)

    draw_button(screen, btn_reset, "СБРОСИТЬ ИГРУ", font_body, PANEL_COLOR, RED, TEXT_WHITE)

    # Правая панель со списком активных систем на рынке
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


# Вкладка R&D (РАЗРАБОТКА)
def render_rd_tab(player: PlayerCompany, components_db, sel_cpu, sel_gpu, sel_media, margin):
    draw_text(screen, "ОТДЕЛ ИССЛЕДОВАНИЙ И РАЗРАБОТОК (R&D)", font_title, AMBER, 30, 70)

    # Управление кадрами (Правая панель)
    pygame.draw.rect(screen, PANEL_COLOR, (650, 110, 544, 320))
    pygame.draw.rect(screen, BORDER_COLOR, (650, 110, 544, 320), 1)
    draw_text(screen, "ШТАТ ИНЖЕНЕРОВ R&D", font_title, TEXT_WHITE, 665, 125)
    draw_text(screen, f"Активные инженеры: {player.engineers}", font_large, AMBER, 665, 160)
    draw_text(screen, f"Фонд з/п (в месяц): ${player.get_monthly_salaries():,.0f}", font_body, TEXT_WHITE, 665, 200)

    # Отрисовка сенсорных кнопок кадров
    draw_button(screen, btn_hire, "НАНЯТЬ (+1)", font_body, PANEL_COLOR, GREEN, GREEN)
    draw_button(screen, btn_fire, "УВОЛИТЬ (-1)", font_body, PANEL_COLOR, RED, RED)

    if not player.active_project:
        # Панель создания новой консоли (если нет активного проекта)
        pygame.draw.rect(screen, PANEL_COLOR, (30, 110, 600, 320))
        pygame.draw.rect(screen, BORDER_COLOR, (30, 110, 600, 320), 1)
        draw_text(screen, "ПРОЕКТИРОВАНИЕ НОВОЙ АРХИТЕКТУРЫ (Кликайте по плашкам для смены)", font_title, TEXT_WHITE,
                  45, 125)

        cpu = components_db["cpus"][sel_cpu]
        gpu = components_db["gpus"][sel_gpu]
        med = components_db["media"][sel_media]
        unit_cost = cpu["cost"] + gpu["cost"] + med["cost"]
        retail_p = int(unit_cost * margin)
        power = (cpu["power"] + gpu["power"]) * med["power_mult"]

        # Интерактивные селекторы комплектующих
        draw_button(screen, btn_cpu_select, f"Процессор: {cpu['name']} (${cpu['cost']})", font_body, PANEL_COLOR,
                    BORDER_COLOR, TEXT_WHITE)
        draw_button(screen, btn_gpu_select, f"Видеочип: {gpu['name']} (${gpu['cost']})", font_body, PANEL_COLOR,
                    BORDER_COLOR, TEXT_WHITE)
        draw_button(screen, btn_media_select, f"Носитель: {med['name']} (${med['cost']})", font_body, PANEL_COLOR,
                    BORDER_COLOR, TEXT_WHITE)

        # Контроллеры наценки
        draw_text(screen, f"Коммерческая наценка: {margin:.1f}x (Розничная цена: ${retail_p})", font_body, TEXT_WHITE,
                  45, 312)
        draw_button(screen, btn_margin_dec, "-", font_title, PANEL_COLOR, BORDER_COLOR, RED)
        draw_button(screen, btn_margin_inc, "+", font_title, PANEL_COLOR, BORDER_COLOR, GREEN)

        # Статистика проекта
        draw_text(screen, f"Сила системы: {power:.1f} HW  |  Себестоимость: ${unit_cost:.1f}", font_body, TEXT_MUTED,
                  300, 312)

        # Кнопка отправки в запуск
        draw_button(screen, btn_launch_project, "ЗАПУСТИТЬ ПРОЕКТ В РАЗРАБОТКУ", font_title, PANEL_COLOR, AMBER, AMBER)
    else:
        # Панель прогресса текущей разработки
        pygame.draw.rect(screen, PANEL_COLOR, (30, 110, 600, 320))
        pygame.draw.rect(screen, BORDER_COLOR, (30, 110, 600, 320), 1)
        project = player.active_project
        draw_text(screen, f"В РАЗРАБОТКЕ: {project.name}", font_large, AMBER, 45, 125)

        phase_titles = {
            "design": "ПРОЕКТИРОВАНИЕ ЧИПОВ И ПЛАТ (R&D)",
            "prototype": "ОТЛАДКА И СБОРКА ПРОТОТИПА",
            "testing": "ТЕСТИРОВАНИЕ И НАПИСАНИЕ ПО",
            "ready": "ГОТОВО К ЗАПУСКУ"
        }
        draw_text(screen, f"Текущая фаза: {phase_titles[project.phase]}", font_title, TEXT_WHITE, 45, 175)

        # Прогресс-бар
        pygame.draw.rect(screen, BG_COLOR, (45, 210, 500, 25))
        pygame.draw.rect(screen, GREEN, (45, 210, int(500 * (project.progress / 100.0)), 25))
        draw_text(screen, f"{project.progress:.1f}%", font_body, BG_COLOR, 270, 215)

        draw_text(screen, f"Ожидаемая розничная цена: ${project.retail_price}", font_body, TEXT_WHITE, 45, 255)
        draw_text(screen, f"Качество софта на старте: {project.quality:.2f}", font_body, GREEN, 45, 280)


# Вкладка ФАБРИКА
def render_factory_tab(player: PlayerCompany):
    draw_text(screen, "УПРАВЛЕНИЕ ЛОГИСТИКОЙ И ЗАКАЗОМ КРЕМНИЕВЫХ ПЛАСТИН", font_title, AMBER, 30, 70)

    if not player.released_consoles:
        draw_text(screen, "У вас нет запущенных на рынке систем. Сначала завершите R&D во вкладке [F2].", font_large,
                  TEXT_MUTED, 30, 150)
        return

    console = player.released_consoles[0]

    # Складские запасы
    pygame.draw.rect(screen, PANEL_COLOR, (30, 110, 450, 300))
    pygame.draw.rect(screen, BORDER_COLOR, (30, 110, 450, 300), 1)
    draw_text(screen, f"ТЕКУЩИЕ ЗАПАСЫ: {console.name}", font_title, TEXT_WHITE, 45, 125)

    draw_text(screen, f"На складе: {console.inventory:,} шт.", font_large, AMBER, 45, 165)
    draw_text(screen, f"Себестоимость производства: ${console.unit_cost:.1f} / шт.", font_body, TEXT_WHITE, 45, 215)
    draw_text(screen, f"Ежемесячная стоимость хранения: $1.00 / шт.", font_body, TEXT_MUTED, 45, 240)

    # Очередь производства
    pygame.draw.rect(screen, PANEL_COLOR, (500, 110, 634, 300))
    pygame.draw.rect(screen, BORDER_COLOR, (500, 110, 634, 300), 1)
    draw_text(screen, "ОЧЕРЕДЬ КРЕМНИЕВЫХ ПОСТАВОК", font_title, TEXT_WHITE, 515, 125)

    offset_y = 165
    if not player.production_orders:
        draw_text(screen, "Производственных заказов у подрядчиков нет.", font_body, TEXT_MUTED, 515, 165)
    else:
        for order in player.production_orders:
            draw_text(screen, f"Партия: {order['quantity']:,} шт. | Осталось: {order['months_left']} мес.", font_body,
                      GREEN, 515, offset_y)
            offset_y += 25

    # Панель заказов готовых партий
    pygame.draw.rect(screen, PANEL_COLOR, (30, 430, 1104, 250))
    pygame.draw.rect(screen, BORDER_COLOR, (30, 430, 1104, 250), 1)
    draw_text(screen, "РАЗМЕСТИТЬ СЕНСОРНЫЙ ЗАКАЗ НА КРЕМНИЕВЫЕ ПЛАСТИНЫ (доставка 1 месяц)", font_title, AMBER, 45,
              450)

    # Отрисовка кнопок заказов
    cost_10k = 10000 * console.unit_cost
    draw_button(screen, btn_order_10k, f"Партия: 10k шт. (-${cost_10k:,.0f})", font_body, PANEL_COLOR, BORDER_COLOR,
                TEXT_WHITE)

    cost_50k = 50000 * console.unit_cost
    draw_button(screen, btn_order_50k, f"Партия: 50k шт. (-${cost_50k:,.0f})", font_body, PANEL_COLOR, BORDER_COLOR,
                TEXT_WHITE)

    cost_100k = 100000 * console.unit_cost
    draw_button(screen, btn_order_100k, f"Партия: 100k шт. (-${cost_100k:,.0f})", font_body, PANEL_COLOR, BORDER_COLOR,
                TEXT_WHITE)


# Вкладка ФИНАНСЫ
def render_finance_tab(player: PlayerCompany):
    draw_text(screen, "ЕЖЕМЕСЯЧНЫЙ ФИНАНСОВЫЙ ОТЧЕТ КОМПАНИИ (ЗА ПРОШЛЫЙ ХОД)", font_title, AMBER, 30, 70)

    pygame.draw.rect(screen, PANEL_COLOR, (30, 110, 1164, 570))
    pygame.draw.rect(screen, BORDER_COLOR, (30, 110, 1164, 570), 1)

    fin = player.financials_last_month

    # Выручка
    draw_text(screen, "ВЫРУЧКА (REVENUES)", font_title, GREEN, 60, 135)
    draw_text(screen, "Продажи железа (Hardware Sales):", font_body, TEXT_WHITE, 60, 175)
    draw_text(screen, f"${fin['hw_revenue']:,.2f}", font_body, TEXT_WHITE, 400, 175)

    draw_text(screen, "Роялти от стороннего софта (Royalty Revenue):", font_body, TEXT_WHITE, 60, 205)
    draw_text(screen, f"${fin['royalty_revenue']:,.2f}", font_body, TEXT_WHITE, 400, 205)

    # Расходы
    draw_text(screen, "РАСХОДЫ (OPERATING EXPENSES)", font_title, RED, 60, 260)

    draw_text(screen, "Оплата поставок чипов (Manufacturing Cost):", font_body, TEXT_WHITE, 60, 300)
    draw_text(screen, f"-${fin['manufacturing_cost']:,.2f}", font_body, TEXT_WHITE, 400, 300)

    draw_text(screen, "Затраты на прототипирование R&D:", font_body, TEXT_WHITE, 60, 330)
    draw_text(screen, f"-${fin['rd_expenses']:,.2f}", font_body, TEXT_WHITE, 400, 330)

    draw_text(screen, "Реклама и Маркетинг (Marketing):", font_body, TEXT_WHITE, 60, 360)
    draw_text(screen, f"-${fin['marketing_expenses']:,.2f}", font_body, TEXT_WHITE, 400, 360)

    draw_text(screen, "Зарплаты штата инженеров:", font_body, TEXT_WHITE, 60, 390)
    draw_text(screen, f"-${fin['salaries']:,.2f}", font_body, TEXT_WHITE, 400, 390)

    draw_text(screen, "Содержание нераспроданных запасов на складе:", font_body, TEXT_WHITE, 60, 420)
    draw_text(screen, f"-${fin['warehouse_cost']:,.2f}", font_body, TEXT_WHITE, 400, 420)

    pygame.draw.line(screen, BORDER_COLOR, (60, 470), (1130, 470), 2)

    # Итог
    draw_text(screen, "ЧИСТАЯ ПРИБЫЛЬ (NET INCOME)", font_title, AMBER, 60, 500)
    profit_color = GREEN if fin["net_profit"] >= 0 else RED
    draw_text(screen, f"${fin['net_profit']:,.2f}", font_large, profit_color, 400, 500)


if __name__ == "__main__":
    main()