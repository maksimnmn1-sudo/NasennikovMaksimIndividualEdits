"""
анализ выручки по временным периодам
содержит функции для построения графиков по дням, неделям и месяцам
"""

import matplotlib.pyplot as plt
import pandas as pd
from config import PLOT_CONFIG, TOP_N
from utils import show_plot, format_currency


def plot_daily_revenue(df):
    """график выручки по дням"""

    # группируем данные по дате, суммируем выручку
    daily_revenue = df.groupby('Order Date')['Amount'].sum()

    # создаем график
    fig, ax = plt.subplots(figsize=PLOT_CONFIG['figsize'])

    # рисуем линейный график
    ax.plot(daily_revenue.index, daily_revenue.values,
            color='#3498db', linewidth=2)

    # настройки графика
    ax.set_title('Выручка по дням', fontsize=14, fontweight='bold')
    ax.set_xlabel('Дата')
    ax.set_ylabel('Выручка ($)')
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=45)  # поворачиваем подписи дат

    plt.tight_layout()
    show_plot(fig, 'Выручка по дням')


def plot_weekly_revenue(df):
    """график выручки по неделям"""

    # создаем столбец с годом и номером недели
    df['YearWeek'] = df['Order Date'].dt.strftime('%Y-W%W')

    # группируем по неделям
    weekly_revenue = df.groupby('YearWeek')['Amount'].sum()

    fig, ax = plt.subplots(figsize=PLOT_CONFIG['figsize'])

    # рисуем график с точками
    ax.plot(range(len(weekly_revenue)), weekly_revenue.values,
            color='#2ecc71', linewidth=2, marker='o', markersize=4)

    ax.set_title('Выручка по неделям', fontsize=14, fontweight='bold')
    ax.set_xlabel('Неделя')
    ax.set_ylabel('Выручка ($)')

    # настраиваем метки на оси X (каждую 5-ю неделю)
    x_positions = range(len(weekly_revenue))
    x_labels = weekly_revenue.index

    display_indices = list(range(0, len(x_labels), 5))
    display_positions = [x_positions[i] for i in display_indices]
    display_labels = [x_labels[i] for i in display_indices]

    ax.set_xticks(display_positions)
    ax.set_xticklabels(display_labels, rotation=45)

    # добавляем деления для всех недель (без подписей)
    ax.set_xticks(x_positions, minor=True)
    ax.grid(True, alpha=0.3, which='both')

    plt.tight_layout()
    show_plot(fig, 'Выручка по неделям')


def plot_monthly_revenue(df):
    """график выручки по месяцам"""

    # группируем по месяцам
    monthly_revenue = df.groupby('YearMonth')['Amount'].sum()

    fig, ax = plt.subplots(figsize=PLOT_CONFIG['figsize'])

    # рисуем столбчатую диаграмму
    bars = ax.bar(monthly_revenue.index.astype(str), monthly_revenue.values,
                  color='#9b59b6', alpha=0.7)

    # добавляем значения поверх столбцов
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height,
                format_currency(height),
                ha='center', va='bottom', fontsize=8)

    ax.set_title('Выручка по месяцам', fontsize=14, fontweight='bold')
    ax.set_xlabel('Месяц')
    ax.set_ylabel('Выручка ($)')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    show_plot(fig, 'Выручка по месяцам')