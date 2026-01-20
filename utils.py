"""
вспомогательные утилиты для работы с графиками
содержит функции для отображения и форматирования
"""

import matplotlib.pyplot as plt


def show_plot(fig, title):
    """
    показывает график пользователю
    ждет, пока пользователь закроет окно графика
    """
    print(f"✓ График отображен: {title}")
    print("Закройте окно графика, чтобы продолжить...")

    # показываем график и ждем закрытия окна
    plt.show(block=True)

    return None


def format_currency(value):
    """форматирует число как валюту (краткий формат)"""
    if value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value / 1_000:.0f}K"
    else:
        return f"${value:,.0f}"