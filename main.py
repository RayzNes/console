# main.py

import pygame
import sys
from config import START_YEAR, END_YEAR
from data_loader import load_data
from ai_competitor import AICompany
from market import Market

# Настройка экрана Pygame
pygame.init()
WIDTH, HEIGHT = 1024, 768
screen = pygame.display.get_surface() or pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Console Tycoon: Silicon Race - Stage 2 (Data Layer)")
clock = pygame.time.Clock()

# Палитра
BG_COLOR = (14, 16, 24)
PANEL_COLOR = (21, 24, 38)
BORDER_COLOR = (38, 44, 66)
TEXT_WHITE = (235, 240, 250)
TEXT_MUTED = (115, 128, 142)
GREEN = (46, 204, 113)
BLUE = (52, 152, 219)
RED = (231, 76, 60)
AMBER = (241, 196, 15)

font_title = pygame.font.Font(None, 24)
font_body = pygame.font.Font(None, 18)
font_large = pygame.font.Font(None, 32)


def draw_text(surface, text, font, color, x, y):
    img = font.render(text, True, color)
    surface.blit(img, (x, y))


def draw_chart(surface, x, y, w, h, market_history, consoles):
    pygame.draw.rect(surface, PANEL_COLOR, (x, y, w, h))
    pygame.draw.rect(surface, BORDER_COLOR, (x, y, w, h), 1)

    for i in range(1, 5):
        grid_y = y + int(h * (i / 5))
        pygame.draw.line(surface, BORDER_COLOR, (x, grid_y), (x + w, grid_y), 1)

    if not market_history:
        return

    # Динамический максимум графика по оси Y для лучшей наглядности краха 1983 года
    max_val = 18_000_000
    years_total = END_YEAR - START_YEAR
    step_x = w / years_total

    # Отрисовка емкости рынка (Фактическая с учетом событий)
    points_capacity = []
    for idx, step in enumerate(market_history):
        px = x + int(idx * step_x)
        py = y + h - int((step["capacity"] / max_val) * h)
        points_capacity.append((px, py))
    if len(points_capacity) > 1:
        pygame.draw.lines(surface, TEXT_MUTED, False, points_capacity, 1)

    # Отрисовка линий консолей
    for console in consoles:
        points_console = []
        for idx, step in enumerate(market_history):
            year_val = START_YEAR + idx
            sales = console.sales_history.get(year_val, 0)
            px = x + int(idx * step_x)
            py = y + h - int((sales / max_val) * h)
            points_console.append((px, py))
        if len(points_console) > 1:
            pygame.draw.lines(surface, console.color, False, points_console, 3)


