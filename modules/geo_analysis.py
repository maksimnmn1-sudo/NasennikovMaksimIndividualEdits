"""
географический анализ продаж
топы штатов и городов по выручке
"""

import matplotlib.pyplot as plt
import pandas as pd
from config import PLOT_CONFIG, TOP_N
from utils import show_plot, format_currency


def plot_state_revenue(df):
    """график топ-5 штатов по выручке"""

    # группируем по штатам, суммируем выручку
    state_revenue = df.groupby('State')['Amount'].sum()

    # топ-5 штатов
    top_5_states = state_revenue.nlargest(TOP_N).sort_values()

    # создаем график
    fig, ax = plt.subplots(figsize=PLOT_CONFIG['figsize'])

    # рисуем горизонтальные столбцы
    bars = ax.barh(top_5_states.index.astype(str), top_5_states.values,
                   color='#e74c3c', alpha=0.7)

    # добавляем значения на столбцы
    for bar in bars:
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height() / 2,
                format_currency(width),
                ha='left', va='center', fontsize=10)

    ax.set_title('Топ-5 штатов по выручке', fontsize=14, fontweight='bold')
    ax.set_xlabel('Выручка ($)')
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    show_plot(fig, 'Топ-5 штатов по выручке')


def plot_city_revenue(df):
    """график топ-5 городов по выручке"""

    # группируем по городам, суммируем выручку
    city_revenue = df.groupby('City')['Amount'].sum()

    # топ-5 городов
    top_5_cities = city_revenue.nlargest(TOP_N).sort_values()

    fig, ax = plt.subplots(figsize=PLOT_CONFIG['figsize'])

    # горизонтальные столбцы оранжевого цвета
    bars = ax.barh(top_5_cities.index.astype(str), top_5_cities.values,
                   color='#f39c12', alpha=0.7)

    # добавляем значения на столбцы
    for bar in bars:
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height() / 2,
                format_currency(width),
                ha='left', va='center', fontsize=10)

    ax.set_title('Топ-5 городов по выручке', fontsize=14, fontweight='bold')
    ax.set_xlabel('Выручка ($)')
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    show_plot(fig, 'Топ-5 городов по выручке')