def main():
    # Загружаем базу компонентов и исторических триггеров
    components_db, events_db = load_data()
    market = Market(events_db)

    # Список исторических ИИ-конкурентов
    ai_companies = [
        AICompany("Magnavox", "budget", 1972, (240, 240, 240)),
        AICompany("Atari Inc.", "balanced", 1977, (230, 126, 34)),
        AICompany("Mattel Electronics", "premium", 1979, (52, 152, 219)),
        AICompany("Coleco Industries", "premium", 1982, (46, 204, 113))
    ]

    auto_play = False
    auto_tick_cooldown = 0

    while True:
        # 1. Спавн консолей ИИ, если пришел их исторический год
        for ai in ai_companies:
            if not ai.launched and market.current_year >= ai.launch_year:
                console = ai.design_console(components_db)
                market.add_console(console)

        # Обработка ввода
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    market.simulate_year()
                elif event.key == pygame.K_SPACE:
                    auto_play = not auto_play
                elif event.key == pygame.K_r:
                    main()
                    return

        if auto_play:
            auto_tick_cooldown += 1
            if auto_tick_cooldown >= 90:
                market.simulate_year()
                auto_tick_cooldown = 0

        # Рендеринг интерфейса
        screen.fill(BG_COLOR)

        # Шапка
        draw_text(screen, "CONSOLE TYCOON: SILICON RACE", font_large, AMBER, 30, 25)
        draw_text(screen, "Stage 2: Core Engine with Components & Dynamic Macro Events", font_body, TEXT_MUTED, 30, 55)

        # Панель 1: Индикаторы рынка (Ширина: 280)
        pygame.draw.rect(screen, PANEL_COLOR, (30, 90, 280, 360))
        pygame.draw.rect(screen, BORDER_COLOR, (30, 90, 280, 360), 1)
        draw_text(screen, "MARKET STATISTICS", font_title, TEXT_WHITE, 45, 105)
        draw_text(screen, f"Year: {market.current_year}", font_large, AMBER, 45, 140)

        inflation = market.get_inflation_factor()
        capacity = market.get_market_capacity()
        draw_text(screen, f"Inflation Factor: x{inflation:.2f}", font_body, TEXT_WHITE, 45, 190)
        draw_text(screen, f"Potential Customers: {capacity:,}", font_body, TEXT_WHITE, 45, 215)

        pygame.draw.line(screen, BORDER_COLOR, (45, 255), (295, 255), 1)
        draw_text(screen, "CONTROLS:", font_body, AMBER, 45, 270)
        draw_text(screen, "[S] - Advance 1 Year Manual", font_body, TEXT_WHITE, 45, 295)
        draw_text(screen, "[Space] - Toggle Auto-Advance", font_body, TEXT_WHITE, 45, 315)
        draw_text(screen, "[R] - Reset Simulation", font_body, TEXT_WHITE, 45, 335)
        status_text = "AUTO ADVANCE: ON" if auto_play else "AUTO ADVANCE: OFF"
        draw_text(screen, status_text, font_body, GREEN if auto_play else RED, 45, 365)

        # Панель 2: Новости и События (Ширина: 300)
        pygame.draw.rect(screen, PANEL_COLOR, (330, 90, 300, 360))
        pygame.draw.rect(screen, BORDER_COLOR, (330, 90, 300, 360), 1)
        draw_text(screen, "NEWS & HISTORICAL EVENT TIKER", font_title, AMBER, 345, 105)

        if market.active_event_info:
            ev = market.active_event_info
            draw_text(screen, f"EVENT: {ev['name']}", font_title, GREEN, 345, 145)

            # Посимвольный перенос текста описания события
            words = ev["desc"].split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if len(test_line) < 32:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            offset_text_y = 180
            for line in lines:
                draw_text(screen, line, font_body, TEXT_WHITE, 345, offset_text_y)
                offset_text_y += 20

            draw_text(screen, f"Effect type: {ev['effect_type']}", font_body, AMBER, 345, offset_text_y + 15)
            draw_text(screen, f"Multiplier/Mod: {ev['effect_value']}", font_body, TEXT_WHITE, 345, offset_text_y + 35)
        else:
            draw_text(screen, "No significant historical events", font_body, TEXT_MUTED, 345, 145)
            draw_text(screen, "are happening this year.", font_body, TEXT_MUTED, 345, 165)

        # Панель 3: Консоли и Спецификации чипов (Ширина: 344)
        pygame.draw.rect(screen, PANEL_COLOR, (650, 90, 344, 360))
        pygame.draw.rect(screen, BORDER_COLOR, (650, 90, 344, 360), 1)
        draw_text(screen, "ACTIVE HARDWARE SPECS", font_title, TEXT_WHITE, 665, 105)

        active_consoles = [c for c in market.consoles if c.launch_year <= market.current_year]
        offset_y = 135
        for console in active_consoles:
            draw_text(screen, f"{console.name}", font_title, console.color, 665, offset_y)
            prev_sales = console.sales_history.get(market.current_year - 1, 0)
            draw_text(screen, f"Prev Sales: {prev_sales:,} units", font_body, TEXT_WHITE, 665, offset_y + 20)

            # Выводим инфу по компонентам, собранным ИИ
            if console.spec_info:
                specs = console.spec_info
                cpu_txt = f"CPU: {specs['cpu_name']}"
                gpu_txt = f"GPU: {specs['gpu_name']}"
                med_txt = f"Media: {specs['media_name']}"
                draw_text(screen, f"{cpu_txt} | {gpu_txt}", font_body, TEXT_MUTED, 665, offset_y + 35)
                draw_text(screen, f"{med_txt} (Cost: ${specs['cost']:.0f})", font_body, TEXT_MUTED, 665, offset_y + 50)
            else:
                draw_text(screen, "Built on pre-analyzed chips", font_body, TEXT_MUTED, 665, offset_y + 35)

            pygame.draw.line(screen, BORDER_COLOR, (665, offset_y + 70), (980, offset_y + 70), 1)
            offset_y += 75

        # График
        draw_chart(screen, 30, 480, 964, 250, market.history, market.consoles)
        draw_text(screen,
                  "Chart: Gray dashed (Market Capacity) | Colored (AI Console Sales). Run to 1983 to see the Video Game Crash!",
                  font_body, TEXT_MUTED, 35, 740)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()